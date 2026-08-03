import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.mark.slow
def test_template_injection_smoke_test():
    """Simulate cloning the template and injecting .agents/ into a new project."""
    source_agents = Path(".agents")
    assert source_agents.exists(), "Source .agents/ directory is missing"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        target_agents = tmp_path / ".agents"

        # Inject
        shutil.copytree(source_agents, target_agents)

        # Verify injection
        assert target_agents.exists()
        assert (target_agents / "rules").exists()
        assert (target_agents / "workflows").exists()
        assert (target_agents / "product").exists()

        # Verify bootstrap phase 1 structural requirements
        assert len(list((target_agents / "rules").glob("*.md"))) > 0
        assert len(list((target_agents / "workflows").glob("*.md"))) > 0
