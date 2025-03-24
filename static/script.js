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
document.addEventListener("DOMContentLoaded", function () {
    const generateButton = document.getElementById("generateButton");
    const foodCategory = document.getElementById("foodCategory");
    const dishesContainer = document.getElementById("dishesContainer");

    const dishes = {
        indian: [
            "Butter Chicken - Rich, creamy tomato-based curry.",
            "Paneer Tikka - Grilled cottage cheese with spices.",
            "Dal Makhani - Lentils cooked in butter and cream.",
            "Biryani - Spiced rice with meat or vegetables.",
            "Aloo Paratha - Stuffed flatbread served with yogurt.",
            "Chole Bhature - Chickpea curry with fried bread.",
            "Dosa - Crispy rice pancake with chutneys.",
            "Pani Puri - Crispy shells filled with tangy water.",
            "Rogan Josh - Kashmiri-style lamb curry.",
            "Samosa - Deep-fried pastry with spicy filling."
        ],
        chinese: [
            "Kung Pao Chicken - Stir-fried chicken with peanuts.",
            "Spring Rolls - Crispy rolls stuffed with veggies.",
            "Fried Rice - Wok-tossed rice with vegetables.",
            "Sweet and Sour Pork - Crispy pork with sweet sauce.",
            "Mapo Tofu - Spicy tofu with minced meat.",
            "Chow Mein - Stir-fried noodles with vegetables.",
            "Hot and Sour Soup - Tangy, spicy soup with mushrooms.",
            "Dumplings - Steamed or fried stuffed delights.",
            "Peking Duck - Roasted duck with crispy skin.",
            "Sesame Chicken - Sweet, crispy chicken with sesame seeds."
        ],
        italian: [
            "Margherita Pizza - Tomato, mozzarella, and basil.",
            "Pasta Carbonara - Creamy pasta with bacon and egg.",
            "Lasagna - Layered pasta with meat sauce and cheese.",
            "Risotto - Creamy rice dish with Parmesan.",
            "Bruschetta - Toasted bread with tomato topping.",
            "Tiramisu - Coffee-flavored Italian dessert.",
            "Minestrone Soup - Vegetable soup with pasta.",
            "Pesto Pasta - Pasta tossed in basil sauce.",
            "Arancini - Fried rice balls with cheese filling.",
            "Osso Buco - Slow-cooked veal shanks."
        ]
        // Add more categories similarly
    };

    generateButton.addEventListener("click", function () {
        const selectedCategory = foodCategory.value;
    
        if (generateButton.textContent === "Generate") {
            if (!selectedCategory) {
                alert("Please select a food category!");
                return;
            }
    
            // Hide dropdown and show dish list
            foodCategory.style.display = "none";
            generateButton.textContent = "Change";
            dishesContainer.innerHTML = "<h3>Dishes</h3>";
            dishes[selectedCategory].forEach(dish => {
                const dishItem = document.createElement("div");
                dishItem.classList.add("dish-item");
                dishItem.textContent = dish;
                dishesContainer.appendChild(dishItem);
            });
            dishesContainer.classList.remove("hidden");
        } else {
            // Revert back to dropdown selection
            foodCategory.style.display = "block";
            generateButton.textContent = "Generate";
            dishesContainer.innerHTML = ""; // Clear the dishes list
            dishesContainer.classList.add("hidden");
        }
    });
    
});
