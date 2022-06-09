import uuid
from core import fields
from core import models as core_models
from django.conf import settings
from django.db import models
from location import models as location_models
# from location.models import UserDistrict
from graphql import ResolveInfo


# Create your models here.
# This class create legal forms for service providers.....
class ServiceProviderLegalForm(core_models.VersionedModel):
    code = models.CharField(db_column='LegalFormCode',
                            primary_key=True, max_length=1)
    legal_form = models.CharField(db_column='LegalForms', max_length=50)
    sort_order = models.IntegerField(
        db_column='SortOrder', blank=True, null=True)

    def __str__(self):
        return self.legal_form

    class Meta:
        managed = True
        db_table = 'tblSPLegalForms'

# This class create levels for service providers.....


class ServiceProviderLevel(core_models.VersionedModel):
    code = models.CharField(db_column='LevelCode',
                            primary_key=True, max_length=1)
    level = models.CharField(db_column='Level', max_length=50)
    sort_order = models.IntegerField(
        db_column='SortOrder', blank=True, null=True)

    def __str__(self):
        return self.level

    class Meta:
        managed = True
        db_table = 'tblSPLevels'

# This class create legal forms for service providers.....


class ServiceProviderSubLevel(core_models.VersionedModel):
    code = models.CharField(db_column='SubLevelCode',
                            primary_key=True, max_length=1)
    sub_level = models.CharField(db_column='SubLevel', max_length=50)
    sort_order = models.IntegerField(
        db_column='SortOrder', blank=True, null=True)

    def __str__(self):
        return self.sub_level

    class Meta:
        managed = True
        db_table = 'tblSPSubLevels'


# This class create service providers
class ServiceProvider(core_models.VersionedModel):
    id = models.AutoField(db_column='ServiceProviderID', primary_key=True)
    uuid = models.CharField(
        db_column='SPUUID', max_length=36, default=uuid.uuid4, unique=True)
    legalForm = models.ForeignKey(
        ServiceProviderLegalForm, models.DO_NOTHING,
        db_column='SPLegalForm', to_field='code',
        related_name="serviceprovider_legalform")
    level = models.ForeignKey(
        ServiceProviderLevel, models.DO_NOTHING,
        db_column='SPLevel', to_field='code',
        related_name="serviceprovider_level")
    subLevel = models.ForeignKey(
        ServiceProviderSubLevel, models.DO_NOTHING,
        db_column='SPSubLevel', to_field='code',
        related_name="serviceprovider_sublevel")
    code = models.CharField(
        db_column='Code', max_length=255)
    name = models.CharField(
        db_column='sevciceProviderName', max_length=255)
    address = models.CharField(
        db_column='Address', max_length=255)
    phoneNumber = models.CharField(
        db_column='PhoneNumber', max_length=255)
    fax = models.CharField(
        db_column='Fax', max_length=255)
    email = models.CharField(
        db_column='Email', max_length=255)
    accountCode = models.CharField(
        db_column='Account_code', max_length=255)

    def __str__(self):
        return self.code+" "+self.name

    class Meta:
        managed = True
        db_table = "tblServiceProviders"


# This class create Paypoint for Service Providers......
class Paypoint(core_models.VersionedModel):
    id = models.AutoField(db_column='PSPId', primary_key=True)
    uuid = models.CharField(
        db_column='PSPUUID', max_length=36, default=uuid.uuid4, unique=True)
    paypointName = models.CharField(
        db_column='PSPName', max_length=255)
    paypointCode = models.CharField(
        db_column='PSPCode', max_length=255)
    geolocation = models.CharField(
        db_column='PSPGeolocation', max_length=255)
    location = models.ForeignKey(
        location_models.Location,
        models.DO_NOTHING, db_column='PSPLocationId', blank=True, null=True)
    # location = models.ForeignKey(
    #     location_models.Location, 
    #     db_column='PSPSettlements', on_delete=models.DO_NOTHING, blank=True, null=True)
    serviceProvider = models.ForeignKey(
        ServiceProvider, db_column='ServiceProvider', on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.paypointCode+" "+self.paypointName

    class Meta:
        managed = True
        db_table = 'tblPaypoints'

# This is the section to create mutation to the classes defined above....
# This class create mutation for ServiceProvider


class ServiceProviderMutation(core_models.UUIDModel, core_models.ObjectMutation):
    service_provider = models.ForeignKey(
        ServiceProvider, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='service_provider')

    class Meta:
        managed = True
        db_table = "serviceprovider_ServiceProviderMutations"

# This class create mutation for ServiceProviderLocation


class PaypointMutation(core_models.UUIDModel, core_models.ObjectMutation):
    pay_point = models.ForeignKey(
        Paypoint, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='pay_point')

    class Meta:
        managed = True
        db_table = "Paypoint_Mutations"


# This class create mutation for ServiceProviderLegalForm
class ServiceProviderLegalFormMutation(core_models.UUIDModel):
    legal_form = models.ForeignKey(
        ServiceProviderLegalForm, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='legal_form')

    class Meta:
        managed = True
        db_table = "serviceprovider_ServiceProviderLegalFormMutation"


# This class create mutation for ServiceProviderLevel
class ServiceProviderLevelMutation(core_models.UUIDModel):
    level = models.ForeignKey(ServiceProviderLevel,
                              models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='level')

    class Meta:
        managed = True
        db_table = "serviceprovider_ServiceProviderLevelMutation"

# This class create mutation for ServiceProviderSubLevel


class ServiceProviderSubLevelMutation(core_models.UUIDModel):
    sub_level = models.ForeignKey(
        ServiceProviderSubLevel, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='sub_level')

    class Meta:
        managed = True
        db_table = "serviceprovider_ServiceProviderSubLevelMutation"
