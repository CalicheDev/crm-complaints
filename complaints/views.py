from rest_framework import generics
from rest_framework.views import APIView
from .models import Complaint
from .serializers import ComplaintSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.decorators import action
from rest_framework.response import Response

class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()  # Permitir quejas anónimas

class ComplaintRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]


class ComplaintAssignAgentView(APIView):
    """
    Endpoint para asignar agentes a quejas.
    Solo los administradores pueden realizar esta acción.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            complaint = Complaint.objects.get(pk=pk)
            agent_id = request.data.get('agent_id')
            agent = User.objects.get(pk=agent_id, groups__name='agent')

            complaint.assigned_to = agent
            complaint.status = 'in_progress'  # Cambiar estado automáticamente
            complaint.save()

            return Response({'message': 'Agente asignado con éxito.'})
        except Complaint.DoesNotExist:
            return Response({'error': 'Queja no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Agente no encontrado o no tiene el rol correcto.'}, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    """
    Endpoint para obtener datos analíticos del dashboard.
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Verificar que el usuario pertenece al grupo 'admin'
        if not request.user.groups.filter(name='admin').exists():
            return Response({'error': 'Permiso denegado. Solo para administradores.'}, status=403)

        # Número total de quejas
        total_complaints = Complaint.objects.count()

        # Quejas por estado
        complaints_by_status = Complaint.objects.values('status').annotate(count=Count('id'))

        # Tiempo promedio de resolución de quejas resueltas
        avg_resolution_time = Complaint.objects.filter(status='resolved').annotate(
            resolution_time=ExpressionWrapper(
                now() - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(avg_time=Avg('resolution_time'))

        # Total de agentes y su carga actual
        agents = Complaint.objects.filter(assigned_to__groups__name='agent').values('assigned_to__username').annotate(
            count=Count('id')
        )

        return Response({
            'total_complaints': total_complaints,
            'complaints_by_status': complaints_by_status,
            'avg_resolution_time': avg_resolution_time['avg_time'].total_seconds() if avg_resolution_time['avg_time'] else None,
            'agents_load': agents
        })
