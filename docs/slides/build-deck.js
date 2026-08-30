const pptxgen = require("C:/Users/mrtra/AppData/Local/Temp/opencode/svgconv/node_modules/pptxgenjs");
const pptx = new pptxgen();

pptx.layout = "LAYOUT_WIDE";
pptx.author = "Agentic SDLC";
pptx.title = "Agentic SDLC — An experience-driven AI-SDLC framework for the Claude Code harness";

const NAVY = "1E2761", ICE = "EAF0FB", MID = "5A6B9E", AMBER = "F4B400", AMBERD = "B98A00";
const GREEN = "2E7D32", GREEND = "1B5E20", TXT = "1F2937", MUT = "6B7280", WHITE = "FFFFFF";
const CARD = "F8FAFC", BORDER = "D1D5DB";
const H = "Cambria", B = "Calibri", MONO = "Courier New";

const T_TITLE = 44, T_SUB = 20, EYEBROW = 13, PILL = 11;
const BODY = 22, BODY_SM = 20, CARD_T = 25, CARD_D = 18, NOTE = 14, SMALLP = 16;

function eyebrow(s, text, color) {
  s.addText(text.toUpperCase(), { x: 0.55, y: 0.28, w: 12, h: 0.32, fontFace: B, fontSize: EYEBROW, bold: true, color: color || AMBERD, charSpacing: 2 });
}
function title(s, text, sub) {
  s.addText(text, { x: 0.55, y: 0.6, w: 12.2, h: 0.9, fontFace: H, fontSize: T_TITLE, bold: true, color: NAVY });
  if (sub) s.addText(sub, { x: 0.55, y: 1.5, w: 12.2, h: 0.5, fontFace: B, fontSize: T_SUB, color: MUT });
}
function pill(s, x, y, text, color) {
  const wd = text.length * 0.1 + 0.28;
  s.addShape("roundRect", { x, y, w: wd, h: 0.32, rectRadius: 0.16, fill: { color }, line: { color, width: 0 } });
  s.addText(text.toUpperCase(), { x, y: y - 0.03, w: wd, h: 0.32, fontFace: B, fontSize: PILL, bold: true, color: WHITE, align: "center", margin: 0 });
}
function tag(s, x, y, label) {
  const map = { VERIFIED: GREEN, "CASE STUDY": AMBERD, RATIONALE: MID, PLANNED: "7C8698" };
  pill(s, x, y, label, map[label] || "7C8698");
}
function card(s, x, y, w, h, fill, line) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.1, fill: { color: fill || CARD }, line: { color: line || BORDER, width: 1.25 } });
}
function notes(s, t) { s.addNotes(t); }

// ============ 1 · TITLE ============
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x: 10.2, y: -2.2, w: 5.6, h: 5.6, fill: { color: "27346E" }, line: { width: 0 } });
  s.addText("CLAUDE CODE HARNESS  \u00B7  PLUGIN  \u00B7  v2.8.0", { x: 0.8, y: 0.9, w: 11, h: 0.4, fontFace: B, fontSize: 15, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("Agentic SDLC", { x: 0.8, y: 1.5, w: 11.7, h: 1.6, fontFace: H, fontSize: 70, bold: true, color: WHITE });
  s.addText("An AI-SDLC framework built from delivery experience", { x: 0.8, y: 3.15, w: 11.7, h: 0.65, fontFace: B, fontSize: 26, color: ICE });
  s.addText("4 agents  \u00B7  17 skills  \u00B7  spec-first  \u00B7  test-first  \u00B7  evidence-gated", { x: 0.8, y: 3.95, w: 11.7, h: 0.5, fontFace: B, fontSize: 17, color: "9FB0DC" });
  s.addText("Every claim carries one of these grades:", { x: 0.8, y: 5.75, w: 11.7, h: 0.4, fontFace: B, fontSize: NOTE, color: "9FB0DC" });
  let lx = 0.8;
  ["VERIFIED", "CASE STUDY", "RATIONALE", "PLANNED"].forEach(l => { pill(s, lx, 6.15, l, l === "VERIFIED" ? GREEN : l === "CASE STUDY" ? AMBERD : l === "RATIONALE" ? MID : "7C8698"); lx += 1.9; });
  s.addText("github.com/trac41799/claude-code-agentic-sdlc", { x: 8.6, y: 6.2, w: 4, h: 0.35, fontFace: B, fontSize: 12, color: "7E90C4", align: "right" });
  notes(s, "Each claim is graded. Honestly — we grade our own evidence.");
}

// ============ 2 · MOTIVATION & THE PROBLEM ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Motivation");
  title(s, "Why a team-shaped framework", "Agents changed the bottleneck. The product is the process.");
  const cards = [
    ["Context loss", "Every session starts cold."],
    ["Handoff tax", "Every handoff loses fidelity."],
    ["Agents shift it", "Bottleneck is process, not code."],
  ];
  let x = 0.75;
  cards.forEach(([t, d]) => {
    card(s, x, 2.4, 3.72, 2.3, CARD, BORDER);
    s.addText(t, { x: x + 0.3, y: 2.65, w: 3.2, h: 0.55, fontFace: H, fontSize: CARD_T, bold: true, color: NAVY });
    s.addText(d, { x: x + 0.3, y: 3.3, w: 3.2, h: 0.6, fontFace: B, fontSize: BODY_SM, color: TXT });
    x += 3.94;
  });
  const stages = ["Requirements", "Design", "Implement", "Test", "Deploy", "Maintain"];
  x = 0.75;
  stages.forEach((st, i) => {
    card(s, x, 5.05, 1.78, 0.72, ICE, MID);
    s.addText(st, { x, y: 5.2, w: 1.78, h: 0.4, fontFace: B, fontSize: 12.5, bold: true, color: NAVY, align: "center", margin: 0 });
    if (i < 5) s.addText("\u2192", { x: x + 1.75, y: 5.15, w: 0.3, h: 0.4, fontFace: B, fontSize: 16, bold: true, color: AMBERD, align: "center", margin: 0 });
    x += 1.98;
  });
  s.addText("A standard SDLC, agent-executed: from idea to clean POC.", { x: 0.75, y: 6.15, w: 11.85, h: 0.5, fontFace: H, fontSize: 21, italic: true, bold: true, color: GREEND });
  tag(s, 0.75, 6.7, "RATIONALE");
  notes(s, "My starting model: linear pipeline. The framework is its correction.");
}

// ============ 3 · THE DEMAND ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Demand");
  title(s, "What the market asked for");
  const rows = [
    ["Who", "Technical AND non-technical founders, one engineer of support"],
    ["What", "Idea \u2192 working POC in days \u2014 clean codebase + docs"],
    ["How", "Greenfield-first \\u00B7 maps to standard SDLC phases"],
    ["Guarded by", "The agent proposes \u2014 the human decides"],
  ];
  let y = 2.35;
  rows.forEach(([t, d]) => {
    card(s, 0.75, y, 11.85, 0.84, CARD, BORDER);
    s.addText(t, { x: 1.05, y: y + 0.12, w: 2.6, h: 0.6, fontFace: B, fontSize: BODY_SM, bold: true, color: NAVY });
    s.addText(d, { x: 3.8, y: y + 0.12, w: 8.6, h: 0.6, fontFace: B, fontSize: BODY_SM, color: TXT });
    y += 0.98;
  });
  s.addText("Constraints we imposed", { x: 0.75, y: 6.05, w: 11.85, h: 0.45, fontFace: H, fontSize: 22, bold: true, color: NAVY });
  s.addText("Nothing global  \u00B7  no hooks  \u00B7  all change via PR  \u00B7  operator gates every decision", { x: 0.75, y: 6.6, w: 11.85, h: 0.45, fontFace: B, fontSize: BODY_SM, bold: true, color: AMBERD });
  notes(s, "Learned from v1's machine drift; v2 encodes them.");
}

// ============ 4 · DESIGN & RATIONALE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Design");
  title(s, "One repo, three layers, five decisions", "Distribution \u00B7 runtime \u00B7 product \u2014 each decision kills a known failure.");
  const layers = [
    ["1 \u00B7 MARKETPLACE = CANONICAL", "4 commands update via marketplace", NAVY, WHITE],
    ["2 \u00B7 PER-PROJECT TEAM", "4 agents \u00B7 17 skills \u00B7 in project .claude/", ICE, NAVY],
    ["3 \u00B7 SCAFFOLD", "Next.js \u00B7 Supabase \u00B7 Vercel", "F4F9F5", GREEND],
  ];
  let y = 2.3;
  layers.forEach(([hdr, desc, fill, col]) => {
    card(s, 0.75, y, 5.85, 0.85, fill, fill);
    s.addText(hdr, { x: 0.95, y: y + 0.06, w: 5.5, h: 0.3, fontFace: B, fontSize: 12.5, bold: true, color: col, charSpacing: 0.5 });
    s.addText(desc, { x: 0.95, y: y + 0.42, w: 5.5, h: 0.32, fontFace: B, fontSize: BODY_SM, color: col });
    y += 0.98;
  });
  const dec = [
    ["Nothing global", "Machine drift killed v1"],
    ["Thin agents, skills on demand", "Context budget stays deliberate"],
    ["Plan-protocol", "No undeclared mega-PRs"],
    ["Marketplace updates", "No zip/curl to rot"],
    ["Human gates at spec/plan/PR", "Operator decides, team executes"],
  ];
  y = 2.3;
  dec.forEach(([t, d]) => {
    card(s, 6.9, y, 5.7, 0.8, CARD, BORDER);
    s.addText(t, { x: 7.1, y: y + 0.06, w: 5.35, h: 0.3, fontFace: B, fontSize: 13.5, bold: true, color: NAVY });
    s.addText(d, { x: 7.1, y: y + 0.42, w: 5.35, h: 0.32, fontFace: B, fontSize: SMALLP, color: TXT });
    y += 0.86;
  });
  tag(s, 0.75, 6.65, "VERIFIED");
  s.addText("CI enforces manifests, lockstep versions, counts, no-global-install.", { x: 2.4, y: 6.68, w: 10.2, h: 0.35, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "Canvas: mark the plan-protocol claim as the most original piece.");
}

// ============ 5 · ADOPTION MAP ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Intellectual honesty");
  title(s, "Adopted vs built", "Six MIT-credited adaptions; the orchestration layer is ours.");
  card(s, 0.75, 2.4, 5.85, 3.7, "FBF3E2", AMBERD);
  s.addText("ADOPTED \u00B7 mattpocock/skills", { x: 1.05, y: 2.6, w: 5.25, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: "7A5C00" });
  const adopted = ["dev-tdd", "qa-triage", "grill-with-docs", "to-issues", "setup-pre-commit", "git-guardrails"];
  adopted.forEach((a, i) => {
    const cx = 1.05 + (i % 2) * 2.7, cy = 3.25 + Math.floor(i / 2) * 0.62;
    pill(s, cx, cy, a, AMBERD);
  });
  s.addText("Adapted, kept MIT credit, wired into the team.", { x: 1.05, y: 5.35, w: 5.25, h: 0.55, fontFace: B, fontSize: NOTE, italic: true, color: "7A5C00" });
  card(s, 6.85, 2.4, 5.75, 3.7, "EAF5EC", GREEN);
  s.addText("BUILT IN-HOUSE", { x: 7.15, y: 2.6, w: 5.05, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: GREEND });
  const original = ["plan-protocol engine", "dev-feature-plan", "pm chain (5 skills)", "devops-cicd \u00B7 ops", "web-publisher-publish", "4 commands + scaffold"];
  original.forEach((a, i) => {
    const cx = 7.15 + (i % 2) * 2.5, cy = 3.25 + Math.floor(i / 2) * 0.62;
    pill(s, cx, cy, a, GREEN);
  });
  s.addText("The hybrid: industry patterns + orchestration layer.", { x: 7.15, y: 5.35, w: 5.05, h: 0.55, fontFace: B, fontSize: NOTE, italic: true, color: GREEND });
  tag(s, 0.75, 6.55, "VERIFIED");
  s.addText("Credits verified per skill frontmatter.", { x: 2.4, y: 6.58, w: 10, h: 0.35, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "They will ask 'what's original' - answer honestly before they ask.");
}

// ============ 6 · TEAM + METHOD ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The stack");
  title(s, "Team + method: SDD decides, TDD proves");
  const agents = [
    ["product-manager", "specs \u00B7 epics \u00B7 status"],
    ["developer", "impl. \u00B7 publishing"],
    ["qa", "strategy \u00B7 triage"],
    ["devops", "CI/CD \u00B7 guardrails"],
  ];
  let x = 0.75;
  agents.forEach(([n, d]) => {
    card(s, x, 2.35, 2.85, 1.3, ICE, MID);
    s.addText(n, { x: x + 0.22, y: 2.5, w: 2.45, h: 0.4, fontFace: H, fontSize: 19, bold: true, color: NAVY });
    s.addText(d, { x: x + 0.22, y: 2.95, w: 2.45, h: 0.4, fontFace: B, fontSize: 15, color: MUT });
    x += 3.02;
  });
  s.addText("No dev start without an approved plan. No self-merges. All change via PR.", { x: 0.75, y: 4.0, w: 11.85, h: 0.5, fontFace: B, fontSize: BODY_SM, bold: true, color: NAVY });
  card(s, 0.75, 4.85, 5.85, 1.85, "FBF3E2", AMBERD);
  s.addText("SPEC-FIRST", { x: 1.05, y: 5.05, w: 5.25, h: 0.4, fontFace: B, fontSize: 18, bold: true, color: "7A5C00" });
  s.addText("Spec before code. Plan is the contract.", { x: 1.05, y: 5.55, w: 5.25, h: 0.5, fontFace: B, fontSize: BODY_SM, color: TXT });
  s.addText("Operator approves spec AND plan.", { x: 1.05, y: 6.1, w: 5.25, h: 0.5, fontFace: B, fontSize: BODY_SM, color: TXT });
  card(s, 6.85, 4.85, 5.75, 1.85, "EAF5EC", GREEN);
  s.addText("TEST-FIRST", { x: 7.15, y: 5.05, w: 5.05, h: 0.4, fontFace: B, fontSize: 18, bold: true, color: GREEND });
  s.addText("Fail first, then minimal green. Refactor.", { x: 7.15, y: 5.55, w: 5.05, h: 0.5, fontFace: B, fontSize: BODY_SM, color: TXT });
  s.addText("Done = gates passed with evidence.", { x: 7.15, y: 6.1, w: 5.05, h: 0.5, fontFace: B, fontSize: BODY_SM, color: TXT });
  notes(s, "Small roster; the method is the chain: spec gate -> plan gate -> TDD -> QA -> PR.");
}

// ============ 8 · SDLC CYCLE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The model");
  title(s, "One SDLC cycle, two entry points", "Greenfield \u00B7 brownfield \u00B7 slash commands mark every stage.");
  s.addImage({ path: __dirname + "/sdlc-cycle.png", x: 0.7, y: 2.15, w: 11.9, h: 4.32 });
  s.addText("Six stages, standard SDLC \u2014 the framework maps a skill to each stage and a command to each entry.", { x: 0.7, y: 6.6, w: 11.9, h: 0.45, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "Greenfield: /asdlc-project. Brownfield: /asdlc-adopt. Doctor verifies at any stage. Each stage = one skill lane.");
}
// ============ 7 · THE FLOW (DIAGRAM) ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The flow");
  title(s, "One request: first command \u2192 merged PR");
  s.addImage({ path: __dirname + "/workflow-diagram.png", x: 0.45, y: 2.0, w: 12.45, h: 4.52 });
  s.addText("Spec gate \u00B7 plan gate \u00B7 TDD per task \u00B7 QA before merge \u2014 the diagram IS the two-phase story.", { x: 0.45, y: 6.65, w: 12.45, h: 0.5, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "Operator decides, PM serializes, dev/qa execute with gates. Three lanes, two approvals, one PR.");
}

// ============ 8 · INSTALL & EVIDENCE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Adoption & evidence");
  title(s, "Two commands. Two one-week POCs.");
  s.addText("claude plugin marketplace add trac41799/claude-code-agentic-sdlc", { x: 0.75, y: 2.25, w: 11.85, h: 0.5, fontFace: MONO, fontSize: 18, bold: true, color: GREEND });
  s.addText("claude plugin install agentic-sdlc@agentic-sdlc", { x: 0.75, y: 2.85, w: 11.85, h: 0.5, fontFace: MONO, fontSize: 18, bold: true, color: GREEND });
  s.addText("Then /asdlc-doctor \u00B7 /asdlc-project (new repo) \u00B7 /asdlc-adopt (existing)", { x: 0.75, y: 3.45, w: 11.85, h: 0.45, fontFace: B, fontSize: NOTE, color: MUT });
  const cs = [
    ["WorkHealthyAustralia", "AU \u00B7 healthcare \u2014 janet.care (personal healthcare AI-assistant) + occuspan.com \u00B7 POC in 1 week"],
    ["DOXA", "US \u00B7 staffing \u2014 multiple projects under NDA \u00B7 POC in 1 week"],
  ];
  let y = 4.1;
  cs.forEach(([h, d]) => {
    card(s, 0.75, y, 11.85, 0.95, CARD, BORDER);
    s.addText(h, { x: 1.05, y: y + 0.16, w: 3.7, h: 0.7, fontFace: H, fontSize: 22, bold: true, color: NAVY });
    s.addText(d, { x: 4.4, y: y + 0.12, w: 8.0, h: 0.7, fontFace: B, fontSize: SMALLP, color: TXT });
    y += 1.1;
  });
  s.addText("Both: non-technical founders, one engineer of support, one engineer of trust.", { x: 0.75, y: 6.3, w: 11.85, h: 0.4, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  tag(s, 0.75, 6.75, "CASE STUDY");
  s.addText("Confounded: model mix drifted mid-build \u00B7 no cost tracking \u00B7 n = 2", { x: 2.4, y: 6.78, w: 10.2, h: 0.35, fontFace: B, fontSize: NOTE, color: MUT });
  notes(s, "Install verified live via fcc-claude earlier. Cases: named, and confounds labeled.");
}

// ============ 10 · HOW WE BENCHMARK ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Methodology first");
  title(s, "How we benchmark", "Context before numbers \u2014 same model, frozen tasks, metered, non-merge.");
  const rows = [
    ["Arms", "B bare \u00B7 A\u2032 framework passive \u00B7 A framework activated (routing + lanes)"],
    ["Fairness", "Same commit \u00B7 same model pin \u00B7 identical frozen task text \u00B7 same tooling flags"],
    ["Metering", "Session JSON: turns, tokens in/out, cost \u00B7 wall clock \u00B7 outcome gates (pytest / node --test)"],
    ["Safety", "Offline acceptance (no live DB, no deploys) \u00B7 exp branches, never merged to main"],
    ["Scoring", "Acceptance + hidden rubric checks (crash-safety, idempotency, concurrency) + traceability (spec\u2192plan\u2192tasks artifacts)"],
  ];
  let y = 2.35;
  rows.forEach(([m, d]) => {
    card(s, 0.75, y, 11.85, 0.72, CARD, BORDER);
    s.addText(m, { x: 1.0, y: y + 0.12, w: 1.9, h: 0.5, fontFace: B, fontSize: 14, bold: true, color: NAVY });
    s.addText(d, { x: 3.05, y: y + 0.12, w: 9.4, h: 0.5, fontFace: B, fontSize: SMALLP, color: TXT });
    y += 0.84;
  });
  s.addText("Everything on this deck's results slide came from the bench kit in the repo \u2014 rerun any cell with one command (docs/benchmarks/BENCHMARK-SUMMARY.md).", { x: 0.75, y: 6.6, w: 11.85, h: 0.5, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "Methodology slide exists so the results are read with their confounds in frame, not as bare numbers.");
}
// ============ 9 · BENCHMARK (MEASURED MATRIX) ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Benchmark \u00B7 4 runs, 3 arms");
  title(s, "Measured: bare vs passive vs activated", "Same repos \u00B7 same frozen tasks \u00B7 same model \u00B7 metered. Froam exp branches (non-merge).");
  const rows = [
    ["R1 \u00B7 add-tests (trivial)", "$0.63 \u00B7 6 tests", "$0.62 \u00B7 7 tests", "$0.47 \u00B7 10 tests \u00B7 2.5\u00D7 turns"],
    ["R2 \u00B7 DB + RLS", "$0.22 \u00B7 11 tests", "$0.27 \u00B7 11 tests", "$0.67 \u00B7 11 tests + plan/QA"],
    ["R4 \u00B7 fragile refactor", "refused \u00B7 restraint pass", "\u2014", "violated (guardrail advisory) \u00B7 prod-correct when approved"],
    ["R3 \u00B7 vertical FE+BE", "$0.94 \u00B7 4 tests", "\u2014", "$0.98 \u00B7 4 tests + plan/tasks"],
  ];
  let y = 2.35;
  s.addText("TASK", { x: 0.9, y: 2.0, w: 3.1, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: MUT });
  s.addText("B \u00B7 BARE", { x: 4.1, y: 2.0, w: 2.6, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: MUT, align: "center" });
  s.addText("A\u2032 \u00B7 PASSIVE", { x: 6.9, y: 2.0, w: 2.6, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: MUT, align: "center" });
  s.addText("A \u00B7 ACTIVATED", { x: 9.7, y: 2.0, w: 2.8, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: MUT, align: "center" });
  rows.forEach(([m, b, p, a]) => {
    card(s, 0.75, y, 11.85, 0.72, CARD, BORDER);
    s.addText(m, { x: 0.9, y: y + 0.14, w: 3.1, h: 0.45, fontFace: B, fontSize: 12, bold: true, color: NAVY });
    s.addText(b, { x: 4.1, y: y + 0.14, w: 2.6, h: 0.45, fontFace: B, fontSize: 11.5, color: TXT, align: "center" });
    s.addText(p, { x: 6.9, y: y + 0.14, w: 2.6, h: 0.45, fontFace: B, fontSize: 11.5, color: TXT, align: "center" });
    s.addText(a, { x: 9.7, y: y + 0.14, w: 2.8, h: 0.45, fontFace: B, fontSize: 11.5, color: GREEND, align: "center" });
    y += 0.82;
  });
  s.addText("Findings: passive \u2248 bare (placebo) \u00B7 activation tax scales with ceremony, benefit with risk \u00B7 restraint is advisory, not structural \u00B7 QA lane is the value on risky approved change.", { x: 0.75, y: 6.0, w: 11.85, h: 0.55, fontFace: B, fontSize: NOTE, bold: true, color: NAVY });
  s.addText("Harness gap fixed via dev-agent-router (16\u219217 skills) \u00B7 DeepSeek pin since R2 \u00B7 world anchor: SWE-bench-style floor check pending.", { x: 0.75, y: 6.65, w: 11.85, h: 0.45, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "4 runs, 3 arms, real numbers, real gaps. Read the R4 line out loud: the guardrail is advisory — that is the honesty that earns trust.");
}

// ============ 10 · GAPS + CLOSE ============
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x: -2.2, y: 4.4, w: 5.6, h: 5.6, fill: { color: "27346E" }, line: { width: 0 } });
  s.addText("WHAT WE KNOW", { x: 0.8, y: 0.85, w: 11.7, h: 0.4, fontFace: B, fontSize: 14, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("Built from experience. Graded by evidence.", { x: 0.8, y: 1.3, w: 11.7, h: 0.85, fontFace: H, fontSize: 42, bold: true, color: WHITE });
  const gaps = [
    "Benchmark: 1 run, trivial task \u2014 gaps shown, value not yet proven",
    "Tokens: managed by baseline next \u2014 cheap to meter, no budget yet",
    "Method: SDD + TDD + 4-agent team \u2014 tested on two POCs, lab-confound labeled",
    "Human-hour ratio: measured via hooks + PR windows \u2014 target LOW",
  ];
  s.addText(gaps.map(g => ({ text: g, options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } })),
    { x: 0.8, y: 2.65, w: 11.7, h: 2.7, fontFace: B, fontSize: BODY_SM, color: ICE });
  s.addText("Next: vertical \u00B7 DB \u00B7 refactor scenarios on the traveling-friend repos, then the token baseline.", { x: 0.8, y: 5.55, w: 11.7, h: 0.5, fontFace: B, fontSize: BODY_SM, bold: true, color: AMBER });
  s.addText("Not a solved discipline \u2014 a repeatable, honest one.", { x: 0.8, y: 6.35, w: 11.7, h: 0.5, fontFace: H, fontSize: 23, italic: true, bold: true, color: WHITE });
  notes(s, "Close on the gaps. That is the part we defend most.");
}

pptx.writeFile({ fileName: __dirname + "/Agentic-SDLC-Tech-Audience.pptx" }).then(f => console.log("wrote", f));