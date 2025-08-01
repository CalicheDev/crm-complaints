from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ], default='pending')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_complaints')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # Permitir valores nulos
        blank=True  # Opcional en formularios
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


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
