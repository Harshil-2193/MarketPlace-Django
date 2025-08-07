
console.log("Js Loaded")
function toggleDescription(id) {
    const desc = document.getElementById(`desc-${id}`);
    const btn = event.target;
    const isCollapsed = desc.classList.toggle('max-h-[4.5rem]');
    btn.textContent = isCollapsed ? "View More" : "View Less";
}

// Stop rerenders on search
document.addEventListener('DOMContentLoaded', function () {
    const searchBox = document.getElementById('searchBox'); 
    searchBox.addEventListener('keyup', function () {
        const query = searchBox.value;
        const currentPath = window.location.pathname;   
        let endpoint = '';
        if (currentPath.includes('My_products')) {
            endpoint = `My_products/search/?q=${query}`;
        } else {
            endpoint = `search/?q=${query}`;
        }   
        fetch(endpoint, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('productList').innerHTML = data.html;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
    // Stop rerenders on Pagination   
    // function setupPaginationLinks() {
    //     document.querySelectorAll('.ajax-page-link').forEach(link => {
    //         link.addEventListener('click', function (e) {
    //             e.preventDefault();
    //             const url = this.href;

    //             fetch(url, {
    //                 headers: { 'X-Requested-With': 'XMLHttpRequest' }
    //             })
    //             .then(response => response.json())
    //             .then(data => {
    //                 document.querySelector('#productList').innerHTML = data.html;
    //                 console.log("Pagination content loaded via AJAX");
    //                 history.pushState(null, '', url); 
    //                 setupPaginationLinks();
    //             });
    //         });
    //     });
    // }

    // setupPaginationLinks();
});



