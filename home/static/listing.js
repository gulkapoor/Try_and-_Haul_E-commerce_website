document.addEventListener('DOMContentLoaded', function() {
      
      // Sort options
      const sortOptions = document.querySelectorAll('.sort-option');
      const currentSortText = document.getElementById('currentSort');
      
      sortOptions.forEach(option => {
        option.addEventListener('click', function() {
          // Remove active class from all options
          sortOptions.forEach(o => o.classList.remove('active'));
          
          // Add active class to clicked option
          this.classList.add('active');
          
          // Update current sort text
          currentSortText.textContent = this.textContent;
          
          // Here you would typically sort the products
          // For demo purposes, we'll just log the sort type
          console.log('Sorting by:', this.getAttribute('data-sort'));
        });
      });
      
    });