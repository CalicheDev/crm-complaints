from rest_framework import serializers
from .models import ComplaintAttachment


class PublicPQRSSerializer(serializers.Serializer):
    """Serializer for public PQRS submissions (anonymous)."""
    title = serializers.CharField(max_length=255, min_length=5)
    description = serializers.CharField(min_length=10, max_length=2000)
    complaint_type = serializers.ChoiceField(
        choices=[
            ('peticion', 'Petición'),
            ('queja', 'Queja'),
            ('reclamo', 'Reclamo'),
            ('sugerencia', 'Sugerencia'),
        ]
    )
    
    # Citizen information
    citizen_name = serializers.CharField(max_length=200)
    citizen_email = serializers.EmailField(required=False, allow_blank=True)
    citizen_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    citizen_address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    citizen_document = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_title(self, value):
        """Validate complaint title."""
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("El título debe tener al menos 5 caracteres.")
        return value
    
    def validate_description(self, value):
        """Validate complaint description."""
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres.")
        return value
    
    def validate_citizen_name(self, value):
        """Validate citizen name."""
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        # At least email or phone is required for contact
        citizen_email = data.get('citizen_email', '').strip()
        citizen_phone = data.get('citizen_phone', '').strip()
        
        if not citizen_email and not citizen_phone:
            raise serializers.ValidationError(
                "Debe proporcionar al menos un email o teléfono para contacto."
            )
        
        return data


class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for complaint attachments."""
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = ComplaintAttachment
        fields = ['id', 'original_filename', 'file_size', 'file_size_mb', 'content_type', 'uploaded_at', 'file']
        read_only_fields = ['id', 'uploaded_at', 'file_size', 'content_type']