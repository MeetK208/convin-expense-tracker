from django.db import models
from passlib.hash import pbkdf2_sha256


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=12)
    
    def verifyPassword(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)
    
    def __str__(self):
        return self.user_id + " - " + self.email + " - " +  self.username