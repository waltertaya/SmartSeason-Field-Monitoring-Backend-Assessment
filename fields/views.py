from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Field, FieldUpdate
from .permissions import IsAdmin, IsAdminOrAssignedAgent
from .serializers import FieldSerializer, FieldUpdateSerializer


class FieldListCreateView(generics.ListCreateAPIView):
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Field.objects.select_related('assigned_agent', 'created_by').prefetch_related('updates').all()
        return Field.objects.select_related('assigned_agent', 'created_by').prefetch_related('updates').filter(
            assigned_agent=user
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class FieldDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedAgent]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Field.objects.select_related('assigned_agent', 'created_by').prefetch_related('updates').all()
        return Field.objects.select_related('assigned_agent', 'created_by').prefetch_related('updates').filter(
            assigned_agent=user
        )

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdmin()]
        return [permissions.IsAuthenticated(), IsAdminOrAssignedAgent()]


class FieldUpdateListCreateView(generics.ListCreateAPIView):
    serializer_class = FieldUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        field_id = self.kwargs['field_pk']
        user = self.request.user
        qs = FieldUpdate.objects.select_related('agent', 'field').filter(field_id=field_id)
        if not user.is_admin:
            qs = qs.filter(field__assigned_agent=user)
        return qs

    def perform_create(self, serializer):
        field_id = self.kwargs['field_pk']
        field = Field.objects.get(pk=field_id)
        user = self.request.user
        if not user.is_admin and field.assigned_agent != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not assigned to this field.")
        serializer.save(field=field)
