import sys
from pathlib import Path
from PyPDF2 import PdfReader

if len(sys.argv) < 3:
    print("Usage: python extract_pdf_text.py <input.pdf> <output.txt>")
    sys.exit(2)

pdf_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
reader = PdfReader(str(pdf_path))
text_parts = []
for page in reader.pages:
    try:
        text_parts.append(page.extract_text() or "")
    except Exception as e:
        text_parts.append("")

out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(text_parts))

print(f"Wrote text to {out_path}")
