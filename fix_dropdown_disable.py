import re

# Read the current file
with open(r'C:\Users\13015646\Desktop\emt_app\templates\document.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the setupEmployeeDropdown function and fix it
# The issue is that the focus event listener doesn't check if the field is disabled

old_setup_function = r'''function setupEmployeeDropdown\(type\) \{[^}]+search\.addEventListener\('focus', \(\) => list\.style\.display = 'block'\);'''

new_setup_function = '''function setupEmployeeDropdown(type) {
            const search = document.getElementById(type + 'Search');
            const list = document.getElementById(type + 'List');
            const input = document.getElementById(type + 'Input');
            if (search) {
                search.addEventListener('focus', () => {
                    if (!search.disabled) {  // Only show dropdown if not disabled
                        list.style.display = 'block';
                    }
                });'''

# Try to replace
if re.search(old_setup_function, content, re.DOTALL):
    content = re.sub(old_setup_function, new_setup_function, content, flags=re.DOTALL)
    print("Fixed setupEmployeeDropdown function")
else:
    print("Could not find setupEmployeeDropdown function pattern")

# Write back
with open(r'C:\Users\13015646\Desktop\emt_app\templates\document.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully")
