from django.contrib import admin
from .models import UserProfile, Roadmap, RoadmapTask, Skill, CareerPath, Activity

@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_required_skills']
    search_fields = ['title', 'description']

    def get_required_skills(self, obj):
        return ", ".join([skill.name for skill in obj.required_skills.all()])
    get_required_skills.short_description = 'Required Skills'

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']

@admin.register(RoadmapTask)
class RoadmapTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'roadmap', 'completed', 'order', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['description']

admin.site.register(UserProfile)

