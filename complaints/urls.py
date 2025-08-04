from django.urls import path
from .views import (
    ComplaintListCreateView, ComplaintDetailView, ComplaintAssignView,
    ComplaintStatusUpdateView, DashboardView, MyComplaintsView,
    AgentComplaintsView, AvailableAgentsView, AtencionListCreateView,
    AtencionDetailView, DiagnosticView, PublicPQRSCreateView
)

urlpatterns = [
    # Public PQRS endpoint (anonymous)
    path('public/pqrs/', PublicPQRSCreateView.as_view(), name='public-pqrs-create'),
    
    # Core complaint endpoints
    path('', ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path('<int:pk>/', ComplaintDetailView.as_view(), name='complaint-detail'),
    
    # Complaint management endpoints
    path('<int:pk>/assign/', ComplaintAssignView.as_view(), name='complaint-assign'),
    path('<int:pk>/status/', ComplaintStatusUpdateView.as_view(), name='complaint-status-update'),
    
    # User-specific endpoints
    path('my/', MyComplaintsView.as_view(), name='my-complaints'),
    path('agent/', AgentComplaintsView.as_view(), name='agent-complaints'),
    
    # Admin endpoints
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('agents/', AvailableAgentsView.as_view(), name='available-agents'),
    
    # Atencion endpoints
    path('<int:complaint_id>/atenciones/', AtencionListCreateView.as_view(), name='atencion-list-create'),
    path('atenciones/<int:pk>/', AtencionDetailView.as_view(), name='atencion-detail'),
    
    # Diagnostic endpoint (temporary)
    path('<int:complaint_id>/diagnostic/', DiagnosticView.as_view(), name='diagnostic'),
]
