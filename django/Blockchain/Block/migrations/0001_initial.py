# Generated by Django 2.1.5 on 2019-04-18 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=25)),
                ('hashValue', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name_plural': 'blocks',
            },
        ),
    ]
