"""Copy stations JSON and full frontend theme from sibling project."""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
SIBLING = ROOT.parent

stations_dst = ROOT / "datasets" / "stations"
stations_dst.mkdir(parents=True, exist_ok=True)
stations_dst.mkdir(parents=True, exist_ok=True)
processed = ROOT / "datasets" / "processed"
processed.mkdir(parents=True, exist_ok=True)
(ROOT / "datasets" / "raw").mkdir(parents=True, exist_ok=True)
(ROOT / "backend" / "models").mkdir(parents=True, exist_ok=True)

src_json = SIBLING / "data" / "pan_india_locations.json"
if src_json.is_file():
    shutil.copy2(src_json, stations_dst / "pan_india_locations.json")
    print("copied stations")

fe = SIBLING / "frontend"
dst_fe = ROOT / "frontend"
for name in ["style.css", "index.html", "script.js"]:
    s, d = fe / name, dst_fe / name
    if s.is_file():
        shutil.copy2(s, d)
        print("copied", name)
for sub in ["map", "charts"]:
    (dst_fe / sub).mkdir(exist_ok=True)
    for f in (fe / sub).glob("*.js"):
        shutil.copy2(f, dst_fe / sub / f.name)
        print("copied", sub + "/" + f.name)
