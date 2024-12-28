from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Interest(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
        ('lead', 'Lead/Manager (8+ years)'),
    ]
    
    WORK_STYLE_CHOICES = [
        ('remote', 'Remote'),
        ('office', 'Office Based'),
        ('hybrid', 'Hybrid'),
        ('flexible', 'Flexible'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill, blank=True)
    skill_proficiencies = models.JSONField(default=dict, blank=True)
    interests = models.ManyToManyField(Interest)
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    preferred_work_style = models.CharField(max_length=20, choices=WORK_STYLE_CHOICES, default='flexible')
    goals = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    current_role = models.CharField(max_length=100, blank=True)
    desired_role = models.CharField(max_length=100, blank=True)
    career_interest = models.CharField(
        max_length=50,
        choices=[
            ('frontend', 'Frontend Developer'),
            ('backend', 'Backend Developer'),
            ('fullstack', 'Full Stack Developer'),
            ('data', 'Data Scientist'),
            ('mobile', 'Mobile Developer'),
        ],
        default='fullstack'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

class SavedCareer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    career_id = models.IntegerField()
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'career_id']

    def __str__(self):
        return f"{self.user.username} - Career {self.career_id}"

# The rest of the models remain unchanged
class CareerPath(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.ManyToManyField('Skill')
    path_type = models.CharField(
        max_length=50, 
        choices=[
            ('frontend', 'Frontend Developer'),
            ('backend', 'Backend Developer'),
            ('fullstack', 'Full Stack Developer'),
            ('data', 'Data Scientist'),
            ('mobile', 'Mobile Developer'),
        ],
        default='fullstack'
    )

    def __str__(self):
        return self.title

    def generate_roadmap_tasks(self, roadmap):
        tasks = self.get_path_specific_tasks()
        for index, task_data in enumerate(tasks, start=1):
            task_data['order'] = index
            RoadmapTask.objects.create(roadmap=roadmap, **task_data)

    def get_path_specific_tasks(self):
        if self.path_type == 'frontend':
            return [
                {
                    'title': 'Learn HTML & CSS Fundamentals',
                    'description': 'Master the basics of HTML5 and CSS3 including semantic markup and responsive design'
                },
                {
                    'title': 'JavaScript Essentials',
                    'description': 'Learn core JavaScript concepts including DOM manipulation, events, and ES6+ features'
                },
                {
                    'title': 'Modern Frontend Framework',
                    'description': 'Master a popular framework like React, Vue, or Angular'
                },
                {
                    'title': 'State Management',
                    'description': 'Learn state management solutions like Redux or Vuex'
                },
                {
                    'title': 'Build Portfolio Projects',
                    'description': 'Create responsive, interactive web applications showcasing your frontend skills'
                }
            ]
        elif self.path_type == 'backend':
            return [
                {
                    'title': 'Python Programming Fundamentals',
                    'description': 'Master Python basics including data structures, functions, and OOP concepts'
                },
                {
                    'title': 'Database Management',
                    'description': 'Learn SQL, database design, and ORM concepts using PostgreSQL and Django ORM'
                },
                {
                    'title': 'Django Web Framework',
                    'description': 'Build web applications using Django, including models, views, and templates'
                },
                {
                    'title': 'API Development',
                    'description': 'Create RESTful APIs using Django REST framework'
                },
                {
                    'title': 'Backend Portfolio Project',
                    'description': 'Build a full-featured backend application with authentication and API endpoints'
                }
            ]
        elif self.path_type == 'fullstack':
            return [
                {
                    'title': 'Frontend Fundamentals',
                    'description': 'Learn HTML, CSS, and JavaScript basics'
                },
                {
                    'title': 'Backend Basics with Python',
                    'description': 'Master Python programming and backend concepts'
                },
                {
                    'title': 'Database Management',
                    'description': 'Learn SQL and database design principles'
                },
                {
                    'title': 'Full Stack Framework',
                    'description': 'Master Django and React/Vue integration'
                },
                {
                    'title': 'Full Stack Portfolio Project',
                    'description': 'Build a complete web application with frontend and backend components'
                }
            ]
        elif self.path_type == 'data':
            return [
                {
                    'title': 'Python for Data Science',
                    'description': 'Learn Python libraries like NumPy and Pandas'
                },
                {
                    'title': 'Data Analysis & Visualization',
                    'description': 'Master data analysis techniques and visualization tools like Matplotlib'
                },
                {
                    'title': 'Machine Learning Basics',
                    'description': 'Learn fundamental ML concepts and scikit-learn'
                },
                {
                    'title': 'Deep Learning',
                    'description': 'Explore neural networks using TensorFlow or PyTorch'
                },
                {
                    'title': 'Data Science Portfolio Project',
                    'description': 'Complete an end-to-end data science project'
                }
            ]
        elif self.path_type == 'mobile':
            return [
                {
                    'title': 'Mobile Development Fundamentals',
                    'description': 'Learn mobile app architecture and UI/UX principles'
                },
                {
                    'title': 'React Native Basics',
                    'description': 'Master React Native components and navigation'
                },
                {
                    'title': 'State Management & APIs',
                    'description': 'Learn Redux and API integration in mobile apps'
                },
                {
                    'title': 'Native Device Features',
                    'description': 'Implement camera, location, and other native features'
                },
                {
                    'title': 'Mobile App Portfolio Project',
                    'description': 'Build and publish a complete mobile application'
                }
            ]
        else:
            return []  # Default empty list for unknown path types

    class Meta:
        ordering = ['title']

class Mentor(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
    ]

    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    bio = models.TextField()
    expertise_areas = models.JSONField(default=list)  # Store as JSON array
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    reviews_count = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='mentor_profiles/', null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Roadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class RoadmapStage(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

# Update Task model to include stage relationship
class Task(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,
        default=1
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

class Meeting(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(help_text='Duration in minutes')
    topic = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Meeting with {self.mentor.name} on {self.date} at {self.time}"

class Review(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.meeting}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update mentor's average rating
        mentor = self.meeting.mentor
        avg_rating = Review.objects.filter(
            meeting__mentor=mentor
        ).aggregate(Avg('rating'))['rating__avg']
        mentor.rating = avg_rating or 5.00
        mentor.reviews_count = Review.objects.filter(meeting__mentor=mentor).count()
        mentor.save()

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in hours")
    url = models.URLField()
    skill_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='beginner'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Milestone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class RoadmapTask(models.Model):
    roadmap = models.ForeignKey(Roadmap, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'

