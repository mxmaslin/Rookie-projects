from django.contrib import admin

from .models import *
# Building, Apartment, Tenant, Payment, Contract, ContractCondition, LeaseRenewalOffer, RentAdjustmentInline

class ApartmentInline(admin.TabularInline):
    model = Apartment
    extra = 4

class BuildingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'address', 'has_garage')
    inlines = [ApartmentInline]


# class ApartmentAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'building', 'apt_num', 'rent_legal', 'has_active_contract')


class TenantAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'phone', 'email')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

class RentAdjustmentInline(admin.TabularInline):
    model = RentAdjustment
    extra = 0

class LeasePeriodInline(admin.TabularInline):
    model = ContractCondition
    extra = 0

class LeaseRenewalInline(admin.TabularInline):
    model = LeaseRenewalOffer
    extra = 0



class PaymentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contract', 'date', 'amount')


class ContractAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'main_tenant_name', 'apartment', 'is_active', 'signed_date')
    inlines = [LeasePeriodInline, RentAdjustmentInline]


class ContractConditionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contract', 'rent_preferential', 'is_active',
                    'lease_start', 'lease_end', 'is_garage_included', 'rent_for_garage')


class LeaseRenewalOfferAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'lease_period', 'date_issued', 'is_sent', 'tenant_choice', 'rent_preferential_one_year', 'rent_preferential_two_years', 'is_garage_included', 'rent_for_garage')


# class DiscountAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'discount_sum', 'contract_conditions')

admin.site.register(Building, BuildingAdmin)
# admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(Tenant, TenantAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Contract, ContractAdmin)
# admin.site.register(ContractCondition, ContractConditionAdmin)
admin.site.register(LeaseRenewalOffer, LeaseRenewalOfferAdmin)
