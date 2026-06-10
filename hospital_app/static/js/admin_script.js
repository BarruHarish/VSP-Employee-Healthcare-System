document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    // Modal Handling
    const modals = document.querySelectorAll('.modal');
    const openModalBtns = document.querySelectorAll('[data-modal-target]');
    const closeBtns = document.querySelectorAll('.close-modal');

    openModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            if (modal) {
                // If it's an edit button, populate data
                if (btn.classList.contains('edit')) {
                    populateEditModal(btn, modal);
                }
                modal.style.display = 'flex';
            }
        });
    });

    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    // Simple search filtering for tables
    const searchInputs = document.querySelectorAll('.search-box');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = document.querySelector(this.getAttribute('data-target'));
            if(table) {
                const tr = table.getElementsByTagName('tr');
                for (let i = 1; i < tr.length; i++) { // Skip header row
                    let txtValue = tr[i].textContent || tr[i].innerText;
                    if (txtValue.toLowerCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        });
    });
});

function populateEditModal(btn, modal) {
    // Gets data attributes from the button and populates the form in the modal
    const data = btn.dataset;
    const form = modal.querySelector('form');
    if(!form) return;
    
    // Set action to 'edit'
    const actionInput = form.querySelector('input[name="action"]');
    if(actionInput) actionInput.value = 'edit';

    // Loop through dataset and fill form inputs
    for (let key in data) {
        if(key === 'modalTarget' || key === 'action') continue;
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = data[key];
        }
    }
}
