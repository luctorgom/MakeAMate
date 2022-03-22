from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.forms.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Aficiones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opcionAficiones', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Gustos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opcionGustos', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('etiqueta', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('piso', models.BooleanField()),
                ('fecha_nacimiento', models.DateField()),
                ('edad', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(18), django.core.validators.MaxValueValidator(30)])),
                ('lugar', models.CharField(max_length=10)),
                ('nacionalidad', models.CharField(max_length=10)),
                ('genero', models.CharField(choices=[('F', 'Femenino'), ('M', 'Masculino'), ('O', 'Otro')], max_length=1)),
                ('pronombres', models.CharField(choices=[('Ella', 'Ella'), ('El', 'El'), ('Elle', 'Elle')], max_length=4)),
                ('idiomas', models.CharField(choices=[('ES', 'Español'), ('EN', 'Inglés'), ('FR', 'Francés'), ('DE', 'Alemán'), ('PT', 'Portugués'), ('IT', 'Italiano'), ('SV', 'Sueco'), ('OT', 'Otro')], max_length=10)),
                ('universidad', models.CharField(max_length=40)),
                ('estudios', models.CharField(max_length=40)),
                ('aficiones', models.ManyToManyField(to='principal.Aficiones')),
                ('gustos', models.ManyToManyField(to='principal.Gustos')),
                ('tags', models.ManyToManyField(to='principal.Tags')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mate', models.BooleanField(default=django.forms.fields.NullBooleanField)),
                ('userEntrada', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='entrada', to=settings.AUTH_USER_MODEL)),
                ('userSalida', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='salida', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('userEntrada', 'userSalida')},
            },
        ),
    ]
