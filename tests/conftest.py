import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def banana_usda():
    return (FIXTURES / "instances_physx_banana.usda").read_text(encoding="utf-8")


@pytest.fixture
def banana_pkg():
    return json.loads((FIXTURES / "packaging_banana.json").read_text(encoding="utf-8"))
