"""Sync RuleGo Direct+.list while excluding the user's Google section."""
from pathlib import Path
import hashlib
import re
import urllib.request

SOURCE = "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Direct%2B.list"
OUTPUT = Path("Ruleset/Direct+.list")
START = "# ---(Alphabet)---"
END = "# ------"


def filter_rules(source):
    if not source.startswith("# Direct+") or "<html" in source.lower():
        raise ValueError("Unexpected upstream content")
    starts = list(re.finditer(r"^" + re.escape(START) + r"[ \t]*\r?$", source, re.M))
    if len(starts) != 1:
        raise ValueError("Missing or duplicate Alphabet boundary")
    following = re.search(r"^" + re.escape(END) + r"[ \t]*\r?$", source[starts[0].end():], re.M)
    if not following:
        raise ValueError("Missing end boundary")
    start = starts[0].start()
    end = starts[0].end() + following.start()
    # Preserve all bytes outside the excluded block, including the end marker.
    result = source[:start] + source[end:]
    count = 0
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not re.fullmatch(r"(DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|DOMAIN-WILDCARD),[^,\s]+(?:,extended-matching)?", line):
            raise ValueError("Unsupported upstream rule: " + line)
        count += 1
    if count < 10:
        raise ValueError("Unexpectedly small upstream")
    return result


def download():
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(SOURCE, headers={"User-Agent": "Surge"})
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except Exception as error:
            last = error
    raise RuntimeError("Upstream download failed") from last


def main():
    data = download()
    result = filter_rules(data.decode("utf-8"))
    temporary = OUTPUT.with_suffix(".list.tmp")
    temporary.write_bytes(result.encode("utf-8"))
    temporary.replace(OUTPUT)
    count = sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in result.splitlines())
    print("Direct+ rules:", count, "; upstream SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
