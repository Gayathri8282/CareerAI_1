# Generated by Django 5.1.4 on 2024-12-28 16:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerai', '0003_course_milestone'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='skill',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='skill_proficiencies',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='skills',
            field=models.ManyToManyField(blank=True, to='careerai.skill'),
        ),
    ]
