from django.db import models

class MyProfile(models.Model):
    user = models.OneToOneField("auth.User")
