from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import os

def complaint_file_upload_path(instance, filename):
    return f'complaints/{instance.id}/{filename}'

class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('peticion', 'Petición'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPES, default='queja')
    
    # Información del ciudadano (para PQRS anónimas)
    citizen_name = models.CharField(max_length=200, null=True, blank=True)
    citizen_email = models.EmailField(null=True, blank=True)
    citizen_phone = models.CharField(max_length=20, null=True, blank=True)
    citizen_address = models.TextField(null=True, blank=True)
    citizen_document = models.CharField(max_length=50, null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ], default='pending')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_complaints')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # Permitir valores nulos para PQRS anónimas
        blank=True  # Opcional en formularios
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def is_anonymous(self):
        return self.created_by is None


class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=complaint_file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.title} - {self.original_filename}"
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)


class Atencion(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='atenciones')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='atenciones_realizadas')
    observacion = models.TextField()
    tipo_contacto = models.CharField(max_length=50, choices=[
        ('telefono', 'Teléfono'),
        ('email', 'Email'),
        ('presencial', 'Presencial'),
        ('chat', 'Chat'),
        ('otro', 'Otro'),
    ], default='telefono')
    resultado = models.CharField(max_length=50, choices=[
        ('contactado', 'Contactado exitosamente'),
        ('no_contactado', 'No se pudo contactar'),
        ('informacion_adicional', 'Se obtuvo información adicional'),
        ('seguimiento_requerido', 'Requiere seguimiento'),
        ('resuelto', 'Resuelto en esta atención'),
    ], default='contactado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Atención'
        verbose_name_plural = 'Atenciones'

    def __str__(self):
        return f"Atención - {self.complaint.title} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
