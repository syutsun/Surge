"""Sync native Surge modules from their verified original upstreams."""
from pathlib import Path
import hashlib
import json
import re
import urllib.request

CONFIG = Path("config/Module-upstreams.json")


def convert(data, spec):
    text = data.decode("utf-8")
    if len(data) < spec["minimum_bytes"] or "<html" in text[:500].lower() or "<!doctype" in text[:500].lower():
        raise ValueError("Empty/error page for " + spec["name"])
    names = list(re.finditer(r"^#!name=[^\r\n]*", text, re.M))
    if len(names) != 1:
        raise ValueError("Missing or duplicate module name")
    sections = set(re.findall(r"^\[([^\]\r\n]+)\][ \t]*\r?$", text, re.M))
    if not set(spec["sections"]).issubset(sections):
        raise ValueError("Required sections missing for " + spec["name"])
    if not any(line.strip() and not line.lstrip().startswith(("#", "[")) for line in text.splitlines()):
        raise ValueError("Module has no settings")
    # Keep the user's display name; preserve all remaining upstream text.
    name = names[0]
    result = text[:name.start()] + "#!name=" + spec["display_name"] + text[name.end():]
    return result.encode("utf-8")


def prepare(specs, downloads):
    names = [spec["name"] for spec in specs]
    if len(set(names)) != len(names) or set(downloads) != set(names):
        raise ValueError("Duplicate/missing/unexpected modules")
    outputs = {}
    for spec in specs:
        name = spec["name"]
        if Path(name).name != name or not name.endswith(".sgmodule"):
            raise ValueError("Invalid destination filename")
        outputs[name] = convert(downloads[name], spec)
    return outputs


def download(url):
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Surge"})
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except Exception as error:
            last = error
    raise RuntimeError("Download failed: " + url) from last


def main():
    specs = json.loads(CONFIG.read_text())
    downloads = {spec["name"]: download(spec["url"]) for spec in specs}
    outputs = prepare(specs, downloads)
    for spec in specs:
        name = spec["name"]
        path = Path("Module") / name
        temporary = path.with_suffix(".sgmodule.tmp")
        temporary.write_bytes(outputs[name])
        temporary.replace(path)
        print(name, "upstream SHA-256:", hashlib.sha256(downloads[name]).hexdigest(),
              "output SHA-256:", hashlib.sha256(outputs[name]).hexdigest())


if __name__ == "__main__":
    main()
