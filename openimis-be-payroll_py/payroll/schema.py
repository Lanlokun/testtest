from core.schema import signal_mutation_module_validate
from django.db.models import Q
import graphene
from multiprocessing.forking import duplicate,
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
from core import prefix_filterset, filter_validity
from core import models as core_models
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from .models import *
from payrollcycle.models import PayrollCycle
from django.utils.translation import gettext as _
import graphene_django_optimizer as gql_optimizer
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from payrollcycle.gql_queries import PayrollCycleGQLType

from .gql_queries import *
from .gql_mutations import *

"""
QraphQL query for payroll
"""
class Query(graphene.ObjectType):
    payroll = OrderedDjangoFilterConnectionField(
        PayrollGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )

    payroll_payment_details = OrderedDjangoFilterConnectionField(
        PayrollPaymentDetailsGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )

    payrollcycle_payrolls = OrderedDjangoFilterConnectionField(
        PayrollGQLType,
        payrollcycle_uuid=graphene.String(required=True),
        orderBy=graphene.List(of_type=graphene.String),
    )

    payrolls_generated = OrderedDjangoFilterConnectionField(
        PayrollCycleGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_payroll(self, info, **kwargs):
        """
        Extra steps to perform when payroll is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(PayrollConfig.gql_query_payroll_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))

        return gql_optimizer.query(Payroll.objects.filter(*filters).all(), info)

    def resolve_payrollcycle_payrolls(self, info, **kwargs):
        if not info.context.user.has_perms(PayrollConfig.gql_query_payroll_perms):
            raise PermissionDenied(_("unauthorized"))
        payrollcycle = PayrollCycle.objects.get(Q(uuid=kwargs.get('payrollcycle_uuid')))
        return Payroll.objects.filter(
            Q(payrollcycle=payrollcycle),
            *filter_validity(**kwargs)
        ).order_by('start_date', 'end_date',)

    def resolve_payrolls_generated(self, info, **kwargs):
        if not info.context.user.has_perms(PayrollConfig.gql_query_payroll_perms):
            raise PermissionDenied(_("unauthorized"))

        filters = []

        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        payrolls = Payroll.objects.order_by('payrollcycle').values('payrollcycle').distinct()

        return gql_optimizer.query(PayrollCycle.objects.filter(id__in = [x['payrollcycle'] for x in payrolls]).all(), info)

def resolve_payroll_payment_details(self, info, **kwargs):
        """
        Extra steps to perform when payroll payment details is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(PayrollConfig.gql_query_payroll_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))

        return gql_optimizer.query(PayrollPaymentDetails.objects.filter(*filters).all(), info)

class Mutation(graphene.ObjectType):
    """
    QraphQL Mutation for payroll
    """
    generate_payroll = GeneratePayrollMutation.Field()
    approve_payroll = ApprovePayrollMutation.Field()
    add_payroll_payment_details = AddPayrollPaymentdetailsMutation.Field()


def on_payroll_mutation(kwargs, k='uuid'):
    """
    This method is called on signal binding for payroll mutation
    """

    # get uuid from data
    payroll_uuid = kwargs['data'].get('uuid', None)
    if not payroll_uuid:
        return []
    # fetch the poayroll object by uuid
    impacted_payroll = Payroll.objects.get(Q(uuid=payroll_uuid))
    # Create a mutation object
    PayrollMutation.objects.create(Payroll=impacted_payroll, mutation_id=kwargs['mutation_log_id'])
    return []

def on_payrolls_mutation(kwargs):
    """
    This method is called on signal binding for payroll mutation 
    of multiple records
    """
    uuids = kwargs['data'].get('uuids', [])
    if not uuids:
        uuid = kwargs['data'].get('uuid', None)
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted_payroll = Payroll.objects.filter(uuid__in=uuids).all()
    for payroll in impacted_payroll:
        PayrollMutation.objects.create(
            Payroll=payroll, mutation_id=kwargs['mutation_log_id'])
    return []
    
def on_pay_mutation(sender, **kwargs):
    return {
        
        GeneratePayrollMutation._mutation_class: lambda x: on_payroll_mutation(x),
        ApprovePayrollMutation._mutation_class: lambda x: on_payroll_mutation(x),
    }.get(sender._mutation_class, lambda x: [])(kwargs)

"""
signal binding of payroll to PayrollMutation which will execute on_payroll_mutation
every time a mutation occure on payroll
"""
def bind_signals():
    signal_mutation_module_validate["payroll"].connect(on_pay_mutation)




