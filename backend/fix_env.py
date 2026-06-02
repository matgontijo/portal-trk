import os

with open('../.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific string replacing the literal "\\nJWT_PUBLIC_KEY" with a real newline
content = content.replace('"\\nJWT_PUBLIC_KEY="', '"\nJWT_PUBLIC_KEY="')

with open('../.env', 'w', encoding='utf-8') as f:
    f.write(content)
