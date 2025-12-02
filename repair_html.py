
import os

file_path = r'C:\Users\13015646\Desktop\emt_app\templates\document.html'

# The correct JavaScript content
js_content = r'''
<script>
    document.addEventListener("DOMContentLoaded", function () {
        const form = document.querySelector('form[action="/new"]');
        const idrReqSelect = document.getElementById('idrReqSelect');
        const idrContainer = document.getElementById('idrReviewersContainer');
        const signoffReqSelect = document.getElementById('signoffReqSelect');
        const reviewerSearch = document.getElementById('reviewerSearch');
        const reviewerInput = document.getElementById('reviewerInput');
        
        // IDR Logic
        function toggleIdr() {
            const reviewerList = document.getElementById('reviewerList');
            if (idrReqSelect && idrReqSelect.value === 'Yes') {
                idrContainer.style.display = 'block';
                // Disable Reviewer if IDR is Yes
                if (reviewerSearch) {
                    reviewerSearch.value = "";
                    if (reviewerInput) reviewerInput.value = "";
                    reviewerSearch.disabled = true;
                    reviewerSearch.removeAttribute('required');
                    if (reviewerList) reviewerList.style.display = 'none';
                }
            } else {
                idrContainer.style.display = 'none';
                // Enable Reviewer if IDR is No
                if (reviewerSearch) {
                    reviewerSearch.disabled = false;
                    reviewerSearch.setAttribute('required', 'required');
                }
            }
        }
        if (idrReqSelect) {
            idrReqSelect.addEventListener('change', toggleIdr);
            toggleIdr(); // Init
        }

        // SignOff Logic
        function toggleSignoff() {
            const signoffInput = document.querySelector('input[name="signoff_eng"]');
            const signoffSearch = signoffInput ? signoffInput.closest('.custom-dropdown').querySelector('input[type="text"]') : null;
            if (signoffReqSelect.value === 'Yes') {
                if (signoffSearch) signoffSearch.disabled = false;
            } else {
                if (signoffSearch) {
                    signoffSearch.disabled = true;
                    signoffSearch.value = ''; // Clear visual
                }
                if (signoffInput) {
                    signoffInput.value = ''; // Clear actual
                }
            }
        }
        if (signoffReqSelect) {
            signoffReqSelect.addEventListener('change', toggleSignoff);
            toggleSignoff(); // Init
        }

        // IDR Multi-Select Logic
        const idrSearch = document.getElementById('idrSearch');
        const idrList = document.getElementById('idrList');
        const idrInput = document.getElementById('idrReviewersInput');
        const selectedIdrContainer = document.getElementById('selectedIdrReviewers');
        let selectedIdrEmails = [];

        if (idrSearch) {
            idrSearch.addEventListener('focus', () => idrList.style.display = 'block');
            document.addEventListener('click', function (e) {
                if (!e.target.closest('#idrReviewersContainer')) {
                    idrList.style.display = 'none';
                }
            });
            idrSearch.addEventListener('input', function () {
                const filter = idrSearch.value.toLowerCase();
                const items = idrList.querySelectorAll('.dropdown-item:not(.no-results)');
                let hasVisible = false;
                items.forEach(item => {
                    const text = item.innerText.toLowerCase();
                    if (text.includes(filter)) {
                        item.style.display = 'block';
                        hasVisible = true;
                    } else {
                        item.style.display = 'none';
                    }
                });
                idrList.querySelector('.no-results').style.display = hasVisible ? 'none' : 'block';
            });
        }

        window.addIdrReviewer = function (email, name) {
            if (!selectedIdrEmails.includes(email)) {
                selectedIdrEmails.push(email);
                updateIdrDisplay();
                updateIdrInput();
            }
            idrSearch.value = '';
            idrList.style.display = 'none';
        };

        window.removeIdrReviewer = function (email) {
            selectedIdrEmails = selectedIdrEmails.filter(e => e !== email);
            updateIdrDisplay();
            updateIdrInput();
        };

        function updateIdrDisplay() {
            selectedIdrContainer.innerHTML = '';
            selectedIdrEmails.forEach(email => {
                const badge = document.createElement('span');
                badge.className = 'badge bg-secondary me-1 mb-1';
                badge.innerHTML = `${email} <i class="fas fa-times ms-1" style="cursor:pointer;" onclick="removeIdrReviewer('${email}')"></i>`;
                selectedIdrContainer.appendChild(badge);
            });
        }

        function updateIdrInput() {
            idrInput.value = selectedIdrEmails.join(',');
        }

        // SignOff Dropdown Logic
        const signoffSearch = document.getElementById('signoffSearch');
        const signoffList = document.getElementById('signoffList');
        const signoffInput = document.getElementById('signoffInput');

        if (signoffSearch) {
            signoffSearch.addEventListener('focus', () => signoffList.style.display = 'block');
            document.addEventListener('click', function (e) {
                if (!e.target.closest('#signoffDropdown')) {
                    signoffList.style.display = 'none';
                }
            });
            signoffSearch.addEventListener('input', function () {
                const filter = signoffSearch.value.toLowerCase();
                const items = signoffList.querySelectorAll('.dropdown-item:not(.no-results)');
                let hasVisible = false;
                items.forEach(item => {
                    const text = item.innerText.toLowerCase();
                    if (text.includes(filter)) {
                        item.style.display = 'block';
                        hasVisible = true;
                    } else {
                        item.style.display = 'none';
                    }
                });
                signoffList.querySelector('.no-results').style.display = hasVisible ? 'none' : 'block';
            });
        }

        window.selectSignoff = function (email, name) {
            signoffSearch.value = name;
            signoffInput.value = email;
            signoffList.style.display = 'none';
        };

        // Generic Employee Selection Logic
        function setupEmployeeDropdown(type) {
            const search = document.getElementById(type + 'Search');
            const list = document.getElementById(type + 'List');
            const input = document.getElementById(type + 'Input');

            if (search) {
                search.addEventListener('focus', () => {
                    if (!search.disabled) {
                        list.style.display = 'block';
                    }
                });

                document.addEventListener('click', function (e) {
                    if (!e.target.closest('#' + type + 'Dropdown')) {
                        list.style.display = 'none';
                    }
                });

                search.addEventListener('input', function () {
                    const filter = search.value.toLowerCase();
                    const items = list.querySelectorAll('.dropdown-item:not(.no-results)');
                    let hasVisible = false;
                    items.forEach(item => {
                        const text = item.innerText.toLowerCase();
                        if (text.includes(filter)) {
                            item.style.display = 'block';
                            hasVisible = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });
                    list.querySelector('.no-results').style.display = hasVisible ? 'none' : 'block';
                });
            }
        }

        window.selectEmployee = function (type, email, name) {
            document.getElementById(type + 'Search').value = name;
            document.getElementById(type + 'Input').value = email;
            document.getElementById(type + 'List').style.display = 'none';
        };

        // Initialize dropdowns
        setupEmployeeDropdown('docOwner');
        setupEmployeeDropdown('originator');
        setupEmployeeDropdown('reviewer');

        // Custom Form Validation
        if (form) {
            form.addEventListener('submit', function (e) {
                if (signoffReqSelect && signoffReqSelect.disabled) return;
                let isValid = true;
                let errorMsg = "";

                // Validate SignOff
                if (signoffReqSelect && signoffReqSelect.value === 'Yes') {
                    const signoffInput = document.querySelector('input[name="signoff_eng"]');
                    if (!signoffInput || !signoffInput.value) {
                        isValid = false;
                        errorMsg += "SignOff Engineer is required.\n";
                    }
                }

                // Validate IDR
                if (idrReqSelect && idrReqSelect.value === 'Yes') {
                    if (!idrInput || !idrInput.value) {
                        isValid = false;
                        errorMsg += "At least one IDR Reviewer is required.\n";
                    }
                }

                if (!isValid) {
                    e.preventDefault();
                    alert(errorMsg);
                }
            });
        }
    });
</script>
{% endblock %}
'''

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with </div> that closes the main container
# Based on previous view_file, it was around line 616
cutoff_index = -1
for i, line in enumerate(lines):
    if '</div>' in line and '{% endif %}' in lines[i-1]:
        cutoff_index = i + 1
        break

if cutoff_index == -1:
    # Fallback: search for the last {% endif %} and assume </div> follows
    for i in range(len(lines) - 1, -1, -1):
        if '{% endif %}' in lines[i]:
            if i + 1 < len(lines) and '</div>' in lines[i+1]:
                cutoff_index = i + 2
                break

if cutoff_index != -1:
    print(f"Truncating file at line {cutoff_index}")
    new_content = "".join(lines[:cutoff_index]) + js_content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File repaired successfully")
else:
    print("Could not find cutoff point")
