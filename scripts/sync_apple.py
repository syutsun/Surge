"""Mirror ConnersHua/RuleGo Apple.list unchanged after validation."""
from pathlib import Path
import hashlib
import ipaddress
import urllib.request

SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Apple/Apple.list"
OUTPUT = Path("Ruleset/Apple.list")


def validate(data):
    text = data.decode("utf-8")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        raise ValueError("Upstream returned HTML")
    if not text.startswith("# Apple"):
        raise ValueError("Unexpected upstream header")
    count = 0
    for original in text.splitlines():
        line = original.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(",")
        if len(fields) not in (2, 3) or not fields[1]:
            raise ValueError("Invalid rule: " + line)
        kind, value = fields[:2]
        if kind in ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD"):
            if any(char.isspace() for char in value):
                raise ValueError("Invalid domain: " + value)
            if len(fields) == 3 and fields[2] != "extended-matching":
                raise ValueError("Unknown domain option: " + line)
        elif kind in ("IP-CIDR", "IP-CIDR6"):
            network = ipaddress.ip_network(value, strict=False)
            if network.version != (6 if kind == "IP-CIDR6" else 4):
                raise ValueError("IP rule version mismatch")
            if len(fields) == 3 and fields[2] != "no-resolve":
                raise ValueError("Unknown IP option: " + line)
        else:
            raise ValueError("Unsupported new upstream rule type: " + kind)
        count += 1
    if count < 10:
        raise ValueError("Unexpectedly small upstream file")
    return count


def main():
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(SOURCE, headers={"User-Agent": "Surge"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            count = validate(data)
            break
        except Exception as error:
            last_error = error
    else:
        raise RuntimeError("Upstream download/validation failed") from last_error
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".list.tmp")
    temporary.write_bytes(data)
    temporary.replace(OUTPUT)
    print("Mirrored original upstream:", count, "rules; SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
