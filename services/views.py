from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from services.models import Service, SubscriptionOption, ServiceRequest
from services.serializers import ServiceRequestSerializer, SubscriptionOptionSerializer, ServiceSerializer

class ServiceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ServiceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SubscriptionOptionListCreateAPIView(generics.ListCreateAPIView):
    queryset = SubscriptionOption.objects.all()
    serializer_class = SubscriptionOptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    
class SubscriptionOptionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionOption.objects.all()
    serializer_class = SubscriptionOptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def service_request_detail(request, service_request_id):
    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id, user=request.user)
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'Service request not found.'}, status=status.HTTP_404_NOT_FOUND)

    serialized_service_request = {
        'id': service_request.id,
        'user': service_request.user.username,
        'service': service_request.service.name,
        'subscription_type': service_request.subscription_type,
        'subscription_option': service_request.subscription_option.name,
        'date': service_request.date,
        'time': service_request.time,
        'offers': service_request.get_offers(),
        'car_number': service_request.car_number,
        'get_total_price': service_request.get_total_price(),
        'payment_status': service_request.payment_status(),
        'get_end_date': service_request.get_end_date(),
    }
    return Response(serialized_service_request)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_service(request):
    serializer = ServiceRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceRequestListAPIView(generics.ListAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ServiceRequest.objects.filter(user=self.request.user)

class ServiceRequestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ServiceRequest.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def services(request):
    queryset = Service.objects.all()
    serializer = ServiceSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_service(request):
    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([permissions.IsAdminUser])
def update_service(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ServiceSerializer(service, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

    service.delete()
    return Response({'success': 'Service deleted successfully.'})

