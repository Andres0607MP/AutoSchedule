"""Auto migration to add new fields added during development.

Generated manually to align DB with models updated in phase 2.
"""
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('queueo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='estimated_duration',
            field=models.IntegerField(null=True, default=15),
        ),
        migrations.AddField(
            model_name='service',
            name='created_at',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AddField(
            model_name='service',
            name='updated_at',
            field=models.DateTimeField(null=True, auto_now=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='estimated_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='position_in_queue',
            field=models.PositiveIntegerField(null=True, default=0),
        ),
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['-priority', 'created_at']},
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['status', 'created_at'], name='queueo_ticket_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['service', 'status'], name='queueo_ticket_service_status_idx'),
        ),
    ]
