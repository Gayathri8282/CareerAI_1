document.addEventListener('DOMContentLoaded', function() {
    // Simulate real-time updates
    function simulateRealTimeUpdates() {
        // Randomly update task completion
        const tasks = document.querySelectorAll('.task-item');
        tasks.forEach(task => {
            if (Math.random() < 0.1) { // 10% chance to update
                const progressBar = task.querySelector('.progress-bar');
                const currentProgress = parseInt(progressBar.style.width) || 0;
                const newProgress = Math.min(100, currentProgress + Math.floor(Math.random() * 20));
                progressBar.style.width = `${newProgress}%`;
                
                if (newProgress === 100) {
                    task.classList.add('completed');
                    showNotification('Task completed!', 'success');
                }
            }
        });

        // Simulate new meetings being scheduled
        const meetingsList = document.querySelector('.meetings-list');
        if (Math.random() < 0.05 && meetingsList) { // 5% chance
            const mentors = ['Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Kim'];
            const topics = ['Code Review', 'Career Guidance', 'Technical Interview Prep', 'Project Planning'];
            
            const newMeeting = document.createElement('div');
            newMeeting.className = 'meeting-item fade-in';
            newMeeting.innerHTML = `
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <span class="text-blue-600 font-medium">${mentors[0][0]}</span>
                        </div>
                        <div>
                            <p class="font-medium">${mentors[Math.floor(Math.random() * mentors.length)]}</p>
                            <p class="text-sm text-gray-500">${topics[Math.floor(Math.random() * topics.length)]}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="text-sm font-medium">Tomorrow</p>
                        <p class="text-xs text-gray-500">2:00 PM</p>
                    </div>
                </div>
            `;
            
            meetingsList.insertBefore(newMeeting, meetingsList.firstChild);
            showNotification('New meeting scheduled!', 'info');
        }

        // Update activity feed
        const activityFeed = document.getElementById('activityFeed');
        if (Math.random() < 0.15 && activityFeed) { // 15% chance
            const activities = [
                'Completed a coding challenge',
                'Submitted a project',
                'Joined a study group',
                'Earned a new badge',
                'Reached a milestone'
            ];
            
            const newActivity = document.createElement('div');
            newActivity.className = 'activity-item fade-in';
            newActivity.innerHTML = `
                <div class="flex items-center space-x-3 p-3">
                    <div class="p-2 bg-green-100 rounded-full">
                        <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                        </svg>
                    </div>
                    <div>
                        <p class="font-medium">${activities[Math.floor(Math.random() * activities.length)]}</p>
                        <p class="text-xs text-gray-500">Just now</p>
                    </div>
                </div>
            `;
            
            activityFeed.insertBefore(newActivity, activityFeed.firstChild);
        }

        // Update stats
        const stats = document.querySelectorAll('.stat-number');
        stats.forEach(stat => {
            if (Math.random() < 0.2) { // 20% chance to update
                const currentValue = parseInt(stat.textContent);
                const newValue = currentValue + Math.floor(Math.random() * 5);
                animateNumber(stat, currentValue, newValue, 1000);
            }
        });
    }

    // Animate number changes
    function animateNumber(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                clearInterval(timer);
                current = end;
            }
            element.textContent = Math.round(current);
        }, 16);
    }

    // Show notifications
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg text-white transform transition-all duration-500 translate-y-full ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            'bg-blue-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.remove('translate-y-full'), 100);
        setTimeout(() => {
            notification.classList.add('translate-y-full');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    // Start real-time updates
    setInterval(simulateRealTimeUpdates, 5000);

    // Initial load animation
    document.querySelectorAll('.fade-in').forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('opacity-100');
        }, index * 100);
    });
}); 