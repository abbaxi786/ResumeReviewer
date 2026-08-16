import os
import importlib.util
from pathlib import Path

packages = [
    "django",
    "rest_framework",
    "spacy",
    "nltk",
    "numpy",
    "sklearn",
    "pdfplumber",
    "docx",
    "striprtf",
    "cloudinary",
    "psycopg",
]

site_packages = Path(next(p for p in __import__("site").getsitepackages()
                          if "site-packages" in p))

def get_size(path):
    total = 0

    if path.is_file():
        return path.stat().st_size

    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                total += (Path(root) / file).stat().st_size
            except OSError:
                pass

    return total


results = []

for package in packages:
    spec = importlib.util.find_spec(package)

    if spec is None:
        results.append((package, "NOT INSTALLED"))
        continue

    if spec.submodule_search_locations:
        location = Path(next(iter(spec.submodule_search_locations)))
    else:
        location = Path(spec.origin)

    size = get_size(location)

    results.append((package, size))


for package, size in sorted(
    results,
    key=lambda x: x[1] if isinstance(x[1], int) else 0,
    reverse=True
):
    if isinstance(size, int):
        print(f"{package:20} {size / 1024 / 1024:8.2f} MB")
    else:
        print(f"{package:20} {size}")