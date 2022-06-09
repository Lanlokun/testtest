import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from graphene_django import DjangoObjectType
from .models import Payroll, PayrollPaymentDetails

class PayrollGQLType(DjangoObjectType):
    """
    Define the Payroll query set
    """
    class Meta:
        model = Payroll
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        #define available filter parameters
        filter_fields = {
            "uuid": ["exact"],
            "start_date": ["exact"],
            "end_date": ["exact"],
            "location_type": ["exact"],
            "transaction_number": ["exact", "istartswith", "icontains", "iexact"],
            "validity_from": ["exact", "lt", "lte", "gt", "gte", "isnull"],
            "validity_to": ["exact", "lt", "lte", "gt", "gte", "isnull"]
        }
        connection_class = ExtendedConnection #Extend connection from core module

class PayrollPaymentDetailsGQLType(DjangoObjectType):
    """
    Define the Payroll PaymentDetails query set
    """
    class Meta:
        model = PayrollPaymentDetails
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        #define available filter parameters
        filter_fields = {
            "uuid": ["exact"],
            "transaction_number": ["exact", "istartswith", "icontains", "iexact"],
            "receipt_number": ["exact", "istartswith", "icontains", "iexact"],
            "payment_status": ["exact", "istartswith", "icontains", "iexact"],
            "validity_from": ["exact", "lt", "lte", "gt", "gte", "isnull"],
            "validity_to": ["exact", "lt", "lte", "gt", "gte", "isnull"]
        }
        connection_class = ExtendedConnection #Extend connection from core module