import json
import logging
import re
from pathlib import Path

import pandas as pd

from pipeline import parse_packaging, parse_usda, parse_usdc
from pipeline.config import CACHE_DIR, DATA_DIR, HF_BASE

logger = logging.getLogger(__name__)
MAX_ERROR_LEN = 200

ASSET_COLUMNS = [
    "asset", "asset_type", "uuid", "asset_location", "taxonomy_root",
    "taxonomy_group", "up_axis", "meters_per_unit", "variants", "mesh_count",
    "rigid_body_count", "mass_kg", "has_articulation", "joint_types",
    "materials", "shader_classes", "semantic_tokens", "validation_profile",
    "validation_profile_version", "validated_date", "export_profile",
    "features_total", "features_passed", "all_features_passed",
    "failing_features", "license", "package_id", "packaged_date",
    "asset_info_mass_kg", "asset_info_category", "size_total_bytes",
    "size_payload_bytes", "geometry_size_bytes", "texture_size_bytes",
    "source_asset_size_bytes", "metadata_size_bytes", "metadata_file_count",
    "bom_file_count", "bom_entry_count", "bom_hash_count", "package_hash_count",
    "package_format_version", "conformance_file_count", "conformance_profile",
    "conformance_versions", "provenance_tool", "provenance_generated_date",
    "provenance_exported_date", "thumb_url", "parse_status", "parse_error",
    "usd_date_generated",
]


def discover_assets(cache_root):
    root = Path(cache_root)
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / "simready_usd").is_dir())


def _payload_files(asset_dir: Path):
    d = asset_dir / "simready_usd" / "payloads"
    if not d.is_dir():
        return []
    return sorted(d.glob("*.usda"))


PHYSICS_PAYLOAD_PRIORITY = (
    "instances_physx.usda",
    "instances_newton.usda",
    "instances_mujoco.usda",
    "instances.usda",
)


def _select_physics_payload(files):
    """Pick the payload file that actually carries per-mesh physics data.

    Only files named in PHYSICS_PAYLOAD_PRIORITY contain `physics:mass` /
    `physics:approximation` attributes. Falling back to an arbitrary .usda
    file (e.g. base.usda or materials.usda) silently yields mass_kg=0 and
    mesh_count=0 with no indication anything went wrong, so we return None
    instead when no known physics payload is present.
    """
    by_name = {f.name: f for f in files}
    for name in PHYSICS_PAYLOAD_PRIORITY:
        if name in by_name:
            return by_name[name]
    return None


MESH_COLUMNS = [
    "asset", "mesh", "mass_kg", "center_of_mass", "diagonal_inertia",
    "approximation", "material", "api_schemas",
]

VALIDATION_COLUMNS = [
    "asset", "feature", "version", "passed", "failing_requirements",
    "dependencies", "validated_date", "profile",
]

MATERIAL_COLUMNS = [
    "asset", "material", "shader_class", "semantic_tokens", "base_name",
]

THUMB_KINDS_BY_PREFERENCE = (
    "thumb_default", "thumb_light", "thumb_transparent", "thumb_composite", "thumb_other",
)


def _semantic_tokens(material_name):
    parts = str(material_name).split("__")
    return "|".join(parts[1:-1]) if len(parts) > 2 else ""


def _base_name(material_name):
    parts = str(material_name).split("__")
    return parts[-1] if len(parts) > 1 else material_name


def _resolve_inventory(row, inv, name):
    if inv is None or inv.empty:
        return
    sub = inv[inv["asset"] == name]
    if sub.empty:
        return
    row["size_total_bytes"] = int(sub["size"].sum())
    row["size_payload_bytes"] = int(sub.loc[sub["kind"] == "payload_usda", "size"].sum())
    for column, kind in (
        ("geometry_size_bytes", "geometry"),
        ("texture_size_bytes", "texture"),
        ("source_asset_size_bytes", "source_asset"),
        ("metadata_size_bytes", "metadata"),
    ):
        row[column] = int(sub.loc[sub["kind"] == kind, "size"].sum())
    for kind in THUMB_KINDS_BY_PREFERENCE:
        candidates = sorted(sub.loc[sub["kind"] == kind, "path"])
        if candidates:
            row["thumb_url"] = HF_BASE + candidates[0]
            break


def _count_hashes(value):
    def is_hash_key(key):
        name = str(key).lower()
        return (
            any(token in name for token in ("hash", "checksum", "digest"))
            or bool(re.fullmatch(r"(?:md|sha)\d+", name))
        )

    def count(value, in_hash_container=False):
        if isinstance(value, dict):
            return sum(
                count(item, in_hash_container or is_hash_key(key))
                for key, item in value.items()
            )
        if isinstance(value, list):
            return sum(count(item, in_hash_container) for item in value)
        return 1 if in_hash_container else 0

    return count(value)


def _find_values(value, names):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in names and isinstance(item, (str, int, float)):
                found.append(str(item))
            found.extend(_find_values(item, names))
    elif isinstance(value, list):
        for item in value:
            found.extend(_find_values(item, names))
    return found


def _find_lists(value, names):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in names and isinstance(item, list):
                found.append(item)
            found.extend(_find_lists(item, names))
    elif isinstance(value, list):
        for item in value:
            found.extend(_find_lists(item, names))
    return found


def _extract_metadata(asset_dir, row):
    metadata_dir = asset_dir / ".metadata"
    files = sorted(metadata_dir.glob("*.json"))
    row["metadata_file_count"] = len(files)
    row["bom_file_count"] = sum("bom" in path.name.lower() for path in files)
    row["conformance_file_count"] = sum("conformance" in path.name.lower() for path in files)
    versions = sorted(
        {
            match.group(1)
            for path in files
            if (match := re.search(r"Package@([^/]+)\.json$", path.name))
        }
    )
    row["conformance_versions"] = ", ".join(versions)
    row["bom_hash_count"] = 0
    row["bom_entry_count"] = 0
    row["package_hash_count"] = 0
    for path in files:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("could not parse metadata file %s", path)
            continue
        if "bom" in path.name.lower():
            row["bom_hash_count"] += _count_hashes(document)
            row["bom_entry_count"] += len(
                sum(
                    _find_lists(document, {"files"}),
                    [],
                )
            )
        row["package_hash_count"] += _count_hashes(document)
        if "conformance" in path.name.lower():
            row["conformance_profile"] = next(
                iter(_find_values(document, {"profile", "package_profile"})),
                None,
            )
        row["provenance_tool"] = row["provenance_tool"] or next(
            iter(_find_values(document, {"tool", "tool_name", "generator", "authoring_tool"})),
            None,
        )
        row["provenance_generated_date"] = row["provenance_generated_date"] or next(
            iter(_find_values(document, {"generated_date", "date_generated", "created_at"})),
            None,
        )
        row["provenance_exported_date"] = row["provenance_exported_date"] or next(
            iter(_find_values(document, {"exported_date", "date_exported", "exported_at"})),
            None,
        )


def _merge_base_data(doc, asset_dir):
    base = asset_dir / "simready_usd" / "payloads" / "base.usda"
    if not base.is_file():
        return
    b = parse_usda.parse_usda_text(
        base.read_text(encoding="utf-8", errors="replace")
    )
    if b["has_articulation"]:
        doc["has_articulation"] = True
    merged = dict(b["joint_types"])
    merged.update(doc["joint_types"])
    doc["joint_types"] = merged


def _extract_validation_rows(name, validation):
    rows = []
    for f in validation["features"]:
        rows.append(
            {
                "asset": name,
                "feature": f["feature"],
                "version": f["version"],
                "passed": f["passed"],
                "failing_requirements": f["failing_requirements"],
                "dependencies": f["dependencies"],
                "validated_date": validation["validated_date"],
                "profile": validation["profile"],
            }
        )
    return rows


def _extract_packaging(asset_dir):
    pkg_path = asset_dir / "com.nvidia.simready.packaging.json"
    if not pkg_path.is_file():
        return {}
    pkg = parse_packaging.parse_packaging(
        pkg_path.read_text(encoding="utf-8", errors="replace")
    )
    if not pkg:
        return {}
    return {
        "license": pkg.get("license"),
        "package_id": pkg.get("package_id"),
        "package_format_version": pkg.get("format_version"),
        "package_hash_count": _count_hashes(pkg),
        "provenance_tool": next(
            iter(_find_values(pkg, {"tool", "tool_name", "generator", "authoring_tool"})),
            None,
        ),
        "provenance_generated_date": next(
            iter(_find_values(pkg, {"generated_date", "date_generated", "created_at"})),
            None,
        ),
        "provenance_exported_date": next(
            iter(_find_values(pkg, {"exported_date", "date_exported", "exported_at"})),
            None,
        ),
        "packaged_date": parse_packaging.deploy_date_from_package_id(
            pkg.get("package_id")
        ),
    }


def extract_asset(asset_dir: Path, inv: pd.DataFrame):
    name = asset_dir.name
    row = {c: None for c in ASSET_COLUMNS}
    row.update(
        asset=name, parse_status="ok", mesh_count=0, rigid_body_count=0,
        mass_kg=None, has_articulation=False, variants=[],
        features_total=0, features_passed=0, size_total_bytes=0,
        size_payload_bytes=0,
        metadata_file_count=0, bom_file_count=0, bom_entry_count=0,
        bom_hash_count=0, package_hash_count=0, conformance_file_count=0,
    )
    mesh_rows, val_rows, mat_rows = [], [], []

    _resolve_inventory(row, inv, name)
    _extract_metadata(asset_dir, row)

    try:
        files = _payload_files(asset_dir)
        if not files:
            row["parse_status"] = "no_payloads"
            return row, mesh_rows, val_rows, mat_rows
        primary = _select_physics_payload(files)
        if primary is None:
            row["parse_status"] = "no_physics_payload"
            row["parse_error"] = (
                "no known physics payload among: "
                + ", ".join(sorted(f.name for f in files))
            )[:MAX_ERROR_LEN]
            return row, mesh_rows, val_rows, mat_rows
        doc = parse_usda.parse_usda_text(
            primary.read_text(encoding="utf-8", errors="replace")
        )
        _merge_base_data(doc, asset_dir)

        tax = parse_usda.taxonomy(doc["asset_location"])
        row.update(
            {
                "asset_type": doc["asset_type"],
                "uuid": doc["uuid"],
                "asset_location": doc["asset_location"],
                "taxonomy_root": tax["root"],
                "taxonomy_group": tax["group"],
                "up_axis": doc["up_axis"],
                "meters_per_unit": doc["meters_per_unit"],
                "variants": doc["variants"],
                "mesh_count": doc["mesh_count"],
                "rigid_body_count": doc["rigid_body_count"],
                "mass_kg": doc["total_mass_kg"],
                "has_articulation": doc["has_articulation"],
                "joint_types": json.dumps(doc["joint_types"]),
                "materials": ", ".join(doc["materials"]),
                "usd_date_generated": doc["usd_date_generated"],
            }
        )
        shaders = sorted(
            {parse_usda.shader_class(m) for m in doc["materials"]} - {None}
        )
        row["shader_classes"] = ", ".join(shaders)
        row["semantic_tokens"] = ", ".join(
            sorted(
                {
                    t
                    for m in doc["materials"]
                    for t in _semantic_tokens(m).split("|")
                    if t
                }
            )
        )
        v = doc["validation"]
        row.update(
            {
                "validation_profile": v["profile"],
                "validation_profile_version": v["profile_version"],
                "validated_date": v["validated_date"],
                "export_profile": v["export_profile"],
                "features_total": len(v["features"]),
                "features_passed": sum(1 for f in v["features"] if f["passed"]),
            }
        )
        row["all_features_passed"] = (
            bool(v["features"]) and all(f["passed"] for f in v["features"])
        )
        fails = sorted({f["feature"] for f in v["features"] if not f["passed"]})
        row["failing_features"] = ", ".join(fails) if fails else None
        val_rows = _extract_validation_rows(name, v)
        for m in doc["meshes"]:
            mesh_rows.append(
                {
                    "asset": name,
                    "mesh": m["mesh"],
                    "mass_kg": m["mass_kg"],
                    "center_of_mass": m["center_of_mass"],
                    "diagonal_inertia": m["diagonal_inertia"],
                    "approximation": m["approximation"],
                    "material": m["material"],
                    "api_schemas": m["api_schemas"],
                }
            )
        for mname in doc["materials"]:
            mat_rows.append(
                {
                    "asset": name,
                    "material": mname,
                    "shader_class": parse_usda.shader_class(mname),
                    "semantic_tokens": _semantic_tokens(mname),
                    "base_name": _base_name(mname),
                }
            )
        row.update(_extract_packaging(asset_dir))
        sm = sorted((asset_dir / "simready_usd").glob("sm_*.usd"))
        if sm:
            info = parse_usdc.parse_sm_usd(sm[0])
            if info:
                row["asset_info_mass_kg"] = info.get("mass_kg")
                row["asset_info_category"] = info.get("category")
    except Exception as e:
        row["parse_status"] = "parse_error"
        row["parse_error"] = str(e)[:MAX_ERROR_LEN]
        logger.warning("parse error for %s: %s", name, e)
    return row, mesh_rows, val_rows, mat_rows


def extract_all(cache_root, inv, out_dir):
    cache_root = Path(cache_root)
    out_dir = Path(out_dir)
    asset_rows, mesh_all, val_all, mat_all = [], [], [], []
    for adir in discover_assets(cache_root):
        r, m, v, mt = extract_asset(adir, inv)
        asset_rows.append(r)
        mesh_all += m
        val_all += v
        mat_all += mt
    out_dir.mkdir(parents=True, exist_ok=True)
    assets = pd.DataFrame(asset_rows, columns=ASSET_COLUMNS)
    assets.to_parquet(out_dir / "assets.parquet")
    pd.DataFrame(mesh_all, columns=MESH_COLUMNS if not mesh_all else None).to_parquet(out_dir / "meshes.parquet")
    pd.DataFrame(val_all, columns=VALIDATION_COLUMNS if not val_all else None).to_parquet(out_dir / "validation.parquet")
    pd.DataFrame(mat_all, columns=MATERIAL_COLUMNS if not mat_all else None).to_parquet(out_dir / "materials.parquet")
    return assets


def main():
    inv = pd.read_parquet(DATA_DIR / "inventory.parquet")
    assets = extract_all(CACHE_DIR / "simready-assets", inv, DATA_DIR)
    counts = assets["parse_status"].value_counts().to_dict()
    logger.info("extracted %d assets -> %s", len(assets), DATA_DIR)
    logger.info("parse_status: %s", counts)


if __name__ == "__main__":
    main()
