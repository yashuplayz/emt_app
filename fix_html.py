
import os

file_path = r'C:\Users\13015646\Desktop\emt_app\templates\document.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of the duplicated content
start_idx = -1
for i, line in enumerate(lines):
    if i > 0 and '{% extends "base.html" %}' in line:
        start_idx = i
        break

if start_idx != -1:
    print(f"Found duplicated content starting at line {start_idx + 1}")
    new_content = lines[start_idx:]
    
    # Determine indentation
    first_line = new_content[0]
    indent = len(first_line) - len(first_line.lstrip())
    print(f"Detected indentation: {indent} spaces")
    
    # Dedent
    final_lines = []
    for line in new_content:
        if len(line) > indent:
            final_lines.append(line[indent:])
        else:
            final_lines.append(line.lstrip()) # Should be just newline
            
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print("Successfully restored document.html")
else:
    print("Could not find duplicated content. File might be okay or structure is different.")
