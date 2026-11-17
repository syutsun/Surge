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


# Local filenames stay stable even when upstream renames a service.
MIRRORS = {
    "Disney+.list": ("Disney+.list", "# > Disney+"),
    "HBO-Asia.list": ("HBO-Asia.list", "# > HBO Asia"),
    "HBO.list": ("Max.list", "# > Max"),
    "Netflix.list": ("Netflix.list", "# > Netflix"),
    "TikTok.list": ("TikTok.list", "# > TikTok"),
    "YouTube.list": ("YouTube.list", "# > YouTube"),
}
VIDEO_SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Streaming/Video/"


def build_outputs(upstream, personal, mirrors):
    # Validate every download before writing any output.
    outputs = {str(OUTPUT): merge_rules(upstream, personal).encode("utf-8")}
    pstart, pend = spotify_span(personal)
    if pstart != 0 or pend != len(personal):
        raise ValueError("Personal Spotify scope mismatch")
    validate_rules(personal, 1)
    outputs["Ruleset/Streaming/Spotify.list"] = personal.encode("utf-8")
    if set(mirrors) != set(MIRRORS):
        raise ValueError("Missing or unexpected standalone mirror")
    for local, (_, header) in MIRRORS.items():
        data = mirrors[local]
        text = data.decode("utf-8")
        if text.splitlines()[0] != header:
            raise ValueError("Wrong upstream service for " + local)
        validate_rules(text, 1)
        outputs["Ruleset/Streaming/" + local] = data
    return outputs


def download(url):
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Surge"})
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except Exception as error:
            last_error = error
    raise RuntimeError("Download failed: " + url) from last_error


def main():
    personal = PERSONAL.read_bytes().decode("utf-8")
    data = download(SOURCE)
    mirrors = {local: download(VIDEO_SOURCE + name) for local, (name, _) in MIRRORS.items()}
    outputs = build_outputs(data.decode("utf-8"), personal, mirrors)
    for name, content in outputs.items():
        path = Path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".list.tmp")
        temporary.write_bytes(content)
        temporary.replace(path)
        print(name, "rules:", validate_rules(content.decode("utf-8"), 1),
              "SHA-256:", hashlib.sha256(content).hexdigest())
    print("Upstream !CN SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
