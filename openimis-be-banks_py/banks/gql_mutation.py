from typing_extensions import Required
import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from graphene.relay import mutation
from .apps import BanksConfig
from graphene import InputObjectType
from .models import *

class BanksInputType(OpenIMISMutation.Input):
    """
    Define the Bank input types
    """
    id = graphene.Int(required=False, read_only=True)
    uuid = graphene.String(required=False)
    bank_name = graphene.String(required=True)
    # bank_account_number = graphene.Int(required=True)
    bank_address = graphene.String(required=True)
    bank_email = graphene.String(required=True)
    bank_contact_detail = graphene.Int(Required=True)
    bank_switch_code = graphene.Int(required=True)
    



def update_or_create_bank(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    # get Bank_uuid from data
    bank_uuid = data.pop('uuid') if 'uuid' in data else None

    if bank_uuid:
        # fetch Bank by uuid
        prBank = Bank.objects.get(uuid=bank_uuid)
        [setattr(prBank, key, data[key]) for key in data]
    else:
        # create new Bank object
        prBank = Bank.objects.create(**data)
        
    # save record to database
    prBank.save()
    return prBank


class CreateOrUpdateBankMutation(OpenIMISMutation):
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

        # calles the create and update method and returns the created record from the Bank object
        prBanks = update_or_create_bank(data, user)

        # log mutation through signal binding everytime a mutation occur
        BankMutation.object_mutated(user, client_mutation_id=client_mutation_id, Bank=prBanks)
        
        return None

class CreateBanksMutation(CreateOrUpdateBankMutation):
    """
    Create new Bank record
    """
    _mutation_module = "banks"
    _mutation_class = "CreateBankMutation"

    # Sets the inputtype of this mutation
    class Input(BanksInputType):
        pass

    # perform mutation asyncroniously
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateBankMutation that checks permission
            and call update_or_create_Bank to perform the creation on Bank record.
            """
            return cls.do_mutate(BanksConfig.gql_mutation_create_prBanks_perms,user, **data)
        except Exception as exc:
            return [{
                'message': "Bank mutation failed with exceptions",
                'detail': str(exc)}]

class UpdateBankMutation(CreateOrUpdateBankMutation):
    """
    Update an existing Bank
    """
    _mutation_module = "banks"
    _mutation_class = "UpdateBankMutation"

    # Sets the input type of this mutation
    class Input(BanksInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdateBankMutation that checks permission
            and call update_or_create_Bank to perform the update on the Bank record.
            """
            return cls.do_mutate(BanksConfig.gql_mutation_update_prBanks_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Bank mutation update failed with exceptions",
                'detail': str(exc)}
            ]

class DeleteBankMutation(OpenIMISMutation):
    """
    Delete Banks by uuid
    """
    _mutation_module = "banks"
    _mutation_class = "DeleteBankMutation"

    # Sets the input type of this mutation
    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(BanksConfig.gql_mutation_delete_prBanks_perms):
                raise PermissionDenied(_("unauthorized"))

            # get programs object by uuid
            prBanks = Bank.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            prBanks.validity_to = now
            prBanks.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete Bank. An exception had occured",
                'detail': str(exc)}]
