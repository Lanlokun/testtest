from django.db import models
import uuid
from core import models as core_models

# Create your models here.
class Bank(core_models.VersionedModel):
    id = models.AutoField(
        db_column='bankID', primary_key=True)
        
    uuid = models.CharField(db_column='bankUUID', max_length=36, default=uuid.uuid4, unique=True)
    bank_name = models.CharField(max_length=250, db_column="bank_name")
    bank_switch_code = models.IntegerField(db_column="switch_code", null=True)
    # bank_account_number = models.IntegerField(db_column="bank_account_number", null=False)
    bank_address = models.CharField(db_column="bank_address", max_length=250, null=True)
    bank_email = models.EmailField(db_column="bank_email", max_length=250, null=True)
    bank_contact_detail = models.IntegerField(db_column="bank_contact_detail", null=True)

    class Meta:
        managed = True
        db_table = 'tblBanks'



class BankMutation(core_models.UUIDModel, core_models.ObjectMutation):
    Bank = models.ForeignKey(Bank, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(core_models.MutationLog, models.DO_NOTHING, related_name='Bank')

    class Meta:
        managed = True
        db_table = "BankMutation"

