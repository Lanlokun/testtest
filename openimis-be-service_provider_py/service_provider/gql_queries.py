
import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from graphene_django import DjangoObjectType
from .models import *
from location.gql_queries import LocationGQLType


# This create service provider legal form GraphQL Type
class ServiceProviderLegalFormGQLType(DjangoObjectType):
    client_mutation_id = graphene.String()
    """
    Define the ServiceProviderLegalForm query set
    """
    class Meta:
        model = ServiceProviderLegalForm
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        filter_fields = {
            "code": ["exact"],
            "legal_form": ["exact"],

        }

        connection_class = ExtendedConnection
    # End of service provider legal form grapgQl type

# This create service provider level GraphQL Type


class ServiceProviderLevelGQLType(DjangoObjectType):
    client_mutation_id = graphene.String()

    """
    Define the ServiceProviderLevel query set
    """

    class Meta:
        model = ServiceProviderLevel
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        filter_fields = {
            "code": ["exact"],
            "level": ["exact"],

        }
        connection_class = ExtendedConnection
    # End of service provider level grapgQl type


# This create service provider sub-level GraphQL Type
class ServiceProviderSubLevelGQLType(DjangoObjectType):
    client_mutation_id = graphene.String()
    """
    Define the ServiceProviderSubLevel query set
    """

    class Meta:
        model = ServiceProviderSubLevel
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        filter_fields = {
            "code": ["exact"],
            "sub_level": ["exact"],

        }
        connection_class = ExtendedConnection
    # End of service provider sub-level grapgQl type


# This create service provider GraphQL Type
class ServiceProviderGQLType(DjangoObjectType):
    client_mutation_id = graphene.String()
    """
    Define the ServiceProvider query set
    """
    class Meta:
        model = ServiceProvider
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        # define available filter parameters
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "code": ["exact", "istartswith", "icontains", "iexact"],
            "name": ["exact", "istartswith", "icontains", "iexact"],
            "address": ["exact", "istartswith", "icontains", "iexact"],
            "phoneNumber": ["exact", "istartswith", "icontains", "iexact"],
            "fax": ["exact", "istartswith", "icontains", "iexact", "isnull"],
            "email": ["exact", "istartswith", "icontains", "iexact", "isnull"],
            "accountCode": ["exact", "istartswith", "icontains", "iexact", "isnull"],

        }

        connection_class = ExtendedConnection
    # End of service provider grapgQl type

# This create Payment Service Provider Location GraphQL Type


class PaypointGQLType(DjangoObjectType):

    client_mutation_id = graphene.String()
    """
    Define the Paypoint query set
    """
    class Meta:
        model = Paypoint
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        # define available filter parameters
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "paypointName": ["exact", "istartswith", "icontains", "iexact"],
            "paypointCode": ["exact", "istartswith", "icontains", "iexact"],
            "geolocation": ["exact", "istartswith", "icontains", "iexact"],

        }

        connection_class = ExtendedConnection
# End of Payment Service Provider Location grapgQl type
