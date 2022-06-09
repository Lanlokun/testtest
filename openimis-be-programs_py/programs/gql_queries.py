import graphene
from graphene_django import DjangoObjectType
from .models import Insuree, InsureePhoto, Education, Profession, Gender, IdentificationType, \
    Family, FamilyType, ConfirmationType, Relation, InsureePolicy, FamilyMutation, InsureeMutation
from location.schema import LocationGQLType
from policy.gql_queries import PolicyGQLType
from core import prefix_filterset, filter_validity, ExtendedConnection
from .models import *


class SchemeGQLType(DjangoObjectType):

    class Meta:
        model = Scheme
        filter_fields = {
            "name": ["exact"],
            "start_date": ["exact", "lt", "lte", "gt", "gte", "isnull"],
            "end_date": ["exact", "lt", "lte", "gt", "gte", "isnull"],
            "code": ["exact"],
            "created_at": ["exact", "lt", "lte", "gt", "gte", "isnull"],
            "status": ["exact", "isnull"],
            "scheme_type": ["exact", "isnull"]
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

class ProgramsGQLType(DjangoObjectType):
    
    class Meta:
        model = Programs
        filter_fields = {
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
