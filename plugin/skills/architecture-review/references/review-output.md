# Architecture Review Output Format & Severity

Standards for structuring architecture review findings.

## Finding Structure

Every finding must follow this format:

```
### ARCH-{NNN}: {Title}

**Severity**: CRITICAL | HIGH | MEDIUM | LOW | INFO
**Dimension**: modularity | coupling | cohesion | testability | deployability | security | governance
**C4 Level**: Context | Container | Component | Code
**Category**: Cycle | Coupling | Decomposition | Convention | Principle Violation

**Evidence**: {specific packages, files, metric values, import chains}

**Connascence** (if applicable): {type} — Strength: {N}, Degree: {N}, Locality: {N} -> Severity: {score}

**Impact**: {which quality attribute is affected and how}

**Recommendation**: {specific, actionable fix with rationale}

**Fitness Function**: {proposed automated check to prevent recurrence}

**Fix Prompt**: {copy-pasteable instruction for remediation}
```

---

## Severity Classification

| Severity | Meaning | CI Behavior | Examples |
|----------|---------|-------------|---------|
| **CRITICAL** | Blocks deployment independence or crosses security boundary | Break build | Dynamic connascence (CoI/CoV) across service boundary; circular dep in critical path |
| **HIGH** | Principle violation with measurable impact | Fail pipeline | SDP violation; cycle > 3 nodes; Zone of Pain with D > 0.7 |
| **MEDIUM** | Architectural drift or suboptimal structure | Warn | Zone of Pain with D 0.3-0.7; instability creep; god module emerging |
| **LOW** | Convention violation or minor structural issue | Info | Naming inconsistencies; orphan modules; mild abstraction deficit |
| **INFO** | Metrics outside recommended range by small margin | Log only | D slightly above 0.3; Ce approaching threshold |

---

## Report Structure

### 1. Executive Summary
3-5 sentences. Include:
- Overall health characterization (one sentence)
- Count of findings by severity
- Most critical issue (one sentence)
- Most impactful recommendation (one sentence)

Example:
> This codebase has a healthy layered structure with clear package boundaries, but the core utility package sits deep in the Zone of Pain (D=0.95). Found 2 CRITICAL, 3 HIGH, 5 MEDIUM findings. The most urgent issue is a 4-node dependency cycle between config, channel, task, and events packages. Extracting interfaces from the core package would resolve 4 of the 10 findings.

### 2. How to Read This Report

Add a compact reader legend before the detailed analysis. Keep it short and explain only terms actually used in the report.

Recommended contents:
- **Metric legend**: `Ca` = inbound dependents, `Ce` = outbound dependencies, `I` = instability (`0` stable, `1` volatile), `A` = abstractness, `D` = distance from the ideal "main sequence" (`0` best, `>0.3` worth attention). If graph-level metrics appear, define `CCD` (cumulative component dependency), `ACD` (average component dependency), and `NCCD` (normalized cumulative component dependency).
- **Finding-field legend**: if findings use `C4 Level`, explain the scale in one line: `Context` = system landscape, `Container` = deployable/runtime building blocks, `Component` = internal module/service slice, `Code` = file/class/function level.
- **Principle legend**: expand any package principles you use such as `ADP` (Acyclic Dependencies Principle), `SDP` (Stable Dependencies Principle), and `SAP` (Stable Abstractions Principle).
- **Zone legend**: explain labels like `Zone of Pain` and `Zone of Uselessness` in one line each when they appear.
- **Connascence legend**: if findings use `Co*` shorthand, explain the static progression `CoN`/`CoT`/`CoM`/`CoP`/`CoA` and the stronger dynamic forms `CoE`/`CoTm`/`CoV`/`CoI`; dynamic cross-boundary connascence is materially riskier.

Prefer one short paragraph plus a compact table or 4-6 bullets. Do not turn this into a tutorial.

### 3. Metrics Dashboard

Per-package table:

| Package | Ca | Ce | I | A | D | Zone | Notes |
|---------|----|----|---|---|---|------|-------|
| core | 14 | 2 | 0.13 | 0.02 | 0.85 | Pain | Concrete hotspot |
| models | 8 | 0 | 0.00 | 0.90 | 0.10 | OK | Pure abstractions |
| server | 0 | 12 | 1.00 | 0.05 | 0.05 | OK | Application leaf |
| storage | 3 | 4 | 0.57 | 0.30 | 0.13 | OK | Near main sequence |

Include graph-level metrics if available: CCD, ACD, NCCD.

### 4. Findings
Sorted by severity (CRITICAL first), then by dimension. Use the finding structure above for each.

### 5. Dependency Graph
Text description of the condensed DAG (SCCs collapsed). Note:
- Direction of all edges
- Which packages are leaves (I ~ 1)
- Which packages are foundations (I ~ 0)
- Any cycles (highlight in findings)

### 6. Decomposition Recommendations
If applicable — modules that should be split or merged, based on findings. Reference the specific findings that drive each recommendation.

### 7. Proposed Fitness Functions
The primary actionable output. For each:
- Name
- What it checks
- Threshold
- Governance stack level (1-4)
- Implementation (language-specific tooling)
- Which findings it addresses

---

## Actionability Requirements

These rules prevent vague, noisy output that erodes trust:

1. **Every finding needs specific evidence**: package names, metric values, file paths, import chains. Never "this module seems too large."
2. **Quantify impact**: "Ce=12" not "high coupling." "D=0.95" not "far from main sequence."
3. **Include fix_prompt**: A copy-pasteable instruction that could be given to an agent or developer to remediate the finding.
4. **Separate detection from explanation**: Detection is metric-based and objective. Explanation is contextual and qualitative. Label which is which.
5. **Avoid false positives**: If a metric is borderline, report as INFO with context, not as HIGH. Noisy reviews get ignored.
6. **Framework attribution**: Every recommendation cites the principle driving it. "Per SAP (Martin)..." not just "you should add interfaces."
7. **Optimize for an informed non-specialist reader**: define jargon in the report legend or on first use. Do not assume the reader already knows connascence, C4 shorthand, or package/graph metric abbreviations.
