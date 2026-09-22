with open("pdf_eval.py", "rb") as f:
    content = f.read()

# Replace Non-Breaking Spaces (\xa0) with standard spaces
content = content.replace(b"\xc2\xa0", b" ")

with open("pdf_eval.py", "wb") as f:
    f.write(content)

print("Cleaned non-breaking spaces successfully.")