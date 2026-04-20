from django.conf import settings
from django.db import models
from django.utils import timezone


class Field(models.Model):
    class Stage(models.TextChoices):
        PLANTED = 'planted', 'Planted'
        GROWING = 'growing', 'Growing'
        READY = 'ready', 'Ready'
        HARVESTED = 'harvested', 'Harvested'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        AT_RISK = 'at_risk', 'At Risk'
        COMPLETED = 'completed', 'Completed'

    # Stage-to-expected-days mapping: after N days without an update the field is at risk
    STAGE_RISK_DAYS = {
        Stage.PLANTED: 7,
        Stage.GROWING: 14,
        Stage.READY: 5,
        Stage.HARVESTED: None,
    }

    name = models.CharField(max_length=255)
    crop_type = models.CharField(max_length=255)
    planting_date = models.DateField()
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.PLANTED)
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_fields',
        limit_choices_to={'role': 'agent'},
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_fields',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def computed_status(self):
        # Harvested fields are always completed
        if self.stage == self.Stage.HARVESTED:
            return self.Status.COMPLETED

        # Determine when the field was last meaningfully updated
        last_update = self.updates.order_by('-created_at').first()
        reference_date = last_update.created_at.date() if last_update else self.planting_date

        days_since = (timezone.now().date() - reference_date).days
        risk_threshold = self.STAGE_RISK_DAYS.get(self.stage)

        if risk_threshold is not None and days_since > risk_threshold:
            return self.Status.AT_RISK

        return self.Status.ACTIVE

    def __str__(self):
        return self.name


class FieldUpdate(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='updates')
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='field_updates',
    )
    stage = models.CharField(max_length=20, choices=Field.Stage.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.field.name} — {self.stage} ({self.created_at:%Y-%m-%d})"
