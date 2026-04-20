import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from fields.models import Field, FieldUpdate


FIELDS_DATA = [
    {"name": "North Field A", "crop_type": "Maize", "stage": "growing"},
    {"name": "North Field B", "crop_type": "Maize", "stage": "planted"},
    {"name": "South Field 1", "crop_type": "Wheat", "stage": "ready"},
    {"name": "South Field 2", "crop_type": "Wheat", "stage": "harvested"},
    {"name": "East Plot Alpha", "crop_type": "Tomato", "stage": "growing"},
    {"name": "East Plot Beta", "crop_type": "Tomato", "stage": "at_risk_growing"},
    {"name": "West Greenhouse 1", "crop_type": "Pepper", "stage": "ready"},
    {"name": "West Greenhouse 2", "crop_type": "Pepper", "stage": "growing"},
    {"name": "River Basin Field", "crop_type": "Soybean", "stage": "harvested"},
    {"name": "Hill Top Field", "crop_type": "Sorghum", "stage": "planted"},
    {"name": "Valley Section A", "crop_type": "Cassava", "stage": "growing"},
    {"name": "Valley Section B", "crop_type": "Cassava", "stage": "at_risk_planted"},
]

NOTES = [
    "Soil moisture looks good. Crop showing healthy growth.",
    "Noticed some pest activity on the eastern edge. Will monitor.",
    "Irrigation system checked and working fine.",
    "Some yellowing on lower leaves — may need fertilizer.",
    "Growth rate is excellent after last week's rain.",
    "Weeding completed across the entire plot.",
    "Ready for harvest within the next few days.",
    "Applied organic pesticide as a preventive measure.",
    "Germination rate looks very healthy.",
    "Stand count done — population is within target range.",
    "Canopy closure observed — moving to next stage.",
    "Soil sample taken and sent for analysis.",
]


class Command(BaseCommand):
    help = "Seed the database with realistic dummy data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing fields and updates before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            FieldUpdate.objects.all().delete()
            Field.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing fields and updates."))

        admin = self._get_or_create_user(
            username="admin",
            password="admin@2026?",
            role=User.Role.ADMIN,
            first_name="Alice",
            last_name="Coordinator",
            email="admin@smartseason.com",
        )
        agent1 = self._get_or_create_user(
            username="agent",
            password="agent@2026?",
            role=User.Role.AGENT,
            first_name="Bob",
            last_name="Fieldman",
            email="agent@smartseason.com",
        )

        agents = [agent1]
        agents_count = len(agents)
        today = date.today()
        created_count = 0

        for i, data in enumerate(FIELDS_DATA):
            agent = agents[i % agents_count]
            raw_stage = data["stage"]

            at_risk = raw_stage.startswith("at_risk_")
            actual_stage = raw_stage.replace("at_risk_", "") if at_risk else raw_stage

            stage_age = {
                "planted": random.randint(3, 10),
                "growing": random.randint(20, 45),
                "ready": random.randint(60, 90),
                "harvested": random.randint(100, 130),
            }
            planting_date = today - timedelta(days=stage_age[actual_stage])

            field, created = Field.objects.get_or_create(
                name=data["name"],
                defaults={
                    "crop_type": data["crop_type"],
                    "planting_date": planting_date,
                    "stage": actual_stage,
                    "assigned_agent": agent,
                    "created_by": admin,
                },
            )
            if not created:
                self.stdout.write(f"  Skipped (already exists): {field.name}")
                continue
            created_count += 1

            stage_order = ["planted", "growing", "ready", "harvested"]
            stages_to_log = stage_order[: stage_order.index(actual_stage) + 1]

            if at_risk:
                risk_gap = {"planted": 10, "growing": 20, "ready": 8}
                last_update_days_ago = risk_gap.get(actual_stage, 15)
            else:
                last_update_days_ago = random.randint(1, 4)

            last_update_date = today - timedelta(days=last_update_days_ago)
            update_dates = self._spread_dates(
                start=planting_date + timedelta(days=2),
                end=last_update_date,
                count=len(stages_to_log),
            )

            for stage_label, update_date in zip(stages_to_log, update_dates):
                dt = timezone.make_aware(
                    timezone.datetime(
                        update_date.year, update_date.month, update_date.day,
                        random.randint(7, 17), random.randint(0, 59),
                    )
                )
                FieldUpdate.objects.create(
                    field=field,
                    agent=agent,
                    stage=stage_label,
                    notes=random.choice(NOTES),
                    created_at=dt,
                )

            self.stdout.write(f"  Created: {field.name} ({actual_stage}{'  [AT RISK]' if at_risk else ''})")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count} fields with update histories.\n"
                f"Demo accounts:\n"
                f"  admin  / admin@2026?  (Admin)\n"
                f"  agent / agent@2026?  (Field Agent - Bob Fieldman)\n"
            )
        )

    def _get_or_create_user(self, username, password, role, first_name, last_name, email):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"role": role, "first_name": first_name, "last_name": last_name, "email": email},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"  Created user: {username} ({role})")
        else:
            self.stdout.write(f"  User exists: {username}")
        return user

    @staticmethod
    def _spread_dates(start: date, end: date, count: int) -> list[date]:
        if count == 1:
            return [end]
        if start >= end:
            return [end] * count
        delta = (end - start).days
        step = delta / (count - 1)
        return [start + timedelta(days=round(i * step)) for i in range(count)]
