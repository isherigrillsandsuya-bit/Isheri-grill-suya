from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_options_alter_customuser_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='otp_code',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='referral_code',
            field=models.CharField(max_length=10, null=True, blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='referred_by',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
