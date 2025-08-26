from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/close/', views.ticket_close_view, name='ticket_close'),
    path('tickets/<int:pk>/rate/', views.ticket_rate_view, name='ticket_rate'),
    # live chat
    path('livechat/history/', views.LiveChatHistoryListView.as_view(), name='livechat_history'),
    path('livechat/start/', views.livechat_start_view, name='livechat_start'),
    path('livechat/<int:session_id>/send/', views.livechat_send_message, name='livechat_send'),
    path('livechat/<int:session_id>/messages/', views.livechat_messages, name='livechat_messages'),
    path('livechat/departments/', views.livechat_departments, name='livechat_departments'),
    path('livechat/ping/', views.livechat_ping, name='livechat_ping'),
]
