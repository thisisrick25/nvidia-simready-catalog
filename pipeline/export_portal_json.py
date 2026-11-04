import json
import logging
from pathlib import Path

import pandas as pd

from pipeline.config import DATA_DIR, PORTAL_STATIC_DATA_DIR

logger = logging.getLogger(__name__)

# Columns to include in the portal JSON (curated subset for performance)
ASSET_PORTAL_COLUMNS = [
    "asset",
    "asset_type",
    "taxonomy_root",
    "taxonomy_group",
    "uuid",
    "up_axis",
    "meters_per_unit",
    "variants",
    "mesh_count",
    "rigid_body_count",
    "mass_kg",
    "has_articulation",
    "joint_types",
    "materials",
    "shader_classes",
    "semantic_tokens",
    "validation_profile",
    "validation_profile_version",
    "validated_date",
    "export_profile",
    "features_total",
    "features_passed",
    "all_features_passed",
    "failing_features",
    "license",
    "package_id",
    "packaged_date",
    "asset_info_mass_kg",
    "asset_info_category",
    "size_total_bytes",
    "size_payload_bytes",
    "geometry_size_bytes",
    "texture_size_bytes",
    "source_asset_size_bytes",
    "metadata_size_bytes",
    "metadata_file_count",
    "bom_file_count",
    "bom_entry_count",
    "bom_hash_count",
    "package_hash_count",
    "package_format_version",
    "conformance_file_count",
    "conformance_profile",
    "conformance_versions",
    "provenance_tool",
    "provenance_generated_date",
    "provenance_exported_date",
    "thumb_url",
    "parse_status",
    "parse_error",
    "usd_date_generated",
]

MESH_PORTAL_COLUMNS = [
    "asset",
    "mesh",
    "mass_kg",
    "center_of_mass",
    "diagonal_inertia",
    "approximation",
    "material",
    "api_schemas",
]

VALIDATION_PORTAL_COLUMNS = [
    "asset",
    "feature",
    "version",
    "passed",
    "failing_requirements",
    "dependencies",
    "validated_date",
    "profile",
]

MATERIAL_PORTAL_COLUMNS = [
    "asset",
    "material",
    "shader_class",
    "semantic_tokens",
    "base_name",
]


def _to_serializable(obj):
    """Convert pandas/numpy types to JSON-serializable Python types."""
    try:
        if pd.isna(obj):
            return None
    except (ValueError, TypeError):
        pass
    if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except ValueError:
            return obj.tolist()
    if isinstance(obj, (list, dict, str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def _records_to_json(df: pd.DataFrame, columns: list[str]) -> list[dict]:
    """Convert DataFrame to list of JSON-serializable dicts with selected columns."""
    if df.empty:
        return []
    available_cols = [c for c in columns if c in df.columns]
    records = df[available_cols].to_dict(orient="records")
    return [
        {k: _to_serializable(v) for k, v in record.items()}
        for record in records
    ]


def export_portal_json():
    """Export Parquet tables to JSON for the Next.js portal."""
    PORTAL_STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    assets = pd.read_parquet(DATA_DIR / "assets.parquet")
    meshes = pd.read_parquet(DATA_DIR / "meshes.parquet")
    validation = pd.read_parquet(DATA_DIR / "validation.parquet")
    materials = pd.read_parquet(DATA_DIR / "materials.parquet")
    stats = json.loads((DATA_DIR / "stats.json").read_text(encoding="utf-8"))

    # Export assets
    assets_json = _records_to_json(assets, ASSET_PORTAL_COLUMNS)
    (PORTAL_STATIC_DATA_DIR / "assets.json").write_text(
        json.dumps(assets_json, separators=(",", ":")),
        encoding="utf-8",
    )

    # Export meshes
    meshes_json = _records_to_json(meshes, MESH_PORTAL_COLUMNS)
    (PORTAL_STATIC_DATA_DIR / "meshes.json").write_text(
        json.dumps(meshes_json, separators=(",", ":")),
        encoding="utf-8",
    )

    # Export validation
    validation_json = _records_to_json(validation, VALIDATION_PORTAL_COLUMNS)
    (PORTAL_STATIC_DATA_DIR / "validation.json").write_text(
        json.dumps(validation_json, separators=(",", ":")),
        encoding="utf-8",
    )

    # Export materials
    materials_json = _records_to_json(materials, MATERIAL_PORTAL_COLUMNS)
    (PORTAL_STATIC_DATA_DIR / "materials.json").write_text(
        json.dumps(materials_json, separators=(",", ":")),
        encoding="utf-8",
    )

    # Export stats (already JSON, just copy)
    (PORTAL_STATIC_DATA_DIR / "stats.json").write_text(
        json.dumps(stats, separators=(",", ":")),
        encoding="utf-8",
    )

    logger.info(
        "portal JSON exported -> %s (assets: %d, meshes: %d, validation: %d, materials: %d)",
        PORTAL_STATIC_DATA_DIR,
        len(assets_json),
        len(meshes_json),
        len(validation_json),
        len(materials_json),
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    export_portal_json()


if __name__ == "__main__":
    main()