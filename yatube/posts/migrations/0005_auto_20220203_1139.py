# Generated by Django 2.2.16 on 2022-02-03 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220202_1734'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'группа', 'verbose_name_plural': 'группы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'пост', 'verbose_name_plural': 'посты'},
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите картинку', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
