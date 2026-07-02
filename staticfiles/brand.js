document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener('DOMContentLoaded', function() {
      // Set current year in footer
      document.getElementById('currentYear').textContent = new Date().getFullYear();
      
      // Mobile menu toggle
      const mobileMenuBtn = document.getElementById('mobileMenuBtn');
      const mobileMenu = document.getElementById('mobileMenu');
      
      if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
          mobileMenu.classList.toggle('active');
          
          // Toggle icon between bars and X
          const icon = mobileMenuBtn.querySelector('i');
          if (icon.classList.contains('fa-bars')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
          } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
          }
        });
      }
      
      // Hide secondary navbar on scroll
      const secondaryNavbar = document.getElementById('secondaryNavbar');
      let lastScrollTop = 0;
      
      window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 50) {
          secondaryNavbar.classList.add('hidden');
        } else {
          secondaryNavbar.classList.remove('hidden');
        }
        
        lastScrollTop = scrollTop;
      });
      
      // Sample brand data
      const brands = [
        {
          id: 1,
          name: 'Nike',
          logo: 'https://via.placeholder.com/150x80?text=Nike',
          category: 'sportswear',
          description: 'Global sports and fitness brand known for innovative athletic footwear, apparel, and accessories.',
          products: 245,
          featured: true
        },
        {
          id: 2,
          name: 'Adidas',
          logo: 'https://via.placeholder.com/150x80?text=Adidas',
          category: 'sportswear',
          description: 'Leading sportswear manufacturer offering performance and lifestyle products for various sports and activities.',
          products: 198,
          featured: true
        },
        {
          id: 3,
          name: 'Gucci',
          logo: 'https://via.placeholder.com/150x80?text=Gucci',
          category: 'luxury',
          description: 'Italian luxury fashion house known for high-end clothing, leather goods, shoes, and accessories.',
          products: 156,
          featured: true
        },
        {
          id: 4,
          name: 'Zara',
          logo: 'https://via.placeholder.com/150x80?text=Zara',
          category: 'clothing',
          description: 'Fast-fashion retailer offering trendy clothing, accessories, and footwear for men, women, and children.',
          products: 320,
          featured: false
        },
        {
          id: 5,
          name: 'H&M',
          logo: 'https://via.placeholder.com/150x80?text=H&M',
          category: 'clothing',
          description: 'Swedish multinational clothing retailer known for fast-fashion clothing for men, women, teenagers, and children.',
          products: 285,
          featured: false
        },
        {
          id: 6,
          name: 'Puma',
          logo: 'https://via.placeholder.com/150x80?text=Puma',
          category: 'sportswear',
          description: 'German multinational corporation designing and manufacturing athletic and casual footwear, apparel, and accessories.',
          products: 175,
          featured: false
        },
        {
          id: 7,
          name: 'Calvin Klein',
          logo: 'https://via.placeholder.com/150x80?text=Calvin+Klein',
          category: 'clothing',
          description: 'American fashion house specializing in clothing, fragrances, and home furnishings.',
          products: 142,
          featured: false
        },
        {
          id: 8,
          name: 'Levi\'s',
          logo: 'https://via.placeholder.com/150x80?text=Levi\'s',
          category: 'clothing',
          description: 'American clothing company known worldwide for its denim jeans and other clothing items.',
          products: 130,
          featured: false
        },
        {
          id: 9,
          name: 'Converse',
          logo: 'https://via.placeholder.com/150x80?text=Converse',
          category: 'footwear',
          description: 'American shoe company that designs, distributes, and licenses sneakers, skating shoes, lifestyle brand footwear, and apparel.',
          products: 95,
          featured: false
        },
        {
          id: 10,
          name: 'Vans',
          logo: 'https://via.placeholder.com/150x80?text=Vans',
          category: 'footwear',
          description: 'Manufacturer of skateboarding shoes and related apparel, started in California and popular among skateboarders and youth culture.',
          products: 88,
          featured: false
        },
        {
          id: 11,
          name: 'Ray-Ban',
          logo: 'https://via.placeholder.com/150x80?text=Ray-Ban',
          category: 'accessories',
          description: 'American-Italian brand of luxury sunglasses and eyeglasses created in 1936 by Bausch & Lomb.',
          products: 75,
          featured: false
        },
        {
          id: 12,
          name: 'Rolex',
          logo: 'https://via.placeholder.com/150x80?text=Rolex',
          category: 'accessories',
          description: 'Swiss luxury watchmaker specializing in high-quality, precision timepieces.',
          products: 62,
          featured: true
        }
      ];
      
      // DOM elements
      const brandGrid = document.getElementById('brandGrid');
      const brandSearch = document.getElementById('brandSearch');
      const categoryFilter = document.getElementById('categoryFilter');
      const sortFilter = document.getElementById('sortFilter');
      const selectedBrandsList = document.getElementById('selectedBrandsList');
      const noBrandsSelected = document.getElementById('noBrandsSelected');
      const selectedCount = document.getElementById('selectedCount');
      const clearAllBtn = document.getElementById('clearAllBtn');
      const continueBtn = document.getElementById('continueBtn');
      const noResults = document.getElementById('noResults');
      const resetFiltersBtn = document.getElementById('resetFiltersBtn');
      
      // Selected brands array
      let selectedBrands = [];
      
      // Render brand cards
      function renderBrands(brandsToRender) {
        brandGrid.innerHTML = '';
        
        if (brandsToRender.length === 0) {
          noResults.style.display = 'block';
          return;
        }
        
        noResults.style.display = 'none';
        
        brandsToRender.forEach(brand => {
          const isSelected = selectedBrands.some(b => b.id === brand.id);
          
          const brandCard = document.createElement('div');
          brandCard.className = 'brand-card';
          brandCard.innerHTML = `
            <div class="brand-card-inner">
              <div class="brand-logo">
                <img src="${brand.logo}" alt="${brand.name} Logo">
              </div>
              <div class="brand-info">
                <h3 class="brand-name">${brand.name}</h3>
                <p class="brand-category">${capitalizeFirstLetter(brand.category)}</p>
                <p class="brand-description">${brand.description}</p>
                <div class="brand-selection">
                  <div class="brand-checkbox">
                    <input type="checkbox" id="brand-${brand.id}" ${isSelected ? 'checked' : ''}>
                    <label for="brand-${brand.id}">Select Brand</label>
                  </div>
                  <div class="brand-products">${brand.products} Products</div>
                </div>
              </div>
            </div>
            ${brand.featured ? '<div class="featured-badge">Featured</div>' : ''}
          `;
          
          brandGrid.appendChild(brandCard);
          
          // Add event listener to checkbox
          const checkbox = brandCard.querySelector(`#brand-${brand.id}`);
          checkbox.addEventListener('change', function() {
            if (this.checked) {
              addSelectedBrand(brand);
            } else {
              removeSelectedBrand(brand.id);
            }
          });
        });
      }
      
      // Add selected brand
      function addSelectedBrand(brand) {
        if (!selectedBrands.some(b => b.id === brand.id)) {
          selectedBrands.push(brand);
          updateSelectedBrandsList();
        }
      }
      
      // Remove selected brand
      function removeSelectedBrand(brandId) {
        selectedBrands = selectedBrands.filter(brand => brand.id !== brandId);
        updateSelectedBrandsList();
        
        // Update checkbox if it exists
        const checkbox = document.getElementById(`brand-${brandId}`);
        if (checkbox) {
          checkbox.checked = false;
        }
      }
      
      // Update selected brands list
      function updateSelectedBrandsList() {
        if (selectedBrands.length === 0) {
          noBrandsSelected.style.display = 'block';
          clearAllBtn.disabled = true;
          continueBtn.disabled = true;
        } else {
          noBrandsSelected.style.display = 'none';
          clearAllBtn.disabled = false;
          continueBtn.disabled = false;
          
          // Clear existing pills
          while (selectedBrandsList.firstChild !== noBrandsSelected) {
            selectedBrandsList.removeChild(selectedBrandsList.firstChild);
          }
          
          // Add brand pills
          selectedBrands.forEach(brand => {
            const brandPill = document.createElement('div');
            brandPill.className = 'selected-brand-pill';
            brandPill.innerHTML = `
              ${brand.name}
              <button class="remove-brand" data-id="${brand.id}">
                <i class="fas fa-times"></i>
              </button>
            `;
            
            selectedBrandsList.insertBefore(brandPill, noBrandsSelected);
            
            // Add event listener to remove button
            const removeBtn = brandPill.querySelector('.remove-brand');
            removeBtn.addEventListener('click', function() {
              removeSelectedBrand(parseInt(this.getAttribute('data-id')));
            });
          });
        }
        
        // Update count
        selectedCount.textContent = selectedBrands.length;
      }
      
      // Filter and sort brands
      function filterAndSortBrands() {
        let filteredBrands = [...brands];
        
        // Apply search filter
        const searchTerm = brandSearch.value.toLowerCase().trim();
        if (searchTerm) {
          filteredBrands = filteredBrands.filter(brand => 
            brand.name.toLowerCase().includes(searchTerm) || 
            brand.description.toLowerCase().includes(searchTerm)
          );
        }
        
        // Apply category filter
        const category = categoryFilter.value;
        if (category !== 'all') {
          filteredBrands = filteredBrands.filter(brand => brand.category === category);
        }
        
        // Apply sorting
        const sortBy = sortFilter.value;
        switch (sortBy) {
          case 'alphabetical':
            filteredBrands.sort((a, b) => a.name.localeCompare(b.name));
            break;
          case 'alphabetical-desc':
            filteredBrands.sort((a, b) => b.name.localeCompare(a.name));
            break;
          case 'popularity':
            filteredBrands.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
            break;
          case 'products':
            filteredBrands.sort((a, b) => b.products - a.products);
            break;
        }
        
        renderBrands(filteredBrands);
      }
      
      // Helper function to capitalize first letter
      function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
      }
      
      // Initialize
      renderBrands(brands);
      updateSelectedBrandsList();
      
      // Event listeners
      brandSearch.addEventListener('input', filterAndSortBrands);
      categoryFilter.addEventListener('change', filterAndSortBrands);
      sortFilter.addEventListener('change', filterAndSortBrands);
      
      clearAllBtn.addEventListener('click', function() {
        selectedBrands = [];
        updateSelectedBrandsList();
        
        // Uncheck all checkboxes
        document.querySelectorAll('.brand-checkbox input').forEach(checkbox => {
          checkbox.checked = false;
        });
      });
      
      continueBtn.addEventListener('click', function() {
        // In a real application, this would redirect to a product page with the selected brands
        alert(`You selected ${selectedBrands.length} brands: ${selectedBrands.map(b => b.name).join(', ')}`);
      });
      
      resetFiltersBtn.addEventListener('click', function() {
        brandSearch.value = '';
        categoryFilter.value = 'all';
        sortFilter.value = 'alphabetical';
        filterAndSortBrands();
      });
      
      // Pagination (for demonstration)
      const pageItems = document.querySelectorAll('.page-item:not(.disabled)');
      
      pageItems.forEach(item => {
        item.addEventListener('click', function() {
          // Remove active class from all page items
          pageItems.forEach(p => p.classList.remove('active'));
          
          // Add active class to clicked page item
          this.classList.add('active');
          
          // In a real application, this would load different brands
          // For demo purposes, we'll just scroll to top
          window.scrollTo({ top: 0, behavior: 'smooth' });
        });
      });
    });
});