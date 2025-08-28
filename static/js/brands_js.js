// Function to toggle between All Brands and My Brands
function toggleBrandsView(viewType) {
    const container = document.getElementById('brandsContainer');
    const allBrandsUrl = container.dataset.allBrandsUrl;
    const myBrandsUrl = container.dataset.myBrandsUrl;
    const url = viewType === 'my_brands' ? myBrandsUrl : allBrandsUrl;
    
    // Show loading state
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'flex justify-center items-center py-12';
    loadingDiv.innerHTML = `
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    `;
    container.innerHTML = '';
    container.appendChild(loadingDiv);
    
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
            .then(data => {
            if (data.success) {
                // Parse the HTML and extract just the brands list
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.html;
                
                // Find the brands list within the content
                const brandsList = tempDiv.querySelector('.brands-list, [data-brands]');
                if (brandsList) {
                    container.innerHTML = brandsList.outerHTML;
                } else {
                    // Fallback: try to find any brands list
                    const fallbackList = tempDiv.querySelector('#brandsContainer');
                    if (fallbackList) {
                        container.innerHTML = fallbackList.innerHTML;
                    } else {
                        container.innerHTML = '<p class="text-center text-gray-400 py-8">No brands found</p>';
                    }
                }
            
            // Update heading
            const heading = document.getElementById('heading');
            if (heading && data.heading) {
                heading.textContent = data.heading;
            }
            
            // Update button styles
            updateBrandsTabStyles(viewType);
            
            // Reinitialize any event listeners
            reinitializeBrandsPageScripts();
            
        } else {
            container.innerHTML = `<p class="text-center text-red-400 py-8">Error: ${data.message}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        container.innerHTML = '<p class="text-center text-red-400 py-8">An error occurred while loading brands.</p>';
    });
}

// Function to update brands tab button styles
function updateBrandsTabStyles(activeView) {
    const allBrandsBtn = document.getElementById('loadAllBrands');
    const myBrandsBtn = document.getElementById('loadMyBrands');
    
    if (allBrandsBtn) {
        if (activeView === 'all_brands') {
            allBrandsBtn.className = 'px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-all duration-300 font-medium shadow-lg ring-2 ring-indigo-400';
        } else {
            allBrandsBtn.className = 'px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-all duration-300 font-medium shadow-lg';
        }
    }
    
    if (myBrandsBtn) {
        if (activeView === 'my_brands') {
            myBrandsBtn.className = 'px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-all duration-300 font-medium shadow-lg ring-2 ring-indigo-400';
        } else {
            myBrandsBtn.className = 'px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-all duration-300 font-medium shadow-lg';
        }
    }
}

// Function to reinitialize brands page scripts
function reinitializeBrandsPageScripts() {
    // Reinitialize toggle description functionality
    const toggleButtons = document.querySelectorAll('[onclick*="toggleDescription"]');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const id = this.getAttribute('data-id') || this.id.replace('toggle-', '');
            toggleDescription(id);
        });
    });
}
