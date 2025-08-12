from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'channels', views.CommunicationChannelViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'conversations', views.ConversationViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'interactions', views.InteractionHistoryViewSet)
router.register(r'tags', views.ConversationTagViewSet)
router.register(r'integrations', views.ChannelIntegrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]