// Dynamic filtering for Doctor dropdown based on selected Department
function filterDoctors() {
    const deptSelect = document.getElementById('department_id');
    const docSelect = document.getElementById('doctor_id');
    
    if(!deptSelect || !docSelect) return;
    
    const selectedDept = deptSelect.value;
    const options = docSelect.getElementsByTagName('option');

    // Reset doctor selection
    docSelect.value = '';

    for (let i = 0; i < options.length; i++) {
        let option = options[i];
        if (option.value === "") {
            option.style.display = "block"; // Keep placeholder visible
            continue;
        }

        let docDept = option.getAttribute('data-dept');
        
        if (selectedDept === "" || docDept === selectedDept) {
            option.style.display = "block";
        } else {
            option.style.display = "none";
        }
    }
}

// Set minimum date to today for appointment booking
document.addEventListener("DOMContentLoaded", function() {
    const dateInput = document.getElementById('date');
    if(dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }
});
