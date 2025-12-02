
import re

file_path = r'C:\Users\13015646\Desktop\emt_app\templates\document.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the backslashes in onclick attributes
content = content.replace(r"\'", "'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully fixed backslashes in onclick attributes.")
