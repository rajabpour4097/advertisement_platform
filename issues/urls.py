from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('report/', views.report_issue, name='report'),
    path('list/', views.IssueListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.IssueDetailView.as_view(), name='detail'),
]
