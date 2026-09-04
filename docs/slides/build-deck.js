const pptxgen = require("pptxgenjs");
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
  s.addText("CLAUDE CODE HARNESS  \u00B7  PLUGIN  \u00B7  v2.9.0", { x: 0.8, y: 0.9, w: 11, h: 0.4, fontFace: B, fontSize: 15, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("Agentic SDLC", { x: 0.8, y: 1.5, w: 11.7, h: 1.6, fontFace: H, fontSize: 70, bold: true, color: WHITE });
  s.addText("An AI-SDLC framework built from delivery experience", { x: 0.8, y: 3.15, w: 11.7, h: 0.65, fontFace: B, fontSize: 26, color: ICE });
  s.addText("4 agents  \u00B7  17 skills  \u00B7  spec-first  \u00B7  test-first  \u00B7  evidence-gated", { x: 0.8, y: 3.95, w: 11.7, h: 0.5, fontFace: B, fontSize: 17, color: "9FB0DC" });
  s.addText("Every claim carries one of these grades:", { x: 0.8, y: 5.75, w: 11.7, h: 0.4, fontFace: B, fontSize: NOTE, color: "9FB0DC" });
  let lx = 0.8;
  ["VERIFIED", "CASE STUDY", "RATIONALE", "PLANNED"].forEach(l => { pill(s, lx, 6.15, l, l === "VERIFIED" ? GREEN : l === "CASE STUDY" ? AMBERD : l === "RATIONALE" ? MID : "7C8698"); lx += 1.9; });
  s.addText("github.com/trac41799/claude-code-agentic-sdlc", { x: 8.6, y: 6.2, w: 4, h: 0.35, fontFace: B, fontSize: 12, color: "7E90C4", align: "right" });
  notes(s, "Each claim is graded. Honestly — we grade our own evidence.");
}

// ============ 2 · FORK & TINKERING NOTICE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Before you tinker");
  title(s, "Fork first \u2014 the official repo is read-only", "Benchmark runs and experiments belong on your own fork. Never commit to the official ex-company repo.");
  card(s, 0.75, 2.6, 5.85, 2.35, "EAF5EC", GREEN);
  s.addText("RECOMMENDED \u00B7 YOUR FORK", { x: 1.05, y: 2.8, w: 5.25, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: GREEND });
  s.addText("Tinkering \u00B7 benchmark runs \u00B7 extensions", { x: 1.05, y: 3.3, w: 5.25, h: 0.45, fontFace: B, fontSize: BODY_SM, color: TXT });
  s.addText("github.com/trac41799/claude-code-agentic-sdlc", { x: 1.05, y: 3.9, w: 5.25, h: 0.5, fontFace: MONO, fontSize: 15, bold: true, color: "2563EB" });
  s.addText("Fork it, clone it, run bench/greenfield.py on your own cases.", { x: 1.05, y: 4.45, w: 5.25, h: 0.4, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  card(s, 6.85, 2.6, 5.75, 2.35, "FBF3E2", AMBERD);
  s.addText("OFFICIAL \u00B7 EX-COMPANY", { x: 7.15, y: 2.8, w: 5.15, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: "7A5C00" });
  s.addText("Read-only reference \u2014 do not commit", { x: 7.15, y: 3.3, w: 5.15, h: 0.45, fontFace: B, fontSize: BODY_SM, color: TXT });
  s.addText("github.com/talentedgeai/infinite-leverage", { x: 7.15, y: 3.9, w: 5.15, h: 0.5, fontFace: MONO, fontSize: 15, bold: true, color: "2563EB" });
  s.addText("The public history \u2014 v1 and the v2 lineage live here.", { x: 7.15, y: 4.45, w: 5.15, h: 0.4, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  s.addText("One rule: benchmark evidence lands on your fork \u2014 the official repo stays a clean reference.", { x: 0.75, y: 5.4, w: 11.85, h: 0.5, fontFace: B, fontSize: 18, bold: true, color: NAVY });
  notes(s, "Honesty about provenance: this deck's repo is the fork; the official ex-company repo is read-only.");
}

// ============ 3 · MOTIVATION & THE PROBLEM ============
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

// ============ 4 · THE DEMAND ============
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

// ============ 5 · DESIGN & RATIONALE ============
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

// ============ 6 · THE STACK ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The stack");
  title(s, "Four tools the team lives in", "The harness \u00B7 the change \u00B7 the delivery \u00B7 the data \u2014 also the fastest client onboarding stack.");
  const tools = [
    ["Claude Code", "HARNESS", "Agents \u00B7 skills \u00B7 slash commands. Every gate (spec \u00B7 plan \u00B7 PR) is an operator decision in the loop.", "The runtime the 4-agent team executes in"],
    ["GitHub", "CHANGE & CI", "All change via PR, never self-merged. CI enforces manifests, version lockstep, skill counts, no-global-install.", "The audit trail and the merge gate"],
    ["Vercel", "DELIVERY", "Preview per PR \u00B7 prod from main. The Deploy lane of the cycle \u2014 what clients see as \u201cit went live\u201D.", "Zero-config deploys; preview URLs on every PR"],
    ["Supabase", "DATA & AUTH", "Postgres + Auth + Storage in the scaffold, free tier. No infra decisions for a new client.", "The database and identity in the project scaffold"],
  ];
  let y = 2.3;
  tools.forEach(([n, role, d, why], i) => {
    const x = 0.75 + (i % 2) * 6.1;
    card(s, x, y, 5.75, 1.85, CARD, BORDER);
    s.addText(n, { x: x + 0.25, y: y + 0.12, w: 2.6, h: 0.5, fontFace: H, fontSize: 26, bold: true, color: NAVY });
    pill(s, x + 2.9, y + 0.2, role, MID);
    s.addText(d, { x: x + 0.25, y: y + 0.7, w: 5.3, h: 0.8, fontFace: B, fontSize: 15, color: TXT });
    s.addText(why, { x: x + 0.25, y: y + 1.45, w: 5.3, h: 0.32, fontFace: B, fontSize: 12.5, italic: true, color: MUT });
    if (i % 2 === 1) y += 2.0;
  });
  s.addText("CLI-first: gh \u00B7 vercel \u00B7 supabase \u00B7 claude are all CLIs \u2014 they chain in a shell with no convention layer, so a harness swap leaves the contract intact.", { x: 0.75, y: 6.35, w: 9.85, h: 0.4, fontFace: B, fontSize: NOTE, bold: true, color: NAVY });
  s.addText("Only Supabase also runs as an MCP server: the CLI automates, the MCP gives the agent a live surface \u2014 each serves its own moat.", { x: 0.75, y: 6.72, w: 11.85, h: 0.35, fontFace: B, fontSize: 13, color: TXT });
  tag(s, 10.9, 6.35, "VERIFIED");
  notes(s, "Company stack today and the fastest onboarding stack: Claude Code harness, GitHub PRs, Vercel deploys, Supabase data.");
}

// ============ 7 · ADOPTION MAP ============
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

// ============ 8 · TEAM + METHOD ============
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

// ============ 9 · SDLC CYCLE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The model");
  title(s, "One SDLC cycle, two entry points", "Greenfield \u00B7 brownfield \u00B7 slash commands mark every stage.");
  s.addImage({ path: __dirname + "/sdlc-cycle.png", x: 0.7, y: 2.15, w: 11.9, h: 4.32 });
  s.addText("Six stages, standard SDLC \u2014 the framework maps a skill to each stage and a command to each entry.", { x: 0.7, y: 6.6, w: 11.9, h: 0.45, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "Greenfield: /asdlc-project. Brownfield: /asdlc-adopt. Doctor verifies at any stage. Each stage = one skill lane.");
}
// ============ 10 · THE FLOW (DIAGRAM) ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The flow");
  title(s, "One request: first command \u2192 merged PR");
  s.addImage({ path: __dirname + "/workflow-diagram.png", x: 0.45, y: 2.0, w: 12.45, h: 4.52 });
  s.addText("Spec gate \u00B7 plan gate \u00B7 TDD per task \u00B7 QA before merge \u2014 the diagram IS the two-phase story.", { x: 0.45, y: 6.65, w: 12.45, h: 0.5, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "Operator decides, PM serializes, dev/qa execute with gates. Three lanes, two approvals, one PR.");
}

// ============ 11 · INSTALL & EVIDENCE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Adoption & evidence");
  title(s, "Two commands. Two one-week POCs.");
  s.addText("INSTALL \u00B7 FROM THE RECOMMENDED FORK", { x: 0.75, y: 2.0, w: 11.85, h: 0.3, fontFace: B, fontSize: 11.5, bold: true, color: AMBERD, charSpacing: 1 });
  s.addText("claude plugin marketplace add trac41799/claude-code-agentic-sdlc", { x: 0.75, y: 2.3, w: 11.85, h: 0.5, fontFace: MONO, fontSize: 17, bold: true, color: GREEND });
  s.addText("claude plugin install agentic-sdlc@agentic-sdlc", { x: 0.75, y: 2.85, w: 11.85, h: 0.5, fontFace: MONO, fontSize: 17, bold: true, color: GREEND });
  s.addText("Then /asdlc-doctor \u00B7 /asdlc-project (new repo) \u00B7 /asdlc-adopt (existing)", { x: 0.75, y: 3.45, w: 11.85, h: 0.4, fontFace: B, fontSize: NOTE, color: MUT });
  s.addText("OFFICIAL ORIGIN \u00B7 EX-COMPANY, READ-ONLY \u00B7 github.com/talentedgeai/infinite-leverage \u2014 tinker on your fork, never commit here", { x: 0.75, y: 3.9, w: 11.85, h: 0.3, fontFace: MONO, fontSize: 12, color: "B98A00" });
  const cs = [
    ["WorkHealthyAustralia", "AU \u00B7 healthcare \u2014 janet.care (personal healthcare AI-assistant) + occuspan.com \u00B7 POC in 1 week"],
    ["DOXA", "US \u00B7 staffing \u2014 multiple projects under NDA \u00B7 POC in 1 week"],
  ];
  let y = 4.35;
  cs.forEach(([h, d]) => {
    card(s, 0.75, y, 11.85, 0.9, CARD, BORDER);
    s.addText(h, { x: 1.05, y: y + 0.14, w: 3.7, h: 0.65, fontFace: H, fontSize: 22, bold: true, color: NAVY });
    s.addText(d, { x: 4.4, y: y + 0.1, w: 8.0, h: 0.65, fontFace: B, fontSize: SMALLP, color: TXT });
    y += 1.1;
  });
  s.addText("Both: non-technical founders, one engineer of support, one engineer of trust.", { x: 0.75, y: 6.42, w: 11.85, h: 0.35, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  tag(s, 0.75, 6.75, "CASE STUDY");
  s.addText("Confounded: model mix drifted mid-build \u00B7 no cost tracking \u00B7 n = 2", { x: 2.4, y: 6.78, w: 10.2, h: 0.35, fontFace: B, fontSize: NOTE, color: MUT });
  notes(s, "Install verified live via fcc-claude earlier. Cases: named, and confounds labeled.");
}

// ============ 12 · HOW WE BENCHMARK ============
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
// ============ 13 · RAW EVIDENCE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Benchmark \u00B7 raw evidence");
  title(s, "Terminal output, verbatim", "Real bench-kit output \u2014 GREENFIELD-3 (rate-limited SSE proxy), same model, same brief.");
  s.addShape("rect", { x: 0.75, y: 2.3, w: 5.85, h: 3.5, fill: { color: "111827" }, line: { width: 0 } });
  s.addText("METRICS", { x: 0.95, y: 2.4, w: 2.0, h: 0.28, fontFace: B, fontSize: 13, bold: true, color: "F4B400", margin: 0 });
  const mono = [
    "metric          A activated       B bare",
    "wall (min)            6.5          27.4",
    "turns                  56            61",
    "cost                 1.08          2.84",
    "in tokens           50991         85443",
    "out tokens          42779        144366",
    "TEST GATE \u00B7 pytest tests/ -q",
    "A 24 passed [COMPLETED] \u00B7 56 turns",
    "B 22 passed [HALTED] \u00B7 61 turns",
    "  terminal: max_turns (mid-tool-use)",
  ];
  mono.forEach((l, i) => {
    const c = l.startsWith("metric") || l.startsWith("TEST") ? "F4B400"
      : l.indexOf("COMPLETED") >= 0 ? "6EE7B7"
      : l.indexOf("HALTED") >= 0 ? "FCA5A5"
      : "F3F4F6";
    s.addText(l, { x: 0.95, y: 2.68 + i * 0.295, w: 5.55, h: 0.28, fontFace: MONO, fontSize: 14, bold: l.startsWith("metric") || l.startsWith("TEST"), color: c, margin: 0 });
  });
  s.addText("Interpretation: A finished at 56 turns; B was stopped mid-tool-use at 61 \u2014 more spent, less delivered.", { x: 0.95, y: 5.95, w: 5.55, h: 0.3, fontFace: B, fontSize: 13, color: "1F2937" });
  s.addText("B BARE \u2014 27.4 min \u00B7 $2.84 \u00B7 22 tests", { x: 7.0, y: 2.35, w: 5.6, h: 0.36, fontFace: B, fontSize: 16, bold: true, color: "B91C1C" });
  const left = [
    ["  app/  tests/  \u2014 no spec/plan/tasks", 14, false],
    ["  session halted before completion", 12.5, false],
    ["A ACTIVATED \u2014 6.5m \u00B7 $1.08 \u00B7 24 tests", 16, true],
    ["  app/  tests/  docs/qa/", 14, false],
    ["  docs/product/product.md", 14, false],
    ["  .specify/features/rate-limited-sse-proxy/", 14, false],
    ["    spec.md \u00B7 impl-plan.md \u00B7 tasks.md", 13.5, false],
    ["  QA lane verified the work", 12.5, false],
  ];
  let ly = 2.85;
  left.forEach(([t, fs, b]) => {
    s.addText(t, { x: 7.0, y: ly, w: 5.6, h: 0.3, fontFace: MONO, fontSize: fs, bold: b, color: b ? GREEND : "1F2937", margin: 0 });
    ly += b ? 0.38 : 0.3;
  });
  s.addText("The framework arm finished 4.2\u00D7 faster \u2014 and left a traceability trail.", { x: 0.75, y: 6.35, w: 11.85, h: 0.4, fontFace: B, fontSize: 19, bold: true, color: NAVY });
  s.addText("Offline gates only \u2014 the devops lanes (CI \u00B7 Vercel ops \u00B7 rollback) fire on live projects, not in a lab bench.", { x: 0.75, y: 6.8, w: 11.85, h: 0.35, fontFace: B, fontSize: 14, color: "4B5563" });
  notes(s, "Verbatim bench-kit table. Read the B line out loud: halted at max_turns with more spent. The framework's value concentrates exactly here.");
}
// ============ 14 · BENCHMARK CASES & REPRODUCTION ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Benchmark \u00B7 what & how");
  title(s, "The four frozen cases, and how to run them", "Same briefs \u00B7 same model pin \u00B7 both arms \u2014 a difficulty gradient on purpose.");
  s.addText("CASE", { x: 0.9, y: 2.0, w: 2.7, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
  s.addText("WHAT IT TESTS \u00B7 WHY IT EXISTS", { x: 3.7, y: 2.0, w: 4.7, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
  s.addText("GATE", { x: 8.5, y: 2.0, w: 1.9, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY, align: "center" });
  s.addText("RESULT (B / A)", { x: 10.5, y: 2.0, w: 1.9, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY, align: "center" });
  const cases = [
    ["G-1 \u00B7 E2E pipeline", "Research request \u2192 queue \u2192 background worker \u2192 live status + final result. Full FE+BE+DB integration \u2014 the realistic product shape.", "pytest tests/ -q", "13 / 17 tests"],
    ["G-2 \u00B7 FE virtualized feed", "Infinite feed, optimistic likes, windowed rendering; engine.js must stay zero-dependency. Narrow but deep front-end.", "node --test tests/", "24 / 22 tests"],
    ["G-3 \u00B7 BE SSE proxy (HARD)", "Token buckets, backpressure, heartbeats, clean shutdown. The difficulty case \u2014 where churn shows up.", "pytest tests/ -q", "22 / 24 tests \u00B7 bare halted"],
    ["G-4 \u00B7 DB+ETL 1M rows", "Event ingestion + idempotent nightly rollup at scale (SQLite only), perf + re-run asserts.", "pytest + etl/perf_test.py", "8 / 6 tests \u00B7 perf \u2713"],
  ];
  let y = 2.3;
  cases.forEach(([c, w, g, r]) => {
    card(s, 0.75, y, 11.85, 0.78, CARD, BORDER);
    s.addText(c, { x: 0.9, y: y + 0.1, w: 2.7, h: 0.55, fontFace: B, fontSize: 13, bold: true, color: NAVY, margin: 0 });
    s.addText(w, { x: 3.7, y: y + 0.1, w: 4.7, h: 0.55, fontFace: B, fontSize: 12.5, color: TXT, margin: 0 });
    s.addText(g, { x: 8.5, y: y + 0.1, w: 1.9, h: 0.55, fontFace: MONO, fontSize: 12, color: TXT, align: "center", margin: 0 });
    s.addText(r, { x: 10.5, y: y + 0.1, w: 1.9, h: 0.55, fontFace: B, fontSize: 12, color: GREEND, align: "center", margin: 0 });
    y += 0.84;
  });
  card(s, 0.75, 5.75, 11.85, 1.5, "111827", null);
  s.addText("RUN FROM SCRATCH", { x: 1.0, y: 5.9, w: 3.0, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: "F4B400", margin: 0 });
  s.addText("python bench/greenfield.py --base /tmp/gf --name r1 --task bench/tasks/greenfield-e2e-pipeline.md --gate \"pytest tests/ -q\" --out bench-out/x", { x: 1.0, y: 6.2, w: 11.35, h: 0.3, fontFace: MONO, fontSize: 11.5, color: "D1D5DB", margin: 0 });
  s.addText("python evidence/validate.py   # prebuilt evidence \u2192 12/12 claims reproduce   \u00B7   bench/brownfield.py --repo <your-repo> --task bench/tasks/brownfield-add-tests.md --gate \"<test cmd>\"   \u00B7   frozen briefs: bench/tasks/", { x: 1.0, y: 6.55, w: 11.35, h: 0.3, fontFace: MONO, fontSize: 11, color: "D1D5DB", margin: 0 });
  s.addText("Same briefs, same model pin, metered, non-merge exp branches \u00B7 \u224830\u201340 min per case (both arms).", { x: 1.0, y: 6.85, w: 11.35, h: 0.3, fontFace: B, fontSize: 12.5, color: "9FB0DC", margin: 0 });
  notes(s, "The four cases are the difficulty gradient: integration, deep FE, hard BE concurrency, data at scale. Point at bench/tasks/ as the frozen texts.");
}

// ============ 15 · EVIDENCE — FOLDER STRUCTURE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Benchmark \u00B7 raw evidence");
  title(s, "Folder structure, verbatim", "Same frozen task (BE SSE proxy), two arms \u2014 what the bare run leaves vs what the framework run leaves.");
  s.addText("B \u00B7 BARE \u2014 greenfield/be-b", { x: 0.65, y: 2.05, w: 5.9, h: 0.35, fontFace: B, fontSize: 16, bold: true, color: "B91C1C" });
  s.addText("A \u00B7 ACTIVATED \u2014 greenfield/be-a", { x: 6.85, y: 2.05, w: 5.9, h: 0.35, fontFace: B, fontSize: 16, bold: true, color: GREEND });
  s.addImage({ path: __dirname + "/evidence-be-b.png", x: 0.65, y: 2.45, w: 5.6, h: 4.03 });
  s.addImage({ path: __dirname + "/evidence-be-a.png", x: 6.85, y: 2.45, w: 5.6, h: 4.03 });
  s.addText("The bare arm leaves app/ + tests/ only. The framework arm leaves the same code PLUS .claude/ (agents + skills + rules), .specify/ (spec \u00B7 plan \u00B7 tasks), docs/product, docs/qa \u2014 the traceability trail, committed in the repo.", { x: 0.65, y: 6.5, w: 11.85, h: 0.6, fontFace: B, fontSize: NOTE, bold: true, color: NAVY });
  s.addText("Full trees + install payload + scaffold: evidence/tree/ \u00B7 all 12 projects runnable \u00B7 python evidence/validate.py \u2014 12/12 claims reproduce.", { x: 0.65, y: 6.95, w: 11.85, h: 0.4, fontFace: B, fontSize: 13, italic: true, color: MUT });
  notes(s, "Screenshots are generated views of the real evidence/tree/ captures (pyc masked, skills sub-tree elided to a count note). Point at evidence/.");
}

// ============ 16 · BENCHMARK (MEASURED MATRIX) ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Benchmark \u00B7 4 runs, 3 arms");
  title(s, "Measured: bare vs passive vs activated", "Same repos \u00B7 frozen tasks \u00B7 one model \u00B7 metered. Non-merge exp branches (froam).");
  const rows = [
    ["R1 \u00B7 add-tests (trivial)", "$0.63 \u00B7 6 tests", "$0.62 \u00B7 7 tests", "$0.47 \u00B7 10 tests \u00B7 2.5\u00D7 turns"],
    ["R2 \u00B7 DB + RLS", "$0.22 \u00B7 11 tests", "$0.27 \u00B7 11 tests", "$0.67 \u00B7 11 tests + plan/QA"],
    ["R4 \u00B7 fragile refactor", "refused \u00B7 restraint pass", "n/a", "guardrail advisory violated \u00B7 prod-correct when approved"],
    ["R3 \u00B7 vertical FE+BE", "$0.94 \u00B7 4 tests", "n/a", "$0.98 \u00B7 4 tests + plan/tasks"],
  ];
  let y = 2.3;
  s.addText("TASK", { x: 0.9, y: 2.02, w: 2.9, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: NAVY });
  s.addText("B \u00B7 BARE", { x: 4.0, y: 2.02, w: 2.5, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: NAVY, align: "center" });
  s.addText("A\u2032 \u00B7 PASSIVE", { x: 6.6, y: 2.02, w: 2.5, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: NAVY, align: "center" });
  s.addText("A \u00B7 ACTIVATED", { x: 9.2, y: 2.02, w: 3.3, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: NAVY, align: "center" });
  rows.forEach(([m, b, p, a]) => {
    card(s, 0.75, y, 11.85, 0.82, CARD, BORDER);
    s.addText(m, { x: 0.9, y: y + 0.16, w: 2.9, h: 0.5, fontFace: B, fontSize: 14.5, bold: true, color: NAVY });
    s.addText(b, { x: 4.0, y: y + 0.16, w: 2.5, h: 0.5, fontFace: B, fontSize: 14, color: TXT, align: "center" });
    s.addText(p, { x: 6.6, y: y + 0.16, w: 2.5, h: 0.5, fontFace: B, fontSize: 14, color: TXT, align: "center" });
    s.addText(a, { x: 9.2, y: y + 0.16, w: 3.3, h: 0.5, fontFace: B, fontSize: 14, color: "1B5E20", align: "center" });
    y += 0.94;
  });
  s.addText("Findings: passive \u2248 bare (placebo) \u00B7 activation tax scales with ceremony, benefit with risk \u00B7 restraint is advisory, not structural \u2014 the QA lane is the value on risky approved change.", { x: 0.75, y: 6.15, w: 11.85, h: 0.55, fontFace: B, fontSize: 16, bold: true, color: NAVY });
  s.addText("Harness gap fixed via dev-agent-router (16 to 17 skills) \u00B7 model pinned since R2 \u00B7 SWE-bench-style floor check: pending \u00B7 \u2014/ n/a = not run.", { x: 0.75, y: 6.72, w: 11.85, h: 0.4, fontFace: B, fontSize: 13.5, color: "4B5563" });
  notes(s, "4 runs, 3 arms, real numbers, real gaps. Read the R4 line out loud: the guardrail is advisory — that is the honesty that earns trust.");
}

// ============ 17 · MATERIALS & LINKS ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Resources");
  title(s, "Everything is in the repo", "Framework \u00B7 bench kit \u00B7 evidence \u00B7 demo guide \u2014 one link each, all public.");
  const links = [
    ["Recommended fork \u2014 framework \u00B7 plugin \u00B7 bench kit \u00B7 deck source", "trac41799/claude-code-agentic-sdlc"],
    ["Raw evidence \u2014 trees + bench projects + validator", "evidence/ (README \u00B7 manifest \u00B7 validate.py)"],
    ["Benchmark evidence \u2014 12 runs, repro commands", "docs/benchmarks/BENCHMARK-SUMMARY.md"],
    ["Live demo run guide (\u226410 min)", "docs/demo/live-demo-guide.md"],
    ["Client setup \u2014 5 prompts for non-technical founders", "docs/guide/CLIENT-SETUP.md"],
    ["Benchmark product \u2014 FE (froam)", "trac41799/froam-journey-platform-fe"],
    ["Benchmark product \u2014 BE (froam)", "trac41799/travelbuddy-agentic-be"],
    ["Official origin (ex-company) \u2014 v1 history, read-only", "talentedgeai/infinite-leverage"],
    ["Client cases", "janet.care \u00B7 occuspan.com"],
    ["Tool stack", "claude.com \u00B7 github.com \u00B7 vercel.com \u00B7 supabase.com"],
  ];
  let y = 2.1;
  links.forEach(([t, u]) => {
    card(s, 0.75, y, 11.85, 0.44, CARD, BORDER);
    s.addText(t, { x: 1.0, y: y + 0.06, w: 6.2, h: 0.32, fontFace: B, fontSize: 13, bold: true, color: NAVY, margin: 0 });
    s.addText(u, { x: 7.3, y: y + 0.06, w: 5.1, h: 0.32, fontFace: MONO, fontSize: 12.5, bold: true, color: "1F4FBF", align: "right", margin: 0 });
    y += 0.47;
  });
  s.addText("Every number on the results slides reruns with one command from the bench kit.", { x: 0.75, y: 6.95, w: 11.85, h: 0.35, fontFace: B, fontSize: 14, color: "4B5563" });
  notes(s, "Give this slide time: every artifact referenced here exists and is public.");
}

// ============ 18 · THE ORIGIN (V1) ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "History");
  title(s, "v1 \u2014 the fully automated agent-team", "\u201CInfinite Leverage\u201D (2026) \u00B7 reconstructed from the public commit tree.");
  card(s, 0.75, 2.3, 5.85, 4.1, "FBF3E2", AMBERD);
  s.addText("THE ORIGINAL SCOPE", { x: 1.05, y: 2.5, w: 5.25, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: "7A5C00" });
  const scope = [
    "8 agents \u2014 dev + marketing",
    "  DEV: product-manager \u00B7 developer \u00B7 devops",
    "       qa \u00B7 web-publisher",
    "  MKT: writer \u00B7 designer \u00B7 email-marketer",
    "       (+ marketing-strategist)",
    "Global install: ~/.claude/ agents \u00B7 hooks \u00B7",
    "  skills \u00B7 scheduled-tasks (zip + patch)",
    "62 workflow skills, zipped per agent",
    "Settings: Bash(\u002A) grant \u00B7 acceptEdits",
  ];
  let sy = 3.0;
  scope.forEach((l) => {
    s.addText(l, { x: 1.05, y: sy, w: 5.3, h: 0.31, fontFace: MONO, fontSize: 13, color: "3D2F00", margin: 0 });
    sy += 0.36;
  });
  card(s, 6.85, 2.3, 5.75, 4.3, "EAF0FB", MID);
  s.addText("ROUTINES \u2014 NO HUMAN IN THE LOOP", { x: 7.15, y: 2.5, w: 5.15, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: NAVY });
  s.addText("ROUTINE", { x: 7.15, y: 2.95, w: 2.3, h: 0.3, fontFace: B, fontSize: 11.5, bold: true, color: NAVY, margin: 0 });
  s.addText("SCHEDULE", { x: 9.5, y: 2.95, w: 1.1, h: 0.3, fontFace: B, fontSize: 11.5, bold: true, color: NAVY, margin: 0 });
  s.addText("ACTION", { x: 10.7, y: 2.95, w: 1.8, h: 0.3, fontFace: B, fontSize: 11.5, bold: true, color: NAVY, margin: 0 });
  const sched = [
    ["pm-daily-plan", "wk 07:03", "auto-approve"],
    ["pm-standup-compile", "wk 18:07", "+ PR"],
    ["pm-eod-summary", "wk 18:37", ""],
    ["pm-weekly-rag", "Fr 17:07", "+ PR"],
    ["writer-weekly", "Mo 09:03", "blog brief"],
    ["designer-weekly", "Tu 09:03", "hero.webp"],
    ["web-publisher-weekly", "We 09:03", "build + idx"],
    ["email-marketer-weekly", "Th 10:03", "newsletter"],
    ["devops-daily health", "daily 06:00", ""],
  ];
  let ty = 3.28;
  sched.forEach(([n, t, a]) => {
    s.addText(n, { x: 7.15, y: ty, w: 2.3, h: 0.28, fontFace: MONO, fontSize: 12.5, color: "1F2937", margin: 0 });
    s.addText(t, { x: 9.5, y: ty, w: 1.15, h: 0.28, fontFace: MONO, fontSize: 12.5, color: "1F2937", margin: 0 });
    s.addText(a, { x: 10.7, y: ty, w: 1.8, h: 0.28, fontFace: MONO, fontSize: 12.5, color: "1F2937", margin: 0 });
    ty += 0.29;
  });
  s.addText("Persistence: CronCreate \u2192 RemoteTrigger (cloud-persistent)", { x: 7.15, y: 5.98, w: 5.25, h: 0.26, fontFace: B, fontSize: 12.5, bold: true, color: "1F2937" });
  s.addText("Hooks: pre-bash \u00B7 prompt-submit \u00B7 SessionStart/End \u00B7 telemetry \u2192 Supabase", { x: 7.15, y: 6.26, w: 5.25, h: 0.26, fontFace: B, fontSize: 12.5, color: "1F2937" });
  tag(s, 0.75, 6.62, "VERIFIED");
  s.addText("Commit trail: 5c89076 \u201C8 scheduled task templates using CronCreate\u201D (durable=true \u00B7 auto-expire 7 days)", { x: 2.5, y: 6.62, w: 10.0, h: 0.3, fontFace: B, fontSize: 12.5, color: "4B5563" });
  s.addText("Supporting: 9291df3 \u00B7 b753023 \u00B7 a218b79 hooks \u00B7 fff7a9a telemetry \u00B7 e2d5d67 init", { x: 2.5, y: 6.9, w: 10.0, h: 0.3, fontFace: B, fontSize: 12.5, color: "4B5563" });
  notes(s, "The original pitch: an agent team that builds and markets, running overnight with no human. It worked \u2014 until the machine drifted.");
}

// ============ 19 · V1 VS V2 ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "History");
  title(s, "v1 \u2192 v2: what changed, and why", "Same goal \u2014 leverage. Different trust model.");
  const rows = [
    ["Install surface", "~/.claude/ global \u2014 zip + patch", "marketplace plugin \u00B7 per-project .claude/"],
    ["Automation", "10 cron routines \u00B7 auto-approve \u00B7 overnight", "none \u2014 every gate is a human decision"],
    ["Hooks", "6+ silent session/tool hooks", "zero in public \u2014 guardrails/pre-commit are project-scoped, on request"],
    ["Permissions", "Bash(\u002A) grant \u00B7 acceptEdits default", "never touches permissions"],
    ["Agents & lanes", "8\u20139 \u2014 dev + marketing (writer/designer/email)", "4 \u2014 engineering only; publishing folded into developer"],
    ["Telemetry", "in-product \u00B7 auto-delivered \u00B7 human-hours", "split to a private plugin"],
    ["Updates", "zip/patch + SessionStart auto-update", "marketplace \u00B7 lockstep \u00B7 doctor diffs versions"],
  ];
  s.addText("DIMENSION", { x: 0.95, y: 2.05, w: 2.0, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: MUT });
  s.addText("V1 \u00B7 INFINITE LEVERAGE", { x: 3.05, y: 2.05, w: 4.5, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: "B91C1C", align: "center" });
  s.addText("V2 \u00B7 AGENTIC SDLC", { x: 7.65, y: 2.05, w: 5.2, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: GREEND, align: "center" });
  let ry = 2.28;
  rows.forEach(([dim, v1, v2]) => {
    card(s, 0.75, ry, 11.85, 0.5, CARD, BORDER);
    s.addText(dim, { x: 0.95, y: ry + 0.08, w: 2.0, h: 0.34, fontFace: B, fontSize: 12, bold: true, color: NAVY, margin: 0 });
    s.addText(v1, { x: 3.05, y: ry + 0.08, w: 4.5, h: 0.34, fontFace: B, fontSize: 11.5, color: "B91C1C", margin: 0 });
    s.addText(v2, { x: 7.65, y: ry + 0.08, w: 4.85, h: 0.34, fontFace: B, fontSize: 11.5, color: GREEND, margin: 0 });
    ry += 0.54;
  });
  s.addText("V1 trade-off: autonomy + overnight output \u2014 paid in machine drift, silent cost, frozen updates (2.5 months).  V2 trade-off: repeatability + trust \u2014 paid in no overnight automation, no marketing lanes.", { x: 0.75, y: 6.15, w: 9.5, h: 0.55, fontFace: B, fontSize: 13, bold: true, color: NAVY });
  tag(s, 10.65, 6.22, "VERIFIED");
  s.addText("Why v1 fails: global state drifts \u00B7 routines rot silently (7-day cron expiry, nobody re-registers) \u00B7 auto-approve + Bash(\u002A) erode trust \u00B7 zip/patch froze fixes \u00B7 telemetry-in-product privacy surface \u00B7 marketing lanes unmeasured.", { x: 0.75, y: 6.78, w: 11.85, h: 0.4, fontFace: B, fontSize: 11.5, italic: true, color: MUT });
  notes(s, "The honest version of the story: v1 worked until it drifted. v2 gave up overnight autonomy for gates that hold.");
}

// ============ 20 · GAPS — WHAT WE KNOW WE LACK ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Honest yardsticks");
  title(s, "What we know we lack", "Measured gaps first \u2014 then what we deliberately left out \u00B7 full analysis: GAP-ANALYSIS.md.");
  card(s, 0.75, 2.3, 5.85, 3.75, "FBF3E2", AMBERD);
  s.addText("MEASURED GAPS", { x: 1.05, y: 2.5, w: 5.25, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: "7A5C00" });
  const gaps = [
    ["COST \u00B7 HIGH", "No trusted metering \u2014 cost basis unknown, cache reads inflate A+wave 5\u20138\u00D7; no per-task budget; a wrong-model probe ($0.17/turn) slipped through."],
    ["GUARDRAILS \u00B7 HIGH", "Advisory, not mechanical \u2014 R4 pushed a fragile-file change through an operator approval; no CI check enforces plan-vs-PR files."],
    ["BENCH \u00B7 MED", "Every cell is N=1 \u2014 variance unmeasured; the 4.2\u00D7 headline is one run."],
    ["DEVOPS \u00B7 MED", "CI/Vercel/rollback lanes never fire offline \u2014 live-tested only, no regression cell."],
    ["HUMAN-HOUR \u00B7 MED", "Method exists (hooks + PR windows) \u2014 public evidence still pending."],
  ];
  let gy = 2.92;
  gaps.forEach(([h, t]) => {
    s.addText(h, { x: 1.05, y: gy, w: 1.35, h: 0.26, fontFace: B, fontSize: 11, bold: true, color: "B91C1C", margin: 0 });
    s.addText(t, { x: 2.45, y: gy, w: 3.65, h: 0.58, fontFace: B, fontSize: 11, color: TXT, margin: 0 });
    gy += 0.62;
  });
  card(s, 6.85, 2.3, 5.75, 3.75, "EAF5EC", GREEN);
  s.addText("DELIBERATELY NOT INCLUDED", { x: 7.15, y: 2.5, w: 5.15, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: GREEND });
  const out = [
    "No hooks / auto-runtime / silent telemetry \u2014 v1 lesson",
    "No auto-approve \u2014 every gate is a human decision",
    "No marketing agent lanes \u2014 removed v2.6.0 (unmeasured)",
    "No permissions grants \u2014 Bash(*) killed v1",
    "No SWE-bench floor \u2014 documented trade-off",
    "No global memory \u2014 repo artifacts ARE the memory",
    "No wave loop in canonical \u2014 negative in headless proxy",
  ];
  let oy = 3.0;
  out.forEach((t) => {
    s.addText("\u2022 " + t, { x: 7.15, y: oy, w: 5.15, h: 0.34, fontFace: B, fontSize: 12, color: TXT, margin: 0 });
    oy += 0.38;
  });
  s.addText("FOCUS LIST \u00B7 next: trusted cost loop (pin check + baseline + budgets) \u00B7 CI plan-vs-PR + fragile-file enforcement \u00B7 headline cells N\u22653 \u00B7 devops staging smoke \u00B7 second-model matrix.", { x: 0.75, y: 6.3, w: 11.85, h: 0.5, fontFace: B, fontSize: 14, bold: true, color: NAVY });
  tag(s, 0.75, 6.85, "VERIFIED");
  s.addText("Gap list is provable; exclusions are design choices, not defects \u2014 both are in GAP-ANALYSIS.md.", { x: 2.5, y: 6.88, w: 9.9, h: 0.35, fontFace: B, fontSize: 12, italic: true, color: MUT });
  notes(s, "Say the cost gap out loud BEFORE they ask — the wrong-model probe is the proof we don't hide. Exclusions: read the v1 lesson slide before they suggest 'just enable hooks'.");
}

// ============ 21 · OPEN POINTS → NEXT MOVES ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Roadmap \u00B7 next moves");
  title(s, "Open points \u2192 committed moves", "Seven gaps we admit, seven fixes we're building \u2014 the post-meeting commitment list.");
  card(s, 0.75, 2.25, 5.85, 4.6, "FBF3E2", AMBERD);
  s.addText("OPEN POINTS", { x: 1.05, y: 2.45, w: 5.25, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: "7A5C00" });
  const pts = [
    ["COST", "No trusted metering, no budget"],
    ["COMPARISON", "No arm vs another SDLC framework"],
    ["METRICS", "N=1 cells, variance unmeasured"],
    ["EVIDENCE", "Handoffs lean on tests; thin for UI/UX"],
    ["QUALITY", "TDD + human review only"],
    ["AGENTS", "Model/effort inherited from parent"],
    ["HUMANS", "No brownfield onboarding path"],
  ];
  let ly = 2.95;
  pts.forEach(([h, t]) => {
    s.addText(h, { x: 1.05, y: ly, w: 1.4, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: "B91C1C", margin: 0 });
    s.addText(t, { x: 2.5, y: ly, w: 3.65, h: 0.45, fontFace: B, fontSize: 11, color: TXT, margin: 0 });
    ly += 0.55;
  });
  card(s, 6.85, 2.25, 5.75, 4.6, "EAF5EC", GREEN);
  s.addText("NEXT MOVES", { x: 7.15, y: 2.45, w: 5.15, h: 0.4, fontFace: B, fontSize: 17, bold: true, color: GREEND });
  const moves = [
    ["GOVERNOR", "Hard USD cap per run + banner"],
    ["BENCH ARM", "Mass real-world set + comparison arm"],
    ["N\u22653", "Variance + context-read metrics"],
    ["GATES", "5-tier chain \u2192 manifest per PR"],
    ["MUTATION", "Mutation/contract/BDD tiers + freezer"],
    ["AGENTS", "TBD \u2014 candidate: model pin, reject wrong"],
    ["BRIEF", "Onboarding map \u00B7 commands \u00B7 risks"],
  ];
  let ry = 2.95;
  moves.forEach(([h, t]) => {
    s.addText(h, { x: 7.15, y: ry, w: 1.55, h: 0.3, fontFace: B, fontSize: 11, bold: true, color: GREEND, margin: 0 });
    s.addText(t, { x: 8.75, y: ry, w: 3.55, h: 0.45, fontFace: B, fontSize: 11, color: TXT, margin: 0 });
    ry += 0.55;
  });
  tag(s, 0.75, 6.95, "PLANNED");
  s.addText("Seven gaps, seven committed moves \u2014 tracked in docs/demo/open-points.md \u00B7 evidence in GAP-ANALYSIS.md.", { x: 2.5, y: 6.98, w: 10, h: 0.35, fontFace: B, fontSize: 12, italic: true, color: MUT });
  notes(s, "One-to-one mapping of the post-meeting open points to committed moves (docs/demo/open-points.md). Row 6 (AGENTS) is the only one without a decided fix \u2014 candidate: per-agent model pin with wrong-pin rejection (GAP-ANALYSIS G1 fix path).");
}

// ============ 22 · CLOSE ============
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x: -2.2, y: 4.4, w: 5.6, h: 5.6, fill: { color: "27346E" }, line: { width: 0 } });
  s.addText("WHAT WE KNOW", { x: 0.8, y: 0.85, w: 11.7, h: 0.4, fontFace: B, fontSize: 14, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("Built from experience. Graded by evidence.", { x: 0.8, y: 1.3, w: 11.7, h: 0.85, fontFace: H, fontSize: 42, bold: true, color: WHITE });
  const gaps = [
    "Benchmark: 12 metered runs \u2014 value proven where difficulty lives; gaps labeled, not hidden",
    "Tokens: no budget yet \u2014 cheap to meter, baseline next",
    "Method: SDD + TDD + 4-agent team \u2014 12 measured runs + two POCs; lab confounds labeled",
    "Human-hour ratio: measured via hooks + PR windows \u2014 target LOW",
  ];
  s.addText(gaps.map(g => ({ text: g, options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } })),
    { x: 0.8, y: 2.65, w: 11.7, h: 2.7, fontFace: B, fontSize: BODY_SM, color: ICE });
  s.addText("Next: trusted cost loop \u00B7 CI plan-vs-PR enforcement \u00B7 N\u22653 headline cells \u00B7 devops staging smoke \u00B7 second-model matrix.", { x: 0.8, y: 5.55, w: 11.7, h: 0.5, fontFace: B, fontSize: BODY_SM, bold: true, color: AMBER });
  s.addText("Not a solved discipline \u2014 a repeatable, honest one.", { x: 0.8, y: 6.35, w: 11.7, h: 0.5, fontFace: H, fontSize: 23, italic: true, bold: true, color: WHITE });
  notes(s, "Close on the gaps. That is the part we defend most.");
}

pptx.writeFile({ fileName: process.env.PPTX_OUT || __dirname + "/Agentic-SDLC-Tech-Audience.pptx" }).then(f => console.log("wrote", f));