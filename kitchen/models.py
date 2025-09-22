from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class DishType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Cook(AbstractUser):
    years_of_experience = models.IntegerField()

class Dish(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField()
    dish_type = models.ForeignKey(DishType, on_delete=models.CASCADE)
    cooks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dishes')

    def __str__(self):
        return self.name


