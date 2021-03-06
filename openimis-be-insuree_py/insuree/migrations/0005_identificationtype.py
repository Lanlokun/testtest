# Generated by Django 3.0.3 on 2020-07-22 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insuree', '0004_confirmationtype_education_profession_relation'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdentificationType',
            fields=[
                ('code', models.CharField(db_column='IdentificationCode', max_length=1, primary_key=True, serialize=False)),
                ('identification_type', models.CharField(db_column='IdentificationTypes', max_length=50)),
                ('alt_language', models.CharField(blank=True, db_column='AltLanguage', max_length=50, null=True)),
                ('sort_order', models.IntegerField(blank=True, db_column='SortOrder', null=True)),
            ],
            options={
                'db_table': 'tblIdentificationTypes',
                'managed': False,
            },
        ),
    ]
