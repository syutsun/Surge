"""Sync RuleGo !CN.list while keeping only Spotify's personal section."""
from pathlib import Path
import hashlib
import ipaddress
import re
import urllib.request

SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Streaming/!CN.list"
OUTPUT = Path("Ruleset/Streaming/!CN.list")
PERSONAL = Path("config/Spotify-personal.list")


def spotify_span(text):
    headers = list(re.finditer(r"^# > Spotify[ \t]*\r?$", text, re.M))
    if len(headers) != 1:
        raise ValueError("Missing or duplicate Spotify header")
    start = headers[0].start()
    following = re.search(r"^# (?:> |\()", text[headers[0].end():], re.M)
    end = headers[0].end() + following.start() if following else len(text)
    return start, end


def validate_rules(text, minimum):
    if "<html" in text.lower() or "<!doctype" in text.lower():
        raise ValueError("Unexpected HTML")
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
                raise ValueError("Invalid domain rule: " + line)
            if len(fields) == 3 and fields[2] != "extended-matching":
                raise ValueError("Unknown domain option")
        elif kind in ("IP-CIDR", "IP-CIDR6"):
            network = ipaddress.ip_network(value, strict=False)
            if network.version != (6 if kind == "IP-CIDR6" else 4):
                raise ValueError("IP version mismatch")
            if len(fields) == 3 and fields[2] != "no-resolve":
                raise ValueError("Unknown IP option")
        elif kind == "GEOIP":
            if len(fields) == 3 and fields[2] != "no-resolve":
                raise ValueError("Unknown GEOIP option")
        else:
            raise ValueError("Unsupported rule type: " + kind)
        count += 1
    if count < minimum:
        raise ValueError("Unexpectedly small rule set")
    return count


def merge_rules(upstream, personal):
    validate_rules(upstream, 100)
    validate_rules(personal, 1)
    start, end = spotify_span(upstream)
    pstart, pend = spotify_span(personal)
    if pstart != 0 or pend != len(personal):
        raise ValueError("Personal file must contain only the Spotify section")
    block = personal.rstrip("\r\n") + "\n"
    result = upstream[:start] + block + upstream[end:]
    rstart, rend = spotify_span(result)
    if result[:rstart] != upstream[:start] or result[rend:] != upstream[end:]:
        raise ValueError("Non-Spotify content changed")
    if result[rstart:rend] != block:
        raise ValueError("Personal Spotify section changed")
    return result


def main():
    personal = PERSONAL.read_bytes().decode("utf-8")
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(SOURCE, headers={"User-Agent": "Surge"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            upstream = data.decode("utf-8")
            result = merge_rules(upstream, personal)
            break
        except Exception as error:
            last_error = error
    else:
        raise RuntimeError("Upstream sync failed") from last_error
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".list.tmp")
    temporary.write_bytes(result.encode("utf-8"))
    temporary.replace(OUTPUT)
    print("Synced streaming rules:", validate_rules(result, 100))
    print("Personal Spotify rules:", validate_rules(personal, 1))
    print("Upstream SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
