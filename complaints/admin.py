from django.contrib import admin
from .models import Complaint, Atencion


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'assigned_to', 'created_by', 'created_at']
    list_filter = ['status', 'created_at', 'assigned_to']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'agent', 'tipo_contacto', 'resultado', 'created_at']
    list_filter = ['tipo_contacto', 'resultado', 'created_at', 'agent']
    search_fields = ['complaint__title', 'agent__username', 'observacion']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('complaint', 'agent')
