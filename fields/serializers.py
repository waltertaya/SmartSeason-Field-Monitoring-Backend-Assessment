from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Field, FieldUpdate


class FieldUpdateSerializer(serializers.ModelSerializer):
    agent = UserSerializer(read_only=True)

    class Meta:
        model = FieldUpdate
        fields = ('id', 'field', 'agent', 'stage', 'notes', 'created_at')
        read_only_fields = ('id', 'agent', 'created_at')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['agent'] = request.user
        update = super().create(validated_data)
        # Advance the field stage to whatever was submitted
        field = update.field
        field.stage = update.stage
        field.save(update_fields=['stage', 'updated_at'])
        return update


class FieldSerializer(serializers.ModelSerializer):
    assigned_agent = UserSerializer(read_only=True)
    assigned_agent_id = serializers.PrimaryKeyRelatedField(
        source='assigned_agent',
        queryset=__import__('accounts').models.User.objects.filter(role='agent'),
        write_only=True,
        required=False,
        allow_null=True,
    )
    created_by = UserSerializer(read_only=True)
    computed_status = serializers.CharField(read_only=True)
    latest_update = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = (
            'id', 'name', 'crop_type', 'planting_date', 'stage',
            'computed_status', 'assigned_agent', 'assigned_agent_id',
            'created_by', 'created_at', 'updated_at', 'latest_update',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def get_latest_update(self, obj):
        update = obj.updates.first()
        if update:
            return FieldUpdateSerializer(update).data
        return None

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
