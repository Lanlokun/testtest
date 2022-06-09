import uuid
import insuree
from payrollcycle.models import PayrollCycle
from programs.models import Scheme
from insuree.models import Insuree, IdentificationType
from service_provider.models import ServiceProvider,Paypoint

from core import fields
from core import models as core_models
from django.conf import settings
from django.db import models
from location import models as location_models


# select options for Payrollcycle_Type
Location_Type = (
    ('R','Region'),
    ('D', 'District'),
    ('W', 'Ward'),
    ('V', 'Settlement'),
    ('P', 'Paypoint'),
)

Payment_Type = (
    ('cash','Cash'),
    ('check', 'Check'),
    ('transfer', 'Transfer'),
    ('kind', 'kind'),
    ('others', 'Others'),
)

# Payroll model
class Payroll(core_models.VersionedModel):
    id = models.AutoField(db_column='PaymentDetailsID', primary_key=True)
    uuid = models.CharField(db_column='PaymentDetailsUUID',
                            max_length=36, default=uuid.uuid4, unique=True)

    payrollcycle = models.ForeignKey(PayrollCycle, on_delete=models.DO_NOTHING)
    scheme = models.ForeignKey(Scheme, on_delete=models.DO_NOTHING)

    insuree = models.ForeignKey(Insuree, on_delete=models.DO_NOTHING)

    expectedamount = models.DecimalField(db_column='ExpectedAmount', max_digits=12, decimal_places=2)
    amount = models.DecimalField(db_column='AmountPaid', max_digits=12, decimal_places=2,blank=True, null=True)

    start_date = models.CharField(db_column='StartDate', max_length=10)
    end_date = models.CharField(db_column='EndDate', max_length=10)
    
    location = models.ForeignKey(location_models.Location, on_delete=models.DO_NOTHING, blank=True, null=True)
    location_type= models.CharField(
        db_column='LocationType', max_length=1, choices=Location_Type, blank=True, null=True)
    psp = models.ForeignKey(ServiceProvider, on_delete=models.DO_NOTHING)

    rundate = models.DateField(db_column='RunDate', blank=True, null=True)

    audit_user_id = models.IntegerField(db_column='AuditUserId', blank=True, null=True)
    
    is_approved = models.BooleanField(db_column='IsApproved', default=False)

    approved_by_id = models.IntegerField(db_column='ApprovedBy', blank=True, null=True)

    transaction_number = models.CharField(db_column='TransactionNumber', max_length=25, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblPayroll'

"""
PayrollMutation model creats relationship between Payroll and mutations
For every mutation made on Payroll a record is inserted into PayrollMutation
to track those records as history
"""
class PayrollMutation(core_models.UUIDModel, core_models.ObjectMutation):
    Payroll = models.ForeignKey(Payroll, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='payroll')

    class Meta:
        managed = True
        db_table = "payroll_PayrollMutation"

class PayrollPaymentDetails(core_models.VersionedModel):
    id = models.AutoField(db_column='PaymentDetailsID', primary_key=True)
    uuid = models.CharField(db_column='PaymentDetailsUUID',
                            max_length=36, default=uuid.uuid4, unique=True)

    payroll = models.ForeignKey(Payroll, on_delete=models.DO_NOTHING)
    transaction_number = models.CharField(db_column='TransactionNumber', max_length=25)

    payment_status = models.BooleanField(db_column='PaymentStatus', default=False)
    received_amount = models.DecimalField(db_column='ReceivedAmount', max_digits=12, decimal_places=2, default=0.00)
    payment_date = models.DateField(db_column='PaymentDate')
    receipt_number = models.CharField(db_column='ReceiptNumber',max_length=24, blank=True, null=True)
    
    type_of_payment = models.CharField(db_column='TypeOfPayment',  max_length=12, choices=Payment_Type, blank=True, null=True)
    transfer_fee = models.DecimalField(db_column='TransferFee', max_digits=12, decimal_places=2, blank=True, null=True)
    reasons_for_not_paid = models.CharField(db_column='ReasonsForNotPaid', max_length=100, blank=True, null=True)
    
    receiver_name = models.CharField(db_column='ReceiverName', max_length=100, blank=True, null=True)
    identification_type = models.ForeignKey(IdentificationType, db_column='IdentificationType', blank=True, null=True, on_delete=models.DO_NOTHING)
    identification_number = models.CharField(db_column='IdentificationNumber', max_length=25, blank=True, null=True)
    receiver_phone_number = models.CharField(db_column='ReceiverPhoneNumber', max_length=25, blank=True, null=True)
    
    psp = models.ForeignKey(ServiceProvider, on_delete=models.DO_NOTHING)
    paypoint =  models.ForeignKey(Paypoint, on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = "tblPayrollPaymentDetails"


class PayrollPaymentDetailsMutation(core_models.UUIDModel, core_models.ObjectMutation):
    PayrollPaymentDetails = models.ForeignKey(PayrollPaymentDetails, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='payrollPaymentDetails')

    class Meta:
        managed = True
        db_table = "payroll_PayrollPaymentDetailsMutation"