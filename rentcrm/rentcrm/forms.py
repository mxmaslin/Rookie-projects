from django import forms
from .models import Apartment, Payment, RentAdjustment, Contract, Tenant, ContractCondition, LeaseRenewalOffer


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('date', 'amount',)
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
            'amount': forms.NumberInput(attrs={'autofocus': ''})
        }


class RentAdjustmentForm(forms.ModelForm):
    class Meta:
        model = RentAdjustment
        fields = ('date', 'amount', 'note')
        widgets = {'date': forms.DateInput(attrs={'class': 'datepicker'}),
                    'note': forms.TextInput(attrs={'size': '40'})
                    }


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'
        widgets = {
            'additional_contacts': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
            'notes': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class ApartmentNotesForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['notes']


class LegalRentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['rent_legal']
        widgets = {'rent_legal': forms.NumberInput(attrs={'class': 'form-control'})}


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ('lease_term',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lease_term'].widget.attrs.update({
            'class': 'form-control'
        })


class MovingOutForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ('lease_end',)
        widgets = {'lease_end': forms.DateInput(attrs={'class': 'datepicker'})}
        labels = {'lease_end': 'Moving Out date'}


class ContractConditionForm(forms.ModelForm):
    class Meta:
        model = ContractCondition
        fields = ('lease_start',
                  'is_garage_included', 'rent_for_garage',)
        widgets = {'lease_start': forms.DateInput(
            attrs={'class': 'datepicker form-control', ' autocomplete': 'off'})}


class LeaseRenewalOfferForm(forms.ModelForm):
    class Meta:
        model = LeaseRenewalOffer
        fields = ('date_issued', 'rent_legal_one_year', 'rent_preferential_one_year',
                  'rent_legal_two_years', 'rent_preferential_two_years',
                  'is_garage_included', 'rent_for_garage')
        widgets = {'date_issued': forms.DateInput(
            attrs={'class': 'datepicker'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            if not (field in {'is_garage_included', 'date_issued'}):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })


class GarageForm(forms.ModelForm):
    class Meta:
        model = ContractCondition
        fields = ('is_garage_included', 'rent_for_garage')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rent_for_garage'].widget.attrs.update({
            'class': 'form-control'
        })


class TermForm(forms.ModelForm):
    class Meta:
        model = LeaseRenewalOffer
        fields = ('tenant_choice', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tenant_choice'].widget.attrs.update({
            'class': 'form-control'
        })


class OfferAcceptanceForm(forms.ModelForm):
    class Meta:
        model = LeaseRenewalOffer
        fields = ('tenant_choice', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tenant_choice'].widget.attrs.update({
            'class': 'form-control'
        })
