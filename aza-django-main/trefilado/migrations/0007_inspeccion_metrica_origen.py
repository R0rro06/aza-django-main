import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trefilado", "0006_metricacaptura_asociaciones_gestion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inspeccion",
            name="lote",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="inspecciones",
                to="trefilado.lote",
            ),
        ),
        migrations.AddField(
            model_name="inspeccion",
            name="metrica",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="inspeccion_generada",
                to="trefilado.metricacaptura",
            ),
        ),
    ]
