from bughound_agent import BugHoundAgent
from llm_client import MockClient


class OverEditMockClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if "Analyze this Python code" in user_prompt:
            return '[{"type":"Code Quality","severity":"Low","msg":"Found print statement."}]'

        if "Rewrite the code to address the issues listed" in user_prompt:
            return (
                "def f():\n"
                "    x = 1\n"
                "    y = 2\n"
                "    z = x + y\n"
                "    a = z * 2\n"
                "    b = a + 5\n"
                "    c = b - 3\n"
                "    d = c * 4\n"
                "    e = d // 2\n"
                "    print(e)\n"
                "    return True\n"
            )

        return ""


def test_workflow_runs_in_offline_mode_and_returns_shape():
    agent = BugHoundAgent(client=None)  # heuristic-only
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)

    assert isinstance(result, dict)
    assert "issues" in result
    assert "fixed_code" in result
    assert "risk" in result
    assert "logs" in result

    assert isinstance(result["issues"], list)
    assert isinstance(result["fixed_code"], str)
    assert isinstance(result["risk"], dict)
    assert isinstance(result["logs"], list)
    assert len(result["logs"]) > 0


def test_offline_mode_detects_print_issue():
    agent = BugHoundAgent(client=None)
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)

    assert any(issue.get("type") == "Code Quality" for issue in result["issues"])


def test_offline_mode_proposes_logging_fix_for_print():
    agent = BugHoundAgent(client=None)
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)

    fixed = result["fixed_code"]
    assert "logging" in fixed
    assert "logging.info(" in fixed


def test_mock_client_forces_llm_fallback_to_heuristics_for_analysis():
    # MockClient returns non-JSON for analyzer prompts, so agent should fall back.
    agent = BugHoundAgent(client=MockClient())
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)

    assert any(issue.get("type") == "Code Quality" for issue in result["issues"])
    # Ensure we logged the fallback path
    assert any("Falling back to heuristics" in entry.get("message", "") for entry in result["logs"])


def test_overedited_fix_triggers_guardrail_and_blocks_autofix():
    agent = BugHoundAgent(client=OverEditMockClient())
    code = "def f():\n    print('hi')\n    return True\n"

    result = agent.run(code)
    risk = result["risk"]

    assert any(
        "Large structural divergence between original and fixed code." in reason
        for reason in risk.get("reasons", [])
    )
    assert risk["should_autofix"] is False
