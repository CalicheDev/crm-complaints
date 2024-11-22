from django.urls import path
from .views import ComplaintListCreateView, ComplaintRetrieveUpdateDeleteView, ComplaintAssignAgentView, DashboardView

urlpatterns = [
    path('', ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path('<int:pk>/', ComplaintRetrieveUpdateDeleteView.as_view(), name='complaint-detail'),
    path('<int:pk>/assign/', ComplaintAssignAgentView.as_view(), name='assign-agent'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
