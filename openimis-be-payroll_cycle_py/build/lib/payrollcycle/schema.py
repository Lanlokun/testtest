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
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied

from .gql_queries import *
from .gql_mutations import *

"""
QraphQL query for payrollcycles
"""
class Query(graphene.ObjectType):
    payrollcycles = OrderedDjangoFilterConnectionField(
        PayrollCycleGQLType,
        show_history=graphene.Boolean(),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )

    payrollcyclesStr = OrderedDjangoFilterConnectionField(
        PayrollCycleGQLType,
        str=graphene.String(),
    )

    def resolve_payrollcycles(self, info, **kwargs):
        """
        Extra steps to perform when payrollcycles is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(PayrollCycleConfig.gql_query_payroll_cycles_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        
        # Used to specify if user want to see all records including invalid records as history
        show_history = kwargs.get('show_history', False)
        if not show_history:
            filters += filter_validity(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))

        return gql_optimizer.query(PayrollCycle.objects.filter(*filters).all(), info)

    def resolve_payrollcyclesStr(self, info, **kwargs):
        """
        Extra steps to perform when payrollcycles is queried
        """
        # Check if user has permission
        if not info.context.user.has_perms(PayrollCycleConfig.gql_query_payroll_cycles_perms):
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
            filters += [ Q(name__icontains=str) | Q(start_month__icontains=str) | Q(end_month__icontains=str) | Q(start_year__icontains=str) | Q(end_year__icontains=str)]

        return gql_optimizer.query(PayrollCycle.objects.filter(*filters).all(), info)


class Mutation(graphene.ObjectType):
    """
    QraphQL Mutation for payrollcycles
    """
    create_payroll_cycle = CreatePayrollCycleMutation.Field()
    update_payroll_cycle = UpdatePayrollCycleMutation.Field()
    delete_payroll_cycle = DeletePayrollCycleMutation.Field()


def on_payroll_cycle_mutation(kwargs, k='uuid'):
    """
    This method is called on signal binding for payroll cycle mutation
    """

    # get uuid from data
    payroll_cycle_uuid = kwargs['data'].get('uuid', None)
    if not payroll_cycle_uuid:
        return []
    # fetch the poayroll cycle object by uuid
    impacted_payroll_cycle = PayrollCycle.objects.get(Q(uuid=payroll_cycle_uuid))
    # Create a mutation object
    PayrollCycleMutation.objects.create(PayrollCycle=impacted_payroll_cycle, mutation_id=kwargs['mutation_log_id'])
    return []

def on_payroll_cycles_mutation(kwargs):
    """
    This method is called on signal binding for payroll cycle mutation 
    of multiple records
    """
    uuids = kwargs['data'].get('uuids', [])
    if not uuids:
        uuid = kwargs['data'].get('uuid', None)
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted_payroll_cycles = PayrollCycle.objects.filter(uuid__in=uuids).all()
    for payroll_cycle in impacted_payroll_cycles:
        PayrollCycleMutation.objects.create(
            PayrollCycle=payroll_cycle, mutation_id=kwargs['mutation_log_id'])
    return []
    
def on_pay_cycle_mutation(sender, **kwargs):
    return {
        
        CreatePayrollCycleMutation._mutation_class: lambda x: on_payroll_cycle_mutation(x),
        UpdatePayrollCycleMutation._mutation_class: lambda x: on_payroll_cycle_mutation(x),
        DeletePayrollCycleMutation._mutation_class: lambda x: on_payroll_cycle_mutation(x),
    }.get(sender._mutation_class, lambda x: [])(kwargs)

"""
signal binding of payrollcycle to payrollcyclemutation which will execute on_payroll_cycle_mutation
every time a mutation occure on payrollcycle
"""
def bind_signals():
    signal_mutation_module_validate["payrollcycle"].connect(on_pay_cycle_mutation)




