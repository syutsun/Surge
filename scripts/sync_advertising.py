"""Mirror ConnersHua/RuleGo Advertising.list unchanged after validation."""
import ipaddress


def validate(data):
    text = data.decode("utf-8")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        raise ValueError("Upstream returned HTML")
    if not text.startswith("# Advertising"):
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
    if count < 500:
        raise ValueError("Unexpectedly small upstream file")
    return count
