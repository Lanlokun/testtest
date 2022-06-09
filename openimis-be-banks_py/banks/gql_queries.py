import graphene
from graphene_django import DjangoObjectType
from core import prefix_filterset, filter_validity, ExtendedConnection
from .models import *


class BankGQLType(DjangoObjectType):

    class Meta:
        model = Bank
        filter_fields = {
            "bank_name": ["exact"],
            # "bank_account_number": ["exact"],
            "bank_address": ["exact"],
            "bank_email": ["exact"],
            "bank_contact_detail": ["exact"],
            "bank_switch_code": ["exact"],
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

# class ProgramsGQLType(DjangoObjectType):
    
#     class Meta:
#         model = Bank
#         filter_fields = {
#         }
#         interfaces = (graphene.relay.Node,)
#         connection_class = ExtendedConnection
