document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('recommendationsForm');
    const skillInput = document.getElementById('skillInput');
    const selectedSkills = document.getElementById('selectedSkills');
    const interestToggles = document.querySelectorAll('.interest-toggle');

    // Handle interest toggle clicks
    interestToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            this.classList.toggle('selected');
            this.classList.toggle('bg-blue-100');
            this.classList.toggle('border-blue-500');
            
            // Add visual feedback
            if (this.classList.contains('selected')) {
                this.style.backgroundColor = '#EBF5FF';  // Light blue background
                this.style.borderColor = '#3B82F6';      // Blue border
            } else {
                this.style.backgroundColor = '';
                this.style.borderColor = '';
            }
        });
    });

    // Handle skill input
    skillInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const skill = this.value.trim();
            if (skill) {
                addSkill(skill);
                this.value = '';
            }
        }
    });

    function addSkill(skill) {
        const skillTag = document.createElement('div');
        skillTag.className = 'skill-tag bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center';
        skillTag.dataset.skill = skill;
        skillTag.innerHTML = `
            ${skill}
            <button type="button" class="ml-2 text-blue-600 hover:text-blue-800">&times;</button>
        `;
        
        skillTag.querySelector('button').addEventListener('click', () => skillTag.remove());
        selectedSkills.appendChild(skillTag);
    }

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const data = {
            skills: Array.from(document.querySelectorAll('.skill-tag')).map(tag => tag.dataset.skill),
            interests: Array.from(document.querySelectorAll('.interest-toggle.selected')).map(toggle => toggle.dataset.interest),
            experience: document.getElementById('experienceLevel').value,
            preferred_work_style: Array.from(document.querySelectorAll('input[name="workStyle"]:checked')).map(input => input.value).join(',')
        };

        fetch('/recommendations/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.redirect) {
                window.location.href = data.redirect;
            }
        })
        .catch(error => console.error('Error:', error));
    });
});