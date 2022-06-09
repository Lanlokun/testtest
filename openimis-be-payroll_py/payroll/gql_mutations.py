import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from graphene.relay import mutation
from .apps import PayrollConfig
from graphene import InputObjectType
from .models import Payroll, PayrollMutation , PayrollCycle, PayrollPaymentDetails, PayrollPaymentDetailsMutation
from programs.models import Programs, Scheme
from location.models import Location
from insuree.models import Insuree, IdentificationType
from service_provider.models import Paypoint, ServiceProvider
from datetime import datetime

#..........................................Payroll..................................
class PayrollInputType(OpenIMISMutation.Input):
    """
    Define the payrolle input types
    """
    id = graphene.Int(required=False, read_only=True)

    uuid = graphene.String(required=False)

    uuids = graphene.List(graphene.String)

    payroll_cycle_uuid = graphene.String(required=True)

    location_code = graphene.String(required=False)

    psp_uuid = graphene.String(required=False)

    approve_all = graphene.Boolean(required=False)

    is_approved = graphene.Boolean(required=False)

def generate_payroll(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        client_mutation_id = data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    
    try:
        payroll_cycle_uuid = data.pop('payroll_cycle_uuid')
        payrollcycle = PayrollCycle.objects.get(uuid=payroll_cycle_uuid)
        data['payrollcycle'] = payrollcycle
        
        scheme = payrollcycle.scheme
        data['scheme'] = scheme
        data['expectedamount'] = payrollcycle.scheme.amount
        data['start_date'] = payrollcycle.start_month +' '+ payrollcycle.start_year
        data['end_date'] = payrollcycle.end_month + ' ' + payrollcycle.end_year

        location_code = data.pop('location_code')
        location = Location.objects.get(code=location_code)
        data['location'] = location
        data['location_type'] = location.type

        programs =  Programs.objects.filter(scheme=data['scheme'])

        psp_uuid = data.pop('psp_uuid')
        psp = ServiceProvider.objects.get(uuid=psp_uuid)
        data['psp'] = psp

        for p in programs:
            new_data = {}
            new_data['insuree'] = p.insuree
            new_data['payrollcycle'] = data['payrollcycle']
            new_data['expectedamount'] = data['expectedamount']
            new_data['start_date'] = data['start_date']
            new_data['end_date'] = data['end_date']
            new_data['location'] = data['location']
            new_data['location_type'] = data['location_type']
            new_data['psp'] = data['psp']
            new_data['scheme'] = data['scheme']
            from core.utils import TimeUtils
            data['validity_from'] = TimeUtils.now()
            new_data['rundate'] = TimeUtils.now()
            new_data['audit_user_id'] = 1

            payroll = Payroll.objects.create(**new_data)
        
            # save record to database
            payroll.save()
            # log mutation through signal binding everytime a mutation occur
            PayrollMutation.object_mutated(user, client_mutation_id=client_mutation_id, Payroll=payroll)

        return None
    except Exception as exc:
        return [{
                'message': "Failed to generate payroll",
                'detail': str(exc)}]

class GenPayrollMutation(OpenIMISMutation):
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

        # calles the create and update method and returns the created record from the Payroll object
        payroll = generate_payroll(data, user)
            
        return payroll
       
class GeneratePayrollMutation(GenPayrollMutation):
    """
    Create new Payroll record
    """
    _mutation_module = "payroll"
    _mutation_class = "GeneratePayrollMutation"

    # Sets the inputtype of this mutation
    class Input(PayrollInputType):
        pass

    # perform mutation asyncroniously
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in GenPayrollMutation that checks permission
            and call generate_payroll to perform the creation on Payroll record.
            """
            return cls.do_mutate(PayrollConfig.gql_mutation_create_payroll_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Payroll mutation failed with exceptions",
                'detail': str(exc)}]

def approveAllPayroll(payroll, user):
    payroll.save()
    return payroll

def updatepayroll(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
        # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
        # get payroll_cycle_uuid from data
    payroll_uuid = data.pop('uuid') if 'uuid' in data else None
    if payroll_uuid:
        # fetch payroll_cycle by uuid
        payroll = Payroll.objects.get(uuid=payroll_uuid)
        [setattr(payroll, key, data[key]) for key in data]
        is_approved = data.get("is_approved")
        if(is_approved):
            key ="transaction_number"
            transaction_number = generateTranscationNumber(payroll.scheme.code)
            setattr(payroll, key, transaction_number)
    else:
        return [{
                'message': "Payroll mutation failed because payroll uuid is empty",
                'detail': str("Payroll mutation failed because payroll uuid is empty")}]
        
    # save record to database
    payroll.save()
    return payroll

def generateTranscationNumber(scheme_code):
    transcation_number= scheme_code + str(datetime.now().timestamp())
    return transcation_number.replace(".", "")

class UpdatePayrollMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        approve_all = data.get("approve_all")
        if(approve_all):
            result = []
            payrolls = cls.getAllByPayrollcycle(PayrollConfig.gql_query_payroll_perms, user, **data)
            for p in payrolls:
                [setattr(p, key, data[key]) for key in data]
                key ="transaction_number"
                transaction_number = generateTranscationNumber(p.scheme.code)
                setattr(p, key, transaction_number)
                pay = approveAllPayroll(p, user)
                result.append(pay)
            payroll = result
        else:
            # calles the create and update method and returns the created record from the payrollcycle object
            payroll = updatepayroll(data, user)

        # log mutation through signal binding everytime a mutation occur
        if(payroll):
            PayrollMutation.object_mutated(user, client_mutation_id=client_mutation_id, Payroll=payroll)
        
        return None
        
    @classmethod
    def getAllByPayrollcycle(cls, perms, user, **data):

        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # Check if client_mutation_id is passed in data
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        # Check if client_mutation_label is passed in data
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        payrollcycle = PayrollCycle.objects.get(Q(uuid=data.get('payroll_cycle_uuid')))

        return Payroll.objects.filter(
            Q(payrollcycle=payrollcycle),
            *filter_validity(**data)
        ).order_by('start_date', 'end_date',)

class ApprovePayrollMutation(UpdatePayrollMutation):
    """
    Update Payroll record
    """
    _mutation_module = "payroll"
    _mutation_class = "ApprovePayrollMutation"

    # Sets the inputtype of this mutation
    class Input(PayrollInputType):
        pass

    # perform mutation asyncroniously
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in GenPayrollMutation that checks permission
            and call generate_payroll to perform the creation on Payroll record.
            """
            data['approved_by_id'] = 1
            
            return cls.do_mutate(PayrollConfig.gql_mutation_update_payroll_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Payroll mutation failed with exceptions",
                'detail': str(exc)}]

class DeletePayrollMutation(OpenIMISMutation):
    """
    Delete Payroll by uuid
    """
    _mutation_module = "payroll"
    _mutation_class = "DeletePayrollMutation"

    # Sets the input type of this mutation
    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(PayrollConfig.gql_mutation_delete_payroll_perms):
                raise PermissionDenied(_("unauthorized"))

            # get Payroll object by uuid
            payroll = Payroll.objects.get(uuid=data['uuid'])

            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            payroll.validity_to = now
            payroll.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete payroll. An exception had occured",
                'detail': str(exc)}]

# ..........................Payment Details...........................................

class PayrollPaymentDetailsType(OpenIMISMutation.Input):
    """
    Define the Payroll Payment Details input types
    """
    id = graphene.Int(required=False, read_only=True)

    uuid = graphene.String(required=False)

    uuids = graphene.List(graphene.String)

    payroll_uuid = graphene.String(required=True)

    transaction_number = graphene.String(required=True)

    payment_status = graphene.Boolean(required=False)

    received_amount = graphene.Decimal(required=True)

    payment_date = graphene.Date(required=True)

    receipt_number = graphene.String(required=False)
    
    type_of_payment = graphene.String(required=False)

    transfer_fee =graphene.Decimal(required=False)

    reasons_for_not_paid = graphene.String(required=False)
    
    receiver_name = graphene.String(required=False)

    identification_type = graphene.String(max_length=1, required=False)

    identification_number = graphene.String(required=False)
    
    receiver_phone_number =graphene.String(required=False)

    psp_uuid = graphene.String(required=True)

    paypoint_uuid = graphene.String(required=True)

def update_or_create_payment_details(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    # get payment_details_uuid from data
    payment_details_uuid = data.pop('uuid') if 'uuid' in data else None

    payroll_uuid = data.pop('payroll_uuid') if 'payroll_uuid' in data else None

    psp_uuid = data.pop('psp_uuid') if 'psp_uuid' in data else None

    paypoint_uuid = data.pop('paypoint_uuid') if 'paypoint_uuid' in data else None

    identification_type = data.pop('identification_type') if 'identification_type' in data else None

    if payroll_uuid:
        payroll = Payroll.objects.get(uuid=payroll_uuid)
        data['payroll'] = payroll

    if psp_uuid:
        psp = ServiceProvider.objects.get(uuid=psp_uuid)
        data['psp'] = psp

    if paypoint_uuid:
        paypoint = Paypoint.objects.get(uuid=paypoint_uuid)
        data['paypoint'] = paypoint

    if identification_type:
        id_type = IdentificationType.objects.get(code=identification_type)
        data['identification_type'] = id_type

    if payment_details_uuid:
        # fetch payment_details by uuid
        payment_details = PayrollPaymentDetails.objects.get(uuid=payment_details_uuid)
        [setattr(payment_details, key, data[key]) for key in data]
    else:
        # create new payment_details object
        payment_details = PayrollPaymentDetails.objects.create(**data)
        
    # save record to database
    payment_details.save()
    return payment_details
    
class CreateOrUpdatePayrollPaymentDetailsMutation(OpenIMISMutation):
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

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the payrollcycle object
        paymentDetails = update_or_create_payment_details(data, user)

        # log mutation through signal binding everytime a mutation occur
        PayrollPaymentDetailsMutation.object_mutated(user, client_mutation_id=client_mutation_id, PayrollPaymentDetails=paymentDetails)
        
        return None

class AddPayrollPaymentdetailsMutation(CreateOrUpdatePayrollPaymentDetailsMutation):
    """
    Add Payment Details record
    """
    _mutation_module = "payroll"
    _mutation_class = "AddPayrollPaymentdetailsMutation"

    # Sets the inputtype of this mutation
    class Input(PayrollPaymentDetailsType):
        pass

    # perform mutation asyncroniously
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdatePayrollCycleMutation that checks permission
            and call update_or_create_payment_details to perform the creation on payrollcycle record.
            """
            return cls.do_mutate(PayrollConfig.gql_mutation_create_payroll_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Payroll cycle mutation failed with exceptions",
                'detail': str(exc)}]

class UpdatePayrollPaymentdetailsMutation(CreateOrUpdatePayrollPaymentDetailsMutation):
    """
    Update an existing payrollcycle
    """
    _mutation_module = "payroll"
    _mutation_class = "UpdatePayrollPaymentdetailsMutation"

    # Sets the input type of this mutation
    class Input(PayrollPaymentDetailsType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdatePayrollCycleMutation that checks permission
            and call update_or_create_payment_details to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(PayrollConfig.gql_mutation_update_payroll_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Payroll cycle mutation update failed with exceptions",
                'detail': str(exc)}
            ]

class DeletePayrollPaymentdetailsMutation(OpenIMISMutation):
    """
    Delete Payroll Payment details by uuid
    """
    _mutation_module = "payroll"
    _mutation_class = "DeletePayrollPaymentdetailsMutation"

    # Sets the input type of this mutation
    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(PayrollConfig.gql_mutation_delete_payroll_perms):
                raise PermissionDenied(_("unauthorized"))

            # get payrollcycle object by uuid
            payrollPaymentDetails = PayrollPaymentDetails.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            payrollPaymentDetails.validity_to = now
            payrollPaymentDetails.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete Payroll Payment Details. An exception had occured",
                'detail': str(exc)}]