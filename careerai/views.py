from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import (
    CareerPath, 
    Mentor, 
    RoadmapStage, 
    UserProfile, 
    Task, 
    Meeting, 
    Review, 
    Roadmap,
    Skill,
    Interest,
    SavedCareer,
    Course,
    Milestone,
    RoadmapTask,
    Activity
)
from .forms import LoginForm, UserProfileForm
from .initial_data import create_initial_data
from django.db.models import Q, Avg
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
import json
from django.db import models

def landing_page(request):
    return render(request, 'careerai/landing.html')

def about(request):
    return render(request, 'careerai/about.html')

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    # Simplified progress calculation
    try:
        total_tasks = Task.objects.filter(user=request.user).count()
        completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
        progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    except:
        progress = 0
    
    today = timezone.now().date()
    
    context = {
        'user_profile': user_profile,
        'skills_count': user_profile.skills.count(),
        'progress': progress,
        'upcoming_meetings': Meeting.objects.filter(
            user=request.user,
            date__gte=today
        ).order_by('date', 'time')[:3],
        'recent_activities': [],
        'saved_careers': SavedCareer.objects.filter(
            user=request.user
        ).order_by('-saved_at')[:3],
    }
    return render(request, 'careerai/dashboard.html', context)

@login_required
def recommendations(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
            
            # Clear existing skills and interests
            user_profile.skills.clear()
            user_profile.interests.clear()
            
            # Add new skills
            if 'skills' in data:
                for skill_name in data['skills']:
                    skill, _ = Skill.objects.get_or_create(name=skill_name.strip())
                    user_profile.skills.add(skill)
            
            # Add new interests
            if 'interests' in data:
                for interest_name in data['interests']:
                    interest, _ = Interest.objects.get_or_create(name=interest_name.strip())
                    user_profile.interests.add(interest)
            
            # Update other fields
            if 'experience' in data:
                user_profile.experience = data['experience']
            if 'preferred_work_style' in data:
                user_profile.preferred_work_style = data['preferred_work_style']
            
            user_profile.save()
            
            return JsonResponse({'success': True, 'redirect': '/recommendations/results/'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # GET request - render the form
    return render(request, 'careerai/recommendations.html')

@login_required
def mentors(request):
    # Create default mentors if none exist
    if not Mentor.objects.exists():
        default_mentors = [
            {
                'name': 'Sarah Johnson',
                'title': 'Senior Software Engineer',
                'bio': 'Over 10 years of experience in full-stack development. Expert in Python, React, and cloud architecture.',
                'expertise_areas': ['Python', 'React', 'AWS', 'System Design'],
                'hourly_rate': 150.00,
                'availability': 'available'
            },
            {
                'name': 'Michael Chen',
                'title': 'Tech Lead',
                'bio': 'Former Google engineer with expertise in scalable systems and machine learning.',
                'expertise_areas': ['Machine Learning', 'Java', 'System Architecture', 'Leadership'],
                'hourly_rate': 200.00,
                'availability': 'available'
            },
            {
                'name': 'Emily Rodriguez',
                'title': 'Frontend Specialist',
                'bio': 'Specialized in modern frontend frameworks and UI/UX design principles.',
                'expertise_areas': ['JavaScript', 'React', 'Vue.js', 'UI/UX'],
                'hourly_rate': 125.00,
                'availability': 'busy'
            },
            {
                'name': 'David Kim',
                'title': 'DevOps Engineer',
                'bio': 'Expert in CI/CD, containerization, and cloud infrastructure.',
                'expertise_areas': ['DevOps', 'Docker', 'Kubernetes', 'AWS'],
                'hourly_rate': 175.00,
                'availability': 'available'
            }
        ]

        for mentor_data in default_mentors:
            Mentor.objects.create(**mentor_data)

    # Get all mentors and unique expertise areas
    mentors = Mentor.objects.all()
    expertise_areas = set()
    for mentor in mentors:
        expertise_areas.update(mentor.expertise_areas)
    
    return render(request, 'careerai/mentors.html', {
        'mentors': mentors,
        'expertise_areas': sorted(expertise_areas)
    })

@login_required
def roadmap(request):
    # Get or create user's roadmap
    roadmap, created = Roadmap.objects.get_or_create(
        user=request.user,
        defaults={
            'title': 'My Learning Path',
            'description': 'Your personalized learning journey'
        }
    )
    
    if created:
        # Get user's selected career path from their profile or preferences
        user_profile = UserProfile.objects.get(user=request.user)
        career_path = CareerPath.objects.filter(path_type=user_profile.career_interest).first()
        
        if career_path:
            career_path.generate_roadmap_tasks(roadmap)
        else:
            # Fallback to default full stack path if no specific path is selected
            default_path = CareerPath.objects.get_or_create(
                path_type='fullstack',
                defaults={
                    'title': 'Full Stack Development',
                    'description': 'Complete full stack web development path'
                }
            )[0]
            default_path.generate_roadmap_tasks(roadmap)

    tasks = roadmap.tasks.all()
    completed_tasks = tasks.filter(completed=True).count()
    total_tasks = tasks.count()
    remaining_tasks = total_tasks - completed_tasks
    
    try:
        progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    except:
        progress = 0

    context = {
        'roadmap': roadmap,
        'tasks': tasks,
        'progress': progress,
        'completed_tasks': completed_tasks,
        'remaining_tasks': remaining_tasks,
        'total_tasks': total_tasks
    }
    return render(request, 'careerai/roadmap.html', context)

# Add a new view to handle task completion
@login_required
def toggle_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        try:
            task = Task.objects.get(id=task_id)
            task.completed = not task.completed
            task.save()
            
            # Recalculate stage progress
            stage = task.stage
            total_tasks = stage.tasks.count()
            completed_tasks = stage.tasks.filter(completed=True).count()
            progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            
            return JsonResponse({
                'success': True,
                'completed': task.completed,
                'stage_progress': progress
            })
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'careerai/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
@require_POST
def save_career_path(request):
    try:
        career_id = request.POST.get('career_id')
        career = CareerPath.objects.get(id=career_id)
        # You might want to create a model for saved careers
        # For now, we'll just return success
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def recommendations_results(request):
    # Get or create user profile
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    # Get user's skills and preferences
    profile_data = {
        'skills': list(user_profile.skills.values_list('name', flat=True)),
        'interests': list(user_profile.interests.values_list('name', flat=True)),
        'experience': user_profile.experience,  # Changed from experience_level to experience
        'preferred_work_style': user_profile.preferred_work_style,
    }

    # Generate career recommendations
    recommended_careers = generate_career_recommendations(profile_data)

    context = {
        'user_profile_data': json.dumps(profile_data),
        'recommended_careers': recommended_careers,
    }
    
    return render(request, 'careerai/recommendations_results.html', context)

def generate_career_recommendations(profile_data):
    # In a real application, this would use a more sophisticated recommendation algorithm
    career_paths = [
        {
            'id': 1,
            'title': 'Full Stack Developer',
            'description': 'Build end-to-end web applications using modern technologies.',
            'requiredSkills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'],
            'salary': 95000,
            'growth': 25,
            'match': calculate_match_percentage(profile_data, ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'])
        },
        {
            'id': 2,
            'title': 'Data Scientist',
            'description': 'Analyze complex data sets to solve business problems.',
            'requiredSkills': ['Python', 'SQL', 'Machine Learning', 'Statistics', 'Data Visualization'],
            'salary': 115000,
            'growth': 35,
            'match': calculate_match_percentage(profile_data, ['Python', 'SQL', 'Machine Learning', 'Statistics'])
        },
        # Add more career paths...
    ]
    return career_paths

def calculate_match_percentage(profile_data, required_skills):
    user_skills = set(profile_data['skills'])
    required_skills = set(required_skills)
    
    if not required_skills:
        return 0
    
    matching_skills = user_skills.intersection(required_skills)
    return int((len(matching_skills) / len(required_skills)) * 100)

@login_required
def save_career(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        career_id = data.get('career_id')
        
        # Save the career to user's saved careers
        SavedCareer.objects.get_or_create(
            user=request.user,
            career_id=career_id
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def schedule_meeting_view(request, mentor_id):
    mentor = get_object_or_404(Mentor, id=mentor_id)
    min_date = timezone.now().date()
    
    return render(request, 'careerai/schedule_meeting.html', {
        'mentor': mentor,
        'min_date': min_date,
    })

@login_required
def get_available_slots(request, date):
    try:
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Generate time slots (9 AM to 5 PM)
        all_slots = []
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('17:00', '%H:%M').time()
        
        current_time = start_time
        while current_time <= end_time:
            all_slots.append(current_time.strftime('%H:%M'))
            current_time = (datetime.combine(datetime.min, current_time) + 
                          timedelta(minutes=30)).time()
        
        # Remove booked slots
        booked_slots = Meeting.objects.filter(
            date=selected_date,
            status__in=['pending', 'confirmed']
        ).values_list('time', flat=True)
        
        available_slots = [slot for slot in all_slots 
                         if slot not in [t.strftime('%H:%M') for t in booked_slots]]
        
        return JsonResponse({'slots': available_slots})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def schedule_meeting(request):
    if request.method == 'POST':
        try:
            mentor_id = request.POST.get('mentor_id')
            date = request.POST.get('date')
            time = request.POST.get('time')
            duration = request.POST.get('duration')
            topic = request.POST.get('topic')
            
            if not all([mentor_id, date, time, duration, topic]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required'
                }, status=400)

            mentor = get_object_or_404(Mentor, id=mentor_id)
            
            # Calculate total price
            duration = int(duration)
            total_price = (mentor.hourly_rate * duration) / 60
            
            meeting = Meeting.objects.create(
                user=request.user,
                mentor=mentor,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                time=datetime.strptime(time, '%H:%M').time(),
                duration=duration,
                topic=topic,
                notes=request.POST.get('notes', ''),
                total_price=total_price,
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('meeting_detail', args=[meeting.id])
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user)
    return render(request, 'careerai/meeting_detail.html', {'meeting': meeting})

@login_required
def cancel_meeting(request, meeting_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user)
        
        if meeting.status not in ['pending', 'confirmed']:
            return JsonResponse({'error': 'Meeting cannot be cancelled'}, status=400)
        
        meeting.status = 'cancelled'
        meeting.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def leave_review(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user)
    
    # Check if review already exists
    if Review.objects.filter(meeting=meeting).exists():
        messages.error(request, 'You have already reviewed this meeting')
        return redirect('meeting_detail', meeting_id=meeting_id)
        
    return render(request, 'careerai/leave_review.html', {'meeting': meeting})

@login_required
def submit_review(request, meeting_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user)
        
        if meeting.status != 'completed':
            return JsonResponse({'error': 'Meeting must be completed to leave a review'}, status=400)
            
        if Review.objects.filter(meeting=meeting).exists():
            return JsonResponse({'error': 'You have already reviewed this meeting'}, status=400)
        
        review = Review.objects.create(
            meeting=meeting,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('meeting_detail', args=[meeting_id])
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def update_task(request, task_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        task = get_object_or_404(Task, id=task_id, stage__roadmap__user=request.user)
        data = json.loads(request.body)
        task.completed = data.get('completed', False)
        task.save()
        
        # Calculate stage progress
        stage = task.stage
        total_tasks = stage.tasks.count()
        completed_tasks = stage.tasks.filter(completed=True).count()
        stage_progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        stage_completed = stage_progress == 100
        
        # Calculate overall progress
        roadmap = stage.roadmap
        total_all_tasks = Task.objects.filter(stage__roadmap=roadmap).count()
        completed_all_tasks = Task.objects.filter(stage__roadmap=roadmap, completed=True).count()
        overall_progress = int((completed_all_tasks / total_all_tasks * 100) if total_all_tasks > 0 else 0)
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'completed': task.completed,
            'stage_progress': stage_progress,
            'stage_completed': stage_completed,
            'overall_progress': overall_progress
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def dashboard_stats(request):
    # Get task statistics
    total_tasks = Task.objects.filter(stage__roadmap__user=request.user).count()
    completed_tasks = Task.objects.filter(
        stage__roadmap__user=request.user,
        completed=True
    ).count()
    
    # Calculate progress for each stage
    stages_progress = {}
    for stage in RoadmapStage.objects.filter(roadmap__user=request.user):
        stage_tasks = stage.tasks.count()
        if stage_tasks > 0:
            completed = stage.tasks.filter(completed=True).count()
            stages_progress[stage.id] = int((completed / stage_tasks) * 100)
        else:
            stages_progress[stage.id] = 0

    return JsonResponse({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress': int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0),
        'stage_progress': stages_progress
    })

@login_required
def recent_activities(request):
    last_id = request.GET.get('last_id')
    query = {}
    
    if last_id:
        query['id__gt'] = last_id

    # Combine recent tasks and meetings
    activities = []
    
    # Get recent task completions
    recent_tasks = Task.objects.filter(
        stage__roadmap__user=request.user,
        completed=True,
        **query
    ).order_by('-updated_at')[:5]

    for task in recent_tasks:
        activities.append({
            'id': f'task_{task.id}',
            'type': 'task',
            'title': 'Task Completed',
            'description': task.title,
            'time_ago': timesince(task.updated_at)
        })

    # Get recent meetings
    recent_meetings = Meeting.objects.filter(
        user=request.user,
        **query
    ).order_by('-created_at')[:5]

    for meeting in recent_meetings:
        activities.append({
            'id': f'meeting_{meeting.id}',
            'type': 'meeting',
            'title': 'Meeting Scheduled',
            'description': f'with {meeting.mentor.name}',
            'time_ago': timesince(meeting.created_at)
        })

    # Sort combined activities by time
    activities.sort(key=lambda x: x['time_ago'])

    return JsonResponse({
        'activities': activities[:5]  # Return only the 5 most recent
    })

@login_required
def task_notes(request, task_id):
    task = get_object_or_404(Task, id=task_id, stage__roadmap__user=request.user)
    
    if request.method == 'GET':
        return JsonResponse({'notes': task.notes})
    
    if request.method == 'POST':
        data = json.loads(request.body)
        task.notes = data.get('notes', '')
        task.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def meetings(request):
    # Get upcoming meetings
    upcoming_meetings = Meeting.objects.filter(
        user=request.user,
        date__gte=timezone.now().date()
    ).order_by('date', 'time')

    return render(request, 'careerai/meetings.html', {
        'meetings': upcoming_meetings
    })

@login_required
def career_path_detail(request, career_id):
    career_paths = {
        1: {  # Full Stack Developer
            'id': 1,
            'title': 'Full Stack Developer',
            'description': 'Build and maintain web applications using both front-end and back-end technologies.',
            'prerequisites': [
                'Basic understanding of HTML/CSS',
                'Problem-solving skills',
                'Logical thinking',
                'Basic mathematics'
            ],
            'salary_progression': {
                'entry_level': '60,000 - 85,000',
                'mid_level': '85,000 - 120,000',
                'senior_level': '120,000 - 180,000',
                'lead_architect': '150,000 - 250,000'
            },
            'market_demand': {
                'growth_rate': '25% annually',
                'job_openings': '150,000+',
                'top_locations': ['San Francisco', 'New York', 'Seattle', 'Austin'],
                'industry_demand': 'Very High'
            },
            'related_paths': [
                {'id': 3, 'title': 'DevOps Engineer'},
                {'id': 6, 'title': 'Cloud Solutions Architect'},
                {'id': 8, 'title': 'Frontend Developer'}
            ],
            'interview_questions': [
                'Explain RESTful API architecture',
                'How does React virtual DOM work?',
                'Describe database normalization',
                'Explain CORS and how to handle it',
                'What are closures in JavaScript?'
            ],
            'portfolio_projects': [
                {
                    'title': 'E-commerce Platform',
                    'description': 'Build a full-stack e-commerce site with user authentication, product catalog, and payment integration',
                    'key_features': ['User auth', 'Shopping cart', 'Payment gateway', 'Admin dashboard']
                },
                {
                    'title': 'Social Media Dashboard',
                    'description': 'Create a real-time social media analytics dashboard with data visualization',
                    'key_features': ['Real-time updates', 'Charts/graphs', 'API integration', 'Responsive design']
                },
                {
                    'title': 'Task Management System',
                    'description': 'Develop a project management tool with team collaboration features',
                    'key_features': ['Drag-drop tasks', 'Team chat', 'File sharing', 'Progress tracking']
                }
            ],
            'stages': [
                # ... existing stages ...
            ]
        },
        2: {  # Data Scientist
            'id': 2,
            'title': 'Data Scientist',
            'prerequisites': [
                'Strong mathematics background',
                'Statistical knowledge',
                'Basic programming experience',
                'Analytical thinking'
            ],
            'salary_progression': {
                'entry_level': '70,000 - 95,000',
                'mid_level': '95,000 - 130,000',
                'senior_level': '130,000 - 190,000',
                'lead_scientist': '160,000 - 270,000'
            },
            'market_demand': {
                'growth_rate': '35% annually',
                'job_openings': '100,000+',
                'top_locations': ['Bay Area', 'Boston', 'New York', 'Seattle'],
                'industry_demand': 'Very High'
            },
            'related_paths': [
                {'id': 4, 'title': 'Machine Learning Engineer'},
                {'id': 9, 'title': 'Data Engineer'},
                {'id': 10, 'title': 'Business Intelligence Analyst'}
            ],
            'interview_questions': [
                'Explain the difference between supervised and unsupervised learning',
                'How do you handle missing data?',
                'Explain overfitting and how to prevent it',
                'What is cross-validation?',
                'Describe the steps in a data science project'
            ],
            'portfolio_projects': [
                {
                    'title': 'Customer Churn Prediction',
                    'description': 'Build a model to predict customer churn using historical data',
                    'key_features': ['Data cleaning', 'Feature engineering', 'Model deployment', 'Dashboard']
                },
                {
                    'title': 'Recommendation System',
                    'description': 'Create a content-based recommendation system for products or media',
                    'key_features': ['Collaborative filtering', 'A/B testing', 'Performance metrics', 'API endpoint']
                },
                {
                    'title': 'Sentiment Analysis',
                    'description': 'Develop a sentiment analysis tool for social media data',
                    'key_features': ['NLP', 'Real-time processing', 'Visualization', 'Model evaluation']
                }
            ],
            'stages': [
                # ... existing stages ...
            ]
        },
        3: {  # Machine Learning Engineer
            'id': 3,
            'title': 'Machine Learning Engineer',
            'description': 'Design and implement machine learning models and systems.',
            'prerequisites': [
                'Strong Python programming',
                'Mathematics and statistics',
                'Deep learning concepts',
                'Data structures and algorithms'
            ],
            'salary_progression': {
                'entry_level': '90,000 - 120,000',
                'mid_level': '120,000 - 160,000',
                'senior_level': '160,000 - 200,000',
                'lead_scientist': '200,000 - 300,000'
            },
            'market_demand': {
                'growth_rate': '40% annually',
                'job_openings': '80,000+',
                'top_locations': ['San Francisco', 'Seattle', 'Boston', 'New York'],
                'industry_demand': 'Very High'
            },
            'stages': [
                {
                    'title': 'Foundation',
                    'duration': '4-6 months',
                    'tasks': [
                        'Master Python and key ML libraries',
                        'Statistics and probability',
                        'Linear algebra and calculus',
                        'Data preprocessing techniques'
                    ]
                },
                {
                    'title': 'Core ML',
                    'duration': '6-8 months',
                    'tasks': [
                        'Supervised learning algorithms',
                        'Neural networks architecture',
                        'Deep learning frameworks',
                        'Model evaluation and validation'
                    ]
                },
                {
                    'title': 'Advanced ML & Deployment',
                    'duration': '6-8 months',
                    'tasks': [
                        'MLOps and model deployment',
                        'Distributed training',
                        'Model optimization',
                        'Production system design'
                    ]
                }
            ],
            'interview_questions': [
                'Explain the difference between CNN and RNN',
                'How do you handle overfitting?',
                'Explain gradient descent',
                'What is transfer learning?',
                'How do you deploy ML models to production?'
            ],
            'portfolio_projects': [
                {
                    'title': 'Computer Vision System',
                    'description': 'Build an object detection system using deep learning',
                    'key_features': ['Real-time detection', 'Multiple object tracking', 'Performance optimization']
                },
                {
                    'title': 'NLP Application',
                    'description': 'Create a sentiment analysis tool for social media',
                    'key_features': ['Text preprocessing', 'Model training', 'API development']
                }
            ]
        },
        4: {  # DevOps Engineer
            'id': 4,
            'title': 'DevOps Engineer',
            'description': 'Implement and maintain CI/CD pipelines and infrastructure.',
            'prerequisites': [
                'Linux administration',
                'Scripting knowledge',
                'Basic networking',
                'Cloud platforms familiarity'
            ],
            'salary_progression': {
                'entry_level': '80,000 - 100,000',
                'mid_level': '100,000 - 140,000',
                'senior_level': '140,000 - 180,000',
                'lead_architect': '180,000 - 250,000'
            },
            'market_demand': {
                'growth_rate': '35% annually',
                'job_openings': '90,000+',
                'top_locations': ['Seattle', 'San Francisco', 'Austin', 'New York'],
                'industry_demand': 'High'
            },
            'stages': [
                {
                    'title': 'Infrastructure Basics',
                    'duration': '3-4 months',
                    'tasks': [
                        'Linux system administration',
                        'Shell scripting',
                        'Networking fundamentals',
                        'Cloud platforms (AWS/Azure)'
                    ]
                },
                {
                    'title': 'Container Orchestration',
                    'duration': '4-5 months',
                    'tasks': [
                        'Docker containerization',
                        'Kubernetes administration',
                        'Service mesh (Istio)',
                        'Container security'
                    ]
                },
                {
                    'title': 'CI/CD & Monitoring',
                    'duration': '4-5 months',
                    'tasks': [
                        'Jenkins pipeline development',
                        'Infrastructure as Code',
                        'Monitoring and logging',
                        'Security practices'
                    ]
                }
            ]
        },
        5: {  # Cloud Architect
            'id': 5,
            'title': 'Cloud Architect',
            'description': 'Design and oversee cloud computing infrastructure and strategy.',
            'prerequisites': [
                'Network architecture',
                'Security protocols',
                'Cloud platforms expertise',
                'System design principles'
            ],
            'salary_progression': {
                'entry_level': '95,000 - 125,000',
                'mid_level': '125,000 - 165,000',
                'senior_level': '165,000 - 200,000',
                'lead_architect': '200,000 - 280,000'
            },
            'market_demand': {
                'growth_rate': '30% annually',
                'job_openings': '70,000+',
                'top_locations': ['Seattle', 'San Francisco', 'New York', 'Chicago'],
                'industry_demand': 'Very High'
            },
            'stages': [
                {
                    'title': 'Cloud Foundations',
                    'duration': '4-6 months',
                    'tasks': [
                        'AWS/Azure core services',
                        'Network architecture',
                        'Security fundamentals',
                        'Cost optimization'
                    ]
                },
                {
                    'title': 'Advanced Architecture',
                    'duration': '6-8 months',
                    'tasks': [
                        'Microservices design',
                        'Serverless architecture',
                        'Multi-cloud strategy',
                        'High availability patterns'
                    ]
                },
                {
                    'title': 'Enterprise Solutions',
                    'duration': '4-6 months',
                    'tasks': [
                        'Migration planning',
                        'Disaster recovery',
                        'Compliance frameworks',
                        'Enterprise governance'
                    ]
                }
            ]
        },
        6: {  # Cybersecurity Engineer
            'id': 6,
            'title': 'Cybersecurity Engineer',
            'description': 'Protect organizations from cyber threats and implement security measures.',
            'prerequisites': [
                'Networking fundamentals',
                'Operating systems knowledge',
                'Programming basics',
                'Security concepts'
            ],
            'salary_progression': {
                'entry_level': '85,000 - 110,000',
                'mid_level': '110,000 - 150,000',
                'senior_level': '150,000 - 190,000',
                'lead_security': '190,000 - 250,000'
            },
            'market_demand': {
                'growth_rate': '45% annually',
                'job_openings': '85,000+',
                'top_locations': ['Washington DC', 'New York', 'San Francisco', 'Boston'],
                'industry_demand': 'Critical'
            },
            'stages': [
                {
                    'title': 'Security Fundamentals',
                    'duration': '4-5 months',
                    'tasks': [
                        'Network security',
                        'Cryptography basics',
                        'Security protocols',
                        'Risk assessment'
                    ]
                },
                {
                    'title': 'Defense Techniques',
                    'duration': '5-6 months',
                    'tasks': [
                        'Penetration testing',
                        'Incident response',
                        'Security tools mastery',
                        'Threat modeling'
                    ]
                },
                {
                    'title': 'Advanced Security',
                    'duration': '5-6 months',
                    'tasks': [
                        'Security architecture',
                        'Cloud security',
                        'Forensics',
                        'Security automation'
                    ]
                }
            ]
        },
        7: {  # Mobile Developer
            'id': 7,
            'title': 'Mobile Developer',
            'description': 'Create mobile applications for iOS and Android platforms.',
            'prerequisites': [
                'Object-oriented programming',
                'UI/UX principles',
                'Mobile design patterns',
                'REST APIs understanding'
            ],
            'salary_progression': {
                'entry_level': '75,000 - 95,000',
                'mid_level': '95,000 - 130,000',
                'senior_level': '130,000 - 170,000',
                'lead_developer': '170,000 - 220,000'
            },
            'market_demand': {
                'growth_rate': '25% annually',
                'job_openings': '65,000+',
                'top_locations': ['San Francisco', 'New York', 'Los Angeles', 'Seattle'],
                'industry_demand': 'High'
            },
            'stages': [
                {
                    'title': 'Platform Basics',
                    'duration': '4-5 months',
                    'tasks': [
                        'Swift/Kotlin fundamentals',
                        'Mobile UI development',
                        'App lifecycle',
                        'Local data storage'
                    ]
                },
                {
                    'title': 'Advanced Development',
                    'duration': '5-6 months',
                    'tasks': [
                        'Network programming',
                        'Performance optimization',
                        'Third-party integrations',
                        'Push notifications'
                    ]
                },
                {
                    'title': 'Professional Development',
                    'duration': '4-5 months',
                    'tasks': [
                        'App store deployment',
                        'Analytics integration',
                        'CI/CD for mobile',
                        'Cross-platform development'
                    ]
                }
            ]
        },
        8: {  # UI/UX Designer
            'id': 8,
            'title': 'UI/UX Designer',
            'description': 'Create intuitive and engaging user interfaces and experiences.',
            'prerequisites': [
                'Design principles',
                'User psychology basics',
                'Wireframing skills',
                'Visual design fundamentals'
            ],
            'salary_progression': {
                'entry_level': '65,000 - 85,000',
                'mid_level': '85,000 - 120,000',
                'senior_level': '120,000 - 150,000',
                'lead_designer': '150,000 - 200,000'
            },
            'market_demand': {
                'growth_rate': '20% annually',
                'job_openings': '50,000+',
                'top_locations': ['San Francisco', 'New York', 'Seattle', 'Austin'],
                'industry_demand': 'High'
            },
            'stages': [
                {
                    'title': 'Design Fundamentals',
                    'duration': '3-4 months',
                    'tasks': [
                        'Color theory',
                        'Typography',
                        'Layout principles',
                        'Design tools (Figma/Sketch)'
                    ]
                },
                {
                    'title': 'UX Process',
                    'duration': '4-5 months',
                    'tasks': [
                        'User research',
                        'Information architecture',
                        'Wireframing',
                        'Prototyping'
                    ]
                },
                {
                    'title': 'Professional Practice',
                    'duration': '4-5 months',
                    'tasks': [
                        'Design systems',
                        'Usability testing',
                        'Interactive prototypes',
                        'Design documentation'
                    ]
                }
            ]
        },
        9: {  # Backend Developer
            'id': 9,
            'title': 'Backend Developer',
            'description': 'Build and maintain server-side applications and databases.',
            'prerequisites': [
                'Programming fundamentals',
                'Database concepts',
                'API design principles',
                'Server architecture basics'
            ],
            'salary_progression': {
                'entry_level': '75,000 - 95,000',
                'mid_level': '95,000 - 135,000',
                'senior_level': '135,000 - 175,000',
                'lead_developer': '175,000 - 230,000'
            },
            'market_demand': {
                'growth_rate': '28% annually',
                'job_openings': '75,000+',
                'top_locations': ['San Francisco', 'Seattle', 'New York', 'Austin'],
                'industry_demand': 'High'
            },
            'stages': [
                {
                    'title': 'Backend Basics',
                    'duration': '4-5 months',
                    'tasks': [
                        'Server-side programming',
                        'Database design',
                        'RESTful APIs',
                        'Authentication/Authorization'
                    ]
                },
                {
                    'title': 'Advanced Backend',
                    'duration': '5-6 months',
                    'tasks': [
                        'Microservices architecture',
                        'Caching strategies',
                        'Message queues',
                        'Performance optimization'
                    ]
                },
                {
                    'title': 'Scalable Systems',
                    'duration': '4-5 months',
                    'tasks': [
                        'Distributed systems',
                        'System design',
                        'Monitoring and logging',
                        'Security best practices'
                    ]
                }
            ]
        },
        10: {  # Product Manager
            'id': 10,
            'title': 'Product Manager',
            'description': 'Lead product development and strategy to meet user needs.',
            'prerequisites': [
                'Business acumen',
                'Technical understanding',
                'Communication skills',
                'Analytical thinking'
            ],
            'salary_progression': {
                'entry_level': '80,000 - 100,000',
                'mid_level': '100,000 - 140,000',
                'senior_level': '140,000 - 180,000',
                'lead_product': '180,000 - 250,000'
            },
            'market_demand': {
                'growth_rate': '22% annually',
                'job_openings': '45,000+',
                'top_locations': ['San Francisco', 'New York', 'Seattle', 'Boston'],
                'industry_demand': 'High'
            },
            'stages': [
                {
                    'title': 'Product Fundamentals',
                    'duration': '3-4 months',
                    'tasks': [
                        'Product lifecycle',
                        'Market research',
                        'User stories',
                        'Agile methodologies'
                    ]
                },
                {
                    'title': 'Product Strategy',
                    'duration': '4-5 months',
                    'tasks': [
                        'Product roadmap',
                        'Competitive analysis',
                        'Stakeholder management',
                        'Data-driven decisions'
                    ]
                },
                {
                    'title': 'Product Leadership',
                    'duration': '5-6 months',
                    'tasks': [
                        'Product vision',
                        'Team leadership',
                        'Product metrics',
                        'Go-to-market strategy'
                    ]
                }
            ]
        }
    }

    career_path = career_paths.get(career_id)
    if not career_path:
        raise Http404("Career path not found")

    return render(request, 'careerai/career_path_detail.html', {
        'career': career_path,
        'career_id': career_id
    })

@login_required
def skills(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        proficiency = request.POST.get('proficiency')
        action = request.POST.get('action')
        
        if action == 'add' and skill_name:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            user_profile.skills.add(skill)
            user_profile.skill_proficiencies[skill_name] = proficiency
            user_profile.save()
            messages.success(request, f'Added {skill_name} to your skills!')
        
        elif action == 'remove':
            skill_id = request.POST.get('skill_id')
            if skill_id:
                user_profile.skills.remove(skill_id)
                messages.success(request, 'Skill removed successfully!')
        
        return redirect('skills')

    context = {
        'user_profile': user_profile,
        'all_skills': Skill.objects.all(),
        'proficiency_levels': [
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ]
    }
    return render(request, 'careerai/skills.html', context)

@login_required
def activity(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    activities = []  # Replace with your activity model if you have one
    
    context = {
        'user_profile': user_profile,
        'activities': activities,
    }
    return render(request, 'careerai/activity.html', context)

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(RoadmapTask, id=task_id)
    if request.method == 'POST':
        task.completed = True
        task.save()
        
        # Create activity record
        Activity.objects.create(
            user=request.user,
            action_type='task_completed',
            description=f'Completed task: {task.title}'
        )
        
        messages.success(request, 'Task marked as complete!')
    return redirect('roadmap')

@login_required
def add_task(request):
    if request.method == 'POST':
        roadmap = Roadmap.objects.get(user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if title:
            last_order = roadmap.tasks.aggregate(models.Max('order'))['order__max'] or 0
            
            task = RoadmapTask.objects.create(
                roadmap=roadmap,
                title=title,
                description=description,
                order=last_order + 1
            )
            
            Activity.objects.create(
                user=request.user,
                action_type='task_added',
                description=f'Added new task: {title}'
            )
            
            messages.success(request, 'Task added successfully!')
        
    return redirect('roadmap')