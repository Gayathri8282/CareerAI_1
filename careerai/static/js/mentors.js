document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('mentorSearch');
    const expertiseFilter = document.getElementById('expertiseFilter');
    const availabilityFilter = document.getElementById('availabilityFilter');
    const mentorsGrid = document.getElementById('mentorsGrid');
    
    // Real-time search and filtering
    function filterMentors() {
        const searchTerm = searchInput.value.toLowerCase();
        const expertise = expertiseFilter.value;
        const availability = availabilityFilter.value;
        
        document.querySelectorAll('.mentor-card').forEach(card => {
            const mentorName = card.querySelector('.mentor-name').textContent.toLowerCase();
            const mentorTitle = card.querySelector('.mentor-title').textContent.toLowerCase();
            const mentorExpertise = card.dataset.expertise.split(',');
            const mentorAvailability = card.dataset.availability;
            
            const matchesSearch = mentorName.includes(searchTerm) || 
                                mentorTitle.includes(searchTerm);
            const matchesExpertise = expertise === 'All Expertise' || 
                                   mentorExpertise.includes(expertise);
            const matchesAvailability = availability === 'Any Availability' || 
                                      mentorAvailability === availability.toLowerCase();
            
            if (matchesSearch && matchesExpertise && matchesAvailability) {
                card.classList.remove('hidden');
                // Add fade-in animation
                card.classList.add('fade-in');
            } else {
                card.classList.add('hidden');
                card.classList.remove('fade-in');
            }
        });
    }

    // Event listeners for real-time filtering
    searchInput.addEventListener('input', filterMentors);
    expertiseFilter.addEventListener('change', filterMentors);
    availabilityFilter.addEventListener('change', filterMentors);

    // Scheduling functionality
    document.querySelectorAll('.schedule-button').forEach(button => {
        button.addEventListener('click', function(e) {
            const mentorId = this.dataset.mentorId;
            const mentorName = this.dataset.mentorName;
            
            // Show scheduling modal
            const modal = document.getElementById('schedulingModal');
            modal.classList.remove('hidden');
            
            // Update modal content
            document.getElementById('selectedMentorName').textContent = mentorName;
            document.getElementById('mentorIdInput').value = mentorId;
        });
    });

    // Rating system
    document.querySelectorAll('.rating-stars').forEach(container => {
        const stars = container.querySelectorAll('.star');
        stars.forEach((star, index) => {
            star.addEventListener('mouseover', () => {
                for (let i = 0; i <= index; i++) {
                    stars[i].classList.add('text-yellow-400');
                }
            });
            
            star.addEventListener('mouseout', () => {
                stars.forEach(s => {
                    if (!s.classList.contains('rated')) {
                        s.classList.remove('text-yellow-400');
                    }
                });
            });
        });
    });

    // Simulated real-time availability updates
    function updateAvailability() {
        document.querySelectorAll('.mentor-card').forEach(card => {
            if (Math.random() > 0.8) { // 20% chance to change status
                const currentStatus = card.dataset.availability;
                const newStatus = currentStatus === 'available' ? 'busy' : 'available';
                card.dataset.availability = newStatus;
                
                const statusBadge = card.querySelector('.availability-badge');
                statusBadge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                statusBadge.className = `availability-badge px-2 py-1 rounded-full text-xs font-medium ${
                    newStatus === 'available' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`;
            }
        });
    }

    // Update availability every 30 seconds
    setInterval(updateAvailability, 30000);
}); 