import uuid
from programs.models import Scheme

from core import fields
from core import models as core_models
from django.conf import settings
from django.db import models
from location import models as location_models
from location.models import UserDistrict
from graphql import ResolveInfo

# select options for Payrollcycle_Type
Payrollcycle_Type = (
    ('national','National'),
    ('regional', 'Regional'),
    ('by_district', 'District'),
    ('by_ward', 'By Ward'),
    ('by_settlement', 'By Settlement'),
    ('by_paypoint', 'By Paypoint'),
)

# PayrollCycle model
class PayrollCycle(core_models.VersionedModel):
    id = models.AutoField(db_column='PayrollCycleID', primary_key=True)
    uuid = models.CharField(db_column='PayrollCycleUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    payroll_cycle_name = models.CharField(db_column='PayrollCycle', max_length=100)

    start_month = models.CharField(db_column='StartMonth', max_length=10)
    start_year = models.CharField(db_column='StartYear', max_length=4)

    
    end_month = models.CharField(db_column='EndMonth', max_length=10)
    end_year = models.CharField(db_column='EndYear', max_length=4)

    audit_user_id = models.IntegerField(db_column='AuditUserId', blank=True, null=True)
    
    scheme = models.ForeignKey(Scheme, on_delete=models.DO_NOTHING)

    Payrollcycle_Type= models.CharField(
        db_column='PayrollcycleType', max_length=255, choices=Payrollcycle_Type, default='national')
    
    location = models.ForeignKey(location_models.Location, on_delete=models.DO_NOTHING, blank=True, null=True)

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = cls.filter_queryset(queryset)
        # GraphQL calls with an info object while Rest calls with the user itself
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)
        return queryset

    class Meta:
        managed = True
        db_table = 'tblPayrollCycle'

"""
PayrollCycleMutation model creats relationship between PayrollCycle and mutations
For every mutation made on PayrollCycle a record is inserted into PayrollCycleMutation
to track those records as history
"""
class PayrollCycleMutation(core_models.UUIDModel, core_models.ObjectMutation):
    PayrollCycle = models.ForeignKey(PayrollCycle, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='payrollcycles')

    class Meta:
        managed = True
        db_table = "payrollcycle_PayrollCycleMutation"