from django.urls import path
from .views import ComplaintListCreateView, ComplaintRetrieveUpdateDeleteView

urlpatterns = [
    path('', ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path('<int:pk>/', ComplaintRetrieveUpdateDeleteView.as_view(), name='complaint-detail'),
]
