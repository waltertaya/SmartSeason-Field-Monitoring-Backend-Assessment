from django.urls import path
from .views import DashboardView, FieldDetailView, FieldListCreateView, FieldUpdateListCreateView

urlpatterns = [
    path('', FieldListCreateView.as_view(), name='field_list_create'),
    path('<int:pk>/', FieldDetailView.as_view(), name='field_detail'),
    path('<int:field_pk>/updates/', FieldUpdateListCreateView.as_view(), name='field_updates'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
