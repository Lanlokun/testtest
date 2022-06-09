import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity, Q, assert_string_length
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from graphene.relay import mutation
from .apps import PayrollCycleConfig
from graphene import InputObjectType
from .models import PayrollCycle, PayrollCycleMutation
from programs.models import Scheme


class PayrollCycleInputType(OpenIMISMutation.Input):
    """
    Define the payrollcycle input types
    """
    id = graphene.Int(required=False, read_only=True)
    uuid = graphene.String(required=False)
    
    payroll_cycle_name = graphene.String(required=True)

    start_month = graphene.String(required=True)
    end_month = graphene.String(required=True)

    start_year = graphene.String(required=True)
    end_year = graphene.String(required=True)

    scheme_uuid = graphene.String(required=True)

    Payrollcycle_Type = graphene.String(required=False)

    location_id = graphene.Int(required=False)

def update_or_create_payroll_cycle(data, user):
    # Check if client_mutation_id is passed in data
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    # Check if client_mutation_label is passed in data
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    # get payroll_cycle_uuid from data
    payroll_cycle_uuid = data.pop('uuid') if 'uuid' in data else None

    scheme_uuid = data.pop('scheme_uuid') if 'scheme_uuid' in data else None

    if scheme_uuid:
        scheme = Scheme.objects.get(uuid=scheme_uuid)
        data['scheme'] = scheme

    if payroll_cycle_uuid:
        # fetch payroll_cycle by uuid
        payroll_cycle = PayrollCycle.objects.get(uuid=payroll_cycle_uuid)
        [setattr(payroll_cycle, key, data[key]) for key in data]
    else:
        # create new payroll_cycle object
        payroll_cycle = PayrollCycle.objects.create(**data)
        
    # save record to database
    payroll_cycle.save()
    return payroll_cycle

class CreateOrUpdatePayrollCycleMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        # Check if user is authenticated
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))

        # Check if user has permission
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # data['audit_user_id'] = user.id_for_audit
        from core.utils import TimeUtils
        data['validity_from'] = TimeUtils.now()

        # get client_mutation_id from data
        client_mutation_id = data.get("client_mutation_id")

        # calles the create and update method and returns the created record from the payrollcycle object
        payroll_cycle = update_or_create_payroll_cycle(data, user)

        # log mutation through signal binding everytime a mutation occur
        PayrollCycleMutation.object_mutated(user, client_mutation_id=client_mutation_id, PayrollCycle=payroll_cycle)
        
        return None

class CreatePayrollCycleMutation(CreateOrUpdatePayrollCycleMutation):
    """
    Create new payrollcycle record
    """
    _mutation_module = "payrollcycle"
    _mutation_class = "CreatePayrollCycleMutation"

    # Sets the inputtype of this mutation
    class Input(PayrollCycleInputType):
        pass

    # perform mutation asyncroniously
    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdatePayrollCycleMutation that checks permission
            and call update_or_create_payroll_cycle to perform the creation on payrollcycle record.
            """
            return cls.do_mutate(PayrollCycleConfig.gql_mutation_create_payroll_cycle_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Payroll cycle mutation failed with exceptions",
                'detail': str(exc)}]

class UpdatePayrollCycleMutation(CreateOrUpdatePayrollCycleMutation):
    """
    Update an existing payrollcycle
    """
    _mutation_module = "payrollcycle"
    _mutation_class = "UpdatePayrollCycleMutation"

    # Sets the input type of this mutation
    class Input(PayrollCycleInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            """
            Calls the do_mutate defiend in CreateOrUpdatePayrollCycleMutation that checks permission
            and call update_or_create_payroll_cycle to perform the update on the payrollcycle record.
            """
            return cls.do_mutate(PayrollCycleConfig.gql_mutation_update_payroll_cycle_perms, user, **data)
        except Exception as exc:
            return [{
                'message': "Payroll cycle mutation update failed with exceptions",
                'detail': str(exc)}
            ]

class DeletePayrollCycleMutation(OpenIMISMutation):
    """
    Delete payrollcycle by uuid
    """
    _mutation_module = "payrollcycle"
    _mutation_class = "DeletePayrollCycleMutation"

    # Sets the input type of this mutation
    class Input(OpenIMISMutation.Input):
        uuid = graphene.String()

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            # Check if user has permission
            if not user.has_perms(PayrollCycleConfig.gql_mutation_delete_payroll_cycle_perms):
                raise PermissionDenied(_("unauthorized"))

            # get payrollcycle object by uuid
            payrollcycle = PayrollCycle.objects.get(uuid=data['uuid'])

            # get current date time
            from core import datetime
            now = datetime.datetime.now()

            # Set validity_to to now to make the record invalid
            payrollcycle.validity_to = now
            payrollcycle.save()
            return None
        except Exception as exc:
            return [{
                'message': "Faild to delete payroll cycle. An exception had occured",
                'detail': str(exc)}]