"""Fix duplicate closing tags in frontend files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = "</" + "d" + "iv" + ">"

script = ROOT / "frontend" / "script.js"
text = script.read_text(encoding="utf-8")
bad = "Coverage</span>" + (C * 5) + "`;"
good = "Coverage</span>" + C + "`;"
if bad in text:
    text = text.replace(bad, good)
    script.write_text(text, encoding="utf-8")
    print("fixed script.js hero line")

index = ROOT / "frontend" / "index.html"
html = index.read_text(encoding="utf-8")
while C + C in html:
    html = html.replace(C + C, C)
index.write_text(html, encoding="utf-8")
print("fixed index.html duplicate closes")
