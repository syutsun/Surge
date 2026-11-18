"""Mirror six selected RuleGo rulesets without changing their bytes."""
from pathlib import Path
import ipaddress
import json

MANIFEST = Path(__file__).resolve().parents[1] / "config/Upstream-mirrors.json"
SPECS = [
    dict(spec, name=Path(spec["path"]).name)
    for spec in json.loads(MANIFEST.read_text(encoding="utf-8"))
    if spec["validator"] == "selected"
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
