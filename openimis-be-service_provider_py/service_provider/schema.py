from core.schema import signal_mutation_module_validate
from multiprocessing.forking import duplicate
from django.db.models import Q
import graphene
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
from core import prefix_filterset, filter_validity
from core import models as core_models
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from .models import *
from django.utils.translation import gettext as _
import graphene_django_optimizer as gql_optimizer
# from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied

from .gql_queries import *
from .gql_mutations import *

"""
QraphQL query for serviceProviderLegalForm, serviceProviderLevel, serviceProviderSublevel, 
serviceProvider and serviceProviderLocation....
"""

#This Query class contain all the queries to perform onto Service Providers and Paypoints...
class Query(graphene.ObjectType):
    serviceProviderLegalForm = OrderedDjangoFilterConnectionField(
        ServiceProviderLegalFormGQLType,
        showHistory=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String)
    )
    serviceProviderLevel = OrderedDjangoFilterConnectionField(
        ServiceProviderLevelGQLType,
        showHistory=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String)
    )
    serviceProviderSubLevel = OrderedDjangoFilterConnectionField(
        ServiceProviderSubLevelGQLType,
        showHistory=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String)
    )
    serviceProvider = OrderedDjangoFilterConnectionField(
        ServiceProviderGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    serviceProvider_details = OrderedDjangoFilterConnectionField(
        ServiceProviderGQLType,
        serviceprovider_uuid=graphene.String(required=True),
        # showHistory=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    serviceProviderStr = OrderedDjangoFilterConnectionField(
        ServiceProviderGQLType,
        showHistory=graphene.Boolean(),
        str=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    paypoint = OrderedDjangoFilterConnectionField(
        PaypointGQLType,
        showHistory=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    serviceProviderPaypoint_details = OrderedDjangoFilterConnectionField(
        PaypointGQLType,
        serviceprovider_uuid=graphene.String(required=True),
        orderBy=graphene.List(of_type=graphene.String),
    )
    paypointStr = OrderedDjangoFilterConnectionField(
        PaypointGQLType,
        showHistory=graphene.Boolean(),
        str=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_serviceProvider_details(self, info, **kwargs):
        # if not info.context.user.has_perms(ServiceProviderConfig.gql_query_service_provider_perms):
        #     raise PermissionDenied(_("unauthorized"))
        serviceprovider = ServiceProvider.objects.get(
            Q(uuid=kwargs.get('serviceprovider_uuid')))
        
        return ServiceProvider.objects.filter(
            Q(uuid=serviceprovider.uuid),
            *filter_validity(**kwargs)
        ).order_by('name', 'code',)

    def resolve_serviceProviderPaypoint_details(self, info, **kwargs):
        # if not info.context.user.has_perms(ServiceProviderConfig.gql_query_pay_points_perms):
        #     raise PermissionDenied(_("unauthorized"))
        serviceprovider = ServiceProvider.objects.get(
            Q(uuid=kwargs.get('serviceprovider_uuid')))
        # print(serviceprovider.id)
        return Paypoint.objects.filter(
            Q(serviceProvider=serviceprovider),
            *filter_validity(**kwargs)
        ).order_by('paypointName', 'paypointCode',)

    def resolve_serviceProvider(self, info, **kwargs):
        """
        Extra steps to perform when service provider details is queried
        """
        # Check if user has permission
        # if not info.context.user.has_perms(ServiceProviderConfig.gql_query_service_provider_perms):
        #     raise PermissionDenied(_("unauthorized"))
        filters = []

        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(
                Q(mutations__mutation__client_mutation_id=client_mutation_id))

    def resolve_serviceProviderStr(self, info, **kwargs):
        """
        Extra steps to perform when payrollcycles is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(ServiceProviderConfig.gql_query_service_providers_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(
                Q(mutations__mutation__client_mutation_id=client_mutation_id))

        str = kwargs.get('str')
        if str is not None:
            filters += [Q(code__icontains=str) | Q(name__icontains=str)]

        return gql_optimizer.query(ServiceProvider.objects.filter(*filters).all(), info)

    def resolve_paypoint(self, info, **kwargs):
        """
        Extra steps to perform when service provider details is queried
        """
        # Check if user has permission
        # if not info.context.user.has_perms(ServiceProviderConfig.gql_query_service_provider_perms):
        #     raise PermissionDenied(_("unauthorized"))
        filters = []

        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(
                Q(mutations__mutation__client_mutation_id=client_mutation_id))

    def resolve_paypointStr(self, info, **kwargs):
        """
        Extra steps to perform when payrollcycles is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(ServiceProviderConfig.gql_query_pay_points_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(
                Q(mutations__mutation__client_mutation_id=client_mutation_id))

        str = kwargs.get('str')
        if str is not None:
            filters += [Q(paypointCode__icontains=str) |
                        Q(paypointName__icontains=str)]

        return gql_optimizer.query(Paypoint.objects.filter(*filters).all(), info)


"""
QraphQL Mutation for serviceProvider
and paypoint
"""


class Mutation(graphene.ObjectType):
    # Create section
    create_service_provider_legalform = CreateServiceProviderLegalFormMutation.Field()
    create_service_provider_level = CreateServiceProviderlevelMutation.Field()
    create_service_provider_sublevel = CreateServiceProviderSublevelMutation.Field()
    create_service_provider = CreateServiceProviderMutation.Field()
    create_paypoint = CreatePaypointMutation.Field()
    # Create section
    delete_service_provider_legalform = DeleteServiceProviderLegalFormMutation.Field()
    delete_service_provider_level = DeleteServiceProviderLevelMutation.Field()
    delete_service_provider_subLevel = DeleteServiceProviderSubLevelMutation.Field()
    delete_service_provider = DeleteServiceProviderMutation.Field()
    delete_paypoint = DeletePaypointMutation.Field()
    # Update Section
    update_service_provider_legalform = UpdateServiceProviderLegalFormMutation.Field()
    update_service_provider_level = UpdateServiceProviderLevelMutation.Field()
    update_service_provider_sublevel = UpdateServiceProviderSubLevelMutation.Field()
    update_service_provider = UpdateServiceProviderMutation.Field()
    update_paypoint = UpdatePaypointMutation.Field()
