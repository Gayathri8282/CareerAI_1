from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    experience = models.CharField(max_length=20, blank=True)
    goals = models.TextField(blank=True)  # Add this line

# The rest of the models remain unchanged
class CareerPath(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    skills = models.TextField()
    match_score = models.IntegerField(default=0)

class Mentor(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    expertise = models.TextField()
    availability = models.CharField(max_length=100)

class RoadmapStage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    progress = models.IntegerField(default=0)

class Task(models.Model):
    stage = models.ForeignKey(RoadmapStage, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    deadline = models.DateField()
    completed = models.BooleanField(default=False)

