import uuid
from core import fields
from core import models as core_models
from django.conf import settings
from django.db import models
from location import models as location_models
from location.models import UserDistrict
from graphql import ResolveInfo
import core  # lgtm [py/import-and-import-from] needed for calendar injection
from django.conf import settings
from django.db import models
from graphql import ResolveInfo
from location import models as location_models
from core import models as core_models
from datetime import datetime
from insuree import models as insuree_models
from insuree.models import *
from core.utils import TimeUtils

# Variables for the drop down in the Scheme_Status in the Scheme Table (Status field).
Scheme_Status = (
    ('active','Active'),
    ('inactive', 'Inactive'),
)

# Variables for the drop down in the Scheme_type in the Scheme Table (scheme_type field).
Scheme_Type = (
    ('cash','Cash'),
    ('in-kind', 'In-kind'),
    ('cash-in-kind', 'Cash & In-Kind'),
)

# Create your models here.

# Scheme model (Creates a scheme and a Scheme table once migration is successful).
class Scheme(core_models.VersionedModel):
    # id field
    id = models.AutoField(
        db_column='SchemeID', primary_key=True)
        
    uuid = models.CharField(db_column='schemeUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    
    name = models.CharField(
        db_column='name', max_length=255, blank=True, null=True)
    start_date = core.fields.DateField(
        db_column='StartDate')
    end_date = core.fields.DateField(
        db_column='EndDate')
    code = models.CharField(
        max_length=15, db_column='code', unique=True)
    created_at = core.fields.DateField(
        db_column='CreatedAt', default=datetime.now)
    status = models.CharField(
        db_column='Status', max_length=255, choices=Scheme_Status, default='active')
    scheme_type = models.CharField(
        db_column='SchemeType', max_length=255, choices=Scheme_Type, default='cash')
    amount = models.DecimalField(db_column='AmountPaid', max_digits=12, decimal_places=2)

    def __str__ (self):
        return self.name
    
    
        
    class Meta:
        managed = True
        db_table = 'tblSchemes'

    

# Program model (Uses the ManyToMany relationship between Scheme and Insuree to create a programs model and table).
class Programs(core_models.VersionedModel):
    id = models.AutoField(
        db_column='ID', primary_key=True)
    uuid = models.CharField(db_column='programsUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    # Scheme field
    scheme = models.ForeignKey(Scheme, on_delete=models.DO_NOTHING)
    # Insuree field
    insuree = models.ForeignKey(Insuree, on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'tblPrograms'




class SchemeMutation(core_models.UUIDModel, core_models.ObjectMutation):
    scheme = models.ForeignKey(Scheme, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='scheme')

    class Meta:
        managed = True
        db_table = "schemeMutation"

class ProgramsMutation(core_models.UUIDModel, core_models.ObjectMutation):
    programs = models.ForeignKey(Programs, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='programs')

    class Meta:
        managed = True
        db_table = "programsMutation"