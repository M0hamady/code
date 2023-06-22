from django.utils import timezone
from rest_framework import serializers
from services.models import Payment, Service, ServiceRequest, ServiceRequestOffer, SubscriptionOption

class ServiceRequestOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestOffer
        fields = ('id', 'offer_name', 'offer_description', 'offer_price', 'offer_expiry')
class ServiceRequestSerializer(serializers.ModelSerializer):
    # date = serializers.DateField(required = False)
    payments = serializers.SerializerMethodField(read_only=True)

    def get_payments(self, instance):
        payments= Payment.objects.filter(service_request__id = instance.id)
        valid_payment = [payment for payment in payments ]
        payment = []
        total_pays = 0 
        needs = 0 
        for payed in valid_payment:
            total_pays += payed.amount 
            if total_pays != instance.request_price:
                status ='pending'
                needs = instance.request_price - total_pays 
            else:
                status = 'success'
                needs = 0
            payment.append({
                        "amount": payed.amount,
                        "needs": needs,
                        "status": status
                    })
        
        return payment
    
    class Meta:
        model = ServiceRequest
        fields = ['id', 'user', 'service', 'subscription_type', 'payment_status','payments','subscription_option', 'date', 'get_end_date','time', 'get_offers','request_price',]
        read_only_fields = ['id', 'user', 'get_offers']

    def validate(self, data):
        # Check if date and time are valid
        datetime = timezone.make_aware(timezone.datetime.combine(data['date'], data['time']))
        if datetime < timezone.now():
            raise serializers.ValidationError('The date and time of the request must be in the future.')
        
        if data['subscription_type'] == 'monthly' and not data.get('subscription_option'):
            subscriptionOption = SubscriptionOption.objects.all().values()
            raise serializers.ValidationError({'error': 'Subscription option should not be blank for monthly service requests.','message':'Subscription option should not be blank for monthly service requests.',
                                               'suggestions':f'{subscriptionOption}'})

        return data
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
class SubscriptionOptionSerializer(serializers.ModelSerializer):
    # get_offers = ServiceRequestOfferSerializer(many=True, read_only=True)

    class Meta:
        model = SubscriptionOption
        fields = ['id', 'name', 'description', 'price','get_offers','get_total_price']

class ServiceSerializer(serializers.ModelSerializer):
    subscription_options = SubscriptionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'subscription_options']


class PaymentSerializer(serializers.ModelSerializer):
    service_request = ServiceRequestSerializer(read_only=True)
    service_request_id = serializers.PrimaryKeyRelatedField(queryset=ServiceRequest.objects.all(), source='service_request', write_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)

    class Meta:
        model = Payment
        fields = ['id', 'service_request', 'service_request_id', 'amount', 'timestamp']

    def validate_service_request_id(self, value):
        """
        Check that the service request is open and the user is the owner.
        """
        service_request = value
        user = self.context['request'].user

        if service_request.user != user:
            raise serializers.ValidationError("You do not have permission to make a payment for this service request.")

        if service_request.subscription_type == 'one-time' and service_request.date < timezone.now().date():
            raise serializers.ValidationError("You cannot make a payment for a past one-time service request.")

        if service_request.subscription_type == 'monthly' and not service_request.subscription_option:
            raise serializers.ValidationError("You cannot make a payment for a monthly service request without a subscription option.")

        if service_request.subscription_type == 'monthly' and service_request.subscription_option and service_request.subscription_option.end_date <= timezone.now().date():
            raise serializers.ValidationError("You cannot make a payment for an expired subscription option.")

        return value

    def create(self, validated_data):
        """
        Create a new payment instance.
        """
        service_request = validated_data['service_request']
        amount = validated_data['amount']
        payment = Payment.objects.create(
            user=service_request.user,
            service_request=service_request,
            amount=amount
        )
        return payment