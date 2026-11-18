"""Validate upstream mirrors independently and preserve successful files byte for byte."""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path

from sync_advertising import validate as validate_advertising
from sync_apple import validate as validate_apple
from sync_modules import convert, download
from sync_selected_rules import validate as validate_selected
from sync_streaming import validate_rules


MANIFEST = Path("config/Upstream-mirrors.json")


def validate(data, path, spec):
    kind = spec["validator"]
    if kind == "advertising":
        return validate_advertising(data)
    if kind == "apple":
        return validate_apple(data)
    if kind == "selected":
        return validate_selected(data, dict(spec, name=path.name))
    if kind == "streaming":
        text = data.decode("utf-8")
        if not text.splitlines() or text.splitlines()[0] != spec["header"]:
            raise ValueError("Unexpected upstream header")
        return validate_rules(text, 1)
    if kind == "module":
        convert(data, dict(spec, name=path.name))
        return None
    raise ValueError("Unknown validator: " + kind)


def sync(item):
    path, spec = item
    try:
        data = download(spec["url"])
        count = validate(data, path, spec)
        if path.read_bytes() == data:
            print(f"{path}: unchanged")
            return True
        temporary = path.with_suffix(path.suffix + ".tmp")
        try:
            temporary.write_bytes(data)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        detail = f"{count} rules; " if count is not None else ""
        print(f"{path}: updated; {detail}SHA-256 {sha256(data).hexdigest()}")
        return True
    except Exception as error:
        print(f"::error::{path}: {error}")
        return False


def main():
    items = []
    seen = set()
    for spec in json.loads(MANIFEST.read_text(encoding="utf-8")):
        path = Path(spec["path"])
        module = spec["validator"] == "module"
        directory, suffix = ("Module", ".sgmodule") if module else ("Ruleset", ".list")
        if (path.is_absolute() or len(path.parts) < 2 or path.parts[0] != directory
                or ".." in path.parts or path.suffix != suffix or path in seen
                or not path.is_file() or path.is_symlink() or "display_name" in spec):
            raise ValueError("Invalid mirror destination: " + str(path))
        items.append((path, spec))
        seen.add(path)
    if not items:
        raise ValueError("Empty mirror manifest")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(sync, items))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
