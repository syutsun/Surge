"""Sync RuleGo Tracking.list and comment the MI section per user policy."""
from pathlib import Path
import hashlib
import ipaddress
import re
import urllib.request

SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Reject/Tracking.list"
OUTPUT = Path("Ruleset/Reject/Tracking.list")


def validate(data):
    text = data.decode("utf-8")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        raise ValueError("Upstream returned HTML")
    if not text.startswith("# Privacy"):
        raise ValueError("Unexpected upstream header")
    count = 0
    for original in text.splitlines():
        line = original.split(" //", 1)[0].strip()
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
    if count < 50:
        raise ValueError("Unexpectedly small upstream file")
    return count


def comment_mi(data):
    validate(data)
    source = data.decode("utf-8")
    headers = list(re.finditer(r"^# > MI[ \t]*\r?$", source, re.M))
    if len(headers) != 1:
        raise ValueError("Missing or duplicate MI section")
    start = headers[0].start()
    following = re.search(r"^# (?:> |---|\()", source[headers[0].end():], re.M)
    end = headers[0].end() + following.start() if following else len(source)
    block = source[start:end]
    commented = "".join(
        "# " + line if line.strip() and not line.lstrip().startswith("#") else line
        for line in block.splitlines(keepends=True)
    )
    if any(line.strip() and not line.lstrip().startswith("#") for line in commented.splitlines()):
        raise ValueError("MI rules remain active")
    result = source[:start] + commented + source[end:]
    return result.encode("utf-8")


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
    result = comment_mi(data)
    active_count = validate(result)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".list.tmp")
    temporary.write_bytes(result)
    temporary.replace(OUTPUT)
    print("Upstream rules:", count, "; active after commenting MI:", active_count,
          "; upstream SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
