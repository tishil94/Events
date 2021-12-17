from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Create your models here.
CATEGORY_CHOICES = (("Music", 'Music'), ('Sports', 'Sports'))


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    location = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField()
    categories = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    published = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.end_date <= timezone.now() or self.start_date >= self.end_date:
            raise ValidationError("Enter Proper dates")


class UserEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)

    def __str__(self):
        return self.user


