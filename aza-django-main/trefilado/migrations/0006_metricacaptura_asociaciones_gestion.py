import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trefilado', '0005_inspeccion_operador'),
    ]

    operations = [
        migrations.AddField(
            model_name='metricacaptura',
            name='lote',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='metricas_capturadas',
                to='trefilado.lote',
            ),
        ),
        migrations.AddField(
            model_name='metricacaptura',
            name='receta',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='metricas_capturadas',
                to='trefilado.receta',
            ),
        ),
        migrations.AddField(
            model_name='metricacaptura',
            name='operador',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='metricas_operadas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
