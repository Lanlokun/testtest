from configparser import DuplicateOptionError
from multiprocessing.forking import duplicate
#from multiprocessing.reduction import duplicate
from core.schema import signal_mutation_module_validate
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
import graphene_django_optimizer as gql_optimizer
from .apps import ProgramsConfig
from .models import FamilyMutation, InsureeMutation
from django.utils.translation import gettext as _
from location.apps import LocationConfig
from core.schema import OrderedDjangoFilterConnectionField, OfficerGQLType
from policy.models import Policy

# We do need all queries and mutations in the namespace here.
from .gql_queries import *  # lgtm [py/polluting-import]
from .gql_mutations import *  # lgtm [py/polluting-import]

class Query(graphene.ObjectType):
    schemes = OrderedDjangoFilterConnectionField(
        SchemeGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    schemesStr = OrderedDjangoFilterConnectionField(
        SchemeGQLType,
        str=graphene.String(),
    )

    programs = OrderedDjangoFilterConnectionField(
        ProgramsGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )

def resolve_schemes(self, info, **kwargs):
        """
        Extra steps to perform when Scheme is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(ProgramsConfig.gql_query_prSchemes_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))

        return gql_optimizer.query(Scheme.objects.filter(*filters).all(), info)

def resolve_schemesStr(self, info, **kwargs):
        """
        Extra steps to perform when Scheme is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(ProgramsConfig.gql_query_prSchemes_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))
        
        str = kwargs.get('str')
        if str is not None:
            filters += [Q(code__icontains=str) | Q(name__icontains=str)]

        return gql_optimizer.query(Scheme.objects.filter(*filters).all(), info)


class Mutation(graphene.ObjectType):
    """
    QraphQL Mutation for schemes
    """
    create_payroll_cycle = CreateSchemeMutation.Field()
    update_payroll_cycle = UpdateSchemeMutation.Field()
    delete_payroll_cycle = DeleteSchemeMutation.Field()


def on_scheme_mutation(kwargs, k='uuid'):
    """
    This method is called on signal binding for scheme mutation
    """

    # get uuid from data
    scheme_uuid = kwargs['data'].get('uuid', None)
    if not scheme_uuid:
        return []
    # fetch the scheme object by uuid
    impacted_scheme = Scheme.objects.get(Q(uuid=scheme_uuid))
    # Create a mutation object
    SchemeMutation.objects.create(Scheme=impacted_scheme, mutation_id=kwargs['mutation_log_id'])
    return []

def on_schemes_mutation(kwargs):
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
    impacted_schemes = Scheme.objects.filter(uuid__in=uuids).all()
    for scheme in impacted_schemes:
        SchemeMutation.objects.create(
            Scheme=scheme, mutation_id=kwargs['mutation_log_id'])
    return []


class Mutation(graphene.ObjectType):
    """
    QraphQL Mutation for schemes and programs
    """
    create_Scheme = CreateSchemeMutation.Field()
    update_Scheme = UpdateSchemeMutation.Field()
    delete_Scheme = DeleteSchemeMutation.Field()
    create_programs = CreateProgramsMutation.Field()
    update_programs = UpdateProgramsMutation.Field()
    delete_programs = DeleteProgramsMutation.Field()
    duplicate_scheme = DuplicateSchemeMutation.Field()
