from django.db import models
from django.contrib.auth.models import User


class Topic (models.Model):
    name= models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room (models.Model):
    host= models.ForeignKey(User, on_delete=models.SET_NULL,null= True)     #if Topic is deleted, Room won't be
    topic= models.ForeignKey(Topic, on_delete=models.SET_NULL,null= True)   #if Topic is deleted, Room won't be
    name= models.CharField(max_length=150)
    description= models.TextField(null=True, blank=True)
    participants= models.ManyToManyField(User, related_name='participants', blank= True)
    updated= models.DateTimeField(auto_now=True)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering= ['-updated','-created_at']

    def __str__(self):          #Room.objects.get(id=pk) return this self.name(which must be a string value) value
        return self.name
    
class Message (models.Model):
    user= models.ForeignKey(User, on_delete= models.CASCADE)
    room= models.ForeignKey(Room, on_delete= models.CASCADE) 
    body= models.TextField()
    updated= models.DateTimeField(auto_now=True)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering= ['-updated', '-created_at']

    def __str__(self): 
        return self.body[0:50]
    