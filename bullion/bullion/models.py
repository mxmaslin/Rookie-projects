from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Investor(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=150, default='')
    email = models.EmailField()
    registration_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    notes = models.TextField(blank=True)

    US = 'ISUSA'
    NONUS = 'NONUS'
    LOCATION = ((US, 'US'), (NONUS, 'Non-US'))
    location = models.CharField(choices=LOCATION, max_length=5, verbose_name='Select your location')

    INDIVIDUAL = 'INDIV'
    ENTITY = 'ENTIT'
    LEGAL_STATUS = ((INDIVIDUAL, 'Individual'), (ENTITY, 'Entity'))
    legal_status = models.CharField(choices=LEGAL_STATUS, max_length=5, verbose_name='Select your legal status')

    is_accredited = models.BooleanField(default=False, verbose_name='Are you accredited as investor?')
    country = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')

    def is_registered(self):
        return self.location or self.legal_status

    def __str__(self):
        return '{}'.format(self.name)


class Document(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(max_length=500)

    US = 'ISUSA'
    NONUS = 'NONUS'
    LOCATION = ((US, 'US'), (NONUS, 'Non-US'))
    reader_location = models.CharField(choices=LOCATION, max_length=5)

    INDIVIDUAL = 'INDIV'
    ENTITY = 'ENTIT'
    NOT_SPECIFIED = 'NOTSP'
    LEGAL_STATUS = ((INDIVIDUAL, 'Individual'), (ENTITY, 'Entity'), (NOT_SPECIFIED, 'Not specified'))
    reader_legal_status = models.CharField(choices=LEGAL_STATUS, max_length=5)

    is_reader_accredited = models.BooleanField(verbose_name='Investor accredited', default=False)

    def __str__(self):
        return self.name
