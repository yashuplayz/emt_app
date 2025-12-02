
import re

file_path = r'C:\Users\13015646\Desktop\emt_app\templates\document.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements
replacements = [
    (
        r'<div class="dropdown-item"\s+onclick="selectEmployee\(\'docOwner\', \'{{ e.email }}\', \'{{ e.name }}\'\)">',
        r'<div class="dropdown-item" data-value="{{ e.email }}" onclick="selectEmployee(\'docOwner\', \'{{ e.email }}\', \'{{ e.name }}\')">'
    ),
    (
        r'<div class="dropdown-item"\s+onclick="selectEmployee\(\'originator\', \'{{ e.email }}\', \'{{ e.name }}\'\)">',
        r'<div class="dropdown-item" data-value="{{ e.email }}" onclick="selectEmployee(\'originator\', \'{{ e.email }}\', \'{{ e.name }}\')">'
    ),
    (
        r'<div class="dropdown-item"\s+onclick="selectEmployee\(\'reviewer\', \'{{ e.email }}\', \'{{ e.name }}\'\)">',
        r'<div class="dropdown-item" data-value="{{ e.email }}" onclick="selectEmployee(\'reviewer\', \'{{ e.email }}\', \'{{ e.name }}\')">'
    ),
    (
        r'<div class="dropdown-item" onclick="selectSignoff\(\'{{ e.email }}\', \'{{ e.name }}\'\)">',
        r'<div class="dropdown-item" data-value="{{ e.email }}" onclick="selectSignoff(\'{{ e.email }}\', \'{{ e.name }}\')">'
    )
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully added data-value attributes to dropdown items.")
