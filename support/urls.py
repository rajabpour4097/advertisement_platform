from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/close/', views.ticket_close_view, name='ticket_close'),
    path('tickets/<int:pk>/rate/', views.ticket_rate_view, name='ticket_rate'),
]
