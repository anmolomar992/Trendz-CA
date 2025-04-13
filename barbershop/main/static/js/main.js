/**
 * Royal Cuts - Premium Indian Barber Shop
 * Main JavaScript file for the website
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    initTooltips();

    // Initialize navbar scroll behavior
    initNavbarScroll();

    // Initialize automatic alert dismissal
    initAlertDismissal();

    // Initialize booking form dynamic behavior if present
    initBookingForm();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize navbar scroll behavior
 * Adds a class to the navbar when scrolling down
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
}

/**
 * Initialize automatic alert dismissal
 * Automatically dismisses success and info alerts after 5 seconds
 */
function initAlertDismissal() {
    const alerts = document.querySelectorAll('.alert-success, .alert-info');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert) {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                } else {
                    alert.remove();
                }
            }
        }, 5000);
    });
}

/**
 * Initialize booking form dynamic behavior
 * - Updates time slots based on selected date, stylist, and service
 * - Updates booking summary
 */
function initBookingForm() {
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        const dateField = document.querySelector('input[type="date"]');
        const timeField = document.querySelector('select[name="time"]');
        const stylistField = document.querySelector('select[name="stylist"]');
        const serviceField = document.querySelector('select[name="service"]');
        const timeLoading = document.getElementById('time-loading');
        const noSlotsMessage = document.getElementById('no-slots-message');
        const bookingSummary = document.getElementById('booking-summary');
        
        // Function to fetch available time slots
        function fetchTimeSlots() {
            if (!dateField || !timeField || !stylistField || !serviceField || !timeLoading || !noSlotsMessage) {
                return;
            }
            
            const date = dateField.value;
            const stylistId = stylistField.value;
            const serviceId = serviceField.value;
            
            if (!date || !stylistId || !serviceId) {
                return;
            }
            
            // Show loading spinner
            timeField.disabled = true;
            timeLoading.classList.remove('d-none');
            noSlotsMessage.classList.add('d-none');
            
            // Clear existing options
            while (timeField.options.length > 0) {
                timeField.remove(0);
            }
            
            // Add default empty option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select Time';
            timeField.appendChild(defaultOption);
            
            // Get CSRF token
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            // Fetch available time slots from server
            fetch('/api/time-slots/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    date: date,
                    stylist_id: stylistId,
                    service_id: serviceId
                })
            })
            .then(response => response.json())
            .then(data => {
                timeLoading.classList.add('d-none');
                
                if (data.time_slots && data.time_slots.length > 0) {
                    // Add time slots as options
                    data.time_slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot;
                        option.textContent = slot;
                        timeField.appendChild(option);
                    });
                    timeField.disabled = false;
                } else {
                    noSlotsMessage.classList.remove('d-none');
                }
                
                // Update booking summary
                updateBookingSummary();
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
                timeLoading.classList.add('d-none');
                noSlotsMessage.classList.remove('d-none');
            });
        }
        
        // Update booking summary
        function updateBookingSummary() {
            if (!bookingSummary) return;
            
            const summaryService = document.getElementById('summary-service');
            const summaryDate = document.getElementById('summary-date');
            const summaryStylist = document.getElementById('summary-stylist');
            const summaryTime = document.getElementById('summary-time');
            
            if (!summaryService || !summaryDate || !summaryStylist || !summaryTime) return;
            
            const serviceText = serviceField.options[serviceField.selectedIndex]?.text || '';
            const stylistText = stylistField.options[stylistField.selectedIndex]?.text || '';
            const dateValue = dateField.value ? new Date(dateField.value).toLocaleDateString() : '';
            const timeValue = timeField.value;
            
            if (serviceText && stylistText && dateValue && timeValue) {
                summaryService.textContent = serviceText;
                summaryDate.textContent = dateValue;
                summaryStylist.textContent = stylistText;
                summaryTime.textContent = timeValue;
                bookingSummary.classList.remove('d-none');
            } else {
                bookingSummary.classList.add('d-none');
            }
        }
        
        // Add event listeners
        if (dateField) dateField.addEventListener('change', fetchTimeSlots);
        if (stylistField) stylistField.addEventListener('change', fetchTimeSlots);
        if (serviceField) serviceField.addEventListener('change', fetchTimeSlots);
        if (timeField) timeField.addEventListener('change', updateBookingSummary);
    }
}

/**
 * Animation for numbers counting up
 * Used for statistics and achievements
 */
function animateNumbers() {
    const numberElements = document.querySelectorAll('.animate-number');
    
    numberElements.forEach(element => {
        const target = parseInt(element.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60fps
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.ceil(current);
            }
        }, 16);
    });
}

/**
 * Handle service filtering in dashboard
 */
function filterServices(category) {
    const serviceCards = document.querySelectorAll('.service-item');
    
    serviceCards.forEach(card => {
        if (category === 'all' || card.getAttribute('data-category') === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Handle appointment status updates in dashboard
 */
function updateAppointmentStatus(appointmentId, status) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.style.display = 'none';
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    const appointmentInput = document.createElement('input');
    appointmentInput.type = 'hidden';
    appointmentInput.name = 'appointment_id';
    appointmentInput.value = appointmentId;
    
    const statusInput = document.createElement('input');
    statusInput.type = 'hidden';
    statusInput.name = 'status';
    statusInput.value = status;
    
    form.appendChild(csrfInput);
    form.appendChild(appointmentInput);
    form.appendChild(statusInput);
    
    document.body.appendChild(form);
    form.submit();
}

/**
 * Handle image preview for profile images
 */
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewElement.src = e.target.result;
            previewElement.style.display = 'block';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Custom confirmation for delete actions
 */
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}
