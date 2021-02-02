from django.db import models


# Create your models here.

class Profile(models.Model):
    user_id = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f'{self.user_id}'
