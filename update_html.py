
import os

file_path = r'C:\Users\13015646\Desktop\emt_app\templates\document.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# New HTML for Employee Dropdowns
new_html = [
    '                        <div class="col-md-4">\n',
    '                            <label class="form-label">Doc Owner</label>\n',
    '                            <div class="custom-dropdown" id="docOwnerDropdown">\n',
    '                                <input type="text" class="form-control" id="docOwnerSearch" placeholder="Search Employee..." autocomplete="off" {{ \'disabled\' if mode==\'edit\' }}>\n',
    '                                <input type="hidden" name="doc_owner" id="docOwnerInput" value="{{ doc.doc_owner if doc else \'\' }}">\n',
    '                                <div class="dropdown-list" id="docOwnerList" style="display: none;">\n',
    '                                    {% for e in employees %}\n',
    '                                    <div class="dropdown-item" onclick="selectEmployee(\'docOwner\', \'{{ e.email }}\', \'{{ e.name }}\')">\n',
    '                                        {{ e.name }} ({{ e.email }})\n',
    '                                    </div>\n',
    '                                    {% endfor %}\n',
    '                                    <div class="dropdown-item no-results" style="display: none;">No employees found</div>\n',
    '                                </div>\n',
    '                            </div>\n',
    '                        </div>\n',
    '                        <div class="col-md-4">\n',
    '                            <label class="form-label">Originator</label>\n',
    '                            <div class="custom-dropdown" id="originatorDropdown">\n',
    '                                <input type="text" class="form-control" id="originatorSearch" placeholder="Search Employee..." autocomplete="off" {{ \'disabled\' if mode==\'edit\' }}>\n',
    '                                <input type="hidden" name="originator" id="originatorInput" value="{{ doc.originator if doc else \'\' }}">\n',
    '                                <div class="dropdown-list" id="originatorList" style="display: none;">\n',
    '                                    {% for e in employees %}\n',
    '                                    <div class="dropdown-item" onclick="selectEmployee(\'originator\', \'{{ e.email }}\', \'{{ e.name }}\')">\n',
    '                                        {{ e.name }} ({{ e.email }})\n',
    '                                    </div>\n',
    '                                    {% endfor %}\n',
    '                                    <div class="dropdown-item no-results" style="display: none;">No employees found</div>\n',
    '                                </div>\n',
    '                            </div>\n',
    '                        </div>\n',
    '                        <div class="col-md-4">\n',
    '                            <label class="form-label">Reviewer</label>\n',
    '                            <div class="custom-dropdown" id="reviewerDropdown">\n',
    '                                <input type="text" class="form-control" id="reviewerSearch" placeholder="Search Employee..." autocomplete="off" {{ \'disabled\' if mode==\'edit\' }}>\n',
    '                                <input type="hidden" name="reviewer" id="reviewerInput" value="{{ doc.reviewer if doc else \'\' }}">\n',
    '                                <div class="dropdown-list" id="reviewerList" style="display: none;">\n',
    '                                    {% for e in employees %}\n',
    '                                    <div class="dropdown-item" onclick="selectEmployee(\'reviewer\', \'{{ e.email }}\', \'{{ e.name }}\')">\n',
    '                                        {{ e.name }} ({{ e.email }})\n',
    '                                    </div>\n',
    '                                    {% endfor %}\n',
    '                                    <div class="dropdown-item no-results" style="display: none;">No employees found</div>\n',
    '                                </div>\n',
    '                            </div>\n',
    '                        </div>\n'
]

# Replace lines 95-125 (indices 94-125)
# Verify start line content
if 'Doc Owner' not in lines[95]:
    print(f"Warning: Line 95 content mismatch: {lines[95]}")
    # Search for the block
    start_idx = -1
    for i, line in enumerate(lines):
        if '<label class="form-label">Doc Owner</label>' in line:
            start_idx = i - 1 # The div before it
            break
    if start_idx != -1:
        print(f"Found block start at {start_idx}")
        # Find end
        end_idx = start_idx
        div_count = 0
        # This is risky to parse HTML with lines, but we know the structure is 3 cols
        # We want to replace 3 col-md-4 divs.
        # Let's just assume the line count is roughly correct or use the hardcoded range if it matches.
        lines[start_idx:start_idx+31] = new_html # 31 lines replaced
    else:
        print("Could not find Doc Owner block")
else:
    lines[94:125] = new_html

# Update JS
# Find toggleIdr function and replace it
js_start = -1
for i, line in enumerate(lines):
    if 'function toggleIdr() {' in line:
        js_start = i
        break

if js_start != -1:
    # Replace the function body
    # We'll just replace a fixed number of lines or until the closing brace
    # The function is about 18 lines long
    new_js = [
        '        function toggleIdr() {\n',
        '            if (idrReqSelect && idrReqSelect.value === \'Yes\') {\n',
        '                idrContainer.style.display = \'block\';\n',
        '                // Disable Reviewer if IDR is Yes\n',
        '                if (reviewerSearch) {\n',
        '                    reviewerSearch.value = "";\n',
        '                    if (reviewerInput) reviewerInput.value = "";\n',
        '                    reviewerSearch.disabled = true;\n',
        '                    reviewerSearch.removeAttribute(\'required\');\n',
        '                }\n',
        '            } else {\n',
        '                idrContainer.style.display = \'none\';\n',
        '                // Enable Reviewer if IDR is No\n',
        '                if (reviewerSearch) {\n',
        '                    reviewerSearch.disabled = false;\n',
        '                    reviewerSearch.setAttribute(\'required\', \'required\');\n',
        '                }\n',
        '            }\n',
        '        }\n'
    ]
    # Find the end of the function
    js_end = js_start
    brace_count = 0
    for j in range(js_start, len(lines)):
        brace_count += lines[j].count('{')
        brace_count -= lines[j].count('}')
        if brace_count == 0:
            js_end = j + 1
            break
    
    lines[js_start:js_end] = new_js

# Add new JS functions before the end block
# Find {% endblock %}
end_block_idx = -1
for i in range(len(lines)-1, -1, -1):
    if '{% endblock %}' in lines[i]:
        end_block_idx = i
        break

if end_block_idx != -1:
    new_funcs = [
        '\n',
        '        // Generic Employee Selection Logic\n',
        '        function setupEmployeeDropdown(type) {\n',
        '            const search = document.getElementById(type + \'Search\');\n',
        '            const list = document.getElementById(type + \'List\');\n',
        '            const input = document.getElementById(type + \'Input\');\n',
        '\n',
        '            if (search) {\n',
        '                search.addEventListener(\'focus\', () => list.style.display = \'block\');\n',
        '\n',
        '                document.addEventListener(\'click\', function (e) {\n',
        '                    if (!e.target.closest(\'#\' + type + \'Dropdown\')) {\n',
        '                        list.style.display = \'none\';\n',
        '                    }\n',
        '                });\n',
        '\n',
        '                search.addEventListener(\'input\', function () {\n',
        '                    const filter = search.value.toLowerCase();\n',
        '                    const items = list.querySelectorAll(\'.dropdown-item:not(.no-results)\');\n',
        '                    let hasVisible = false;\n',
        '                    items.forEach(item => {\n',
        '                        const text = item.innerText.toLowerCase();\n',
        '                        if (text.includes(filter)) {\n',
        '                            item.style.display = \'block\';\n',
        '                            hasVisible = true;\n',
        '                        } else {\n',
        '                            item.style.display = \'none\';\n',
        '                        }\n',
        '                    });\n',
        '                    list.querySelector(\'.no-results\').style.display = hasVisible ? \'none\' : \'block\';\n',
        '                });\n',
        '            }\n',
        '        }\n',
        '\n',
        '        window.selectEmployee = function (type, email, name) {\n',
        '            document.getElementById(type + \'Search\').value = name;\n',
        '            document.getElementById(type + \'Input\').value = email;\n',
        '            document.getElementById(type + \'List\').style.display = \'none\';\n',
        '        };\n',
        '\n',
        '        // Initialize dropdowns\n',
        '        setupEmployeeDropdown(\'docOwner\');\n',
        '        setupEmployeeDropdown(\'originator\');\n',
        '        setupEmployeeDropdown(\'reviewer\');\n'
    ]
    lines[end_block_idx:end_block_idx] = new_funcs

# Add variable declarations for new inputs
# Find const reviewerSelect
var_idx = -1
for i, line in enumerate(lines):
    if "const reviewerSelect =" in line:
        var_idx = i
        break

if var_idx != -1:
    lines[var_idx] = "        const reviewerSearch = document.getElementById('reviewerSearch');\n        const reviewerInput = document.getElementById('reviewerInput');\n"

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully updated document.html")
