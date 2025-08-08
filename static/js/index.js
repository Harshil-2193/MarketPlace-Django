
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

    // Go On Top Button
    const scrollBtn = document.createElement("button");
    scrollBtn.innerText = "↑ Top";
    scrollBtn.className = "fixed bottom-6 right-6 bg-indigo-600 text-white px-3 py-2 rounded-full shadow-lg hover:bg-indigo-700 transition hidden z-50";
    scrollBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    document.body.appendChild(scrollBtn);

    window.addEventListener("scroll", () => {
        scrollBtn.style.display = window.scrollY > 200 ? "block" : "none";
    });

//  Stop ReRenders on pagination


});



