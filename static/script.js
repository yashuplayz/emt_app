// Frontend logic for EMT Tool

// Delete button confirmation
function confirmDelete(docId) {
    if (confirm('Are you sure you want to mark this document as Inactive?')) {
        window.location.href = `/soft-delete/${docId}`;
    }
}

// Form validation
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // Validate major_issues and minor_issues are numbers
            const majorIssues = form.querySelector('input[name="major_issues"]');
            const minorIssues = form.querySelector('input[name="minor_issues"]');

            if (majorIssues && isNaN(majorIssues.value)) {
                e.preventDefault();
                alert('Major Issues must be a number!');
                return false;
            }

            if (minorIssues && isNaN(minorIssues.value)) {
                e.preventDefault();
                alert('Minor Issues must be a number!');
                return false;
            }

            // Validate Custom Dropdowns
            const dropdowns = form.querySelectorAll('.custom-dropdown');
            let valid = true;
            dropdowns.forEach(dd => {
                const hidden = dd.querySelector('input[type="hidden"]');
                const search = dd.querySelector('input[type="text"]');

                // Special check for SignOff Engineer
                if (hidden && hidden.name === 'signoff_eng') {
                    const signoffReq = form.querySelector('select[name="signoff_req"]');
                    if (signoffReq && signoffReq.value === 'No') {
                        return; // Skip validation for SignOff Eng if not required
                    }
                }

                // Special check for IDR Reviewers (skip validation as it uses a different mechanism)
                if (search && search.id === 'idrSearch') {
                    return;
                }

                // If search has text but hidden has no value, user didn't select from list
                if (hidden && search && search.value.trim() !== '' && hidden.value === '') {
                    valid = false;
                    search.classList.add('is-invalid'); // Bootstrap error class
                } else {
                    if (search) search.classList.remove('is-invalid');
                }
            });

            if (!valid) {
                e.preventDefault();
                alert('Please select valid options from the dropdown lists (click to select).');
                return false;
            }
        });
    });
});

// Auto-dismiss flash messages after 5 seconds
setTimeout(function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);

// Searchable Dropdown Logic
document.addEventListener('DOMContentLoaded', function () {
    const dropdowns = document.querySelectorAll('.custom-dropdown');

    dropdowns.forEach(dropdown => {
        const searchInput = dropdown.querySelector('input[type="text"]');
        const hiddenInput = dropdown.querySelector('input[type="hidden"]');
        const list = dropdown.querySelector('.dropdown-list');
        const items = list.querySelectorAll('.dropdown-item:not(.no-results)');
        const noResults = list.querySelector('.dropdown-item.no-results');

        if (searchInput && list) {
            // Show list on focus
            searchInput.addEventListener('focus', () => {
                list.style.display = 'block';
            });

            // Filter items
            searchInput.addEventListener('keyup', function () {
                const filter = searchInput.value.toLowerCase();
                let hasResults = false;

                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(filter)) {
                        item.style.display = 'block';
                        hasResults = true;
                    } else {
                        item.style.display = 'none';
                    }
                });

                if (hasResults) {
                    if (noResults) noResults.style.display = 'none';
                } else {
                    if (noResults) noResults.style.display = 'block';
                }
                list.style.display = 'block';
            });

            // Handle item selection (Generic)
            items.forEach(item => {
                item.addEventListener('click', function (e) {
                    // Skip if this is an IDR item (handled by inline onclick)
                    if (searchInput.id === 'idrSearch') return;

                    e.stopPropagation(); // Prevent event bubbling
                    const value = this.getAttribute('data-value');
                    // Get text from the strong tag if it exists, otherwise use full text
                    const strongTag = this.querySelector('strong');
                    const text = strongTag ? strongTag.textContent.trim() : this.textContent.trim();

                    searchInput.value = text; // Show name
                    if (hiddenInput) {
                        hiddenInput.value = value; // Store ID or Name
                        console.log(`Selected: ${text}, Value: ${value}`); // Debug
                    }
                    list.style.display = 'none';
                    searchInput.classList.remove('is-invalid'); // Remove error style
                });
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', function (e) {
                if (!dropdown.contains(e.target)) {
                    list.style.display = 'none';
                }
            });
        }
    });

    // IDR Specific Logic
    const idrReqSelect = document.getElementById('idrReqSelect');
    const idrContainer = document.getElementById('idrReviewersContainer');

    if (idrReqSelect && idrContainer) {
        idrReqSelect.addEventListener('change', function () {
            if (this.value === 'Yes') {
                idrContainer.style.display = 'block';
            } else {
                idrContainer.style.display = 'none';
                // Clear selections if hidden? Optional.
            }
        });

        // Initial check
        if (idrReqSelect.value === 'Yes') {
            idrContainer.style.display = 'block';
        }
    }
});

// IDR Multi-Select Functions
let selectedIdrReviewers = [];

function addIdrReviewer(email, name) {
    if (selectedIdrReviewers.includes(email)) {
        alert('Reviewer already added!');
        return;
    }

    selectedIdrReviewers.push(email);
    updateIdrInput();

    const list = document.getElementById('idrSelectedList');
    const chip = document.createElement('div');
    chip.className = 'badge bg-primary p-2 d-flex align-items-center';
    chip.innerHTML = `
        ${name} 
        <span class="ms-2" style="cursor: pointer;" onclick="removeIdrReviewer('${email}', this)">×</span>
    `;
    list.appendChild(chip);

    // Clear search
    document.getElementById('idrSearch').value = '';
    document.getElementById('idrDropdownList').style.display = 'none';
}

function removeIdrReviewer(email, element) {
    selectedIdrReviewers = selectedIdrReviewers.filter(e => e !== email);
    updateIdrInput();
    element.parentElement.remove();
}

function updateIdrInput() {
    document.getElementById('idrReviewersInput').value = selectedIdrReviewers.join(',');
}
