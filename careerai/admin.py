from django.contrib import admin
from .models import UserProfile, CareerPath, Mentor, RoadmapStage, Task

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'interests', 'experience')
    search_fields = ('user__username', 'skills', 'interests')

@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'skills', 'match_score')
    search_fields = ('title', 'skills')

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'company', 'expertise', 'availability')
    search_fields = ('name', 'role', 'company', 'expertise')

@admin.register(RoadmapStage)
class RoadmapStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'progress')
    search_fields = ('title',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'stage', 'type', 'deadline', 'completed')
    list_filter = ('stage', 'type', 'completed')
    search_fields = ('title',)

