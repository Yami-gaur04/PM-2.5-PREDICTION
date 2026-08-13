"""One-time fix: corrupted HTML tag names in frontend files."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
BAD = bytes.fromhex("6d6f74696f6e6c657373").decode()  # motionless
GOOD = "d" + "iv"

for path in ROOT.rglob("*"):
    if path.suffix.lower() not in {".html", ".js", ".css"}:
        continue
    text = path.read_text(encoding="utf-8")
    if BAD not in text:
        continue
    path.write_text(text.replace(BAD, GOOD), encoding="utf-8")
    print("fixed:", path.relative_to(ROOT))
