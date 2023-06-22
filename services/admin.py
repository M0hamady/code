from django.contrib import admin
from .models import Payment, Service, SubscriptionOption, ServiceRequest, ServiceRequestOffer

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

class SubscriptionOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'count', 'price', 'duration')
    search_fields = ('name', 'description')
    ordering = ('name',)

class ServiceRequestOfferInline(admin.StackedInline):
    model = ServiceRequestOffer
    extra = 1

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'service','payment_status', 'subscription_type', 'subscription_option', 'date', 'time')
    list_filter = ('service__name', 'subscription_type', 'subscription_option', 'date')
    search_fields = ('user__username', 'service__name')
    ordering = ('-date',)
    inlines = [ServiceRequestOfferInline]

admin.site.register(Service, ServiceAdmin)
admin.site.register(SubscriptionOption, SubscriptionOptionAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(ServiceRequestOffer)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_request', 'amount',)
    list_filter = ('user', 'service_request')
    search_fields = ('user__username', 'service_request__service__name')

admin.site.register(Payment, PaymentAdmin)