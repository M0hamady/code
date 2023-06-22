from django.urls import path
from services.views import (
    ServiceListCreateAPIView,
    ServiceRetrieveUpdateDestroyAPIView,
    SubscriptionOptionListCreateAPIView,
    SubscriptionOptionRetrieveUpdateDestroyAPIView,
    ServiceRequestListAPIView,
    ServiceRequestRetrieveUpdateDestroyAPIView,
    service_request_detail,
    request_service,
    services,
    create_service,
    update_service,
    delete_service,
)

urlpatterns = [
    path('services/', ServiceListCreateAPIView.as_view(), name='service_list_create'),
    path('services/<int:pk>/', ServiceRetrieveUpdateDestroyAPIView.as_view(), name='service_retrieve_update_destroy'),
    path('subscription_options/', SubscriptionOptionListCreateAPIView.as_view(), name='subscription_option_list_create'),
    path('subscription_options/<int:pk>/', SubscriptionOptionRetrieveUpdateDestroyAPIView.as_view(), name='subscription_option_retrieve_update_destroy'),
    path('service_requests/', ServiceRequestListAPIView.as_view(), name='service_request_list'),
    path('service_requests/<int:pk>/', ServiceRequestRetrieveUpdateDestroyAPIView.as_view(), name='service_request_retrieve_update_destroy'),
    path('service_requests/<int:service_request_id>/detail/', service_request_detail, name='service_request_detail'),
    path('service_requests/request/', request_service, name='request_service'),
    path('services/all/', services, name='all_services'),
    path('services/create/', create_service, name='create_service'),
    path('services/<int:service_id>/update/', update_service, name='update_service'),
    path('services/<int:service_id>/delete/', delete_service, name='delete_service'),
]