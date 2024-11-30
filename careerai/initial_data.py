# careerai/initial_data.py

from django.contrib.auth.models import User
from .models import CareerPath, Mentor, RoadmapStage, Task, UserProfile

def create_initial_data():
    # Create sample career paths
    career_paths = [
        {
            'title': 'Software Developer',
            'description': 'Design and develop software applications',
            'skills': 'Python,JavaScript,SQL,Git',
            'match_score': 85
        },
        {
            'title': 'Data Scientist',
            'description': 'Analyze complex data sets to drive business decisions',
            'skills': 'Python,R,SQL,Machine Learning,Statistics',
            'match_score': 75
        },
        {
            'title': 'UX Designer',
            'description': 'Create user-centered digital experiences',
            'skills': 'UI Design,User Research,Wireframing,Prototyping',
            'match_score': 70
        }
    ]
    
    for path_data in career_paths:
        CareerPath.objects.get_or_create(
            title=path_data['title'],
            defaults={
                'description': path_data['description'],
                'skills': path_data['skills'],
                'match_score': path_data['match_score']
            }
        )

    # Create sample mentors
    mentors = [
        {
            'name': 'Dr. Sarah Chen',
            'role': 'Senior Data Scientist',
            'company': 'Tech Corp',
            'expertise': 'Machine Learning, AI, Data Analytics',
            'availability': 'Tuesday and Thursday evenings'
        },
        {
            'name': 'John Smith',
            'role': 'Lead Software Engineer',
            'company': 'Innovation Labs',
            'expertise': 'Full-stack Development, System Architecture',
            'availability': 'Monday and Wednesday afternoons'
        },
        {
            'name': 'Emma Wilson',
            'role': 'UX Research Manager',
            'company': 'Design Solutions',
            'expertise': 'User Research, Product Strategy',
            'availability': 'Friday mornings'
        }
    ]
    
    for mentor_data in mentors:
        Mentor.objects.get_or_create(
            name=mentor_data['name'],
            defaults={
                'role': mentor_data['role'],
                'company': mentor_data['company'],
                'expertise': mentor_data['expertise'],
                'availability': mentor_data['availability']
            }
        )

    # Create sample roadmap stages
    stages = [
        {
            'title': 'Foundation',
            'description': 'Build your fundamental skills',
            'progress': 75,
            'tasks': [
                {
                    'title': 'Complete Python Basics Course',
                    'type': 'Course',
                    'deadline': '2024-12-31',
                    'completed': True
                },
                {
                    'title': 'Build Portfolio Website',
                    'type': 'Project',
                    'deadline': '2024-12-31',
                    'completed': False
                }
            ]
        },
        {
            'title': 'Advanced Skills',
            'description': 'Develop specialized expertise',
            'progress': 50,
            'tasks': [
                {
                    'title': 'Machine Learning Certification',
                    'type': 'Certification',
                    'deadline': '2024-12-31',
                    'completed': False
                },
                {
                    'title': 'Contribute to Open Source',
                    'type': 'Project',
                    'deadline': '2024-12-31',
                    'completed': False
                }
            ]
        }
    ]
    
    for stage_data in stages:
        stage, created = RoadmapStage.objects.get_or_create(
            title=stage_data['title'],
            defaults={
                'description': stage_data['description'],
                'progress': stage_data['progress']
            }
        )
        
        if created:
            for task_data in stage_data['tasks']:
                Task.objects.create(
                    stage=stage,
                    title=task_data['title'],
                    type=task_data['type'],
                    deadline=task_data['deadline'],
                    completed=task_data['completed']
                )