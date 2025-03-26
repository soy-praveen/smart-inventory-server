const canvas = document.getElementById("backgroundCanvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const dots = [];
const numDots = 100;

// Create dots
for (let i = 0; i < numDots; i++) {
    dots.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 0.8,
        dx: (Math.random() - 0.5) * 2,
        dy: (Math.random() - 0.5) * 2
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".refresh-button").addEventListener("click", function () {
        fetch("/trigger_client", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                if (data.success) {
                    setTimeout(() => {
                        document.querySelector(".card img").src = "/get_image?" + new Date().getTime();
                    }, 2000);
                }
            })
            .catch(error => console.error("❌ Error:", error));
    });
});


function drawDots() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    dots.forEach(dot => {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 1.5);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
    });

    moveDots();
}

function moveDots() {
    dots.forEach(dot => {
        dot.x += dot.dx;
        dot.y += dot.dy;

        if (dot.x < 0 || dot.x > canvas.width) dot.dx *= -1;
        if (dot.y < 0 || dot.y > canvas.height) dot.dy *= -1;
    });
}

function animate() {
    drawDots();
    requestAnimationFrame(animate);
}

window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

animate();
document.addEventListener("DOMContentLoaded", function () {
    fetchInventoryData(); // Load inventory when page loads

    // Function to fetch inventory data from backend
    function fetchInventoryData() {
        fetch("/get_inventory")
            .then(response => response.json())
            .then(data => {
                updateInventoryUI(data);
            })
            .catch(error => console.error("Error fetching inventory:", error));
    }

    // Function to update UI with dynamic inventory
    function updateInventoryUI(data) {
        const inventoryContainer = document.querySelector(".popup-content");

        let htmlContent = `<h2>Inventory</h2>`;

        // ✅ Display Fruits
        if (data.fruits && Object.keys(data.fruits).length > 0) {
            htmlContent += `<div class="inventory-section"><h3>Fruits Count</h3>`;
            for (let fruit in data.fruits) {
                htmlContent += `<p>${fruit}: Fresh (>80%) - ${data.fruits[fruit]["freshness above 80%"]}, Medium (>50%) - ${data.fruits[fruit]["freshness above 50%"]}, Rotten - ${data.fruits[fruit]["cannot be used for cooking"]}</p>`;
            }
            htmlContent += `</div>`;
        }

        // ✅ Display Vegetables
        if (data.vegetables && Object.keys(data.vegetables).length > 0) {
            htmlContent += `<div class="inventory-section"><h3>Vegetables Count</h3>`;
            for (let vegetable in data.vegetables) {
                htmlContent += `<p>${vegetable}: Fresh (>80%) - ${data.vegetables[vegetable]["freshness above 80%"]}, Medium (>50%) - ${data.vegetables[vegetable]["freshness above 50%"]}</p>`;
            }
            htmlContent += `</div>`;
        }

        inventoryContainer.innerHTML = htmlContent;
    }

    // Refresh inventory data every 5 seconds
    setInterval(fetchInventoryData, 5000);
});

document.addEventListener("DOMContentLoaded", function () {
    const generateButton = document.getElementById("generateButton");
    const foodCategory = document.getElementById("foodCategory");
    const dishesContainer = document.getElementById("dishesContainer");

    generateButton.addEventListener("click", function () {
        const selectedCategory = foodCategory.value;
        if (!selectedCategory) {
            alert("❌ Please select a food category first!");
            return;
        }

        fetch("/generate_dishes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ category: selectedCategory })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // ✅ Display the generated dishes
                dishesContainer.innerHTML = "<h2>Suggested Dishes:</h2>";
                data.dishes.forEach(dish => {
                    const dishElement = document.createElement("p");
                    dishElement.textContent = dish;
                    dishesContainer.appendChild(dishElement);
                });
                dishesContainer.classList.remove("hidden");
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error("Error fetching dishes:", error));
    });
});
