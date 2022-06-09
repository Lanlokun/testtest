import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from graphene.relay import mutation
from .apps import ProgramsConfig
from graphene import InputObjectType
from .models import *
from insuree.models import *


class SchemeInputType(OpenIMISMutation.Input):
    """
    Define the Scheme input types
    """
    id = graphene.Int(required=False, read_only=True)
    uuid = graphene.String(required=False)
    name = graphene.String(required=True)
    start_date = graphene.Date(required=False)
    end_date = graphene.Date(required=False)
    code = graphene.String(required=False)
    status = graphene.String(required=True)
    scheme_type = graphene.String(required=True)
    amount = graphene.Decimal(required=True)



def update_or_create_scheme(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    # get scheme_uuid from data
    scheme_uuid = data.pop('uuid') if 'uuid' in data else None

    if scheme_uuid:
        # fetch scheme by uuid
        prScheme = Scheme.objects.get(uuid=scheme_uuid)
        [setattr(prScheme, key, data[key]) for key in data]
    else:
        # create new scheme object
        prScheme = Scheme.objects.create(**data)
        
    # save record to database
    prScheme.save()
    return prScheme

class CreateOrUpdateSchemeMutation(OpenIMISMutation):
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

        # calles the create and update method and returns the created record from the scheme object
        prScheme = update_or_create_scheme(data, user)

        # log mutation through signal binding everytime a mutation occur
        SchemeMutation.object_mutated(user, client_mutation_id=client_mutation_id, Scheme=prScheme)
        
        return None

class CreateSchemeMutation(CreateOrUpdateSchemeMutation):
    """
    Create new scheme record
    """
    _mutation_module = "programs"
    _mutation_class = "CreateSchemeMutation"

    # Sets the inputtype of this mutation
    class Input(SchemeInputType):
        pass

    # perform mutation asyncroniously
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateSchemeMutation that checks permission
            and call update_or_create_scheme to perform the creation on scheme record.
            """
            return cls.do_mutate(ProgramsConfig.gql_mutation_create_prScheme_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Scheme mutation failed with exceptions",
                'detail': str(exc)}]

class UpdateSchemeMutation(CreateOrUpdateSchemeMutation):
    """
    Update an existing scheme
    """
    _mutation_module = "programs"
    _mutation_class = "UpdateSchemeMutation"

    # Sets the input type of this mutation
    class Input(SchemeInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateSchemeMutation that checks permission
            and call update_or_create_scheme to perform the update on the scheme record.
            """
            return cls.do_mutate(ProgramsConfig.gql_mutation_update_prScheme_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "scheme mutation update failed with exceptions",
                'detail': str(exc)}
            ]


class DuplicateSchemeMutation(CreateOrUpdateSchemeMutation):

    _mutation_module = "programs"
    _mutation_class = "DuplicateSchemeMutation"

    class Input(SchemeInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # ensure we don't duplicate the existing one, but recreate a new one!
            if 'scheme_uuid' in data:
                data.pop('scheme_uuid')
            # data["status"] = Scheme.STATUS_IDLE
            # data["stage"] = Scheme.STAGE_RENEWED
            return cls.do_mutate(ProgramsConfig.gql_mutation_duplicate_perScheme_perms, user, **data)
        except Exception as exc:
            return [{
                'message': _("Scheme.mutation.failed_to_duplicate_policy"),
                'detail': str(exc)}]



class DeleteSchemeMutation(OpenIMISMutation):
    """
    Delete programs by uuid
    """
    _mutation_module = "programs"
    _mutation_class = "DeleteSchemeMutation"

    # Sets the input type of this mutation
    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ProgramsConfig.gql_mutation_delete_prScheme_perms):
                raise PermissionDenied(_("unauthorized"))

            # get programs object by uuid
            prScheme = Scheme.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            prScheme.validity_to = now
            prScheme.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete scheme. An exception had occured",
                'detail': str(exc)}]

class ProgramsInputType(OpenIMISMutation.Input):
    
    id = graphene.String(required=False, read_only=True)
    uuid = graphene.String(required=False)
    scheme_uuid = graphene.String(required=True)
    insuree_uuid = graphene.String(required=True)


   #This section create or update program mutation....
def update_or_create_programs(data, user):

    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    
    programsID = data.pop('uuid') if 'uuid' in data else None

    if programsID:
        # fetch program by uuid
        programs = Programs.objects.get(uuid=programsID)
        [setattr(programs, key, data[key]) for key in data]
    else:
        # create new program object
        programs = Programs.objects.create(**data)
        
    # save record to database
    programs.save()
    return programs

class CreateOrUpdateProgramsMutation(OpenIMISMutation):
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
        
        #This create instance of insuree and sschem
        insuree = data.pop('insuree_uuid')
        scheme = data.pop('scheme_uuid')

        prinsuree =Insuree.objects.get(uuid=insuree)
        prscheme =Scheme.objects.get(uuid=scheme)

        data['insuree'] = prinsuree
        data['scheme'] = prscheme

        
        # calles the create and update method and returns the created record from the programs object
        programs = update_or_create_programs(data, user)

        # log mutation through signal binding everytime a mutation occur
        ProgramsMutation.object_mutated(user, Programs=programs)
        
        return None
    #End of create or update programs


# This class create mtation for service provider.....
class CreateProgramsMutation(CreateOrUpdateProgramsMutation):
    _mutation_module = "programs"
    _mutation_class = "CreateProgramsMutation"

    class Input(ProgramsInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateProgramsMutation that checks permission
            and call update_or_create_programs to perform the update on the programs record.
            """
            return cls.do_mutate(ProgramsConfig.gql_mutation_create_programs_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Programs mutation failed",
                'detail': str(exc)}]
    #End of programs Mutation section...................
    
  
class UpdateProgramsMutation(CreateOrUpdateProgramsMutation):
    """
    Update an existing PSP
    """
    _mutation_module = "programs"
    _mutation_class = "UpdateProgramsMutation"

    # Sets the input type of this mutation
    class Input(ProgramsInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateProgramsMutation that checks permission
            and call update_or_create_programs to perform the update on the programs record.
            """
            return cls.do_mutate(ProgramsConfig.gql_mutation_update_programs_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Programs mutation update failed with exceptions",
                'detail': str(exc)}
            ]
#End of update prorams

    
    #This class delete programs mutation....
class DeleteProgramsMutation(OpenIMISMutation):
    _mutation_module = "programs"
    _mutation_class = "DeleteProgramsMutation"

    class Input(OpenIMISMutation.Input):
        
        uuid = graphene.String()
        
        
                        
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(ProgramsConfig.gql_mutation_delete_programs_perms):
                raise PermissionDenied(_("unauthorized"))

            # get programs object by uuid
            programs = Programs.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            programs.validity_to = now
            programs.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete program provider. An exception had occured",
                'detail': str(exc)}]
    #End of delete service provider subLevel mutation....