document.addEventListener("DOMContentLoaded", function () {
    const sortOptions = document.querySelectorAll(".sort-option");
    const productGrid = document.querySelector(".product-grid");

    sortOptions.forEach(option => {
        option.addEventListener("click", function () {
            const sortType = this.getAttribute("data-sort");
            let products = Array.from(document.querySelectorAll(".product-card"));

            if (sortType === "price-low-high") {
                products.sort((a, b) => {
                    return (
                        parseFloat(a.querySelector(".product-price").textContent.replace("₹", "").trim()) -
                        parseFloat(b.querySelector(".product-price").textContent.replace("₹", "").trim())
                    );
                });
            } else if (sortType === "price-high-low") {
                products.sort((a, b) => {
                    return (
                        parseFloat(b.querySelector(".product-price").textContent.replace("₹", "").trim()) -
                        parseFloat(a.querySelector(".product-price").textContent.replace("₹", "").trim())
                    );
                });
            } else if (sortType === "newest") {
                products.sort((a, b) => {
                    let dateA = new Date(a.getAttribute("data-created-at"));
                    let dateB = new Date(b.getAttribute("data-created-at"));
                    return dateB - dateA; // Sort newest first
                });
            }

            // Clear and append sorted elements
            productGrid.innerHTML = "";
            products.forEach(product => productGrid.appendChild(product));
        });
    });
});
