document.addEventListener('DOMContentLoaded', function() {
    const careerSearch = document.getElementById('careerSearch');
    const sortBy = document.getElementById('sortBy');
    const careerMatches = document.getElementById('careerMatches');
    const loadingState = document.getElementById('loadingState');

    // Career data with roadmaps
    const careerData = [
        {
            id: 1,
            title: 'Full Stack Developer',
            description: 'Build and maintain web applications using both front-end and back-end technologies.',
            requiredSkills: ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
            salary: 95000,
            growth: 25,
            match: 95
        },
        {
            id: 2,
            title: 'Data Scientist',
            description: 'Analyze complex data sets to help organizations make better decisions.',
            requiredSkills: ['Python', 'Machine Learning', 'SQL', 'Statistics', 'Data Visualization'],
            salary: 115000,
            growth: 35,
            match: 88
        },
        {
            id: 3,
            title: 'Machine Learning Engineer',
            description: 'Design and implement machine learning models and systems.',
            requiredSkills: ['Python', 'TensorFlow', 'PyTorch', 'Deep Learning', 'MLOps'],
            salary: 125000,
            growth: 40,
            match: 90
        },
        {
            id: 4,
            title: 'DevOps Engineer',
            description: 'Implement and maintain CI/CD pipelines and infrastructure.',
            requiredSkills: ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Linux'],
            salary: 105000,
            growth: 35,
            match: 85
        },
        {
            id: 5,
            title: 'Cloud Architect',
            description: 'Design and oversee cloud computing infrastructure and strategy.',
            requiredSkills: ['AWS', 'Azure', 'Cloud Security', 'Microservices', 'Serverless'],
            salary: 135000,
            growth: 30,
            match: 82
        },
        {
            id: 6,
            title: 'Cybersecurity Engineer',
            description: 'Protect organizations from cyber threats and implement security measures.',
            requiredSkills: ['Network Security', 'Penetration Testing', 'Security Tools', 'Risk Assessment'],
            salary: 110000,
            growth: 45,
            match: 87
        },
        {
            id: 7,
            title: 'Mobile Developer',
            description: 'Create mobile applications for iOS and Android platforms.',
            requiredSkills: ['Swift', 'Kotlin', 'React Native', 'Mobile UI', 'REST APIs'],
            salary: 95000,
            growth: 25,
            match: 84
        },
        {
            id: 8,
            title: 'UI/UX Designer',
            description: 'Create intuitive and engaging user interfaces and experiences.',
            requiredSkills: ['Figma', 'User Research', 'Prototyping', 'Design Systems', 'Wireframing'],
            salary: 85000,
            growth: 20,
            match: 80
        },
        {
            id: 9,
            title: 'Backend Developer',
            description: 'Build and maintain server-side applications and databases.',
            requiredSkills: ['Python/Java', 'Databases', 'APIs', 'System Design', 'Microservices'],
            salary: 100000,
            growth: 28,
            match: 86
        },
        {
            id: 10,
            title: 'Product Manager',
            description: 'Lead product development and strategy to meet user needs.',
            requiredSkills: ['Product Strategy', 'Agile', 'Data Analysis', 'User Stories', 'Stakeholder Management'],
            salary: 110000,
            growth: 22,
            match: 83
        }
    ];

    function updateRecommendations() {
        // Show loading state
        loadingState.classList.remove('hidden');
        careerMatches.innerHTML = '';

        // Simulate API call delay
        setTimeout(() => {
            let filteredCareers = [...careerData];

            // Apply search filter
            if (careerSearch.value) {
                const searchTerm = careerSearch.value.toLowerCase();
                filteredCareers = filteredCareers.filter(career => 
                    career.title.toLowerCase().includes(searchTerm) ||
                    career.description.toLowerCase().includes(searchTerm)
                );
            }

            // Apply sorting
            if (sortBy.value === 'match') {
                filteredCareers.sort((a, b) => b.match - a.match);
            } else if (sortBy.value === 'salary') {
                filteredCareers.sort((a, b) => b.salary - a.salary);
            } else if (sortBy.value === 'growth') {
                filteredCareers.sort((a, b) => b.growth - a.growth);
            }

            // Update UI
            careerMatches.innerHTML = filteredCareers.map(career => `
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                    <div class="p-6">
                        <div class="flex justify-between items-start mb-4">
                            <h3 class="text-xl font-bold">${career.title}</h3>
                            <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                                ${career.match}% Match
                            </span>
                        </div>
                        <p class="text-gray-600 mb-4">${career.description}</p>
                        <div class="flex flex-wrap gap-2 mb-4">
                            ${career.requiredSkills.map(skill => `
                                <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                                    ${skill}
                                </span>
                            `).join('')}
                        </div>
                        <div class="space-y-2 mb-4">
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">Average Salary</span>
                                <span class="font-medium">$${career.salary.toLocaleString()}/year</span>
                            </div>
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">Growth Potential</span>
                                <span class="font-medium">${career.growth}%</span>
                            </div>
                        </div>
                        <div class="flex justify-between items-center">
                            <a href="/career-path/${career.id}/" 
                               class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                View Career Path
                            </a>
                            <button onclick="saveCareer('${career.id}')" 
                                    class="p-2 text-gray-500 hover:text-blue-500 transition-colors">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                          d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');

            // Hide loading state
            loadingState.classList.add('hidden');
        }, 1000);
    }

    // Event listeners
    careerSearch.addEventListener('input', updateRecommendations);
    sortBy.addEventListener('change', updateRecommendations);

    // Initial load
    updateRecommendations();
}); 