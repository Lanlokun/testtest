import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from graphene_django import DjangoObjectType
from .models import PayrollCycle, PayrollCycleMutation

class PayrollCycleGQLType(DjangoObjectType):
    """
    Define the payrollcycle query set
    """
    client_mutation_id = graphene.String()

    class Meta:
        model = PayrollCycle
        exclude_fields = ('row_id',)
        interfaces = (graphene.relay.Node,)

        #define available filter parameters
        filter_fields = {
            "uuid": ["exact"],
            "payroll_cycle_name": ["exact", "istartswith", "icontains", "iexact"],
            "start_month": ["exact"],
            "start_year": ["exact"],
            "end_month": ["exact"],
            "end_year": ["exact"],
            "Payrollcycle_Type": ["exact"],
            "validity_from": ["exact", "lt", "lte", "gt", "gte", "isnull"],
            "validity_to": ["exact", "lt", "lte", "gt", "gte", "isnull"]
        }
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection #Extend connection from core module

            

    def resolve_client_mutation_id(self, info):
        payrollcycle_mutation = self.mutations.select_related(
            'mutation').filter(mutation__status=0).first()
        return payrollcycle_mutation.mutation.client_mutation_id if payrollcycle_mutation else None

    @classmethod
    def get_queryset(cls, queryset, info):
        return PayrollCycle.get_queryset(queryset, info)

class PayrollCycleMutationGQLType(DjangoObjectType):
    class Meta:
        model = PayrollCycleMutation