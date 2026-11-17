"""Mirror six selected RuleGo rulesets without changing their bytes."""
from pathlib import Path
import hashlib
import ipaddress
import urllib.request

SPECS = [
    {
        "name": "PayPal.list",
        "url": "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/PayPal.list",
        "header": "# > PayPal",
        "minimum": 1
    },
    {
        "name": "Proxy+.list",
        "url": "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Proxy+.list",
        "header": "# Proxy+",
        "minimum": 1
    },
    {
        "name": "Proxy.list",
        "url": "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Proxy.list",
        "header": "# Proxy",
        "minimum": 100
    },
    {
        "name": "Telegram.list",
        "url": "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/Telegram.list",
        "header": "# Telegram",
        "minimum": 1
    },
    {
        "name": "WeChat.list",
        "url": "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/WeChat.list",
        "header": "# > WeChat",
        "minimum": 1
    },
    {
        "name": "X.list",
        "url": "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/X.list",
        "header": "# > Twitter",
        "minimum": 1
    }
]


def validate(data, spec):
    text = data.decode("utf-8")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        raise ValueError("Unexpected HTML")
    if not text.splitlines() or text.splitlines()[0] != spec["header"]:
        raise ValueError("Wrong upstream header: " + spec["name"])
    count = 0
    for original in text.splitlines():
        line = original.split(" //", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(",")
        if len(fields) not in (2, 3) or not fields[1]:
            raise ValueError("Invalid rule: " + line)
        kind, value = fields[:2]
        if kind in ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD", "USER-AGENT"):
            if any(char.isspace() for char in value):
                raise ValueError("Invalid domain/user-agent rule")
            if len(fields) == 3 and fields[2] != "extended-matching":
                raise ValueError("Unsupported domain option")
        elif kind in ("IP-CIDR", "IP-CIDR6"):
            network = ipaddress.ip_network(value, strict=False)
            if network.version != (6 if kind == "IP-CIDR6" else 4):
                raise ValueError("IP version mismatch")
            if len(fields) == 3 and fields[2] != "no-resolve":
                raise ValueError("Unsupported IP option")
        elif kind == "GEOIP":
            if len(fields) == 3 and fields[2] != "no-resolve":
                raise ValueError("Unsupported GEOIP option")
        else:
            raise ValueError("Unsupported rule type: " + kind)
        count += 1
    if count < spec["minimum"]:
        raise ValueError("Unexpectedly small rule set: " + spec["name"])
    return count


def prepare(downloads):
    if set(downloads) != {spec["name"] for spec in SPECS}:
        raise ValueError("Incomplete or unexpected files")
    for spec in SPECS:
        validate(downloads[spec["name"]], spec)
    return dict(downloads)


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
    outputs = prepare({spec["name"]: download(spec["url"]) for spec in SPECS})
    # Validate every file before writing; CI commits only after complete success.
    for spec in SPECS:
        data = outputs[spec["name"]]
        path = Path("Ruleset") / spec["name"]
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".list.tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
        print(spec["name"], "rules:", validate(data, spec),
              "SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
