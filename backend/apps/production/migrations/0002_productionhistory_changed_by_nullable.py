import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Permite changed_by=NULL en ProductionHistory.
    NULL indica que el cambio fue realizado por el sistema (cancelación automática, scheduler, etc.)
    """

    dependencies = [
        ("production", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="productionhistory",
            name="changed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="production_history_changes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
