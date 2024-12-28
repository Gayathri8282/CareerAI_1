document.addEventListener('DOMContentLoaded', function() {
    // Task completion handling
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const taskCard = this.closest('.task-card');
            const progressBar = document.querySelector(`[data-stage-id="${this.dataset.stageId}"]`);
            
            showLoadingSpinner();
            fetch(`/api/update-task/${taskId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    completed: this.checked
                })
            })
            .then(response => response.json())
            .then(data => {
                hideLoadingSpinner();
                if (data.success) {
                    // Update task card appearance
                    taskCard.classList.toggle('completed', this.checked);
                    
                    // Update progress bar
                    progressBar.style.width = `${data.stage_progress}%`;
                    
                    // Update stage completion status
                    if (data.stage_completed) {
                        progressBar.closest('.stage-card').classList.add('stage-completed');
                    } else {
                        progressBar.closest('.stage-card').classList.remove('stage-completed');
                    }
                    
                    // Show completion celebration if stage is completed
                    if (data.stage_completed && this.checked) {
                        showCelebration();
                    }
                    
                    // Update overall progress
                    updateOverallProgress(data.overall_progress);
                } else {
                    this.checked = !this.checked;
                    showNotification(data.error || 'Failed to update task', 'error');
                }
            })
            .catch(error => {
                hideLoadingSpinner();
                this.checked = !this.checked;
                showNotification('An error occurred', 'error');
            });
        });
    });

    // Task notes handling
    const taskNotes = document.querySelectorAll('.task-notes');
    taskNotes.forEach(noteBtn => {
        noteBtn.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const notesModal = document.getElementById('notesModal');
            const notesContent = document.getElementById('notesContent');
            const saveNotesBtn = document.getElementById('saveNotes');
            
            fetch(`/api/task-notes/${taskId}/`)
                .then(response => response.json())
                .then(data => {
                    notesContent.value = data.notes || '';
                    notesModal.classList.remove('hidden');
                    
                    saveNotesBtn.onclick = function() {
                        fetch(`/api/task-notes/${taskId}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                            },
                            body: JSON.stringify({
                                notes: notesContent.value
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                notesModal.classList.add('hidden');
                                showNotification('Notes saved successfully');
                            }
                        });
                    };
                });
        });
    });

    // Resources expansion
    const resourceButtons = document.querySelectorAll('.resources-btn');
    resourceButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const resourcesList = this.nextElementSibling;
            resourcesList.classList.toggle('hidden');
            this.querySelector('svg').classList.toggle('rotate-180');
        });
    });

    // Progress animation
    function animateProgress() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const target = parseFloat(bar.dataset.progress);
            let current = 0;
            const increment = target / 100;
            const interval = setInterval(() => {
                if (current >= target) {
                    clearInterval(interval);
                } else {
                    current += increment;
                    bar.style.width = `${Math.min(current, target)}%`;
                }
            }, 10);
        });
    }

    // Initialize progress bars
    animateProgress();

    // Celebration animation
    function showCelebration() {
        const celebration = document.createElement('div');
        celebration.className = 'fixed inset-0 flex items-center justify-center z-50';
        celebration.innerHTML = `
            <div class="celebration-animation">
                🎉 Stage Completed! 🎉
            </div>
        `;
        document.body.appendChild(celebration);
        setTimeout(() => celebration.remove(), 3000);
    }

    // Update overall progress
    function updateOverallProgress(progress) {
        const overallProgress = document.getElementById('overallProgress');
        const overallProgressText = document.getElementById('overallProgressText');
        
        overallProgress.style.width = `${progress}%`;
        overallProgressText.textContent = `${Math.round(progress)}%`;
    }

    // Animate progress bars on page load
    const progressBars = document.querySelectorAll('.progress-bar, #overallProgress');
    progressBars.forEach(bar => {
        const progress = bar.dataset.progress || 0;
        setTimeout(() => {
            bar.style.width = `${progress}%`;
        }, 300);
    });
}); 