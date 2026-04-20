from django.contrib import admin
from .models import Field, FieldUpdate


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'crop_type', 'stage', 'assigned_agent', 'planting_date')
    list_filter = ('stage',)


@admin.register(FieldUpdate)
class FieldUpdateAdmin(admin.ModelAdmin):
    list_display = ('field', 'agent', 'stage', 'created_at')
    list_filter = ('stage',)
