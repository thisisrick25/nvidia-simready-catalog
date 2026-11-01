import re

try:
    from pxr import Usd

    HAS_PXR = True
except ImportError:
    HAS_PXR = False


def parse_sm_usd(path):
    """Read asset_info off the default prim of a binary sm_*.usd. Optional enrichment."""
    if not HAS_PXR:
        return None
    try:
        stage = Usd.Stage.Open(str(path))
        if not stage:
            return None
        prim = stage.GetDefaultPrim()
        if not prim or not prim.IsValid():
            return None
        info = prim.GetAssetInfo() or {}
        out = {}
        for key in (
            "category",
            "mass",
            "rigid_body_count",
            "SemanticLabels",
            "physicsMaterials",
            "profile",
            "version",
        ):
            if key in info:
                out[key] = str(info[key])
        m = re.search(r"[-+]?\d*\.?\d+", out.get("mass", ""))
        if m:
            out["mass_kg"] = float(m.group())
        return out
    except Exception:
        return None
