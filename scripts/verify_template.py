import sys
from pathlib import Path

# Force UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    print("Verifying Antigravity Template Installation...\n")
    all_passed = True

    # 1. Rules
    rules_path = Path(".agents/rules")
    if rules_path.exists() and len(list(rules_path.glob("*.md"))) > 0:
        print("✅ .agents/rules/ - Valid")
    else:
        print("❌ .agents/rules/ - Missing or empty")
        all_passed = False

    # 2. Skills
    skills_path = Path(".agents/skills")
    if skills_path.exists() and len(list(skills_path.rglob("SKILL.md"))) > 0:
        print("✅ .agents/skills/ - Valid")
    else:
        print("❌ .agents/skills/ - Missing or empty")
        all_passed = False

    # 3. Workflows
    workflows_path = Path(".agents/workflows")
    if workflows_path.exists() and len(list(workflows_path.glob("*.md"))) > 0:
        print("✅ .agents/workflows/ - Valid")
    else:
        print("❌ .agents/workflows/ - Missing or empty")
        all_passed = False

    # 4. Product Templates
    templates_path = Path(".agents/product/templates")
    if templates_path.exists() and len(list(templates_path.glob("*.md"))) == 5:
        print("✅ Product templates - 5/5 present")
    else:
        print("❌ Product templates - Missing some or all templates")
        all_passed = False

    # 5. MCP Server
    try:
        from src.antigravity.capabilities.mcp.server import server  # noqa: F401
        print("✅ MCP server - Importable")
    except ImportError:
        print("❌ MCP server - Failed to import")
        all_passed = False

    # 6. Eval History
    eval_hist = Path("data/eval_history.json")
    if eval_hist.exists():
        print("✅ Eval history - Present")
    else:
        print("⚠️  No eval history - run /self-eval to establish baseline")

    print("\n")
    if all_passed:
        print("All structural checks passed! The governance environment is ready.")
        sys.exit(0)
    else:
        print("Some checks failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
