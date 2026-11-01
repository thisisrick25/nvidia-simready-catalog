from pipeline.inventory import asset_of, classify, build_inventory


def test_asset_of_nested():
    assert asset_of("food_produce_banana_m01/simready_usd/payloads/base.usda") == "food_produce_banana_m01"


def test_asset_of_root_file():
    assert asset_of(".gitattributes") == "__root__"


def test_classify_kinds():
    assert classify("a/com.nvidia.simready.packaging.json") == "packaging_json"
    assert classify("a/.metadata/com.nvidia.simready.packaging.bom.json") == "metadata"
    assert classify("a/simready_usd/payloads/base.usda") == "payload_usda"
    assert classify("a/simready_usd/payloads/PhysX/base.usda") == "payload_usda"
    assert classify("a/simready_usd/payloads/geometries.usd") == "geometry"
    assert classify("a/simready_usd/sm_a_01.usd") == "sm_usd"
    assert classify("a/.thumbs/256x256/sm_a_01.usd.png") == "thumb_default"
    assert classify("a/.thumbs/256x256/sm_a_01.usd_light.png") == "thumb_light"
    assert classify("a/.thumbs/256x256/sm_a_01.usd_transparent.png") == "thumb_transparent"
    assert classify("a/.thumbs/256x256/sm_a_01_thumbnail.png") == "thumb_composite"
    assert classify("a/Textures/tile.png") == "texture"
    assert classify("a/simready_usd/source_assets/model.usd") == "source_asset"


def test_build_inventory_schema():
    recs = [
        {"path": "a/com.nvidia.simready.packaging.json", "size": 500},
        {"path": "a/simready_usd/payloads/base.usda", "size": 10007},
        {"path": ".gitattributes", "size": 100},
    ]
    df = build_inventory(recs)
    assert list(df.columns) == ["path", "asset", "size", "kind", "ext"]
    assert len(df) == 3
    assert df.loc[df.path == ".gitattributes", "asset"].iloc[0] == "__root__"
    assert df["size"].sum() == 10607
