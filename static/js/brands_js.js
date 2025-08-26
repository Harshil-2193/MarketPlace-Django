// Function to toggle between All Brands and My Brands
    function toggleBrandsView(viewType) {
        const container = document.getElementById('brandsContainer');
        const allBrandsUrl = container.dataset.allBrandsUrl;
        const myBrandsUrl = container.dataset.myBrandsUrl;
        const url = viewType === 'my_brands' ? myBrandsUrl : allBrandsUrl;;
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the brands container
                console.log(data.html)
                document.getElementById('brandsContainer').innerHTML = data.html;
                
                // Update the heading
                document.getElementById('heading').textContent = data.heading;
                
                // Update button styles
                if (viewType === 'my_brands') {
                    document.getElementById('loadMyBrands').classList.remove('bg-gray-700');
                    document.getElementById('loadMyBrands').classList.add('bg-indigo-600');
                    document.getElementById('loadAllBrands').classList.remove('bg-indigo-600');
                    document.getElementById('loadAllBrands').classList.add('bg-gray-700');
                } else {
                    document.getElementById('loadAllBrands').classList.remove('bg-gray-700');
                    document.getElementById('loadAllBrands').classList.add('bg-indigo-600');
                    if (document.getElementById('loadMyBrands')) {
                        document.getElementById('loadMyBrands').classList.remove('bg-indigo-600');
                        document.getElementById('loadMyBrands').classList.add('bg-gray-700');
                    }
                }
            } else {
                alert('Error loading brands: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while loading brands.');
        });
    }
