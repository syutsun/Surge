"""Sync RuleGo Direct.list, excluding the PayPal section."""
from pathlib import Path
import hashlib
import ipaddress
import re
import urllib.request

SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Direct.list"
OUTPUT = Path("Ruleset/Direct.list")


def filter_rules(source):
    if not source.startswith("# Direct\n") or "<html" in source.lower():
        raise ValueError("Unexpected upstream content")
    headers = list(re.finditer(r"^# > PayPal[ \t]*\r?$", source, re.M))
    if len(headers) != 1:
        raise ValueError("Missing or duplicate PayPal section")
    start = headers[0].start()
    following = re.search(r"^# (?:> |---|\()", source[headers[0].end():], re.M)
    end = headers[0].end() + following.start() if following else len(source)
    count = 0
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(",")
        if len(fields) not in (2, 3) or not fields[1]:
            raise ValueError("Invalid rule: " + line)
        kind, value = fields[:2]
        if kind in ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD"):
            if any(char.isspace() for char in value) or (len(fields) == 3 and fields[2] != "extended-matching"):
                raise ValueError("Invalid domain rule")
        elif kind in ("IP-CIDR", "IP-CIDR6"):
            network = ipaddress.ip_network(value, strict=False)
            if network.version != (6 if kind == "IP-CIDR6" else 4) or (len(fields) == 3 and fields[2] != "no-resolve"):
                raise ValueError("Invalid IP rule")
        else:
            raise ValueError("Unsupported rule type: " + kind)
        count += 1
    if count < 10:
        raise ValueError("Unexpectedly small upstream")
    return source[:start] + source[end:]


def main():
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(SOURCE, headers={"User-Agent": "Surge"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            result = filter_rules(data.decode("utf-8"))
            break
        except Exception as error:
            last = error
    else:
        raise RuntimeError("Upstream download/filter failed") from last
    temporary = OUTPUT.with_suffix(".list.tmp")
    temporary.write_bytes(result.encode("utf-8"))
    temporary.replace(OUTPUT)
    count = sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in result.splitlines())
    print("Direct rules:", count, "; upstream SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
