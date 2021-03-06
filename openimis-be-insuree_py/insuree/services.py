import logging

from core.apps import CoreConfig
from django.db.models import Q
from insuree.apps import InsureeConfig
from insuree.models import InsureePhoto, PolicyRenewalDetail

logger = logging.getLogger(__name__)


def create_insuree_renewal_detail(policy_renewal):
    from core import datetime, datetimedelta
    now = datetime.datetime.now()
    adult_birth_date = now - datetimedelta(years=CoreConfig.age_of_majority)
    photo_renewal_date_adult = now - datetimedelta(months=InsureeConfig.renewal_photo_age_adult)  # 60
    photo_renewal_date_child = now - datetimedelta(months=InsureeConfig.renewal_photo_age_child)  # 12
    photos_to_renew = InsureePhoto.objects.filter(insuree__family=policy_renewal.insuree.family) \
        .filter(insuree__validity_to__isnull=True) \
        .filter(Q(insuree__photo_date__isnull=True)
                | Q(insuree__photo_date__lte=photo_renewal_date_adult)
                | (Q(insuree__photo_date__lte=photo_renewal_date_child)
                   & Q(insuree__dob__gt=adult_birth_date)
                   )
                )
    for photo in photos_to_renew:
        detail, detail_created = PolicyRenewalDetail.objects.get_or_create(
            policy_renewal=policy_renewal,
            insuree_id=photo.insuree_id,
            validity_from=now,
            audit_user_id=0,
        )
        logger.debug("Photo due for renewal for insuree %s, renewal detail %s, created an entry ? %s",
                     photo.insuree_id, detail.id, detail_created)


def validate_insuree_number(insuree_number):
    if InsureeConfig.get_insuree_number_validator():
        return InsureeConfig.get_insuree_number_validator()(insuree_number)
    if InsureeConfig.get_insuree_number_length():
        if not insuree_number:
            return [
                {
                    "message": "Invalid insuree number (empty), should be %s" %
                    (InsureeConfig.get_insuree_number_length(),)
                }
            ]
        if len(insuree_number) != InsureeConfig.get_insuree_number_length():
            return [
                {
                    "message": "Invalid insuree number length %s, should be %s" %
                    (len(insuree_number), InsureeConfig.get_insuree_number_length())
                }
            ]
    if InsureeConfig.get_insuree_number_modulo_root():
        try:
            base = int(insuree_number[:-1])
            mod = int(insuree_number[-1])
            if base % InsureeConfig.get_insuree_number_modulo_root() != mod:
                return [{"message": "Invalid checksum"}]
        except Exception as exc:
            logger.exception("Failed insuree number validation", exc)
            return [{"message": "Insuree number validation failed"}]
    return []
