document.addEventListener('DOMContentLoaded', function() {
    addLoadingStyles();
    
    const navLinks = document.querySelectorAll('nav a[href*="/"], #mobile-menu a[href*="/"]');
    
    navLinks.forEach(link => {
        if (shouldSkipAjax(link)) {
            return;
        }
        
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            loadContentAjax(url, this);
        });
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.url) {
            loadContentAjax(e.state.url, null, true);
        }
    });
});

// Function to add loading overlay styles
function addLoadingStyles() {
    const style = document.createElement('style');
    style.textContent = `
        #loading-overlay {
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        }
        
        #loading-overlay .animate-spin {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .loading-fade-in {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

// Function to determine if a link should skip AJAX
function shouldSkipAjax(link) {
    const href = link.getAttribute('href');
    const skipPatterns = [
        'logout',
        'login',
        'register',
        'view_profile',
        'update_profile',
        'edit_product',
        'delete_product'
    ];
    
    return skipPatterns.some(pattern => href.includes(pattern));
}

// Function to load content via AJAX
function loadContentAjax(url, linkElement, isPopState = false) {
    // Show loading state
    showLoadingState();
    
    // Update active link styling
    if (linkElement && !isPopState) {
        updateActiveLink(linkElement);
    }
    
    // Make AJAX request
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update the main content area
            updateMainContent(data.html);
            
            // Update page title
            if (data.title) {
                document.title = data.title;
            }
            
            // Update URL without page reload
            if (!isPopState) {
                window.history.pushState({url: url}, '', url);
            }
            
            // Show success message if any
            if (data.message) {
                showMessage(data.message, 'success');
            }
        } else {
            // Handle error
            showMessage(data.message || 'Failed to load content', 'error');
            console.error('AJAX Error:', data.message);
        }
    })
    .catch(error => {
        console.error('AJAX Error:', error);
        showMessage('Failed to load content. Please try again.', 'error');
        
        // Fallback to regular navigation for critical errors
        if (!isPopState) {
            window.location.href = url;
        }
    })
    .finally(() => {
        hideLoadingState();
    });
}

// Function to update the main content area
function updateMainContent(html) {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        // Create a temporary container to parse the HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Extract the content from the block content
        const contentBlock = tempDiv.querySelector('[data-content-block]') || tempDiv;
        
        // Update the main content
        // Preserve the wrapper to keep alignment/spacing/styles consistent
        mainContent.innerHTML = contentBlock.outerHTML;
        
        // Reinitialize any scripts that might be in the new content
        const scripts = contentBlock.querySelectorAll('script');
        scripts.forEach(script => {
            if (script.src) {
                // For external scripts, create a new script element
                const newScript = document.createElement('script');
                newScript.src = script.src;
                document.head.appendChild(newScript);
            } else {
                // For inline scripts, execute them safely
                try {
                    const newScript = document.createElement('script');
                    newScript.textContent = script.innerHTML;
                    document.head.appendChild(newScript);
                } catch (error) {
                    console.warn('Could not execute inline script:', error);
                }
            }
        });
        
        // Reinitialize any event listeners that might be needed
        reinitializePageScripts();
        if (window.ProductsPageInit) {
            window.ProductsPageInit();
        }
    }
}

// Function to update active link styling
function updateActiveLink(activeLink) {
    // Remove active state from all links (both desktop and mobile)
    document.querySelectorAll('nav a, #mobile-menu a').forEach(link => {
        link.classList.remove('text-white', 'after:scale-x-100');
        link.classList.add('text-gray-300');
    });
    
    // Add active state to clicked link
    if (activeLink) {
        activeLink.classList.remove('text-gray-300');
        activeLink.classList.add('text-white', 'after:scale-x-100');
        
        // Also update mobile menu if it's open
        const mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
            // Close mobile menu after navigation
            mobileMenu.classList.add('hidden');
        }
    }
}

// Function to show loading state
function showLoadingState() {
    // Create loading overlay if it doesn't exist
    if (!document.getElementById('loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="text-gray-700">Loading...</span>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    document.getElementById('loading-overlay').style.display = 'flex';
}

// Function to hide loading state
function hideLoadingState() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Function to show messages
function showMessage(message, type = 'info') {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-20 right-5 z-[100] p-4 rounded-lg shadow-lg max-w-sm ${
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'success' ? 'bg-green-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    messageDiv.textContent = message;
    
    // Add to page
    document.body.appendChild(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}

function reinitializePageScripts() {
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (!form.hasAttribute('data-ajax-initialized')) {
            form.setAttribute('data-ajax-initialized', 'true');
            form.addEventListener('submit', handleFormSubmit);
        }
    });
    
    // Reinitialize any custom event listeners that might be needed
    reinitializeCustomEventListeners();
}

// Function to reinitialize custom event listeners
function reinitializeCustomEventListeners() {
    // Reinitialize brands toggle buttons if they exist
    const loadAllBrandsBtn = document.getElementById('loadAllBrands');
    const loadMyBrandsBtn = document.getElementById('loadMyBrands');
    
    if (loadAllBrandsBtn) {
        loadAllBrandsBtn.addEventListener('click', function() {
            if (typeof toggleBrandsView === 'function') {
                toggleBrandsView('all_brands');
            }
        });
    }
    
    if (loadMyBrandsBtn) {
        loadMyBrandsBtn.addEventListener('click', function() {
            if (typeof toggleBrandsView === 'function') {
                toggleBrandsView('my_brands');
            }
        });
    }
    
    // Reinitialize any other custom functions that might be needed
    if (typeof toggleDescription === 'function') {
        // Reinitialize toggle description buttons
        const toggleButtons = document.querySelectorAll('[onclick*="toggleDescription"]');
        toggleButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const id = this.getAttribute('data-id') || this.id.replace('toggle-', '');
                toggleDescription(id);
            });
        });
    }
}

// Function to handle form submissions
function handleFormSubmit(e) {
    const form = e.target;
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    
    // Check if form should use AJAX
    if (form.hasAttribute('data-ajax-form')) {
        e.preventDefault();
        
        const csrftoken = getCsrfToken();
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message || 'Form submitted successfully', 'success');
                // Handle success (e.g., redirect, update content, etc.)
            } else {
                showMessage(data.message || 'Form submission failed', 'error');
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            showMessage('Form submission failed. Please try again.', 'error');
        });
    }
}

// Export functions for global access if needed
window.AjaxNavigation = {
    loadContent: loadContentAjax,
    showMessage: showMessage,
    showLoading: showLoadingState,
    hideLoading: hideLoadingState
};

// Minimal helper: read CSRF token from cookie
function getCsrfToken() {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie || '');
    const parts = decodedCookie.split(';');
    for (let i = 0; i < parts.length; i++) {
        let c = parts[i].trim();
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return '';
}
