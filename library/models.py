from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE

class User(AbstractUser):
    pass

class Books(models.Model):
    bookid = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=256, null=True)
    description = models.CharField(max_length=5000, null=True)
    authors = models.CharField(max_length=256, null=True)
    isbn = models.CharField(max_length=16, null=True)
    thumbnail = models.URLField(null=True)
    
class record(models.Model):
    user =  models.ForeignKey(User, on_delete=CASCADE, null=True)
    book =  models.ForeignKey(Books, on_delete=CASCADE, null=True)
    timeCreated = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('book', 'user',)
