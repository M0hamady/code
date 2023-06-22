import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify
class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    compound = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.compound} - {self.building} "
class Service(models.Model):
    name = models.CharField(max_length=255,null=True)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class SubscriptionOption(models.Model):
    name = models.CharField(max_length=255)
    count = models.PositiveBigIntegerField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text='Duration in days')
    slug = models.SlugField(unique=True, blank=True,null=True)

    def __str__(self):
        return self.slug + self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def get_offers(self):
        offers = ServiceRequestOffer.objects.filter(subscription_option__slug=self.slug)
        serialized_offers = []
        for offer in offers:
            serialized_offer = {
                'name': offer.offer_name,
                'description': offer.offer_description,
                'price': offer.offer_price,
                'expiry_date': offer.offer_expiry
            }
            serialized_offers.append(serialized_offer)
        return serialized_offers
    def get_total_price(self):
        offers = ServiceRequestOffer.objects.filter(subscription_option__slug=self.slug)
        valid_offers = [offer for offer in offers if offer.offer_expiry >= timezone.now().date() ]  # Get only valid offers with an offer_discount attribute
        if valid_offers:  # If there are valid offers associated with this subscription option
            discount = max(offer.offer_price for offer in valid_offers)  # Get the maximum discount among all valid offers
            discounted_price = self.price - discount  # Calculate the discounted price
            return {'total-price': f'{discounted_price}'}
        else:  # If there are no valid offers associated with this subscription option
            return {'total': f'{self.price}'}
    @property
    def total_price(self):
        offers = ServiceRequestOffer.objects.filter(subscription_option__slug=self.slug)
        valid_offers = [offer for offer in offers if offer.offer_expiry >= timezone.now().date() ]  # Get only valid offers with an offer_discount attribute
        if valid_offers:  # If there are valid offers associated with this subscription option
            discount = max(offer.offer_price for offer in valid_offers)  # Get the maximum discount among all valid offers
            discounted_price = self.price - discount  # Calculate the discounted price
            return discounted_price
        else:  # If there are no valid offers associated with this subscription option
            return self.price
    @property
    def payment_succeeded(self):
        payments= Payment.objects.filter(service_request = self)
        valid_payment = [payment for payment in payments if payment.status == 'success']
        payment = []
        for payed in valid_payment:
            payment.append({
                "amount":payed.amount,
                "status":payed.status
            })
        return payment

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=10, choices=[('one-time', 'One-time'), ('monthly', 'Monthly')])
    subscription_option = models.ForeignKey(SubscriptionOption, on_delete=models.CASCADE, null=True, blank=True )
    date = models.DateField()
    time = models.TimeField()
    car_brand = models.CharField(max_length=255, choices=[('Toyota', 'Toyota'), ('Honda', 'Honda'), ('Ford', 'Ford'), ('Chevrolet', 'Chevrolet'), ('Nissan', 'Nissan'), ('Other', 'Other')],blank=True)
    car_model = models.CharField(max_length=255,blank=True)
    car_color = models.CharField(max_length=255,blank=True)
    car_number = models.CharField(max_length=255,blank=True)
    request_price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

    def __str__(self):
        return f"{self.service}"+ '-'+f"{self.user}"

    def clean(self):
        if self.date < timezone.now().date():
            raise ValidationError('The date of the request must be in the future.')
        if self.date == timezone.now().date() and self.time < timezone.now().time():
            raise ValidationError('The time of the request must be in the future.')

        if self.subscription_type == 'one-time':
            if self.subscription_option is not None:
                raise ValidationError('Subscription option should be blank for one-time service requests.')
            self.price = self.service.price
        elif self.subscription_type == 'monthly':
            if self.subscription_option is None:
                raise ValidationError('Subscription option should not be blank for monthly service requests.')
            if self.subscription_option.duration != 30:
                raise ValidationError('Subscription option duration should be 30 days for monthly service requests.')
            self.price = self.subscription_option.price

    def save(self, *args, **kwargs):
        self.request_price = self.get_total_price()
        self.full_clean()
        super().save(*args, **kwargs)
    def get_offers(self):
        offers = ServiceRequestOffer.objects.filter(service_request=self)
        serialized_offers = []
        for offer in offers:
            serialized_offer = {
                'name': offer.offer_name,
                'description': offer.offer_description,
                'price': offer.offer_price,
                'expiry_date': offer.offer_expiry
            }
            serialized_offers.append(serialized_offer)
        return serialized_offers
    def get_total_price(self):
        if self.subscription_type == 'one-time':
            return self.service.price
        elif self.subscription_type == 'monthly' and self.subscription_option is not None:
            if self.subscription_option.duration != 30:
                raise ValueError('Subscription option duration should be 30 days for monthly service requests.')
            return self.subscription_option.total_price
        else:
            raise ValueError('Invalid subscription type or option.')
    def payment_status(self):
        payments= Payment.objects.filter(service_request__id = self.id)
        valid_payment = [payment for payment in payments ]
        payment = []
        total_pays = 0 
        needs = 0 
        status ='pending'

        for payed in valid_payment:
            total_pays += payed.amount 
            if total_pays != self.request_price:
                needs = self.request_price - total_pays 
            else:
                status = 'success'
                needs = 0
            payment.append({
                        "amount": payed.amount,
                        "needs": needs,
                        "status": status
                    })
        
        return status
    @property
    def total_price(self):
        if self.subscription_type == 'one-time':
            return self.service.price
        elif self.subscription_type == 'monthly' and self.subscription_option is not None:
            if self.subscription_option.duration != 30:
                raise ValueError('Subscription option duration should be 30 days for monthly service requests.')
            return self.subscription_option.total_price
        else:
            raise ValueError('Invalid subscription type or option.')
    def get_end_date(self):
        if self.subscription_type == 'one-time':
            return self.date
        elif self.subscription_type == 'monthly' and self.subscription_option is not None:
            if self.subscription_option.duration != 30:
                raise ValueError('Subscription option duration should be 30 days for monthly service requests.')
            delta = datetime.timedelta(days=30)
            return self.date + delta
        else:
            raise ValueError('Invalid subscription type or option.')

    

class ServiceRequestOffer(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,null=True,blank=True)
    subscription_option = models.OneToOneField(SubscriptionOption, on_delete=models.CASCADE,null=True,blank=True)  # New field
    offer_name = models.CharField(max_length=255)
    offer_description = models.TextField()
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_expiry = models.DateField()

    def __str__(self):
        return self.offer_name
    

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # status = models.CharField(choices=[('processing','processing'),('success','success')],max_length=10)

    def __str__(self):
        return f"Payment for {self.service_request}"

    @classmethod
    def create_payment(cls, user, service_request):
        amount = service_request.get_total_price()
        payment = cls(user=user, service_request=service_request, amount=amount)
        payment.save()
        return payment