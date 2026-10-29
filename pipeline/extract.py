import json
from pathlib import Path

import pandas as pd

from pipeline import parse_packaging, parse_usda, parse_usdc
from pipeline.config import CACHE_DIR, DATA_DIR, HF_BASE

ASSET_COLUMNS = [
    "asset", "asset_type", "uuid", "asset_location", "taxonomy_root",
    "taxonomy_group", "up_axis", "meters_per_unit", "variants", "mesh_count",
    "rigid_body_count", "mass_kg", "has_articulation", "joint_types",
    "materials", "shader_classes", "semantic_tokens", "validation_profile",
    "validation_profile_version", "validated_date", "export_profile",
    "features_total", "features_passed", "all_features_passed",
    "failing_features", "license", "package_id", "packaged_date",
    "asset_info_mass_kg", "asset_info_category", "size_total_bytes",
    "size_payload_bytes", "thumb_url", "parse_status", "parse_error",
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


def _semantic_tokens(material_name):
    parts = str(material_name).split("__")
    return "|".join(parts[1:-1]) if len(parts) > 2 else ""


def _base_name(material_name):
    parts = str(material_name).split("__")
    return parts[-1] if len(parts) > 1 else material_name


def extract_asset(asset_dir: Path, inv: pd.DataFrame):
    name = asset_dir.name
    row = {c: None for c in ASSET_COLUMNS}
    row.update(
        asset=name, parse_status="ok", mesh_count=0, rigid_body_count=0,
        mass_kg=None, has_articulation=False, variants=[],
        features_total=0, features_passed=0, size_total_bytes=0,
        size_payload_bytes=0,
    )
    mesh_rows, val_rows, mat_rows = [], [], []

    if inv is not None and len(inv):
        sub = inv[inv["asset"] == name]
        if len(sub):
            row["size_total_bytes"] = int(sub["size"].sum())
            row["size_payload_bytes"] = int(sub.loc[sub["kind"] == "payload_usda", "size"].sum())
            lit = sorted(sub.loc[sub["kind"] == "thumb_lit", "path"])
            if lit:
                row["thumb_url"] = HF_BASE + lit[0]

    try:
        files = _payload_files(asset_dir)
        if not files:
            row["parse_status"] = "no_payloads"
            return row, mesh_rows, val_rows, mat_rows
        primary = next(
            (f for f in files if f.name == "instances_physx.usda"), files[0]
        )
        doc = parse_usda.parse_usda_text(
            primary.read_text(encoding="utf-8", errors="replace")
        )
        base = asset_dir / "simready_usd" / "payloads" / "base.usda"
        if base.is_file():
            b = parse_usda.parse_usda_text(
                base.read_text(encoding="utf-8", errors="replace")
            )
            if b["has_articulation"]:
                doc["has_articulation"] = True
            merged = dict(b["joint_types"])
            merged.update(doc["joint_types"])
            doc["joint_types"] = merged

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
        for f in v["features"]:
            val_rows.append(
                {
                    "asset": name,
                    "feature": f["feature"],
                    "version": f["version"],
                    "passed": f["passed"],
                    "failing_requirements": f["failing_requirements"],
                    "dependencies": f["dependencies"],
                    "validated_date": v["validated_date"],
                    "profile": v["profile"],
                }
            )
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
        pkg_path = asset_dir / "com.nvidia.simready.packaging.json"
        if pkg_path.is_file():
            pkg = parse_packaging.parse_packaging(
                pkg_path.read_text(encoding="utf-8", errors="replace")
            )
            if pkg:
                row["license"] = pkg.get("license")
                row["package_id"] = pkg.get("package_id")
                row["packaged_date"] = parse_packaging.deploy_date_from_package_id(
                    pkg.get("package_id")
                )
        sm = sorted((asset_dir / "simready_usd").glob("sm_*.usd"))
        if sm:
            info = parse_usdc.parse_sm_usd(sm[0])
            if info:
                row["asset_info_mass_kg"] = info.get("mass_kg")
                row["asset_info_category"] = info.get("category")
    except Exception as e:  # never fail the whole run for one asset
        row["parse_status"] = "parse_error"
        row["parse_error"] = str(e)[:200]
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
    pd.DataFrame(mesh_all).to_parquet(out_dir / "meshes.parquet")
    pd.DataFrame(val_all).to_parquet(out_dir / "validation.parquet")
    pd.DataFrame(mat_all).to_parquet(out_dir / "materials.parquet")
    return assets


def main():
    inv = pd.read_parquet(DATA_DIR / "inventory.parquet")
    assets = extract_all(CACHE_DIR / "simready-assets", inv, DATA_DIR)
    counts = assets["parse_status"].value_counts().to_dict()
    print(f"extracted {len(assets)} assets -> {DATA_DIR}")
    print(f"parse_status: {counts}")


if __name__ == "__main__":
    main()