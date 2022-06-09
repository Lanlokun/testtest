import graphene
from graphene_django import DjangoObjectType
from .models import Insuree, InsureePhoto, Education, Profession, Gender, IdentificationType, \
    Family, FamilyType, ConfirmationType, Relation, InsureePolicy, FamilyMutation, InsureeMutation
from location.schema import LocationGQLType
from policy.gql_queries import PolicyGQLType
from core import prefix_filterset, filter_validity, ExtendedConnection
from .models import *


class NiueInsureeGQLType(DjangoObjectType):

    class Meta:
        model = NiueInsuree
        filter_fields = {
            "niuean_descendant": ["exact"],
            "New_zealand_citizen": ["exact"],
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
