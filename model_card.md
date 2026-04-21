# BugHound Mini Model Card (Reflection)

Fill this out after you run BugHound in **both** modes (Heuristic and Gemini).

---

## 1) What is this system?

**Name:** BugHound  
**Purpose:** Analyze a Python snippet, propose a fix, and run reliability checks before suggesting whether the fix should be auto-applied.

**Intended users:** Students learning agentic workflows and AI reliability concepts.

---

## 2) How does it work?

BugHound follows a five-step loop: **plan -> analyze -> act -> test -> reflect**.

- In **plan**, the agent initializes a scan-and-fix workflow and records trace logs.
- In **analyze**, BugHound detects issues either with:
  - **Heuristic mode** (offline): deterministic pattern checks such as `print(...)`, bare `except:`, and `TODO`.
  - **Gemini mode**: model-generated issue output that must be valid JSON and match the required schema (`type`, `severity`, `msg`). If output is malformed or API calls fail, analysis falls back to heuristics.
- In **act**, BugHound proposes code changes:
  - Heuristic fixer applies rule-based rewrites.
  - Gemini fixer returns rewritten code; if output is empty or errors occur, it falls back to the heuristic fixer.
- In **test**, BugHound runs explicit risk checks and computes `score`, `level`, `reasons`, and `should_autofix`.
- In **reflect**, auto-fix is allowed only when risk is low; otherwise human review is recommended.

---

## 3) Inputs and outputs

**Inputs:**

- What kind of code snippets did you try?
- What was the “shape” of the input (short scripts, functions, try/except blocks, etc.)?

**Outputs:**

- What types of issues were detected?
- What kinds of fixes were proposed?
- What did the risk report show?

---

## 4) Reliability and safety rules

### Rule 1: Return statement count divergence
- **What it checks:** whether the number of `return` statements changes between original and fixed code.
- **Why it matters:** return-count changes are a practical signal of possible control-flow or behavior drift.
- **Potential false positive:** a safe refactor can add or remove returns while preserving behavior (for example, early-return style cleanup).
- **Potential false negative:** behavior can still change without changing return count (for example, altered conditions or returned expressions).

### Rule 2: Large structural divergence by line ratio
- **What it checks:** whether fixed code is much shorter or longer than original code (large line-ratio divergence).
- **Why it matters:** large size shifts can indicate over-editing or generation drift beyond intended minimal changes.
- **Potential false positive:** legitimate fixes can require added validation/logging and therefore increase code size.
- **Potential false negative:** harmful edits can remain similar in length and bypass this signal.

---

## 5) Observed failure modes

Provide at least **two** examples:

1. A time BugHound missed an issue it should have caught  
2. A time BugHound suggested a fix that felt risky, wrong, or unnecessary  

For each, include the snippet (or describe it) and what went wrong.

---

## 6) Heuristic vs Gemini comparison

Compare behavior across the two modes:

- What did Gemini detect that heuristics did not?
- What did heuristics catch consistently?
- How did the proposed fixes differ?
- Did the risk scorer agree with your intuition?

---

## 7) Human-in-the-loop decision

BugHound already includes several human-in-the-loop triggers that refuse auto-fix or increase review requirements:

- **Risk gate trigger:** if risk is not `low`, `should_autofix` is false and human review is recommended.
- **Over-edit trigger:** large structural divergence between original and fixed code increases risk and can block auto-fix.
- **Control-flow trigger:** return-count divergence increases risk and can block auto-fix.
- **No-fix trigger:** if no fix is produced, risk is set high and auto-fix is blocked.
- **LLM reliability trigger:** if Gemini analyzer output is malformed or schema-invalid, analysis falls back to heuristics instead of trusting unreliable output.
- **API failure trigger:** on API errors, BugHound falls back to heuristic analysis/fixing paths.

These triggers provide layered safeguards: malformed model output is rejected early, risky edits are scored conservatively, and non-low-risk outcomes require human judgment.

---

## 8) Improvement idea

Propose one improvement that would make BugHound more reliable *without* making it dramatically more complex.

Examples:

- A better output format and parsing strategy
- A new guardrail rule + test
- A more careful “minimal diff” policy
- Better detection of changes that alter behavior

Write your idea clearly and briefly.
