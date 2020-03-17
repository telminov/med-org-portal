# Generated by Django 3.0.3 on 2020-03-02 19:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_ids', models.CharField(help_text='список id организаций из внешней системы', max_length=255, verbose_name='ID организаций')),
                ('django_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='core', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_workers_done_report', 'Просмотр отчета по прошедшим'), ('view_direction', 'Просмотр направлений на осмотр'), ('add_direction', 'Создание направлений на осмотр'), ('change_direction', 'Редактирование направлений на осмотр'), ('delete_direction', 'Удаление направлений на осмотр')),
            },
        ),
    ]
