from configparser import DuplicateOptionError
from core.schema import signal_mutation_module_validate
from django.db.models import Q
from multiprocessing.forking import duplicate
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
import graphene_django_optimizer as gql_optimizer
from django.utils.translation import gettext as _
from location.apps import LocationConfig
from core.schema import OrderedDjangoFilterConnectionField, OfficerGQLType
from policy.models import Policy

# We do need all queries and mutations in the namespace here.
from .gql_queries import *  # lgtm [py/polluting-import]
from .gql_mutation import *  # lgtm [py/polluting-import]

class Query(graphene.ObjectType):
    bank = OrderedDjangoFilterConnectionField(
        BankGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    banksStr = OrderedDjangoFilterConnectionField(
        BankGQLType,
        str=graphene.String(),
    )

def resolve_banks(self, info, **kwargs):
        """
        Extra steps to perform when Scheme is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(BanksConfig.gql_query_prBanks_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))

        return gql_optimizer.query(Bank.objects.filter(*filters).all(), info)

def resolve_banksStr(self, info, **kwargs):
        """
        Extra steps to perform when Scheme is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(BanksConfig.gql_query_prBanks_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))
        
        # str = kwargs.get('str')
        # if str is not None:
        #     filters += [Q(code__icontains=str) | Q(name__icontains=str)]

        return gql_optimizer.query(Bank.objects.filter(*filters).all(), info)


class Mutation(graphene.ObjectType):
    """
    QraphQL Mutation for schemes
    """
    create_bank = CreateBanksMutation.Field()
    update_bank = UpdateBankMutation.Field()
    delete_bank = DeleteBankMutation.Field()


def on_bank_mutation(kwargs, k='uuid'):
    """
    This method is called on signal binding for scheme mutation
    """

    # get uuid from data
    bank_uuid = kwargs['data'].get('uuid', None)
    if not bank_uuid:
        return []
    # fetch the scheme object by uuid
    impacted_bank = Bank.objects.get(Q(uuid=bank_uuid))
    # Create a mutation object
    BankMutation.objects.create(Bank=impacted_bank, mutation_id=kwargs['mutation_log_id'])
    return []

def on_bank_mutation(kwargs):
    """
    This method is called on signal binding for scheme mutation 
    of multiple records
    """
    uuids = kwargs['data'].get('uuids', [])
    if not uuids:
        uuid = kwargs['data'].get('uuid', None)
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted_banks = Bank.objects.filter(uuid_in=uuids).all()
    for bank in impacted_banks:
        BankMutation.objects.create(
            Bank=bank, mutation_id=kwargs['mutation_log_id'])
    return []


# class Mutation(graphene.ObjectType):
#     """
#     QraphQL Mutation for schemes and programs
#     """
#     create_Bank = CreateBanksMutation.Field()
#     update_Bank = UpdateBankMutation.Field()
#     delete_Bank = DeleteBankMutation.Field()
    
