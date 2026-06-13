from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class UserSettings(models.Model):
    class Language(models.TextChoices):
        EN = 'en', 'English'
        UK = 'uk', 'Ukrainian'

    class Theme(models.TextChoices):
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'
        SYSTEM = 'system', 'System'
    
    class AccentColor(models.TextChoices):
        PURPLE = "purple", "Purple"
        BLUE = "blue", "Blue"
        CYAN = "cyan", "Cyan"
        GREEN = "green", "Green"
        ORANGE = "orange", "Orange"
        RED = "red", "Red"
        PINK = "pink", "Pink"

    class Density(models.TextChoices):
        COMFORTABLE = "comfortable", "Comfortable"
        COMPACT = "compact", "Compact"

    class SidebarBehavior(models.TextChoices):
        EXPANDED = "expanded", "Expanded"
        COLLAPSED = "collapsed", "Collapsed"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    language = models.CharField(
        max_length=10, choices=Language.choices, default=Language.EN
    )

    timezone = models.CharField(
        max_length=64,
        default='UTC',
    )

    theme = models.CharField(
        max_length=20,
        choices=Theme.choices,
        default=Theme.SYSTEM,
    )

    accent_color = models.CharField(
        max_length=20,
        choices=AccentColor.choices,
        default=AccentColor.CYAN,
    )

    density = models.CharField(
        max_length=20,
        choices=Density.choices,
        default=Density.COMFORTABLE,
    )

    sidebar_behavior = models.CharField(
        max_length=20,
        choices=SidebarBehavior.choices,
        default=SidebarBehavior.EXPANDED,
    )

    animations_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Settings for {self.user}'
