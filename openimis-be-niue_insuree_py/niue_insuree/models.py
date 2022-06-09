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
from banks.models import *

# Create your models here.

# Scheme model (Creates a scheme and a Scheme table once migration is successful).
class NiueInsuree(core_models.VersionedModel):
    # id field
    id = models.AutoField(
        db_column='niueInsureeID', primary_key=True)
        
    uuid = models.CharField(db_column='niueInsureeUUID', max_length=36, default=uuid.uuid4, unique=True)
    
    insuree = models.ForeignKey(Insuree, on_delete=models.DO_NOTHING)

    banks = models.ForeignKey(Bank, on_delete=models.DO_NOTHING, null=True)

    #Application for Newborn Infant 
    birth_register_entry_number = models.CharField(db_column='birthRegisterEntryNumber', max_length=36, unique=True, null=True, blank=True)
    
    date_of_registration = core.fields.DateField(db_column='dateOfRegistration', default=datetime.now, null=True, blank=True)
    
    father_first_name = models.CharField(db_column='fatherFirstName', max_length=36, null=True, blank=True)

    father_last_name = models.CharField(db_column='fatherLastName', max_length=36, null=True, blank=True)

    father_residency_status = models.CharField(db_column='fatherResidencyStatus', max_length=36, null=True, blank=True)

    mother_first_name = models.CharField(db_column='motherFirstName', max_length=36, null=True, blank=True)

    mother_last_name = models.CharField(db_column='motherLastName', max_length=36, null=True, blank=True)

    mother_residency_status = models.CharField(db_column='motherResidencyStatus', max_length=36, null=True, blank=True)
    
    #Child Allowance Application Form
    applicant_relationship_to_the_child = models.CharField(db_column='applicantRelationshipChild', max_length=36, null=True, blank=True)
    
    proof_of_permanent_resident = models.CharField(db_column='proofOfPermanentResident', max_length=255, null=True, blank=True)
    #attachment?

    proof_of_identity = models.CharField(db_column='proofOfIdentity', max_length=36, null=True, blank=True)
    #attachment?

    # #Pension Application Form – 60 years

    #Yes / No option 
 
    niuean_descendant = models.CharField(db_column='niueanDescendant', max_length=36, null=True, blank=True)

    New_zealand_citizen = models.CharField(db_column='newZealandCitizen', max_length=36, null=True, blank=True)

    obtained_permanent_resident_status = models.CharField(db_column='permanentResidentStatus', max_length=36, null=True, blank=True)

    Attached_certificate = models.CharField(db_column='attachedCertificate', max_length=36, null=True, blank=True)

    receive_pension_payments = models.CharField(db_column='receivePensionPayments', max_length=36, null=True, blank=True)

    copy_of_passport = models.CharField(db_column='copyOfPassoprt', max_length=36, null=True, blank=True)

    copy_of_permanent_residence_certificate = models.CharField(db_column='copyOfPermanentResidenceCert', max_length=36, null=True, blank=True)
    
    #Application For a Welfare Benefits
    # Test
    
    nationality = models.CharField(db_column='nationality', max_length=36, null=True, blank=True)
    citizenship = models.CharField(db_column='citizenship', max_length=36, null=True, blank=True)
    reason_for_applying_welfare_benefit = models.CharField(db_column='welfareBenefitReason', max_length=255, null=True, blank=True)
    dependency_children = models.CharField(db_column='childrenDependency', max_length=5, null=True, blank=True)
    dependency_relative = models.CharField(db_column='relativeDependency', max_length=5, null=True, blank=True)
    Person_take_care_applicant = models.CharField(db_column='personToTakeCareApplicant', max_length=36, null=True, blank=True)
    receive_any_support_at_all = models.CharField(db_column='receiveSupport', max_length=36, null=True, blank=True)
    receive_money_from_any_source = models.CharField(db_column='receiveMoney', max_length=36, null=True, blank=True)
    employed = models.CharField(db_column='employed', max_length=36, null=True, blank=True)
    weekly_wage = models.CharField(db_column='weekly_wage', max_length=36, null=True, blank=True)
    employment_for_you = models.CharField(db_column='employmentFoundForYou', max_length=36, null=True, blank=True)
    if_NO_Why = models.CharField(db_column='whyNoEmploymentIfFound', max_length=36, null=True, blank=True)
    cash_assets = models.CharField(db_column='cashAssets', max_length=36, null=True, blank=True)
    Debts_owing  = models.CharField(db_column='debtsOwing', max_length=36, null=True, blank=True)
    interest_in_property = models.CharField(db_column='interestInProperty', max_length=36, null=True, blank=True)
    own_following_household_items = models.CharField(db_column='ownFollowingHouseholdItems', max_length=36, null=True, blank=True)

    applicant_first_name = models.CharField(db_column='applicantFirstName', max_length=36, null=True, blank=True)
    applicant_last_name = models.CharField(db_column='applicantLastName', max_length=36, null=True, blank=True)
    bank_number = models.CharField(db_column='bankNumber', max_length=36, null=True, blank=True)
    applicant_DOB = core.fields.DateField(db_column='applicantDOB', max_length=36, null=True, blank=True)
    tin_no = models.CharField(db_column='tinNo', max_length=36, null=True, blank=True)

    
    
        
    class Meta:
        managed = True
        db_table = 'tblNiueInsurees'




class NiueInsureeMutation(core_models.UUIDModel, core_models.ObjectMutation):
    niueInsuree = models.ForeignKey(NiueInsuree, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='niueinsuree')

    class Meta:
        managed = True
        db_table = "niueInsureeMutation"

