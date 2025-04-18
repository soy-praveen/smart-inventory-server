// Background Canvas Animation
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

// Inventory Management
document.addEventListener("DOMContentLoaded", function() {
    fetchInventoryData(); // Load inventory when page loads
    
    // Event listener for dish generation
    const generateButton = document.getElementById("generateButton");
    if (generateButton) {
        generateButton.addEventListener("click", function() {
            const foodCategory = document.getElementById("foodCategory").value;
            if (!foodCategory) {
                alert("❌ Please select a food category first!");
                return;
            }

            generateDishes(foodCategory);
        });
    }
    
    // Set up inventory refresh interval
    setInterval(fetchInventoryData, 5000);
});

// Function to fetch inventory data from backend
function fetchInventoryData() {
    fetch("/get_inventory")
        .then(response => response.json())
        .then(data => {
            processInventoryData(data);
        })
        .catch(error => {
            console.error("Error fetching inventory:", error);
            document.getElementById("inventoryItems").innerHTML = 
                '<div class="loading-message">Failed to load inventory. Please try again later.</div>';
        });
}

// Function to generate dishes based on selected category
function generateDishes(category) {
    fetch("/generate_dishes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: category })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display the generated dishes
            const dishesContainer = document.getElementById("dishesContainer");
            dishesContainer.innerHTML = "<h2>Suggested Dishes:</h2>";
            data.dishes.forEach(dish => {
                const dishElement = document.createElement("p");
                dishElement.textContent = dish;
                dishesContainer.appendChild(dishElement);
            });
            dishesContainer.classList.remove("hidden");
        } else {
            alert(data.error || "Error generating dishes");
        }
    })
    .catch(error => console.error("Error fetching dishes:", error));
}

// Function to process and display inventory data
function processInventoryData(data) {
    const inventoryContainer = document.getElementById("inventoryItems");
    
    // Check if data has the expected structure
    if (!data || !data.items || !Array.isArray(data.items)) {
        inventoryContainer.innerHTML = '<div class="loading-message">No inventory data available</div>';
        return;
    }
    
    // Parse the inventory data
    try {
        let parsedItems = [];
        
        data.items.forEach(item => {
            // Extract inventory item details using regex patterns
            const nameMatch = item.match(/Name of fruit: (.+)/);
            const countMatch = item.match(/Count: (\d+)/);
            const freshnessMatch = item.match(/Freshness rate \(1-100\): (\d+)/);
            const expiryMatch = item.match(/Least estimated days before rotting: (\d+)/);
            
            if (nameMatch && countMatch && freshnessMatch && expiryMatch) {
                parsedItems.push({
                    name: nameMatch[1].trim(),
                    count: parseInt(countMatch[1]),
                    freshness: parseInt(freshnessMatch[1]),
                    expiry: parseInt(expiryMatch[1])
                });
            }
        });
        
        // Render the inventory items
        renderInventoryItems(parsedItems);
    } catch (error) {
        console.error("Error parsing inventory data:", error);
        inventoryContainer.innerHTML = '<div class="loading-message">Error processing inventory data</div>';
    }
}

// Render inventory items with countdown timer visualization
function renderInventoryItems(items) {
    const inventoryContainer = document.getElementById("inventoryItems");
    
    if (!items || items.length === 0) {
        inventoryContainer.innerHTML = '<div class="loading-message">No items in inventory</div>';
        return;
    }
    
    let html = '';
    
    // Sort items by expiry days (ascending) so most urgent items appear first
    items.sort((a, b) => a.expiry - b.expiry);
    
    items.forEach((item, index) => {
        // Calculate urgency class
        let urgencyClass = '';
        let timerBgColor = '';
        let timerAnimation = '';
        
        if (item.expiry <= 1) {
            urgencyClass = 'urgent';
            timerBgColor = '#ff3d3d';
            timerAnimation = 'countdown-pulse-urgent 1.5s infinite';
        } else if (item.expiry <= 3) {
            urgencyClass = 'warning';
            timerBgColor = '#ff9f1c';
            timerAnimation = 'countdown-pulse-warning 2s infinite';
        } else {
            urgencyClass = 'normal';
            timerBgColor = '#4CAF50';
        }
        
        // Create countdown segments (one segment per day)
        let countdownHtml = '';
        for (let i = 0; i < 7; i++) {
            let segmentClass = i < item.expiry ? 'countdown-segment active' : 'countdown-segment';
            countdownHtml += `<div class="${segmentClass}"></div>`;
        }
        
        html += `
        <div class="fruit-item ${urgencyClass}">
            <div class="fruit-number">${index + 1}</div>
            <div class="fruit-name">${item.name}</div>
            <div class="freshness">${item.freshness}%</div>
            <div class="count-box">×${item.count}</div>
            <div class="expiry-timer">
                <div class="timer-icon">⏱️</div>
                <div class="countdown-container">
                    ${countdownHtml}
                </div>
                <div class="timer-text" style="color:${timerBgColor}; animation: ${timerAnimation}">${item.expiry}d</div>
            </div>
        </div>
        `;
    });
    
    inventoryContainer.innerHTML = html;
}
