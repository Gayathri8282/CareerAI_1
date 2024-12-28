// Utility functions
function showLoadingSpinner() {
    document.getElementById('loading-spinner').classList.remove('hidden');
}

function hideLoadingSpinner() {
    document.getElementById('loading-spinner').classList.add('hidden');
}

// Task completion animation
function animateTaskCompletion(element) {
    element.classList.add('scale-110', 'bg-green-100');
    setTimeout(() => {
        element.classList.remove('scale-110');
    }, 200);
}

// Progress bar animation
function updateProgressBar(element, progress) {
    element.style.width = '0%';
    setTimeout(() => {
        element.style.width = `${progress}%`;
    }, 50);
}

// Dynamic search/filter
function filterItems(inputElement, itemsSelector) {
    const searchTerm = inputElement.value.toLowerCase();
    const items = document.querySelectorAll(itemsSelector);
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = '';
            item.classList.add('fade-in');
        } else {
            item.style.display = 'none';
            item.classList.remove('fade-in');
        }
    });
}

// Notification system
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-y-0 z-50 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('translate-y-[-100%]', 'opacity-0');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
} 