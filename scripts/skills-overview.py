#!/usr/bin/env python3
"""Emit assets/skills-overview.svg – the README overview figure.

One file serves two roles: GitHub's README renders it through <img> (static,
dark-mode aware via prefers-color-scheme); opened directly from raw GitHub
(image/svg+xml, inline styles allowed, scripts blocked) the CSS-only
hover/focus hotspots show each skill's purpose in the bottom panel.

Rerun after a skill is added, renamed, or removed – the layout is computed,
the inventory and the one-line purposes are the tables below.
"""
from pathlib import Path

W = 1160
BX, BW = 24, W - 48          # band x / width
BR = BX + BW                 # band right edge
LX = BX + 22                 # flow start inside a band
BH = 44                      # step box height
PANEL_H = 86
SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

out = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, cls="t1", size=13, anchor="start", family=SANS, weight=None, spacing=None):
    a = [f'x="{x:.0f}"', f'y="{y:.0f}"', f'class="{cls}"', f'font-size="{size}"', f'font-family="{family}"']
    if anchor != "start":
        a.append(f'text-anchor="{anchor}"')
    if weight:
        a.append(f'font-weight="{weight}"')
    if spacing:
        a.append(f'letter-spacing="{spacing}"')
    out.append(f'<text {" ".join(a)}>{esc(s)}</text>')


def band(x, y, w, h, cls, kicker, title, sub):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" class="{cls}"/>')
    text(x + 22, y + 26, kicker, "kick", 10, family=MONO, spacing="0.12em")
    text(x + 22, y + 50, title, "t1", 16, weight="600")
    for i, ln in enumerate(sub if isinstance(sub, list) else [sub]):
        text(x + 22, y + 69 + i * 15, ln, "t2", 11.5)


def arrow(x1, y1, x2, y2):
    out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" class="arrow" marker-end="url(#ah)"/>')


def link(x1, y1, x2, y2):
    out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" class="link" stroke-dasharray="4,4"/>')
    out.append(f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="3.5" class="dot"/><circle cx="{x2:.0f}" cy="{y2:.0f}" r="3.5" class="dot"/>')


def detail(kicker, lines):
    out.append('<g class="d">')
    out.append(f'<rect x="{BX}" y="{PANEL_Y}" width="{BW}" height="{PANEL_H}" rx="14" class="panel"/>')
    text(BX + 22, PANEL_Y + 26, kicker, "dk", 10.5, family=MONO, spacing="0.12em")
    for i, ln in enumerate(lines if isinstance(lines, list) else [lines]):
        text(BX + 22, PANEL_Y + 48 + i * 18, ln, "db", 13.5)
    out.append('</g>')


def hot(key, x, y, w, h, label, cls, kicker, body, sub=None, size=13, rx=9):
    """A hotspot: box + label, plus a detail block drawn in the bottom panel."""
    out.append(f'<g class="hot" tabindex="0" data-hotspot="{key}">')
    out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" class="{cls}"/>')
    ly = y + h / 2 + size * 0.36 - (7 if sub else 0)
    text(x + w / 2, ly, label, cls + "-t", size, anchor="middle", family=MONO, weight="600")
    if sub:
        text(x + w / 2, ly + 15, sub, cls + "-s", 10.5, anchor="middle")
    detail(kicker, body)
    out.append('</g>')


class Flow:
    """Left-to-right cursor for a row of boxes and arrows."""
    def __init__(self, x, y, h=BH):
        self.x, self.y, self.h = x, y, h

    def box(self, w, **kw):
        hot(x=self.x, y=self.y, w=w, h=self.h, **kw)
        self.x += w
        return self.x - w / 2

    def stack(self, w, items):
        """Two stacked dashed boxes occupying one step slot – the design stage."""
        h = (self.h - 6) / 2
        for i, kw in enumerate(items):
            hot(x=self.x, y=self.y + i * (h + 6), w=w, h=h, cls="pre", size=10.5, rx=5, **kw)
        self.x += w
        return self.x - w / 2

    def arrow(self, gap=18):
        arrow(self.x + 6, self.y + self.h / 2, self.x + gap, self.y + self.h / 2)
        self.x += gap + 6

    def pr(self):
        out.append(f'<rect x="{self.x}" y="{self.y + 7}" width="56" height="{self.h - 14}" rx="15" class="pill"/>')
        text(self.x + 28, self.y + self.h / 2 + 4, "PR", "pill-t", 12, anchor="middle", family=MONO, weight="600")
        self.x += 56


# ---------------------------------------------------------------- document
H = 876
PANEL_Y = H - PANEL_H - 22

out.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="ttl" font-family="{SANS}">')
out.append('<title id="ttl">AndThen skills and workflow – the one workflow, the design stage, the artifacts they exchange, the standalone skills, and the delegation roles</title>')
out.append('''<style>
.bg{fill:#FBF8F3}
.t1{fill:#1A140E}.t2{fill:#5E564C}.t3{fill:#8A8075}
.kick{fill:#2C5738}
.band-flow{fill:#F2F6F3;stroke:#B9D0BD;stroke-width:1.5}
.band-art{fill:#FFFFFF;stroke:#D4C9B3;stroke-width:1.5;stroke-dasharray:6,5}
.band-core{fill:#FFFFFF;stroke:#B9D0BD;stroke-width:1.5}
.band-roles{fill:#F5F0E7;stroke:#D4C9B3;stroke-width:1.5}
.step{fill:#21452C}.step-t{fill:#FBF8F3}.step-s{fill:#B9D0BD}
.exec{fill:#11251A}.exec-t{fill:#FBF8F3}.exec-s{fill:#8DB294}
.tail{fill:#3E6E48}.tail-t{fill:#FBF8F3}.tail-s{fill:#DFEAE1}
.pre{fill:#FFFFFF;stroke:#8DB294;stroke-width:1.5;stroke-dasharray:5,4}.pre-t{fill:#21452C}.pre-s{fill:#5E564C}
.core{fill:#FBF8F3;stroke:#8DB294;stroke-width:1.5}.core-t{fill:#21452C}
.role{fill:#E9E1D2}.role-t{fill:#1A140E}.role-s{fill:#5E564C}
.pill{fill:none;stroke:#5E564C;stroke-width:1.5}.pill-t{fill:#5E564C}
.card{fill:#FBF8F3;stroke:#D4C9B3;stroke-width:1.5}.card-t{fill:#1A140E}.card-s{fill:#5E564C}.fold{fill:#E9E1D2}
.arrow{stroke:#5E564C;stroke-width:1.8;fill:none}.ah{fill:#5E564C}
.link{stroke:#8A8075;stroke-width:1.3}.dot{fill:#8A8075}
.panel{fill:#11251A}.dk{fill:#E29A63}.db{fill:#FBF8F3}.dh{fill:#8DB294}
.hot{cursor:pointer}.hot:focus{outline:none}
.hot:hover>rect,.hot:focus>rect{stroke:#C46326;stroke-width:2.5;stroke-dasharray:none}
.d{display:none;pointer-events:none}.hot:hover .d,.hot:focus .d{display:block}
:root:has(.hot:hover) .hot:focus:not(:hover) .d{display:none}
@media (prefers-color-scheme:dark){
.bg{fill:#0F1A13}
.t1{fill:#FBF8F3}.t2{fill:#C9C0B2}.t3{fill:#8A8075}
.kick{fill:#8DB294}
.band-flow{fill:#172A1D;stroke:#2C5738}
.band-art{fill:#131C16;stroke:#3D362E}
.band-core{fill:#142218;stroke:#2C5738}
.band-roles{fill:#1C1A15;stroke:#3D362E}
.step{fill:#3E6E48}.step-s{fill:#DFEAE1}
.exec{fill:#2C5738}.exec-s{fill:#B9D0BD}
.tail{fill:#5F8E69}
.pre{fill:#142218;stroke:#5F8E69}.pre-t{fill:#DFEAE1}.pre-s{fill:#C9C0B2}
.core{fill:#1B2A1F;stroke:#3E6E48}.core-t{fill:#DFEAE1}
.role{fill:#3D362E}.role-t{fill:#F5F0E7}.role-s{fill:#C9C0B2}
.pill{stroke:#C9C0B2}.pill-t{fill:#C9C0B2}
.card{fill:#1A211C;stroke:#3D362E}.card-t{fill:#FBF8F3}.card-s{fill:#C9C0B2}.fold{fill:#3D362E}
.arrow{stroke:#C9C0B2}.ah{fill:#C9C0B2}
.panel{fill:#21452C}
.hot:hover>rect,.hot:focus>rect{stroke:#E29A63}
}
</style>''')
out.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>')
out.append(f'<rect width="{W}" height="{H}" class="bg"/>')

text(BX, 40, "AndThen skills and workflow", "t1", 26, weight="700")
text(BX, 62, "Spec-driven development for AI coding agents – one workflow, the artifacts it exchanges, standalone skills on call", "t2", 13)

# panel hint – drawn before the hotspots so their detail blocks overlay it
out.append(f'<rect x="{BX}" y="{PANEL_Y}" width="{BW}" height="{PANEL_H}" rx="14" class="panel"/>')
text(BX + 22, PANEL_Y + 26, "SKILL DETAILS", "dk", 10.5, family=MONO, spacing="0.12em")
text(BX + 22, PANEL_Y + 50, "Hover a skill, artifact, or role to read what it does; click to keep it in view.", "db", 13.5)
text(BX + 22, PANEL_Y + 70, "Inside the README this image is static – click it to open the interactive version.", "dh", 12.5)

# ------------------------------------------------ the workflow
y = 84
band(BX, y, BW, 218, "band-flow", "THE WORKFLOW", "Idea to merged, one chain",
     ["Every step reads what the step before it wrote, and each authoring step closes on the next command – printed, never worked out.",
      "The design stage between clarify and plan is optional: clarify recommends a trade-off for a fork the PRD leaves open, and UI design where a screen has none."])
f = Flow(LX, y + 100)
FLOW_Y = f.y
CLARIFY_X = f.box(110, key="clarify", label="clarify", cls="pre", size=12, rx=7, sub="unless a PRD exists",
                  kicker="andthen · clarify",
                  body=["The requirements skill: Discovery & Ideation over an idea, a file or a tracker item – gaps, edge cases, scope boundaries, alternatives.",
                        "Writes prd.md, or PRODUCT.md at product scope, after at least one round of answered questions; --auto synthesises and records the assumptions."])
f.arrow()
DESIGN_X = f.stack(136, [
    dict(key="architecture", label="architecture", kicker="andthen · architecture",
         body=["--mode trade-off settles an ADR from weighted options; advise gives design guidance grounded in CUPID / DDD.",
               "review, decompose, fitness, strategic-design and event-storming run the deep analysis, singly or chained. No code changes."]),
    dict(key="ui-ux-design", label="ui-ux-design", kicker="andthen · ui-ux-design",
         body=["UX research, design systems, and wireframes – singly or chained. Validating the built UI is visual-validation."]),
])
f.arrow()
PLAN_X = f.box(126, key="plan", label="plan", cls="step", sub="prd.md · file · issue",
               kicker="andthen · plan",
               body=["The entry for PRD-backed work: plan.json plus a FIS per story, from a prd.md, a requirements file, or a tracker item.",
                     "One cross-cutting review over the bundle, one preflight, then Closure: READY and the exec-plan line. One story is a normal outcome."])
f.arrow()
f.box(140, key="exec-plan", label="exec-plan", cls="exec", sub="one exec-spec per story",
      kicker="andthen · exec-plan",
      body=["Run a plan bundle: admit every schedulable FIS, one fresh exec-spec subagent per ready story, then the full tier on the final tree.",
            "Ends on a Next: line – one paste, the plan-level review with --fix – for a fresh session. exec-spec is yours to run per story by hand too."])
f.arrow()
f.box(234, key="review", label="review", cls="tail", sub="--mode code,gap,security,outcome --fix",
      kicker="andthen · review",
      body=["Proof-led code / gap / security / outcome review and PR review; a story's own review is one --quick pass. Proves coverage",
            "before the verdict and routes findings into Fix / Note; --fix hands the Fix set to implement-fix. Runs on any diff."])
f.arrow()
f.box(126, key="implement-fix", label="implement-fix", cls="tail", size=12,
      kicker="andthen · implement-fix",
      body=["Apply a report's Fix-routed findings – what review --fix runs on its own report – or a sentence-sized request of your",
            "own, as minimal changes across code, specs, plans, and docs, then re-verify once and annotate. No re-review."])
f.arrow()
f.pr()
assert f.x <= BR - 14, f.x

# the quick track – same band, clear of the artifact links below the main row
QT_X, QT_Y = 790, 254
text(QT_X, QT_Y - 9, "QUICK TRACK · one story, no PRD", "t3", 10, family=MONO, spacing="0.08em")
q = Flow(QT_X, QT_Y, h=34)
SPEC_X = q.box(92, key="spec", label="spec", cls="step", size=12, rx=7,
               kicker="andthen · spec",
               body=["One FIS from a description, a file or an issue URL, with its one-story plan.json beside it – prd: null, the request is the record.",
                     "Also authors one story of a plan under plan --batch. Self-review, preflight, then Closure: READY and the exec-spec line."])
q.arrow()
q.box(116, key="exec-spec", label="exec-spec", cls="exec", size=12, rx=7,
      kicker="andthen · exec-spec",
      body=["Implement one FIS where it is invoked: the tasks, the story's proofs and the full tier, one fresh reviewer subagent, then the fixes.",
            "Completes by recording the verified line it saw executed. The same per-story unit exec-plan spawns – run it yourself to watch a single story."])
q.arrow()
q.pr()
assert q.x <= BR - 14, q.x

# ------------------------------------------------ artifacts
y = 318
band(BX, y, BW, 112, "band-art", "ARTIFACTS", "The hand-offs",
     ["Branch-scoped until", "the merge"])
CX0 = 224
CW, CH = 196, 74
CG = (BR - 22 - CX0 - 4 * CW) / 3
cards = [("intent", "a short source", ["from anywhere, or clarify --brief:", "a note, an issue, intent.md"],
          "artifact · a short source · optional",
          ["Written by hand – a pasted note, a tracker issue, a sentence, the five-section intent.md – or by clarify --brief; read by clarify,",
           "now-what and architecture. The next clarify run folds its substance into prd.md – nothing cites it by path afterwards."]),
         ("prd", "prd.md", ["what and why, agreed;", "the surviving product record"],
          "artifact · prd.md · durable",
          ["Written by clarify; read by plan and review --mode gap. The governing artifact, and the one that outlives the branch:",
           "plan.json and the FIS files are branch-scoped – delete them before the merge; prd.md stays."]),
         ("planjson", "plan.json", ["story inventory, dependencies,", "status, one FIS pointer per story"],
          "artifact · plan.json · branch-scoped",
          ["Written by plan, or by spec for the one-story plan, and by the run session alone at runtime; read by exec-plan, exec-spec, review, now-what and tracker.",
           "a story reaches done only together with the verified line quoting what ran. Its prd field is the in-repo source, or null for a tracker item."]),
         ("fis", "FIS", ["intent, scenarios with Proof", "bindings, scope boundaries, tasks"],
          "artifact · Feature Implementation Specification · branch-scoped",
          ["One per story, authored by spec – standalone on the quick track, one subagent per story under plan; read by exec-spec and review.",
           "scenarios with runnable Proof bindings, what we are not doing, and tasks naming what they SATISFY and how to Verify."])]
card = {}
for i, (key, title, desc, kick, body) in enumerate(cards):
    cx = CX0 + i * (CW + CG)
    cy = y + 20
    card[key] = (cx + CW / 2, cy, cy + CH)
    out.append(f'<g class="hot" tabindex="0" data-hotspot="{key}">')
    out.append(f'<rect x="{cx:.0f}" y="{cy}" width="{CW}" height="{CH}" rx="8" class="card"/>')
    out.append(f'<path d="M{cx + CW - 18:.0f},{cy} L{cx + CW:.0f},{cy + 18} L{cx + CW - 18:.0f},{cy + 18} z" class="fold"/>')
    text(cx + 14, cy + 24, title, "card-t", 13, family=MONO, weight="700")
    for j, ln in enumerate(desc):
        text(cx + 14, cy + 44 + j * 15, ln, "card-s", 11)
    detail(kick, body)
    out.append('</g>')
assert CG >= 20, CG

# artifact links, once the box geometry is known
link(CLARIFY_X - 10, FLOW_Y + BH + 2, card["intent"][0], card["intent"][1] - 2)
link(CLARIFY_X + 10, FLOW_Y + BH + 2, card["prd"][0], card["prd"][1] - 2)
link(PLAN_X - 12, FLOW_Y + BH + 2, card["planjson"][0], card["planjson"][1] - 2)
link(PLAN_X + 12, FLOW_Y + BH + 2, card["fis"][0], card["fis"][1] - 2)
link(SPEC_X, QT_Y + 36, card["fis"][0], card["fis"][1] - 2)

# ------------------------------------------------ standalone skills
y = 446
SEC_H = 220
band(BX, y, BW, SEC_H, "band-core", "STANDALONE", "andthen – call any time", "No pipeline or setup required; 21 skills in all")
core = [("now-what", "First-stop router – inspects project state (init'd? greenfield? brownfield? mid-flow?) and routes to the right skill."),
        ("init", ["Set up the workflow structure: CLAUDE.md / AGENTS.md, the Project Document Index, the orientation docs,",
                  "the foundational rules guideline, and the four opt-in roles below."]),
        ("handoff", "Compact the conversation into a document a fresh session resumes from; durable fragments go to the plan and the Learnings document."),
        ("triage", ["Investigate, diagnose, and fix build failures, config errors, runtime bugs, regressions, test failures.",
                    "A reproducible bug gets a failing test before the fix. No spec, no plan state."]),
        ("testing", ["Test strategy (writes the Testing Strategy document), test authoring, TDD, and the Prove-It bugfix flow.",
                     "Suites at every level, E2E included."]),
        ("visual-validation", "Validate screenshots and built UI against wireframes, design specs, and baselines; visual regression checks."),
        ("describe", ["Describe what a project already is: --mode codebase maps it into docs, --mode domain extracts the Ubiquitous",
                      "Language; --model emits the typed architecture or domain model."]),
        ("tracker", ["Project a plan bundle into the issue tracker: publish creates the parent and one child issue per story,",
                     "and a re-run refreshes them from the plan's current state."]),
        ("backlog-triage", "Label, categorize, and route untriaged tracker items toward implementation or a human decision. Debugging a failure is the triage skill."),
        ("spike", "Answer one named design question by building a throwaway runnable spike, then report a verdict – evidence, not product."),
        ("simplify-code", "Behavior-preserving simplification: less complexity, less over-engineering, exact behavior kept."),
        ("skill-review", ["Review one skill bundle or prompt-like file against skill craft – trigger surface, conflicts, contracts, prose failure modes;",
                          "--fix tightens it with zero contract loss."])]
COLS = 7
ch, cg = 38, 10
cw = (BW - 44 - (COLS - 1) * cg) / COLS
cx, cy = BX + 22, y + 88
rows = (len(core) + COLS - 1) // COLS
for i, (key, body) in enumerate(core):
    hot(key, cx + (i % COLS) * (cw + cg), cy + (i // COLS) * (ch + cg), cw, ch,
        key, "core", f"andthen · {key}", body, size=12, rx=7)
FOOT_Y = cy + rows * (ch + cg) + 6
text(cx, FOOT_Y, "+ the 9 workflow skills above", "t3", 11.5)
assert FOOT_Y + 16 <= y + SEC_H, (FOOT_Y, SEC_H)

# ------------------------------------------------ roles
y = 446 + SEC_H + 16
band(BX, y, BW, 64, "band-roles", "ROLES", "", "")
text(BX + 22, y + 48, "Opt-in subagent tiers installed by init; each pins its model and effort.", "t2", 11.5)
roles = [("oracle", "top model · xhigh", ["Judgment work the user assigns it, and hard problems an agent hands over because they exceed its tier: a failure that",
                                          "survives a real fix, a design that will not close, a cause the material at hand cannot explain."]),
         ("implementer", "top model · high", ["One fully-specified unit of work: executing a story or spec, research that weighs or synthesises sources,",
                                              "authoring a FIS for a pinned plan story."]),
         ("reviewer", "top model · medium", ["One review pass over a pinned target – a diff, a document, a design, a claim. Effort sits below",
                                             "implementation on purpose: more review effort breeds scope creep, not findings."]),
         ("worker", "cheap model · medium", ["One small, well-specified, verifiable subtask: retrieval, scans, mechanical edits, fact lookups against a pinned",
                                             "question. Answers found, never made."])]
rw, rg = 150, 10
rx = BR - 22 - 4 * rw - 3 * rg
for i, (key, tier, body) in enumerate(roles):
    hot("role-" + key, rx + i * (rw + rg), y + 12, rw, 40, key, "role", f"role · {key} · {tier}", body, sub=tier, size=12, rx=20)
assert y + 64 + 16 <= PANEL_Y, (y, PANEL_Y)

out.append('</svg>')
target = Path(__file__).resolve().parents[1] / "assets" / "skills-overview.svg"
target.write_text("\n".join(out) + "\n")
print(f"wrote {target.relative_to(Path.cwd())} {target.stat().st_size} bytes")
