from django.db import models

# Create your models here.


class dataModel(models.Model):
    RegistrationNo = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    Father = models.CharField(max_length=255)
    Mother = models.CharField(max_length=255)
    College = models.CharField(max_length=255)
    Place = models.CharField(max_length=255)
    Roll = models.CharField(max_length=255)
    Group = models.CharField(max_length=255)
    GPA = models.CharField(max_length=255)
