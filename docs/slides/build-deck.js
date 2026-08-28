const pptxgen = require("C:/Users/mrtra/AppData/Local/Temp/opencode/svgconv/node_modules/pptxgenjs");
const pptx = new pptxgen();

pptx.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pptx.author = "Agentic SDLC";
pptx.title = "Agentic SDLC — An experience-driven AI-SDLC framework for the Claude Code harness";

// ---------- palette ----------
const NAVY = "1E2761", ICE = "EAF0FB", MID = "5A6B9E", AMBER = "F4B400", AMBERD = "B98A00";
const GREEN = "2E7D32", GREEND = "1B5E20", TXT = "1F2937", MUT = "6B7280", WHITE = "FFFFFF";
const CARD = "F8FAFC", BORDER = "D1D5DB", RED = "C0392B";

const H = "Cambria", B = "Calibri";
const W = 13.333, HGT = 7.5;

// ---------- helpers ----------
function eyebrow(s, text, color) {
  s.addText(text.toUpperCase(), { x: 0.55, y: 0.28, w: 12, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: color || AMBERD, charSpacing: 2 });
}
function title(s, text, sub) {
  s.addText(text, { x: 0.55, y: 0.6, w: 12.2, h: 0.85, fontFace: H, fontSize: 33, bold: true, color: NAVY });
  if (sub) s.addText(sub, { x: 0.55, y: 1.42, w: 12.2, h: 0.5, fontFace: B, fontSize: 15, color: MUT });
}
function pill(s, x, y, text, color) {
  s.addShape("roundRect", { x, y, w: text.length * 0.078 + 0.24, h: 0.26, rectRadius: 0.13, fill: { color }, line: { color, width: 0 } });
  s.addText(text.toUpperCase(), { x, y: y - 0.015, w: text.length * 0.078 + 0.24, h: 0.26, fontFace: B, fontSize: 8.5, bold: true, color: WHITE, align: "center", margin: 0 });
}
function tag(s, x, y, label) {
  // evidence-grade pill: VERIFIED / CASE STUDY / RATIONALE / PLANNED
  const map = { VERIFIED: GREEN, "CASE STUDY": AMBERD, RATIONALE: MID, PLANNED: "7C8698" };
  pill(s, x, y, label, map[label] || "7C8698");
}
function card(s, x, y, w, h, fill, line) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.09, fill: { color: fill || CARD }, line: { color: line || BORDER, width: 1 } });
}
function chip(s, x, y, n, color) {
  s.addShape("ellipse", { x, y, w: 0.34, h: 0.34, fill: { color }, line: { color, width: 0 } });
  s.addText(String(n), { x, y: y - 0.02, w: 0.34, h: 0.34, fontFace: B, fontSize: 13, bold: true, color: WHITE, align: "center", margin: 0 });
}
function bullets(s, x, y, w, h, items, size, color) {
  s.addText(items.map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } })),
    { x, y, w, h, fontFace: B, fontSize: size || 13.5, color: color || TXT, valign: "top" });
}
function notes(s, t) { s.addNotes(t); }

// ================= SLIDE 1 — TITLE (dark) =================
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x: 10.2, y: -2.2, w: 5.6, h: 5.6, fill: { color: "27346E" }, line: { width: 0 } });
  s.addShape("ellipse", { x: 11.6, y: -0.6, w: 3.4, h: 3.4, fill: { color: "2C3B7C" }, line: { width: 0 } });
  s.addText("CLAUDE CODE HARNESS  \u00B7  PLUGIN MARKETPLACE  \u00B7  v2.8.0", { x: 0.8, y: 1.0, w: 11, h: 0.3, fontFace: B, fontSize: 12, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("Agentic SDLC", { x: 0.8, y: 1.55, w: 11.7, h: 1.6, fontFace: H, fontSize: 66, bold: true, color: WHITE });
  s.addText("An experience-driven AI-SDLC framework for the Claude Code harness", { x: 0.8, y: 3.15, w: 11.7, h: 0.6, fontFace: B, fontSize: 22, color: ICE });
  s.addText("Spec-first planning  \u00B7  Test-first implementation  \u00B7  Evidence-gated delivery", { x: 0.8, y: 3.85, w: 11.7, h: 0.4, fontFace: B, fontSize: 14, color: "9FB0DC" });
  s.addText("4 agents  \u00B7  16 workflow skills  \u00B7  4 plugin commands  \u00B7  per-project isolation  \u00B7  zero global installs", { x: 0.8, y: 5.9, w: 11.7, h: 0.35, fontFace: B, fontSize: 12.5, color: ICE });
  s.addText("github.com/trac41799/claude-code-agentic-sdlc", { x: 0.8, y: 6.35, w: 11.7, h: 0.35, fontFace: B, fontSize: 12, color: "9FB0DC" });
  notes(s, "Positioning: this is not a research report claiming control groups we don't have. It is an experience-driven framework presented with report discipline: every claim carries an evidence grade. For a young-senior engineering audience: lead with trade-offs and honest gaps.");
}

// ================= SLIDE 2 — HOW TO READ THIS DECK =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Evidence & framing");
  title(s, "How to read this deck", "Every claim is graded. Nothing is asserted without a grade.");
  const rows = [
    ["VERIFIED", GREEN, "Reproduced in this repo's CI or by local runs on this machine (e.g. doctor.sh, plugin install, plan-protocol test suite, E2E adopt run)."],
    ["CASE STUDY", AMBERD, "Observed in real engagements. Labeled with its confounds — small n, uncontrolled model mix, no cost tracking. Treated as signal, not proof."],
    ["RATIONALE", MID, "A design decision and the reason we made it. You may disagree; the reason is stated so the disagreement is about substance."],
    ["PLANNED", "7C8698", "A protocol that exists on paper and will be run (benchmark + token baseline). Not yet evidence."],
  ];
  let y = 1.95;
  rows.forEach(([lbl, c, desc]) => {
    card(s, 0.75, y, 11.8, 1.02, CARD, BORDER);
    pill(s, 1.0, y + 0.36, lbl, c);
    s.addText(desc, { x: 2.55, y: y + 0.13, w: 9.75, h: 0.8, fontFace: B, fontSize: 13.5, color: TXT, valign: "middle" });
    y += 1.16;
  });
  s.addText("Framing choice: expertise over process, delivered with academic-report discipline. The framework encodes judgment (where to gate, what to verify); the process is the servant, not the master.", { x: 0.75, y: 6.6, w: 11.8, h: 0.45, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "Explain the grading legend live. The honest bit: two case studies exist, both confounded; benchmark is planned, not run. That honesty is the credibility engine for this audience.");
}

// ================= SLIDE 3 — MOTIVATION =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Motivation");
  title(s, "Why a team-shaped framework instead of a better copilot");
  const cards = [
    ["Context loss", "Each session starts cold. Requirements, decisions and rationale live in chat history, inboxes and someone's head \u2014 not in the repo.", "The pain"],
    ["Handoff tax", "Spec \u2192 design \u2192 code \u2192 test \u2192 deploy is an information pipeline. Every handoff loses fidelity. Human SDLC spends most of its energy on re-discovery.", "The cost"],
    ["Agents change the unit", "An LLM agent can act \u2014 write, run, test, commit, open a PR. The bottleneck stops being 'can it code' and becomes 'does it know what to build, and is it kept honest'.", "The shift"],
  ];
  let x = 0.75;
  cards.forEach(([t, d, role], i) => {
    card(s, x, 2.15, 3.72, 3.1, CARD, BORDER);
    chip(s, x + 0.28, 2.45, i + 1, NAVY);
    s.addText(t, { x: x + 0.28, y: 2.95, w: 3.2, h: 0.45, fontFace: H, fontSize: 20, bold: true, color: NAVY });
    s.addText(d, { x: x + 0.28, y: 3.5, w: 3.2, h: 1.55, fontFace: B, fontSize: 12.5, color: TXT });
    s.addText(role.toUpperCase(), { x: x + 0.28, y: 5.05, w: 3.2, h: 0.3, fontFace: B, fontSize: 10, bold: true, color: AMBERD, charSpacing: 1 });
    x += 3.94;
  });
  s.addText("Conclusion we acted on: if agents can do the work, the product becomes the process around them \u2014 the team, its rules, and the loop they run in.", { x: 0.75, y: 5.6, w: 11.8, h: 0.75, fontFace: H, fontSize: 18, bold: true, color: NAVY });
  tag(s, 0.75, 6.75, "RATIONALE");
  notes(s, "The 'agents change the unit' point is the load-bearing idea: process engineering, not prompt engineering.");
}

// ================= SLIDE 4 — MY UNDERSTANDING OF SDLC AT THE TIME =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Baseline");
  title(s, "SDLC as I understood it", "A linear pipeline, leaking information at every handoff.");
  const stages = ["Requirements", "Design", "Implement", "Test", "Deploy", "Maintain"];
  let x = 0.75;
  stages.forEach((st, i) => {
    card(s, x, 2.2, 1.85, 1.15, ICE, MID);
    s.addText(st, { x, y: 2.48, w: 1.85, h: 0.6, fontFace: B, fontSize: 15, bold: true, color: NAVY, align: "center", margin: 0 });
    if (i < stages.length - 1) s.addText("\u2192", { x: x + 1.82, y: 2.45, w: 0.35, h: 0.6, fontFace: B, fontSize: 18, bold: true, color: AMBERD, align: "center", margin: 0 });
    x += 2.03;
  });
  const fails = [
    ["Documentation drift", "What was decided lives outside the repo; the repo is the only honest record and it is rarely updated."],
    ["Definition-of-done gap", "'Done' means 'looks finished'. Nothing verifies it against a spec or a test."],
    ["Review bottleneck", "One human reviews everything \u2014 the constraint that makes delivery linear, not parallel."],
    ["Re-discovery", "By the time work starts, the context that justified the design has been half-forgotten."],
  ];
  let y = 3.8;
  fails.forEach(([t, d]) => {
    card(s, 0.75, y, 11.8, 0.72, CARD, BORDER);
    s.addText(t, { x: 1.05, y: y + 0.12, w: 2.9, h: 0.5, fontFace: B, fontSize: 13.5, bold: true, color: NAVY });
    s.addText(d, { x: 4.05, y: y + 0.12, w: 8.3, h: 0.5, fontFace: B, fontSize: 12.5, color: TXT });
    y += 0.74;
  });
  s.addText("The mental model that shaped the design: an SDLC is an information pipeline. Fix the pipeline, not the prompt.", { x: 0.75, y: 6.8, w: 11.8, h: 0.35, fontFace: H, fontSize: 15.5, italic: true, bold: true, color: GREEND });
  notes(s, "Honest about my starting model: linear, handoff-heavy. The framework is my correction to that model, not a claim that the model was wrong for everyone.");
}

// ================= SLIDE 5 — THE DEMAND =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Demand");
  title(s, "What the market asked for", "Non-technical founders shipping real products \u2014 with one engineer of support.");
  const d1 = [
    ["Who", "Non-technical founders ('vibecoding' as a delivery mode), guided by one senior engineer."],
    ["What", "A complete working POC in days, not months \u2014 with a quality floor that survives handoff to real users."],
    ["How", "One machine, one Claude Code install, one framework. No infrastructure project, no consulting staff-up."],
    ["Guarded by", "The operator stays the decision-maker: specs, plans, merges. The agent team proposes; the human disposes."],
  ];
  let y = 2.1;
  d1.forEach(([t, d]) => {
    card(s, 0.75, y, 5.9, 0.95, CARD, BORDER);
    s.addText(t, { x: 1.0, y: y + 0.1, w: 1.6, h: 0.7, fontFace: B, fontSize: 13, bold: true, color: NAVY });
    s.addText(d, { x: 2.7, y: y + 0.08, w: 3.85, h: 0.85, fontFace: B, fontSize: 11.5, color: TXT });
    y += 1.1;
  });
  s.addText("Hard constraints we imposed on ourselves", { x: 7.0, y: 2.1, w: 5.6, h: 0.4, fontFace: H, fontSize: 18, bold: true, color: NAVY });
  const c2 = [
    "Nothing installs globally \u2014 zero writes to ~/.claude from the shipped payload (CI-enforced).",
    "No hooks, no telemetry, no background behavior in the product plugin.",
    "Per-project teams: agents + skills live in the project's own .claude/.",
    "All changes land via PR; nobody merges their own work; the developer never starts without an approved plan.",
    "The operator's existing code and history are never rewritten by adoption.",
  ];
  bullets(s, 7.0, 2.62, 5.6, 3.4, c2, 12.5);
  tag(s, 7.0, 6.1, "CASE STUDY");
  s.addText("Two live deployments back these constraints \u2014 slide 15. Both shipped a POC in one week.", { x: 7.0, y: 6.45, w: 5.6, h: 0.55, fontFace: B, fontSize: 12, italic: true, color: MUT });
  notes(s, "The constraints were learned the hard way (v1 installed globally and drifted). v2 is the correction.");
}

// ================= SLIDE 6 — ARCHITECTURE =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Attempted design");
  title(s, "Architecture: one repo, three layers", "The marketplace repo is the canonical source of everything a project needs.");
  // Layer 1
  card(s, 0.75, 2.05, 11.85, 1.35, NAVY, NAVY);
  s.addText("1 \u00B7 MARKETPLACE REPO = CANONICAL", { x: 1.05, y: 2.2, w: 11, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: AMBER, charSpacing: 1 });
  s.addText("claude plugin marketplace add trac41799/claude-code-agentic-sdlc \u2192 plugin ships 4 commands", { x: 1.05, y: 2.55, w: 11.2, h: 0.3, fontFace: B, fontSize: 13, color: WHITE });
  s.addText("/asdlc-project  \u00B7  /asdlc-adopt  \u00B7  /asdlc-doctor  \u00B7  /asdlc-memory-cleanup \u2014 plus agent definitions, skills, rules, scaffold template", { x: 1.05, y: 2.9, w: 11.2, h: 0.35, fontFace: B, fontSize: 12, color: ICE });
  // Layer 2
  card(s, 0.75, 3.65, 11.85, 1.35, ICE, MID);
  s.addText("2 \u00B7 PER-PROJECT TEAM (installed into the project's .claude/)", { x: 1.05, y: 3.8, w: 11, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: NAVY, charSpacing: 1 });
  s.addText("4 agents \u2014 product-manager \u00B7 developer \u00B7 qa \u00B7 devops  \u2014  16 workflow skills  \u00B7  engineering rules  \u00B7  delegation block in CLAUDE.md", { x: 1.05, y: 4.15, w: 11.2, h: 0.3, fontFace: B, fontSize: 13, color: TXT });
  s.addText("Active only inside this project. Never global. Fresh clones get the team via /asdlc-adopt.", { x: 1.05, y: 4.5, w: 11.2, h: 0.3, fontFace: B, fontSize: 12, color: MID });
  // Layer 3
  card(s, 0.75, 5.25, 11.85, 1.35, "F4F9F5", GREEN);
  s.addText("3 \u00B7 CANONICAL SCAFFOLD (templates/project-scaffold/)", { x: 1.05, y: 5.4, w: 11, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: GREEND, charSpacing: 1 });
  s.addText("Next.js + Tailwind + shadcn/ui \u00B7 Supabase (db, auth, storage) \u00B7 Vercel deploy \u00B7 docs/ product + engineering layout \u00B7 FOLDER-STRUCTURE.md as the authoritative spec", { x: 1.05, y: 5.75, w: 11.2, h: 0.3, fontFace: B, fontSize: 13, color: TXT });
  s.addText("The scaffold is a product decision: every project starts with the same quality floor.", { x: 1.05, y: 6.1, w: 11.2, h: 0.3, fontFace: B, fontSize: 12, color: GREEND });
  tag(s, 0.75, 6.7, "VERIFIED");
  s.addText("CI enforces: manifests parse, versions in lockstep, 4 agents / 16 skills, no global-install writes, frontmatter name == directory.", { x: 2.35, y: 6.73, w: 10.2, h: 0.35, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "Three layers: distribution (marketplace), runtime (per-project team), product (scaffold). Each is small on purpose.");
}

// ================= SLIDE 7 — RATIONALE =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Attempted design");
  title(s, "Why the architecture looks like this", "Each decision names the failure it prevents.");
  const rows = [
    ["Nothing installs globally", "Machine drift killed v1: stale copies, shadow skills, 'works on my laptop'. v2 payload is CI-blocked from any write into ~/.claude.", "VERIFIED"],
    ["Thin agents, skills do the work", "Agent .md files stay under ~4KB; workflow detail lives in skills loaded on demand. Keeps every session's context budget spend deliberate.", "RATIONALE"],
    ["Plan-protocol engine", "A dependency-free plan registry + blast-radius guard + pre-push hook stops undeclared mega-PRs. Runtime-agnostic (Node builtins only; 32/32 tests green).", "VERIFIED"],
    ["Marketplace is the update channel", "Installed plugins update through the marketplace \u2014 no zip/curl/copy machinery to rot. /asdlc-doctor compares installed vs released version.", "VERIFIED"],
    ["Human gates where judgment lives", "Spec approval, plan approval, PR review, merge. The agent team is fast; the operator is accountable.", "RATIONALE"],
  ];
  let y = 2.1;
  rows.forEach(([t, d, g]) => {
    card(s, 0.75, y, 11.85, 0.85, CARD, BORDER);
    s.addText(t, { x: 1.0, y: y + 0.12, w: 3.1, h: 0.6, fontFace: B, fontSize: 13.5, bold: true, color: NAVY });
    s.addText(d, { x: 4.2, y: y + 0.1, w: 7.3, h: 0.7, fontFace: B, fontSize: 11.8, color: TXT });
    tag(s, 11.05, y + 0.3, g);
    y += 0.97;
  });
  notes(s, "Walk the table as decision -> failure prevented. The plan-protocol engine is the most 'invented' piece and the one to defend.");
}

// ================= SLIDE 8 — ADOPTION MAP =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Intellectual honesty");
  title(s, "What we adopted vs what we built", "Credit where credit is due \u2014 adaptation with license-compliant attribution in every skill.");
  card(s, 0.75, 2.1, 5.9, 4.45, "FBF3E2", AMBERD);
  s.addText("ADOPTED \u2014 adapted from mattpocock/skills (MIT, credited in frontmatter)", { x: 1.05, y: 2.3, w: 5.35, h: 0.55, fontFace: B, fontSize: 12.5, bold: true, color: "7A5C00" });
  const adopted = [
    "dev-tdd \u2190 tdd (red\u2013green\u2013refactor)",
    "qa-triage \u2190 triage",
    "pm-grill-with-docs \u2190 grill-with-docs",
    "pm-to-issues \u2190 to-issues",
    "devops-setup-pre-commit \u2190 setup-pre-commit",
    "devops-git-guardrails \u2190 git-guardrails-claude-code",
  ];
  adopted.forEach((a, i) => {
    s.addText(a, { x: 1.05, y: 2.95 + i * 0.52, w: 5.4, h: 0.45, fontFace: B, fontSize: 12.5, color: TXT, bullet: true });
  });
  s.addText("Rule: don't reinvent a working skill; adapt it, keep the MIT credit, wire it into the team.", { x: 1.05, y: 6.05, w: 5.4, h: 0.4, fontFace: B, fontSize: 11.5, italic: true, color: "7A5C00" });
  card(s, 6.9, 2.1, 5.7, 4.45, "EAF5EC", GREEN);
  s.addText("ORIGINAL \u2014 built in-house for this framework", { x: 7.2, y: 2.3, w: 5.2, h: 0.55, fontFace: B, fontSize: 12.5, bold: true, color: GREEND });
  const original = [
    "plan-protocol engine (registry + blast-radius + pre-push guard)",
    "dev-feature-plan (spec \u2192 impl-plan.md + tasks.md)",
    "pm-client-interview \u00B7 pm-constitution-sync \u00B7 pm-epic-writing \u00B7 pm-project-status",
    "devops-cicd \u00B7 devops-ops \u00B7 web-publisher-publish",
    "the 4 plugin commands + agent roster + routing table",
    "the canonical scaffold + FOLDER-STRUCTURE.md",
  ];
  original.forEach((a, i) => {
    s.addText(a, { x: 7.2, y: 2.95 + i * 0.52, w: 5.2, h: 0.45, fontFace: B, fontSize: 12.5, color: TXT, bullet: true });
  });
  s.addText("The hybrid: industry patterns (SDD/TDD, plan registry, pre-commit guards) + our orchestration layer.", { x: 7.2, y: 6.05, w: 5.2, h: 0.4, fontFace: B, fontSize: 11.5, italic: true, color: GREEND });
  tag(s, 0.75, 6.7, "VERIFIED");
  s.addText("Credits verified by grep of every SKILL.md frontmatter in the repo.", { x: 2.35, y: 6.73, w: 10, h: 0.35, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "This slide exists because the audience will ask. Six skills are adaptations of Matt Pocock's MIT skills, credited per-file.");
}

// ================= SLIDE 9 — THE TEAM =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Supported features");
  title(s, "The agentic development team", "Four thin roles, one routing table, hard cross-agent rules.");
  const agents = [
    ["product-manager", "Roadmap, specs, epics, project-status, approval triage", "7 skills"],
    ["developer", "Implementation, debugging, architecture, publishing", "4 skills"],
    ["qa", "Test strategy, bug triage, regression verification", "1 skill"],
    ["devops", "CI/CD, Vercel ops, git guardrails, pre-commit", "4 skills"],
  ];
  let x = 0.75;
  agents.forEach(([n, d, c]) => {
    card(s, x, 2.2, 2.85, 1.9, ICE, MID);
    s.addText(n, { x: x + 0.22, y: 2.4, w: 2.4, h: 0.4, fontFace: H, fontSize: 17, bold: true, color: NAVY });
    s.addText(d, { x: x + 0.22, y: 2.85, w: 2.45, h: 0.95, fontFace: B, fontSize: 11.5, color: TXT });
    s.addText(c, { x: x + 0.22, y: 3.82, w: 2.4, h: 0.3, fontFace: B, fontSize: 10.5, bold: true, color: AMBERD });
    x += 3.02;
  });
  s.addText("Cross-agent hard rules", { x: 0.75, y: 4.5, w: 11.8, h: 0.4, fontFace: H, fontSize: 17, bold: true, color: NAVY });
  const rules = [
    "The developer never starts without a plan the PM approved.",
    "Every bug is triaged (qa-triage) before anyone works on it \u2014 security/data bugs carry a priority floor.",
    "Nothing is committed unless the operator asked; nothing is pushed to main; all changes land through a PR.",
    "No agent merges its own PR.",
  ];
  bullets(s, 0.75, 5.0, 11.8, 1.6, rules, 12.5);
  s.addText("Routing: a delegation block in the project's CLAUDE.md routes each request to exactly one agent (operator can override).", { x: 0.75, y: 6.75, w: 11.8, h: 0.4, fontFace: B, fontSize: 12, italic: true, color: MUT });
  notes(s, "Four agents, not an army: each owns a lane. The routing table is the single source of truth for delegation.");
}

// ================= SLIDE 10 — PRODUCT WORKFLOW =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Supported features");
  title(s, "The agent product-development workflow", "From raw business intent to an issue backlog \u2014 with the operator as approver.");
  const steps = [
    ["pm-client-interview", "captures business context"],
    ["pm-constitution-sync", "records decisions + rules"],
    ["pm-epic-writing", "decision-complete spec"],
    ["pm-grill-with-docs", "adversarial check vs docs"],
    ["APPROVE", "operator gate"],
    ["pm-to-issues", "issue backlog"],
  ];
  let x = 0.75;
  steps.forEach(([t, d], i) => {
    const wdt = 1.72;
    card(s, x, 2.2, wdt, 1.45, i === 4 ? AMBER : ICE, i === 4 ? AMBERD : MID);
    s.addText(t, { x: x + 0.08, y: 2.55, w: wdt - 0.16, h: 0.55, fontFace: B, fontSize: 10.5, bold: true, color: i === 4 ? "4A3A00" : NAVY, align: "center", margin: 0 });
    s.addText(d, { x: x + 0.08, y: 3.15, w: wdt - 0.16, h: 0.55, fontFace: B, fontSize: 9.5, color: TXT, align: "center", margin: 0 });
    if (i < steps.length - 1) s.addText("\u2192", { x: x + wdt - 0.02, y: 2.8, w: 0.3, h: 0.5, fontFace: B, fontSize: 16, bold: true, color: AMBERD, align: "center", margin: 0 });
    x += wdt + 0.18;
  });
  const art = [
    ["docs/product/product.md", "strategy + scope"],
    ["docs/product/epics.md \u00B7 epic-status.md", "epic backlog + status"],
    [".specify/features/{slug}/", "specs, impl-plans, tasks"],
    ["docs/project-status.html", "operator dashboard"],
    ["docs/qa/{date}-{slug}-triage.md", "triage reports"],
    ["docs/brand/style-guide.md", "brand tokens"],
  ];
  s.addText("Where the product state lives (the repo is the single source of truth)", { x: 0.75, y: 4.1, w: 11.8, h: 0.4, fontFace: H, fontSize: 17, bold: true, color: NAVY });
  let y = 4.55;
  art.forEach(([p, d]) => {
    s.addText(p, { x: 1.0, y, w: 5.6, h: 0.38, fontFace: "Courier New", fontSize: 11.5, bold: true, color: GREEND });
    s.addText(d, { x: 6.9, y, w: 5.6, h: 0.38, fontFace: B, fontSize: 12, color: MUT });
    y += 0.33;
  });
  s.addText("Gate: no feature is spec'd without operator approval of the epic; no work starts without an approved plan.", { x: 0.75, y: 6.75, w: 11.8, h: 0.35, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
  notes(s, "This is the 'product' loop: the PM agent serializes business intent into decision-complete specs, then issues.");
}

// ================= SLIDE 11 — IMPLEMENTATION DEV-LOOP =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Supported features");
  title(s, "The implementation dev-loop", "One issue in \u2014 a reviewed PR out. No skipping, no side-doors.");
  const steps = [
    ["dev-feature-plan", "impl-plan.md + tasks.md with acceptance criteria"],
    ["APPROVE", "operator reviews the plan"],
    ["dev-tdd \u00B7 per task", "RED failing test \u2192 GREEN minimal \u2192 REFACTOR, evidence at each step"],
    ["qa-triage", "verify + regression"],
    ["Open PR", "blast-radius guard + CI gates run"],
    ["REVIEW & MERGE", "operator decides"],
  ];
  let x = 0.75;
  steps.forEach(([t, d], i) => {
    const wdt = 1.72;
    card(s, x, 2.25, wdt, 1.9, i === 1 || i === 5 ? AMBER : "F4F9F5", i === 1 || i === 5 ? AMBERD : GREEN);
    s.addText(t, { x: x + 0.08, y: 2.5, w: wdt - 0.16, h: 0.7, fontFace: B, fontSize: 10.5, bold: true, color: i === 1 || i === 5 ? "4A3A00" : GREEND, align: "center", margin: 0 });
    s.addText(d, { x: x + 0.08, y: 3.25, w: wdt - 0.16, h: 0.9, fontFace: B, fontSize: 9, color: TXT, align: "center", margin: 0 });
    if (i < steps.length - 1) s.addText("\u2192", { x: x + wdt - 0.02, y: 3.0, w: 0.3, h: 0.5, fontFace: B, fontSize: 16, bold: true, color: AMBERD, align: "center", margin: 0 });
    x += wdt + 0.18;
  });
  s.addText("What keeps the loop honest", { x: 0.75, y: 4.6, w: 11.8, h: 0.4, fontFace: H, fontSize: 17, bold: true, color: NAVY });
  const guards = [
    ["Plan registry + blast-radius guard", "pre-push hook rejects undeclared changes outside the approved plan \u2014 kills surprise mega-PRs."],
    ["TDD evidence", "every task shows the failing test first (RED), then the minimal change (GREEN) \u2014 the diff carries its own justification."],
    ["CI gate set", "manifests, lockstep versions, no-global-install, skill frontmatter integrity, engine tests, web-template query/migration sync."],
    ["qa-triage before merge", "the QA lane re-checks the change against the plan, not just the code."],
  ];
  let y = 4.95;
  guards.forEach(([t, d]) => {
    s.addText("\u25B8  " + t, { x: 1.0, y, w: 5.3, h: 0.42, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
    s.addText(d, { x: 6.5, y, w: 6.1, h: 0.42, fontFace: B, fontSize: 11.5, color: TXT });
    y += 0.42;
  });
  tag(s, 0.75, 6.75, "VERIFIED");
  s.addText("Guard mechanics verified by CI run and the live E2E adopt/doctor runs (slide 14).", { x: 2.35, y: 6.78, w: 10.2, h: 0.35, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "The dev-loop is the core claim of the framework: plan -> test-first -> gates -> PR. Everything else serves it.");
}

// ================= SLIDE 12 — HYBRID SDD-TDD =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Methodology");
  title(s, "Hybrid SDD-TDD: decisions first, tests first", "Spec-driven for what to build; test-driven for how to build it.");
  card(s, 0.75, 2.15, 5.75, 3.9, "FBF3E2", AMBERD);
  s.addText("SDD \u2014 SPEC-DRIVEN DESIGN", { x: 1.05, y: 2.35, w: 5.2, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: "7A5C00" });
  bullets(s, 1.05, 2.8, 5.2, 3.0, [
    "Decision-complete spec before any code: pm-epic-writing + pm-grill-with-docs against the docs.",
    "dev-feature-plan turns the approved spec into impl-plan.md (phases, decisions, risks, estimates) and tasks.md (dependency-ordered, each with acceptance criteria).",
    "The plan is the contract the developer and the operator both sign.",
  ], 12.5);
  s.addText("Why: agents are fluent but not omniscient \u2014 most failures in agentic delivery are design failures, not coding failures.", { x: 1.05, y: 5.6, w: 5.2, h: 0.5, fontFace: B, fontSize: 11.5, italic: true, color: "7A5C00" });
  card(s, 6.85, 2.15, 5.75, 3.9, "EAF5EC", GREEN);
  s.addText("TDD \u2014 TEST-FIRST PER TASK", { x: 7.15, y: 2.35, w: 5.2, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: GREEND });
  bullets(s, 7.15, 2.8, 5.2, 3.0, [
    "dev-tdd runs red\u2013green\u2013refactor per task: write the failing test first, observe it fail (evidence), implement the minimal change, reach green.",
    "Refactor only on green; rerun the affected suite.",
    "Definition of done = gates passed with pasted evidence \u2014 never a bare claim.",
  ], 12.5);
  s.addText("Why: tests are the only machine-checkable record of intent \u2014 they make agent work auditable.", { x: 7.15, y: 5.6, w: 5.2, h: 0.5, fontFace: B, fontSize: 11.5, italic: true, color: GREEND });
  s.addText("Sequence per change: approve spec \u2192 approve plan \u2192 TDD each task \u2192 gates \u2192 PR. The SDD layer decides, the TDD layer proves.", { x: 0.75, y: 6.45, w: 11.85, h: 0.5, fontFace: H, fontSize: 15.5, bold: true, color: NAVY });
  notes(s, "This mirrors the SDD methodology (specify -> tdd -> gates) that this operator applies to all projects; the framework encodes it in dev-* skills.");
}

// ================= SLIDE 13 — WORKFLOW DIAGRAM =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The flow");
  title(s, "One request: from first command to merged PR", "Empty repo or established repo \u2014 the same guarded loop.");
  s.addImage({ path: __dirname + "/workflow-diagram.png", x: 0.6, y: 1.95, w: 12.15, h: 4.41 });
  s.addText("Formal diagram: hand-authored SVG source in docs/slides/workflow-diagram.svg, lanes = operator \u00B7 product manager \u00B7 developer/qa/devops.", { x: 0.6, y: 6.5, w: 12.1, h: 0.4, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "Walk the diagram top to bottom: operator decides, PM serializes, dev/qa execute with gates. Note the two approval loops (spec, plan) and the review/merge gate.");
}

// ================= SLIDE 14 — PREREQUISITES & INSTALLATION =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Adoption");
  title(s, "Prerequisites & installation", "Two commands to a working team. Verified by a live install run.");
  card(s, 0.75, 2.15, 4.6, 3.4, ICE, MID);
  s.addText("PREREQUISITES", { x: 1.0, y: 2.35, w: 4.1, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: NAVY });
  bullets(s, 1.0, 2.8, 4.2, 2.6, [
    "Claude Code CLI (any supported model)",
    "git + authenticated gh",
    "perl, node/npm/npx, rsync (scaffold steps)",
    "GitHub (marketplace source)",
    "Nothing else \u2014 no infra, no server, no DB to provision",
  ], 12);
  s.addText("Checked by /asdlc-doctor before anything else runs.", { x: 1.0, y: 5.15, w: 4.2, h: 0.35, fontFace: B, fontSize: 11.5, italic: true, color: MID });
  card(s, 5.65, 2.15, 6.95, 3.4, NAVY, NAVY);
  s.addText("INSTALL \u2014 2 COMMANDS", { x: 5.95, y: 2.35, w: 6.3, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: AMBER });
  s.addText("claude plugin marketplace add trac41799/claude-code-agentic-sdlc", { x: 5.95, y: 2.85, w: 6.4, h: 0.35, fontFace: "Courier New", fontSize: 12.5, color: WHITE });
  s.addText("claude plugin install agentic-sdlc@agentic-sdlc", { x: 5.95, y: 3.3, w: 6.4, h: 0.35, fontFace: "Courier New", fontSize: 12.5, color: WHITE });
  s.addText("Then:  /asdlc-doctor  \u2192  check setup", { x: 5.95, y: 3.8, w: 6.4, h: 0.3, fontFace: B, fontSize: 12, color: ICE });
  s.addText("      /asdlc-project  \u2192  new project   \u00B7   /asdlc-adopt  \u2192  existing repo", { x: 5.95, y: 4.15, w: 6.4, h: 0.3, fontFace: B, fontSize: 12, color: ICE });
  s.addText("Updates: claude plugin update agentic-sdlc@agentic-sdlc \u2014 projects refresh via /asdlc-adopt.", { x: 5.95, y: 4.6, w: 6.4, h: 0.3, fontFace: B, fontSize: 11.5, color: "9FB0DC" });
  s.addText("Nothing global: no hooks, no telemetry, no writes outside the project you scaffold.", { x: 5.95, y: 5.05, w: 6.4, h: 0.3, fontFace: B, fontSize: 11.5, italic: true, color: "9FB0DC" });
  tag(s, 0.75, 6.0, "VERIFIED");
  s.addText("Executed live during prep for this deck: marketplace add \u2192 install \u2192 /asdlc-doctor \u2192 /asdlc-adopt on a sandbox repo \u2014 all green (isolated CLAUDE_CONFIG_DIR, real GitHub marketplace).", { x: 2.35, y: 6.03, w: 10.2, h: 0.6, fontFace: B, fontSize: 11.5, color: MUT });
  s.addText("Prerequisite set from doctor.sh: git, gh (authenticated), perl, node/npm/npx, rsync.", { x: 0.75, y: 6.75, w: 11.85, h: 0.35, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "The install path was executed live with the Free Claude Code proxy in prep for this deck - strong evidence slide.");
}

// ================= SLIDE 15 — CASE STUDIES =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Practical evidence");
  title(s, "Two POCs, one week each, one engineer", "Non-technical founders vibecoding with the framework on this machine.");
  const cs = [
    ["AU \u00B7 HEALTHCARE", "Non-technical founder. Installed the framework, worked with one supporting engineer. Delivered a complete working POC in one week \u2014 product surface, auth, data, deployment."],
    ["US \u00B7 STAFFING", "Non-technical founder. Same setup, same support model. Complete working POC in one week \u2014 recruitment workflow, notifications, publishing."],
  ];
  let y = 2.1;
  cs.forEach(([h, d]) => {
    card(s, 0.75, y, 11.85, 1.15, CARD, BORDER);
    s.addText(h, { x: 1.05, y: y + 0.18, w: 3.0, h: 0.75, fontFace: H, fontSize: 17, bold: true, color: NAVY });
    s.addText(d, { x: 4.2, y: y + 0.15, w: 8.2, h: 0.9, fontFace: B, fontSize: 12.5, color: TXT });
    y += 1.3;
  });
  card(s, 0.75, 4.7, 11.85, 1.8, "FBF3E2", AMBERD);
  s.addText("Evidence grade: CASE STUDY \u2014 real, but not controlled. Read the confounds:", { x: 1.05, y: 4.88, w: 11.2, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: "7A5C00" });
  bullets(s, 1.05, 5.28, 11.2, 1.25, [
    "Model mix drifted: both clients started on Opus 4.8-class models and switched to Sonnet 4.6-class late in the build \u2014 outcome can't be attributed to the framework alone.",
    "No cost tracking (we never wired accurate cost metering for Claude Code); token tracking only partial.",
    "n = 2, no control group, no competitor-plugin comparison.",
  ], 11.5);
  s.addText("What we can claim: repeatable setup (same machine, same framework, two different domains), one-week POC cadence, one-engineer support model \u2014 and that the framework was the constant.", { x: 0.75, y: 6.62, w: 11.85, h: 0.45, fontFace: B, fontSize: 12.5, italic: true, color: NAVY });
  notes(s, "Lead with the confounds before anyone asks. The credibility play: we grade our own evidence.");
}

// ================= SLIDE 16 — BENCHMARK PLAN =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Planned experiment");
  title(s, "Benchmark: the traveling-friend repos", "Dedicated non-merge branches, same tasks, with and without the framework.");
  const bench = [
    ["Repos", "traveling-friend-fe \u00B7 traveling-friend-agentic-be \u2014 feature + backend, the same codebase for every run. Branches are non-merge by design: they never touch main."],
    ["Scenario 1 \u2014 isolated change", "New feature touching only FE or only BE \u2014 measures the framework's overhead on trivial surface."],
    ["Scenario 2 \u2014 vertical feature", "FE + BE both change (schema \u2192 API \u2192 UI) \u2014 the framework's core case: cross-layer coordination."],
    ["Scenario 3 \u2014 database changes", "Migration + RLS + query changes \u2014 measures plan/QA discipline on risky surface."],
    ["Scenario 4 \u2014 refactor", "Framework migration (LlamaIndex \u2192 LangChain/LangGraph) or convention cleanup \u2014 measures discipline without new features."],
    ["Scenario 5 \u2014 ETL (optional)", "Azure DevOps + AWS on free/limited accounts \u2014 pipeline work outside the scaffold's comfort zone."],
  ];
  let y = 2.1;
  bench.forEach(([t, d]) => {
    s.addText(t, { x: 0.75, y, w: 3.4, h: 0.5, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
    s.addText(d, { x: 4.3, y, w: 8.3, h: 0.5, fontFace: B, fontSize: 12, color: TXT });
    y += 0.56;
  });
  card(s, 0.75, 5.6, 11.85, 1.15, ICE, MID);
  s.addText("Method & fairness", { x: 1.05, y: 5.72, w: 11.2, h: 0.35, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
  s.addText("Same task, three arms: (a) framework, (b) bare Claude Code, (c) a marketplace alternative. Metrics live outside the framework core (scripts + dashboard in the test harness repo, isolated from the plugin) so the framework cannot influence its own score. Branches are throwaway \u2014 results can't leak into product code.", { x: 1.05, y: 6.12, w: 11.3, h: 0.7, fontFace: B, fontSize: 12, color: TXT });
  tag(s, 0.75, 6.82, "PLANNED");
  notes(s, "The isolation principle: measurement harness lives outside the framework core. Three-arm design: framework vs bare vs competitor plugin.");
}

// ================= SLIDE 17 — TOKEN BASELINE =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Planned experiment");
  title(s, "Token-usage baseline: the measurement we're missing", "We track tokens, not costs \u2014 and we haven't benchmarked either. This is the fix.");
  card(s, 0.75, 2.15, 5.75, 3.3, CARD, BORDER);
  s.addText("WHAT WE KNOW", { x: 1.05, y: 2.35, w: 5.2, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: NAVY });
  bullets(s, 1.05, 2.8, 5.25, 2.5, [
    "No cost tracking \u2014 we never wired accurate cost metering for Claude Code (partial understanding at the time).",
    "Token tracking exists but is partial and was never turned into a benchmark.",
    "POC clients ran Opus 4.8-class early, Sonnet 4.6-class late \u2014 no clean model-controlled data.",
    "Repo inspection (grep over .claude/, plugin/, docs/): the framework ships ZERO token-optimization features. No auto-compact guidance, no budget skills, no context tooling.",
  ], 12);
  card(s, 6.85, 2.15, 5.75, 3.3, ICE, MID);
  s.addText("THE PLAN \u2014 CONTROLLED BASELINE", { x: 7.15, y: 2.35, w: 5.2, h: 0.35, fontFace: B, fontSize: 13, bold: true, color: NAVY });
  bullets(s, 7.15, 2.8, 5.25, 2.5, [
    "Run the framework via fcc-claude (Free Claude Code proxy, already wired): pin Opus-equivalent and Sonnet-equivalent models over OpenRouter.",
    "Isolated CLAUDE_CONFIG_DIR per run; metering from API usage records (tokens in / tokens out per request).",
    "Metrics: tokens per task, tokens per agent role, tokens per gate (plan/TDD/review).",
    "Baseline first, optimize after \u2014 candidates: auto-compact window, context7-style lookup, skill disclosure order.",
  ], 12);
  s.addText("Why it matters: without a token baseline, every 'cost' claim about agentic frameworks is vibes.", { x: 0.75, y: 5.75, w: 11.85, h: 0.5, fontFace: H, fontSize: 16, bold: true, color: GREEND });
  tag(s, 0.75, 6.45, "PLANNED");
  s.addText("Inspection method: ripgrep for token|compact|context|optimiz across the repo \u2014 only credential-token hits found (global-engineering.md).", { x: 2.35, y: 6.48, w: 10.2, h: 0.4, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "This slide answers 'did you add token optimization?' - no, and here's the measurement plan to decide whether we need any.");
}

// ================= SLIDE 18 — GAPS & LIMITATIONS =================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Honest accounting");
  title(s, "Gaps, weaknesses, and what we knew at the time", "The framework's limits, stated by the people who built it.");
  const gaps = [
    ["No controlled benchmark yet", "Protocol is designed (slide 16); repos (traveling-friend-*) not yet ready. Until it runs, 'better than bare Claude Code' is a hypothesis.", "PLANNED"],
    ["Case studies are confounded", "n=2, model mix drifted (Opus 4.8 \u2192 Sonnet 4.6), no cost data, no control arm. Directional signal only.", "CASE STUDY"],
    ["Token economy unmanaged", "No token-optimization features ship in the framework (verified by inspection). Baseline measurement comes first (slide 17).", "VERIFIED"],
    ["Competency at the time", "v1 installed globally and drifted \u2014 that failure is why v2's nothing-global invariant exists. Cost tracking was a known blind spot we didn't close before shipping.", "RATIONALE"],
    ["Toolchain assumptions", "doctor.sh and scaffold steps assume a unix-ish toolchain (rsync, perl); Windows needs git-bash. Windows-first testing on our side.", "VERIFIED"],
    ["Model-dependence of skills", "Skill quality tracks the underlying model. The framework raises the floor, not the ceiling.", "RATIONALE"],
  ];
  let y = 2.05;
  gaps.forEach(([t, d, g]) => {
    card(s, 0.75, y, 11.85, 0.68, CARD, BORDER);
    s.addText(t, { x: 1.0, y: y + 0.1, w: 3.4, h: 0.5, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
    s.addText(d, { x: 4.5, y: y + 0.1, w: 6.6, h: 0.55, fontFace: B, fontSize: 11.2, color: TXT });
    tag(s, 11.25, y + 0.23, g);
    y += 0.78;
  });
  s.addText("We are not claiming a solved discipline. We are claiming a repeatable, honest one.", { x: 0.75, y: 6.75, w: 11.85, h: 0.35, fontFace: H, fontSize: 15.5, italic: true, bold: true, color: NAVY });
  notes(s, "Read gaps before strengths. The v1->v2 story is the strongest credibility signal in the deck.");
}

// ================= SLIDE 19 — CLOSE (dark) =================
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x: -2.2, y: 4.4, w: 5.6, h: 5.6, fill: { color: "27346E" }, line: { width: 0 } });
  s.addText("Summary", { x: 0.8, y: 0.9, w: 11.7, h: 0.4, fontFace: B, fontSize: 13, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("What we built, and what we still owe you", { x: 0.8, y: 1.35, w: 11.7, h: 0.7, fontFace: H, fontSize: 38, bold: true, color: WHITE });
  const sum = [
    "A team-shaped framework on the Claude Code harness: 4 agents, 16 skills, 4 commands, per-project isolation, zero global installs.",
    "Spec-first planning, test-first implementation, evidence-gated delivery \u2014 hybrid SDD-TDD as the working loop.",
    "Adopted, credited, and adapted \u2014 6 skills from mattpocock/skills (MIT), the orchestration layer built in-house.",
    "Two one-week POCs as directional evidence \u2014 with their confounds labeled on the slide.",
    "A controlled benchmark (traveling-friend repos, three arms, isolated harness) and a token-usage baseline \u2014 the honest next steps.",
  ];
  s.addText(sum.map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } })),
    { x: 0.8, y: 2.5, w: 11.7, h: 3.2, fontFace: B, fontSize: 15, color: ICE });
  s.addText("Questions are welcome \u2014 the confounds and the gaps are the part we're most interested in defending.", { x: 0.8, y: 6.3, w: 11.7, h: 0.5, fontFace: B, fontSize: 13.5, italic: true, color: "9FB0DC" });
  notes(s, "Close on the honesty note: we defend the confounds, not the hype.");
}

pptx.writeFile({ fileName: __dirname + "/Agentic-SDLC-Tech-Audience.pptx" }).then(f => console.log("wrote", f));