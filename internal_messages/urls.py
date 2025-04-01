from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('sent/', views.SentView.as_view(), name='sent'),
    path('compose/', views.ComposeView.as_view(), name='compose'),
    path('detail/<int:pk>/', views.MessageDetailView.as_view(), name='detail'),
]