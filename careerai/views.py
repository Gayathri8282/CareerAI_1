from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CareerPath, Mentor, RoadmapStage, UserProfile
from .forms import LoginForm, UserProfileForm
from .initial_data import create_initial_data

def landing_page(request):
    return render(request, 'careerai/landing.html')

def about(request):
    return render(request, 'careerai/about.html')

@login_required
def dashboard(request):
    return render(request, 'careerai/dashboard.html')

@login_required
def recommendations(request):
    # Create initial data if none exists
    if CareerPath.objects.count() == 0:
        create_initial_data()
    
    # Ensure UserProfile exists
    UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            career_paths = CareerPath.objects.all()
            for career in career_paths:
                career.match_score = career.match_score or 0
                career.skills_list = [skill.strip() for skill in (career.skills or '').split(',') if skill.strip()]
            return render(request, 'careerai/recommendations_results.html', {
                'career_paths': career_paths
            })
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'careerai/recommendations_form.html', {'form': form})

@login_required
def mentors(request):
    # Create initial data if none exists
    if Mentor.objects.count() == 0:
        create_initial_data()
    
    mentors = Mentor.objects.all()
    return render(request, 'careerai/mentors.html', {'mentors': mentors})

@login_required
def roadmap(request):
    # Create initial data if none exists
    if RoadmapStage.objects.count() == 0:
        create_initial_data()
    
    stages = RoadmapStage.objects.prefetch_related('tasks').all()
    return render(request, 'careerai/roadmap.html', {
        'stages': stages
    })

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