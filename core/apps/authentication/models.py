from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, Value
from django.db.models.functions import Concat, Upper, Substr, MD5
import secrets
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key_seed = models.CharField(max_length=128, unique=True, blank=True)
    is_api_key_active = models.BooleanField(default=True)

    # Django 5 GeneratedField for API key
    api_key = models.GeneratedField(
        expression=Concat(
            Value("ak_"),  # Prefix for identification
            Upper(Substr(MD5(Concat("id", "api_key_seed")), 1, 32)),
        ),
        output_field=models.CharField(max_length=35),
        db_persist=True,  # Store in database for performance
    )

    def save(self, *args, **kwargs):
        if not self.api_key_seed:
            self.api_key_seed = secrets.token_urlsafe(64)
        super().save(*args, **kwargs)

    def regenerate_api_key(self):
        """Regenerate API key by changing the seed"""
        self.api_key_seed = secrets.token_urlsafe(64)
        self.save()
        # The api_key field will be automatically updated by the database

    def __str__(self):
        return f"{self.username} (API: {self.api_key[:8]}...)"

    class Meta:
        db_table = "auth_user"
