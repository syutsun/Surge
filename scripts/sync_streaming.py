"""Sync RuleGo streaming lists; sync upstream Spotify with personal additions and comment YouTube in !CN only."""
from pathlib import Path
import hashlib
import ipaddress
import re
import urllib.request

SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Streaming/!CN.list"
OUTPUT = Path("Ruleset/Streaming/!CN.list")
PERSONAL = Path("config/Spotify-personal.list")
SPOTIFY_SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Streaming/Music/Spotify.list"


def section_span(text, name):
    headers = list(re.finditer(r"^# > " + re.escape(name) + r"[ \t]*\r?$", text, re.M))
    if len(headers) != 1:
        raise ValueError("Missing or duplicate " + name + " header")
    start = headers[0].start()
    following = re.search(r"^# (?:> |\()", text[headers[0].end():], re.M)
    end = headers[0].end() + following.start() if following else len(text)
    return start, end


def spotify_span(text):
    return section_span(text, "Spotify")


def comment_youtube(text):
    start, end = section_span(text, "YouTube")
    block = text[start:end]
    # Preserve the title, existing comments, whitespace and following providers.
    commented = "".join(
        "# " + line if line.strip() and not line.lstrip().startswith("#") else line
        for line in block.splitlines(keepends=True)
    )
    if validate_rules(commented, 0) != 0:
        raise ValueError("YouTube rules are still active")
    return text[:start] + commented + text[end:]


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


def add_spotify_rules(upstream, personal):
    """Keep upstream Spotify rules current and append only missing personal rules."""
    validate_rules(upstream, 1)
    validate_rules(personal, 1)
    start, end = spotify_span(upstream)
    pstart, pend = spotify_span(personal)
    if start != 0 or end != len(upstream) or pstart != 0 or pend != len(personal):
        raise ValueError("Spotify inputs must contain only the Spotify section")
    seen = {line.split(" //", 1)[0].strip() for line in upstream.splitlines()
            if line.strip() and not line.lstrip().startswith("#")}
    additions = []
    for line in personal.splitlines()[1:]:
        key = line.split(" //", 1)[0].strip()
        if not key or key.startswith("#"):
            continue
        if key not in seen:
            additions.append(line)
            seen.add(key)
    if not additions:
        return upstream
    newline = "\r\n" if "\r\n" in upstream else "\n"
    return upstream.rstrip("\r\n") + newline + newline.join(additions) + newline


def merge_rules(upstream, personal):
    validate_rules(upstream, 100)
    start, end = spotify_span(upstream)
    block = add_spotify_rules(upstream[start:end], personal)
    result = upstream[:start] + block + upstream[end:]
    rstart, rend = spotify_span(result)
    if result[:rstart] != upstream[:start] or result[rend:] != upstream[end:]:
        raise ValueError("Non-Spotify content changed")
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


def build_outputs(upstream, personal, mirrors, spotify_upstream):
    # Validate every download before writing any output.
    outputs = {str(OUTPUT): comment_youtube(merge_rules(upstream, personal)).encode("utf-8")}
    outputs["Ruleset/Streaming/Spotify.list"] = add_spotify_rules(spotify_upstream, personal).encode("utf-8")
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
    spotify_upstream = download(SPOTIFY_SOURCE).decode("utf-8")
    outputs = build_outputs(data.decode("utf-8"), personal, mirrors, spotify_upstream)
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
