import re

FLOAT = r"[-+0-9.eE]+"

JOINT_PATTERNS = {
    "PhysicsRevoluteJoint": "revolute",
    "PhysicsPrismaticJoint": "prismatic",
    "PhysicsSphericalJoint": "spherical",
    "PhysicsFixedJoint": "fixed",
    "PhysicsD6Joint": "d6",
    "PhysicsJoint": "generic",
}


def _first(pattern, text, cast=str):
    m = re.search(pattern, text)
    if not m:
        return None
    try:
        return cast(m.group(1))
    except (ValueError, TypeError):
        return None


def parse_header_strings(text):
    out = {}
    for m in re.finditer(r'string ([A-Za-z_][A-Za-z0-9_]*) = "([^"]*)"', text):
        out.setdefault(m.group(1), m.group(2))
    return out


def parse_variants(text):
    return sorted(set(re.findall(r"dictionary (MuJoCo|Newton|PhysX|Isaac) = \{", text)))


def parse_validation(text):
    feats = []
    for fm in re.finditer(
        r'dictionary (FET\d+_[A-Z0-9_]+) = \{\s*'
        r'string dependencies = "(.*?)"\s*'
        r'(?:string "failing requirements" = "(.*?)"\s*)?'
        r'bool passed = (0|1)\s*'
        r'string version = "([^"]*)"',
        text,
        re.S,
    ):
        name, deps, failing, passed, version = fm.groups()
        feats.append(
            {
                "feature": name,
                "passed": passed == "1",
                "failing_requirements": failing or "[]",
                "version": version,
                "dependencies": deps or "[]",
            }
        )
    profiles = re.findall(r'string profile = "([^"]*)"', text)
    return {
        "profile": profiles[0] if profiles else None,
        "export_profile": profiles[-1] if len(profiles) > 1 else None,
        "profile_version": _first(r'string profile_version = "([^"]*)"', text),
        "validated_date": _first(r'dictionary "(\d{4}-\d{2}-\d{2})" = \{', text),
        "features": feats,
    }


def parse_meshes(text):
    meshes = []
    parts = re.split(r"\n\s*def Xform \"", text)
    for part in parts[1:]:
        name = part[: part.index('"')]
        com = re.search(r"point3f physics:centerOfMass = \(([^)]*)\)", part)
        inertia = re.search(r"float3f physics:diagonalInertia = \(([^)]*)\)", part)
        meshes.append(
            {
                "mesh": name,
                "mass_kg": _first(r"float physics:mass = (" + FLOAT + ")", part, float),
                "center_of_mass": com.group(1).strip() if com else None,
                "diagonal_inertia": inertia.group(1).strip() if inertia else None,
                "approximation": _first(r'token physics:approximation = "(\w+)"', part),
                "material": _first(r"material:[Bb]inding = <[^>]*?/([A-Za-z0-9_]+)>", part),
                "api_schemas": _first(r"apiSchemas = \[([^\]]*)\]", part),
            }
        )
    return meshes


def detect_joints(text):
    found = {}
    for token, kind in JOINT_PATTERNS.items():
        n = len(re.findall(rf"\b{token}\b", text))
        if n:
            found[kind] = n
    has_articulation = "PhysicsArticulationRootAPI" in text or bool(found)
    return {"joint_types": found, "has_articulation": has_articulation}


def parse_materials(text):
    seen = []
    bindings = re.findall(r"material:[Bb]inding = <[^>]*?/([A-Za-z0-9_]+)>", text)
    defs = re.findall(r'def Material "([^"]+)"', text)
    for n in list(bindings) + list(defs):
        if n not in seen:
            seen.append(n)
    return seen


def taxonomy(asset_location):
    if not asset_location:
        return {"root": None, "group": None}
    parts = str(asset_location).replace("\\", "/").strip("/").split("/")
    return {
        "root": parts[1] if len(parts) > 1 else None,
        "group": parts[2] if len(parts) > 2 else None,
    }


def shader_class(material_name):
    if not material_name:
        return None
    first = str(material_name).split("__")[0]
    for prefix in ("physics_mat_m_", "m_"):
        if first.startswith(prefix):
            return first[len(prefix):]
    return first


def parse_usda_text(text):
    header = parse_header_strings(text)
    meshes = parse_meshes(text)
    joints = detect_joints(text)
    validation = parse_validation(text)
    total_mass = sum(m["mass_kg"] for m in meshes if m["mass_kg"] is not None)
    rigid = sum(
        1
        for m in meshes
        if "PhysicsMassAPI" in (m["api_schemas"] or "")
        or "PhysicsRigidBodyAPI" in (m["api_schemas"] or "")
    )
    return {
        "asset_type": header.get("asset_type"),
        "uuid": header.get("uuid"),
        "asset_location": header.get("asset_location") or header.get("asset_dir"),
        "asset_name": header.get("asset_name"),
        "usd_date_generated": header.get("usd_date_generated"),
        "up_axis": _first(r'upAxis = "(\w+)"', text),
        "meters_per_unit": _first(r"metersPerUnit = (" + FLOAT + ")", text, float),
        "variants": parse_variants(text),
        "meshes": meshes,
        "total_mass_kg": total_mass,
        "rigid_body_count": rigid,
        "mesh_count": len(meshes),
        "joint_types": joints["joint_types"],
        "has_articulation": joints["has_articulation"],
        "materials": parse_materials(text),
        "validation": validation,
    }