import graphene
from django.utils.translation import gettext as _
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from graphene import InputObjectType
from location.models import Location
from graphene.relay import mutation
from .models import *
from .apps import ServiceProviderConfig
from core import datetime
from core.utils import TimeUtils


# This class creates service provider Legal Form input type....
class ServiceProviderLegalFormInputType(OpenIMISMutation.Input):

    code = graphene.String(required=False, read_only=True)
    legal_form = graphene.String(required=True)
    ValidityFrom = graphene.Date(required=False)
    ValidityTo = graphene.Date(required=False)
# End of service provider Legal Form input type....

   # This section  create or update ServiceProviderLevelMutation....


def update_legal_form(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')

    legalFormID = data.pop('code') if 'code' in data else None

    if legalFormID:
        # fetch legalForm by id
        legalForm = ServiceProviderLegalForm.objects.get(code=legalFormID)
        [setattr(legalForm, key, data[key]) for key in data]
    else:
        # create new legalForm object
        legalForm = ServiceProviderLegalForm.objects.get(code=legalFormID)

    # save record to database
    legalForm.save()
    return legalForm


class CreateOrUpdateServiceProviderLegalFormMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # data['audit_user_id'] = user.id_for_audit
        # data['validity_from'] = TimeUtils.now()

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the serviceProvider object
        serviceProviderLegalForm = update_legal_form(data, user)

        # log mutation through signal binding everytime a mutation occur
        ServiceProviderLegalFormMutation.object_mutated(
            user, client_mutation_id=client_mutation_id, ServiceProviderLegalForm=serviceProviderLegalForm)

        return None
# End of create or update ServiceProviderLevelMutation


# This class create mtation for service provider legal form.....
class CreateServiceProviderLegalFormMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "CreateServiceProviderLegalFormMutation"

    class Input(ServiceProviderLegalFormInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # TODO move this verification to OIMutation
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))

            # data['audit_user_id'] = user.id_for_audit
            from core.utils import TimeUtils
            data['validity_from'] = TimeUtils.now()

            ServiceProviderLegalForm.objects.create(**data)
        except Exception as exc:
            return [{
                'message': "Service Provider Legal Form mutation failed",
                'detail': str(exc)}]
    # End of create mtation for service provider legal form.....


# This class update service legal-form
class UpdateServiceProviderLegalFormMutation(CreateOrUpdateServiceProviderLegalFormMutation):
    """
    Update an existing legal form
    """
    _mutation_module = "service_provider"
    _mutation_class = "UpdateServiceProviderLegalFormMutation"

    # Sets the input type of this mutation
    class Input(ServiceProviderLegalFormInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdatePayrollCycleMutation that checks permission
            and call update_or_create_payroll_cycle to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_update_service_provider_legalForm_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Service provider legalForm mutation update failed with exceptions",
                'detail': str(exc)}
            ]
# End of update service provider legal form mutation..........


# This class delete service provider Legal Form....
class DeleteServiceProviderLegalFormMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "DeleteServiceProviderLegalFormMutation"

    class Input(OpenIMISMutation.Input):
        code = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ServiceProviderConfig.gql_mutation_delete_service_legalForm_perms):
                raise PermissionDenied(_("unauthorized"))

            # get legalForm object by code
            legalForm = ServiceProviderLegalForm.objects.get(code=data['code'])

            # get current date time
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            legalForm.validity_to = now
            legalForm.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete legalFor. An exception had occured",
                'detail': str(exc)}]
    # End of delete service provider Legal Form....

# This class creates service provider Level input type....


class ServiceProviderLevelInputType(OpenIMISMutation.Input):

    code = graphene.String(required=False, read_only=True)
    level = graphene.String(required=True)
    ValidityFrom = graphene.Date(required=False)
    ValidityTo = graphene.Date(required=False)
# End of service provider Level input type.............

   # This section create or update ServiceProviderLevelMutation....


def update_level(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')

    levelID = data.pop('code') if 'code' in data else None

    if levelID:
        # fetch level by code
        level = ServiceProviderLevel.objects.get(code=levelID)
        [setattr(level, key, data[key]) for key in data]
    else:
        # create new level object
        level = ServiceProviderLevel.objects.get(code=levelID)

    # save record to database
    level.save()
    return level


class CreateOrUpdateServiceProviderLevelMutation(OpenIMISMutation):

    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # data['audit_user_id'] = user.id_for_audit
        # data['validity_from'] = TimeUtils.now()

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the serviceProvider object
        serviceProviderLevel = update_level(data, user)

        # log mutation through signal binding everytime a mutation occur
        ServiceProviderLevelMutation.object_mutated(
            user, client_mutation_id=client_mutation_id, ServiceProviderLevel=serviceProviderLevel)

        return None
# End of create or update ServiceProviderLevelMutation


# This class create mtation for service provider level.....
class CreateServiceProviderlevelMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "CreateServiceProviderLevelMutation"

    class Input(ServiceProviderLevelInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # TODO move this verification to OIMutation
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))

            # data['audit_user_id'] = user.id_for_audit
            from core.utils import TimeUtils
            data['validity_from'] = TimeUtils.now()

            ServiceProviderLevel.objects.create(**data)
        except Exception as exc:
            return [{
                'message': "Service Provider Level mutation failed",
                'detail': str(exc)}]
    # End of create mtation for service provider level.............

 # This class update service legal-form


class UpdateServiceProviderLevelMutation(CreateOrUpdateServiceProviderLevelMutation):
    """
    Update an existing legal form
    """
    _mutation_module = "service_provider"
    _mutation_class = "UpdateServiceProviderLevelMutation"

    # Sets the input type of this mutation
    class Input(ServiceProviderLevelInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateServiceProviderLevelMutation that checks permission
            and call update_or_create_service_provider_level to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_update_service_provider_level_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Service provider level mutation update failed with exceptions",
                'detail': str(exc)}
            ]
# End of update service provider level..........

    # This class delete service provider Levels....


class DeleteServiceProviderLevelMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "DeleteServiceProviderLevelMutation"

    class Input(OpenIMISMutation.Input):
        code = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ServiceProviderConfig.gql_mutation_delete_service_level_perms):
                raise PermissionDenied(_("unauthorized"))

            # get level object by code
            level = ServiceProviderLevel.objects.get(code=data['code'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            level.validity_to = now
            level.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete level. An exception had occured",
                'detail': str(exc)}]
    # End of delete service provider Level mutation....

    # This class creates service provider Sub-Level input type........


class ServiceProviderSubLevelInputType(OpenIMISMutation.Input):

    code = graphene.String(required=False, read_only=True)
    sub_level = graphene.String(required=True)
    ValidityFrom = graphene.Date(required=False)
    ValidityTo = graphene.Date(required=False)
# End of service provider Level input type....


# This section create or update ServiceProviderSubLevel....
def update_sub_level(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')

    subLevelID = data.pop('code') if 'code' in data else None

    if subLevelID:
        # fetch sub_level by code
        subLevel = ServiceProviderSubLevel.objects.get(code=subLevelID)
        [setattr(subLevel, key, data[key]) for key in data]
    else:
        # create new sub_level object
        subLevel = ServiceProviderSubLevel.objects.get(code=subLevelID)

    # save record to database
    subLevel.save()
    return subLevel


class CreateOrUpdateServiceProviderSubLevelMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # data['audit_user_id'] = user.id_for_audit
        # data['validity_from'] = TimeUtils.now()

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the serviceProvider object
        serviceProviderSubLevel = update_sub_level(data, user)

        # log mutation through signal binding everytime a mutation occur
        ServiceProviderSubLevelMutation.object_mutated(
            user, client_mutation_id=client_mutation_id, ServiceProviderSubLevel=serviceProviderSubLevel)

        return None
# End of create or update ServiceProviderSubLevelMutation


# This class create mtation for service provider Sub-level.....
class CreateServiceProviderSublevelMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "CreateServiceProviderSubLevelMutation"

    class Input(ServiceProviderSubLevelInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # TODO move this verification to OIMutation
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))

            # data['audit_user_id'] = user.id_for_audit
            from core.utils import TimeUtils
            data['validity_from'] = TimeUtils.now()

            ServiceProviderSubLevel.objects.create(**data)
        except Exception as exc:
            return [{
                'message': "Service Provider SubLevel mutation failed",
                'detail': str(exc)}]
    # End of create mtation for service provider Sub-legal form.....


# This class update service sublevel
class UpdateServiceProviderSubLevelMutation(CreateOrUpdateServiceProviderSubLevelMutation):
    """
    Update an existing legal form
    """
    _mutation_module = "service_provider"
    _mutation_class = "UpdateServiceProviderSubLevelMutation"

    # Sets the input type of this mutation
    class Input(ServiceProviderSubLevelInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateServiceProviderSubLevelMutation that checks permission
            and call update_or_create_service_provider_sublevel to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_update_service_provider_subLevel_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Service provider sublevel mutation update failed with exceptions",
                'detail': str(exc)}
            ]
# End of update service provider sublevel..........


# This class delete service provider subLevels....
class DeleteServiceProviderSubLevelMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "DeleteServiceProviderSubLevelMutation"

    class Input(OpenIMISMutation.Input):
        code = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ServiceProviderConfig.gql_mutation_delete_service_subLevel_perms):
                raise PermissionDenied(_("unauthorized"))

            # get level object by code
            sublevel = ServiceProviderSubLevel.objects.get(code=data['code'])

            # get current date time
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            sublevel.validity_to = now
            sublevel.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete sublevel. An exception had occured",
                'detail': str(exc)}]
    # End of delete service provider subLevel mutation....

# This class creates service provider input type....


class ServiceProviderInputType(OpenIMISMutation.Input):
    """
    Define the Scheme input types
    """

    id = graphene.String(required=False, read_only=True)
    uuid = graphene.String(required=False)
    legalFormCode = graphene.String(required=True)
    levelCode = graphene.String(required=True)
    subLevelCode = graphene.String(required=True)
    code = graphene.String(required=True)
    name = graphene.String(required=True)
    accountCode = graphene.String(required=True)
    address = graphene.String(required=False)
    phoneNumber = graphene.String(required=False)
    fax = graphene.String(required=False)
    email = graphene.String(required=False)
    ValidityFrom = graphene.Date(required=False)
    ValidityTo = graphene.Date(required=False)
# End of service provider input type....


# This section create or update service providers mutation....
def update_or_create_service_provider(data, user):

    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')

    serviceProvider_uuid = data.pop('uuid') if 'uuid' in data else None

    if serviceProvider_uuid:
        # fetch service_provider by uuid
        serviceProvider = ServiceProvider.objects.get(
            uuid=serviceProvider_uuid)
        [setattr(serviceProvider, key, data[key]) for key in data]
    else:
        # create new service provider object
        serviceProvider = ServiceProvider.objects.create(**data)

    # save record to database
    serviceProvider.save()
    return serviceProvider

# This section creates or update service provider mutation...


class CreateOrUpdateServiceProviderMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # data['audit_user_id'] = user.id_for_audit
        from core.utils import TimeUtils
        data['validity_from'] = TimeUtils.now()

        #  # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the serviceProvider object
        serviceProvider = update_or_create_service_provider(data, user)

        # log mutation through signal binding everytime a mutation occur
        ServiceProviderMutation.object_mutated(
            user, client_mutation_id=client_mutation_id,  ServiceProvider=serviceProvider)

        return None
# End of create or update ServiceProviderMutation


# This class create mtation for service provider.....
class CreateServiceProviderMutation(CreateOrUpdateServiceProviderMutation):
    """
    Create new service provider record
    """
    _mutation_module = "service_provider"
    _mutation_class = "CreateServiceProviderMutation"

    class Input(ServiceProviderInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):

        try:
            # TODO move this verification to OIMutation
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))

            # data['audit_user_id'] = user.id_for_audit
            from core.utils import TimeUtils
            # data['validityFrom'] = TimeUtils.now()

            legalFormCode = data.pop('legalFormCode')
            levelCode = data.pop('levelCode')
            subLevelCode = data.pop('subLevelCode')

            LegalForm = ServiceProviderLegalForm.objects.get(
                code=legalFormCode)
            level = ServiceProviderLevel.objects.get(code=levelCode)
            subLevel = ServiceProviderSubLevel.objects.get(code=subLevelCode)

            data['legalForm'] = LegalForm
            data['level'] = level
            data['subLevel'] = subLevel

            # ServiceProvider.objects.create(**data)
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_create_service_provider_perms, user, **data)

        except Exception as exc:
            return [{
                'message': "Service Provider mutation failed",
                'detail': str(exc)}]


# End of Service Provider Mutation section...................................


class UpdateServiceProviderMutation(CreateOrUpdateServiceProviderMutation):
    """
    Update an existing legal form
    """
    _mutation_module = "service_provider"
    _mutation_class = "UpdateServiceProviderMutation"

    # Sets the input type of this mutation
    class Input(ServiceProviderInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateServiceProviderMutation that checks permission
            and call update_or_create_service_provider to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_update_service_provider_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Service provider mutation update failed with exceptions",
                'detail': str(exc)}
            ]
# End of update service provider..........


# This class delete service providers mutation....
class DeleteServiceProviderMutation(OpenIMISMutation):
    """
    Delete service provider by uuid
    """
    _mutation_module = "service_provider"
    _mutation_class = "DeleteServiceProviderMutation"

    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ServiceProviderConfig.gql_mutation_delete_service_provider_perms):
                raise PermissionDenied(_("unauthorized"))

            # get srviceProvider object by uuid
            srviceProvider = ServiceProvider.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            srviceProvider.validity_to = now
            srviceProvider.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete srviceProvider. An exception had occured",
                'detail': str(exc)}]
    # End of delete service provider  mutation....

# This class creates service provider input type....


class PaypointInputType(OpenIMISMutation.Input):

    id = graphene.Int(required=False, read_only=True)
    uuid = graphene.String(required=False)
    paypointName = graphene.String(required=True)
    paypointCode = graphene.String(required=True)
    geolocation = graphene.String(required=True)
    location_uuid = graphene.String(required=True)
    serviceprovider_uuid = graphene.String(required=True)
    ValidityFrom = graphene.Date(required=False)
    ValidityTo = graphene.Date(required=False)
# End of pay point Mutation section...................................

   # This section create or update pay point mutation....


def update_or_update_pay_point(data, user):

    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')

    paypoint_uuid = data.pop('uuid') if 'uuid' in data else None

    if paypoint_uuid:
        # fetch service_provider by uuid
        paypoint = Paypoint.objects.get(uuid=paypoint_uuid)
        [setattr(paypoint, key, data[key]) for key in data]
    else:
        # create new service provider object
        paypoint = Paypoint.objects.create(**data)

    # save record to database
    paypoint.save()
    return paypoint


class CreateOrUpdatePaypointMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # data['audit_user_id'] = user.id_for_audit
        # data['validity_from'] = TimeUtils.now()

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the paymentServiceProvider object
        payPoint = update_or_update_pay_point(data, user)

        # log mutation through signal binding everytime a mutation occur
        PaypointMutation.object_mutated(
            user, client_mutation_id=client_mutation_id, Paypoint=payPoint)

        return None
    # End of create or update PayPointMutation


# This class create mtation for service provider.....
class CreatePaypointMutation(CreateOrUpdatePaypointMutation):
    """
    Create new pay point record
    """
    _mutation_module = "service_provider"
    _mutation_class = "CreatePaypointMutation"

    class Input(PaypointInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # TODO move this verification to OIMutation
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))

            # data['audit_user_id'] = user.id_for_audit
            data['validity_from'] = TimeUtils.now()

            locationUuid = data.pop('location_uuid')
            serviceProviderUuid = data.pop('serviceprovider_uuid')

            pspLocation = Location.objects.get(uuid=locationUuid)
            pspServiceProvider = ServiceProvider.objects.get(
                uuid=serviceProviderUuid)

            data['location'] = pspLocation
            data['serviceProvider'] = pspServiceProvider

            # PayPoint.objects.create(**data)
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_create_pay_point_perms, user, **data)

        except Exception as exc:
            return [{
                'message': "Pay point mutation failed",
                'detail': str(exc)}]
    # End of pay point Mutation section...................


class UpdatePaypointMutation(CreateOrUpdatePaypointMutation):
    """
    Update an existing PSP
    """
    _mutation_module = "service_provider"
    _mutation_class = "UpdatePaypointMutation"

    # Sets the input type of this mutation
    class Input(PaypointInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreatePaymentServiceProviderMutation that checks permission
            and call update_or_create_pay_point to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(ServiceProviderConfig.gql_mutation_update_pay_point_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Pay point mutation update failed with exceptions",
                'detail': str(exc)}
            ]
# End of update pay point..........

    # This class delete pay point mutation....


class DeletePaypointMutation(OpenIMISMutation):
    _mutation_module = "service_provider"
    _mutation_class = "DeletePaypointMutation"

    class Input(OpenIMISMutation.Input):

        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ServiceProviderConfig.gql_mutation_delete_pay_point_perms):
                raise PermissionDenied(_("unauthorized"))

            # get paymentServiceProvider object by uuid
            payPoint = Paypoint.objects.get(uuid=data['uuid'])

            # get current date time
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            payPoint.validity_to = now
            payPoint.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete pay point. An exception had occured",
                'detail': str(exc)}]
    # End of delete pay point mutation....
