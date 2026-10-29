import json
import re


def parse_packaging(text: str):
    """Parse com.nvidia.simready.packaging.json content. Returns dict or None."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def deploy_date_from_package_id(package_id):
    """Extract YYYY-MM-DD from a package_id like '....2026.10.09_141223'."""
    if not package_id:
        return None
    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", str(package_id))
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"