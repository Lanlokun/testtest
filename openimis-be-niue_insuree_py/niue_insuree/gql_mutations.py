import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from graphene.relay import mutation
from .apps import NiueInsureeConfig
from graphene import InputObjectType
from .models import *
from insuree.models import *
from banks.models import *

class NiueInsureeInputType(OpenIMISMutation.Input):
    
    id = graphene.String(required=False, read_only=True)
    uuid = graphene.String(required=False)
    insuree_uuid = graphene.String(required=True)
    bank_uuid = graphene.String(required=True)
    birth_register_entry_number = graphene.String(required=False)
    date_of_registration = graphene.Date(required=False)
    father_first_name = graphene.String(required=False)
    father_last_name = graphene.String(required=False)
    father_residency_status = graphene.String(required=False)
    mother_first_name = graphene.String(required=False)
    mother_last_name = graphene.String(required=False)
    mother_residency_status = graphene.String(required=False)
    #Child Allowance Application Form
    applicant_relationship_to_the_child = graphene.String(required=False)
    proof_of_permanent_resident = graphene.String(required=False)
    proof_of_identity = graphene.String(required=False)
    #attachment?
    #Pension Application Form – 60 years
    #Yes / No option
    niuean_descendant = graphene.String(required=False)
    New_zealand_citizen = graphene.String(required=False)
    obtained_permanent_resident_status = graphene.String(required=False)
    Attached_certificate = graphene.String(required=False)
    receive_pension_payments = graphene.String(required=False)
    copy_of_passport = graphene.String(required=False)
    copy_of_permanent_residence_certificate = graphene.String(required=False)
    #Application For a Welfare Benefits
    nationality = graphene.String(required=False)
    citizenship = graphene.String(required=False)
    reason_for_applying_welfare_benefit = graphene.String(required=False)
    dependency_children = graphene.String(required=False)
    dependency_relative = graphene.String(required=False)
    Person_take_care_applicant = graphene.String(required=False)
    receive_any_support_at_all = graphene.String(required=False)
    receive_money_from_any_source = graphene.String(required=False)
    employed = graphene.String(required=False)
    weekly_wage = graphene.String(required=False)
    employment_for_you = graphene.String(required=False)
    if_NO_Why = graphene.String(required=False)
    cash_assets  = graphene.String(required=False)
    Debts_owing = graphene.String(required=False)
    interest_in_property = graphene.String(required=False)
    own_following_household_items = graphene.String(required=False)
    applicant_first_name = graphene.String(required=False)
    applicant_last_name = graphene.String(required=False)
    bank_number = graphene.String(required=False)
    applicant_DOB = graphene.String(required=False)
    tin_no = graphene.String(required=False)


#    #This section create or update niue insuree mutation....
# def update_or_create_niue_insuree(data, user):

#     # Check if client_mutation_id is passed in data
#     if "client_mutation_id" in data:
#         data.pop('client_mutation_id')
#     # Check if client_mutation_label is passed in data
#     if "client_mutation_label" in data:
#         data.pop('client_mutation_label')
    
#     niueInsureeID = data.pop('uuid') if 'uuid' in data else None

#     if niueInsureeID:
#         # fetch niue insuree by uuid
#         niue_insuree = NiueInsuree.objects.get(uuid=niueInsureeID)
#         [setattr(niue_insuree, key, data[key]) for key in data]
#     else:
#         # create new niue insuree object
#         niue_insuree = NiueInsuree.objects.create(**data)
        
#     # save record to database
#     niue_insuree.save()
#     return niue_insuree

# class CreateOrUpdateNiueInsureeMutation(OpenIMISMutation):
#     @classmethod
#     def do_mutate(cls, perms, user, **data):
#         # Check if user is authenticated
#         if type(user) is AnonymousUser or not user.id:
#             raise ValidationError(
#                 _("mutation.authentication_required"))

#         # Check if user has permission
#         if not user.has_perms(perms):
#             raise PermissionDenied(_("unauthorized"))

#         # data['audit_user_id'] = user.id_for_audit
#         from core.utils import TimeUtils
#         data['validity_from'] = TimeUtils.now()
        
#         #This create instance of insuree and sschem
#         insuree = data.pop('insuree_uuid')

#         insuree =Insuree.objects.get(uuid=insuree)

#         data['insuree'] = insuree

        
#         # calles the create and update method and returns the created record from the NiueInsureeobject
#         niue_insuree = update_or_create_niue_insuree(data, user)

#         # log mutation through signal binding everytime a mutation occur
#         NiueInsureeMutation.object_mutated(user, niueInsuree=niue_insuree)
        
#         return None
#     #End of create or update NiueInsuree


# # This class create mtation for service provider.....
# class CreateNiueInsureeMutation(CreateOrUpdateNiueInsureeMutation):
#     _mutation_module = "niueInsuree"
#     _mutation_class = "CreateNiueInsureeMutation"

#     class Input(NiueInsureeInputType):
#         pass

#     @classmethod
#     def async_mutate(cls, user, **data):
#         try:
#             """
#             Calls the do_mutate defiend in CreateNiueInsureeMutation that checks permission
#             and call update_or_create_NiueInsuree to perform the update on the NiueInsuree record.
#             """
#             return cls.do_mutate(NiueInsureeConfig.gql_mutation_create_niue_insuree_perms, user, **data)
#         except Exception as exc:
#             return [{
#                 'message': "Niue Insuree mutation failed",
#                 'detail': str(exc)}]
#     #End of NiueInsuree Mutation section...................
    
  
# class UpdateNiueInsureeMutation(CreateOrUpdateNiueInsureeMutation):
#     """
#     Update an existing PSP
#     """
#     _mutation_module = "niueInsuree"
#     _mutation_class = "UpdateNiueInsureeMutation"

#     # Sets the input type of this mutation
#     class Input(NiueInsureeInputType):
#         pass

#     @classmethod
#     def async_mutate(cls, user, **data):
#         try:
#             """
#             Calls the do_mutate defiend in CreateNiueInsureeMutation that checks permission
#             and call update_or_create_NiueInsuree to perform the update on the NiueInsuree record.
#             """
#             return cls.do_mutate(NiueInsureeConfig.gql_mutation_update_niue_insuree_perms, user, **data)
#         except Exception as exc:
#             return [{
#                 'message': "Niue Insuree mutation update failed with exceptions",
#                 'detail': str(exc)}
#             ]
# #End of update prorams

    
#     #This class delete NiueInsuree mutation....
# class DeleteNiueInsureeMutation(OpenIMISMutation):
#     _mutation_module = "niueInsuree"
#     _mutation_class = "DeleteNiueInsureeMutation"

#     class Input(OpenIMISMutation.Input):
        
#         uuid = graphene.String()
        
        
                        
#     @classmethod
#     def async_mutate(cls, user, **data):
#         try:
#             # Check if user has permission
#             if not user.has_perms(NiueInsureeConfig.gql_mutation_delete_niue_insuree_perms):
#                 raise PermissionDenied(_("unauthorized"))

#             # get NiueInsuree object by uuid
#             niue_insuree = NiueInsuree.objects.get(uuid=data['uuid'])

#             # get current date time
#             from core import datetime
#             now = datetime.datetime.now()

#             # Set validity_to to now to make the record invalid
#             niue_insuree.validity_to = now
#             niue_insuree.save()
#             return None
#         except Exception as exc:
#             return [{
#                 'message': "Faild to delete program provider. An exception had occured",
#                 'detail': str(exc)}]
#     #End of delete service provider subLevel mutation....

def update_or_create_niueInsuree(data, user):

    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    
    niueInsureeID = data.pop('uuid') if 'uuid' in data else None

    if niueInsureeID:
        # fetch program by uuid
        niueInsuree = NiueInsuree.objects.get(uuid=niueInsureeID)
        [setattr(niueInsuree, key, data[key]) for key in data]
    else:
        # create new program object
        niueInsuree = NiueInsuree.objects.create(**data)
        
    # save record to database
    niueInsuree.save()
    return niueInsuree

class CreateOrUpdateNiueInsureeMutation(OpenIMISMutation):
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
        bank = data.pop('bank_uuid')

        nInsuree =Insuree.objects.get(uuid=insuree)
        nBank =Bank.objects.get(uuid=bank)

        data['insuree'] = nInsuree
        data['bank'] = nBank

        
        # calles the create and update method and returns the created record from the NiueInsuree object
        niueInsuree = update_or_create_niueInsuree(data, user)

        # log mutation through signal binding everytime a mutation occur
        NiueInsureeMutation.object_mutated(user, NiueInsuree=niueInsuree)
        
        return None
    #End of create or update NiueInsuree


# This class create mtation for service provider.....
class CreateNiueInsureeMutation(CreateOrUpdateNiueInsureeMutation):
    _mutation_module = "niue"
    _mutation_class = "CreateNiueInsureeMutation"

    class Input(NiueInsureeInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateNiueInsureeMutation that checks permission
            and call update_or_create_NiueInsuree to perform the update on the NiueInsuree record.
            """
            return cls.do_mutate(NiueInsureeConfig.gql_mutation_create_niue_insuree_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "NiueInsuree mutation failed",
                'detail': str(exc)}]
    #End of NiueInsuree Mutation section...................
    
  
class UpdateNiueInsureeMutation(CreateOrUpdateNiueInsureeMutation):
    """
    Update an existing PSP
    """
    _mutation_module = "niue"
    _mutation_class = "UpdateNiueInsureeMutation"

    # Sets the input type of this mutation
    class Input(NiueInsureeInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateNiueInsureeMutation that checks permission
            and call update_or_create_NiueInsuree to perform the update on the NiueInsuree record.
            """
            return cls.do_mutate(NiueInsureeConfig.gql_mutation_update_niue_insuree_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "NiueInsuree mutation update failed with exceptions",
                'detail': str(exc)}
            ]
#End of update prorams

    
    #This class delete NiueInsuree mutation....
class DeleteNiueInsureeMutation(OpenIMISMutation):
    _mutation_module = "niue"
    _mutation_class = "DeleteNiueInsureeMutation"

    class Input(OpenIMISMutation.Input):
        
        uuid = graphene.String()
        
        
                        
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(NiueInsureeConfig.gql_mutation_delete_niue_insuree_perms):
                raise PermissionDenied(_("unauthorized"))

            # get NiueInsuree object by uuid
            niueInsuree = NiueInsuree.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            niueInsuree.validity_to = now
            niueInsuree.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete program provider. An exception had occured",
                'detail': str(exc)}]
    #End of delete service provider subLevel mutation....