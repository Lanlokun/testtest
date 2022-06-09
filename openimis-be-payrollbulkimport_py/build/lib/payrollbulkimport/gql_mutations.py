import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from insuree import gql_mutations as insuree_gql_mutations
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from graphene import InputObjectType
import csv
import json
from datetime import datetime

from insuree.models import Family

class Switcher(object):
    def get_id_from_code(self, class_name, argument):
        """Dispatch method"""
        method_name = 'get_' + str(class_name)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda: "Invalid class name " + str(class_name))
        # Call the method as we return it
        return method(argument)
 
    def get_location(self,arg):
        from location.models import Location
        return Location.objects.get(code=arg)

    def get_education(self,arg):
        from insuree.models import Education
        return Education.objects.get(education=arg)

    def get_gender(self,arg):
        from insuree.models import Gender
        return Gender.objects.get(gender=arg)

    def get_profession(self,arg):
        from insuree.models import Profession
        return Profession.objects.get(profession=arg)

    def get_confirmationType(self,arg):
        from insuree.models import ConfirmationType
        return ConfirmationType.objects.get(confirmationtype=arg)

    def get_identificationType(self,arg):
        from insuree.models import IdentificationType
        return IdentificationType.objects.get(identification_type=arg)

    def get_familyType(self,arg):
        from insuree.models import FamilyType
        return FamilyType.objects.get(type=arg)

def set_import_insuree_data(data, user):

    data_list = []
    col_list = []
    all_data = []
    file_path = data['file_path']
    try:
        with open(file_path, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in data:
                data_list.append(row)

            for col in data_list[0]:
                col_list.append(col)
            data_list.pop(0)

            for r in data_list:
                date_of_birth = r[col_list.index('BirthDate')]
                dob = ''
                if date_of_birth:
                    d = datetime.strptime(date_of_birth, "%d/%m/%Y")
                    dob = d.date()
                
                switch=Switcher()
                vals={
                        
                        'poverty' : r[col_list.index('PovertyStatus')],
                        'confirmation_no' : r[col_list.index('ConfirmationNo')],
                        'address' : r[col_list.index('PermanentAddress')],

                        'family_type' : switch.get_id_from_code('familyType',r[col_list.index('FamilyType')]),
					    'confirmation_type' : switch.get_id_from_code('confirmationType',r[col_list.index('ConfirmationType')]),
					    'location' : switch.get_id_from_code('location',r[col_list.index('PermanentVillageCode')]),

                        'chf_id' : r[col_list.index('SRNumber')],
                        'last_name' : r[col_list.index('LastName')],
                        'other_names' : r[col_list.index('OtherNames')],
                        'dob' : dob,
                        'marital' : r[col_list.index('MaritalStatus')],
                        'current_address' : r[col_list.index('CurrentAddress')],
                        'phone' : r[col_list.index('PhoneNumber')],
                        'email' : r[col_list.index('Email')],
                        'passport' : r[col_list.index('IdentificationNumber')],
                        'profession' : switch.get_id_from_code('profession',r[col_list.index('Proffesion')]),
                        'current_village' : switch.get_id_from_code('location',r[col_list.index('CurrentVillageCode')]),
                        'education' : switch.get_id_from_code('education',r[col_list.index('Education')]),
                        'gender' : switch.get_id_from_code('gender',r[col_list.index('Gender')]),
                        'type_of_id' : switch.get_id_from_code('identificationType',r[col_list.index('IdentificationType')])
                    }
                    
                all_data.append(vals)
        return all_data
    except Exception as exc:
        return [{
            'message': "Bulk import of insuree failed to read file",
            'detail': str(exc)}]
    
class BulkImportInputType(OpenIMISMutation.Input):
    file_path =graphene.String(required=True)

class CreateBulkImportPayrollMutation(OpenIMISMutation):
    _mutation_module = "bulkimportinsurees"
    _mutation_class = "CreateBulkImportPayrollMutation"

    class Input(BulkImportInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        insurees = []
        try:
            all_data= set_import_insuree_data(data, user)
            for insuree_data in all_data:
                has_message = 'message' in insuree_data
                if has_message:
                    return insuree_data
                else:
                    insuree_data['audit_user_id'] = 1
                    if not insuree_data['dob']:
                        insuree_data.pop('dob')

                    from core.utils import TimeUtils
                    insuree_data['validity_from'] = TimeUtils.now()
                    # if not 'head' in insuree_data:
                    #     insuree_data['head'] = False
                    if not 'card_issued' in insuree_data:
                        insuree_data['card_issued'] = False
                        
                    family_data = {
                        'poverty' : insuree_data.pop('poverty'),
                        'confirmation_no' : insuree_data.pop('confirmation_no'),
                        'address' : insuree_data.pop('address'),
                        'confirmation_type' : insuree_data.pop('confirmation_type'),
                        'family_type' : insuree_data.pop('family_type'),
                        'location' : insuree_data.pop('location')
                    }
                    
                    family_data['audit_user_id'] = 1
                    family_data['head_insuree'] = insuree_data
                    family = insuree_gql_mutations.update_or_create_family(family_data,user)
                    # insuree_data['family'] = family
                    # insuree = insuree_gql_mutations.update_or_create_insuree(insuree_data,user)
                    client_mutation_id = data.get("client_mutation_id")
                    insuree_gql_mutations.FamilyMutation.object_mutated(user, client_mutation_id=client_mutation_id, family=family)
                    # insuree_gql_mutations.InsureeMutation.object_mutated(user, client_mutation_id=client_mutation_id, insuree=insuree)
                    
            return None
        except Exception as exc:
            return [{
                'message': "Bulk import of insuree failed",
                'detail': str(exc)}]
