// Agentic SDLC — CONDENSED deck (9 slides). Shares design system + assets with
// the full 20-slide deck; keeps rationale, workings, both diagrams, outputs,
// benchmarks, strengths & weaknesses. Build: node docs/slides/build-deck-condensed.js
const pptxgen = require("C:/Users/mrtra/AppData/Local/Temp/opencode/svgconv/node_modules/pptxgenjs");
const pptx = new pptxgen();

pptx.layout = "LAYOUT_WIDE";
pptx.author = "Agentic SDLC";
pptx.title = "Agentic SDLC \u2014 condensed (9 slides)";

const NAVY = "1E2761", ICE = "EAF0FB", MID = "5A6B9E", AMBER = "F4B400", AMBERD = "B98A00";
const GREEN = "2E7D32", GREEND = "1B5E20", TXT = "1F2937", MUT = "6B7280", WHITE = "FFFFFF";
const CARD = "F8FAFC", BORDER = "D1D5DB";
const H = "Cambria", B = "Calibri", MONO = "Courier New";

const T_TITLE = 40, T_SUB = 18, EYEBROW = 13, PILL = 11;
const BODY = 20, BODY_SM = 18, CARD_T = 22, NOTE = 14, SMALLP = 15;

function eyebrow(s, text, color) {
  s.addText(text.toUpperCase(), { x: 0.55, y: 0.28, w: 12, h: 0.32, fontFace: B, fontSize: EYEBROW, bold: true, color: color || AMBERD, charSpacing: 2 });
}
function title(s, text, sub) {
  s.addText(text, { x: 0.55, y: 0.6, w: 12.2, h: 0.85, fontFace: H, fontSize: T_TITLE, bold: true, color: NAVY });
  if (sub) s.addText(sub, { x: 0.55, y: 1.45, w: 12.2, h: 0.5, fontFace: B, fontSize: T_SUB, color: MUT });
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
  s.addText("Agentic SDLC", { x: 0.8, y: 1.5, w: 11.7, h: 1.6, fontFace: H, fontSize: 66, bold: true, color: WHITE });
  s.addText("An AI-SDLC framework built from delivery experience", { x: 0.8, y: 3.1, w: 11.7, h: 0.6, fontFace: B, fontSize: 24, color: ICE });
  s.addText("4 agents  \u00B7  17 skills  \u00B7  spec-first  \u00B7  test-first  \u00B7  evidence-gated", { x: 0.8, y: 3.85, w: 11.7, h: 0.5, fontFace: B, fontSize: 16, color: "9FB0DC" });
  s.addText("Every claim carries one of these grades:", { x: 0.8, y: 5.7, w: 11.7, h: 0.4, fontFace: B, fontSize: NOTE, color: "9FB0DC" });
  let lx = 0.8;
  ["VERIFIED", "CASE STUDY", "RATIONALE", "PLANNED"].forEach(l => { pill(s, lx, 6.1, l, l === "VERIFIED" ? GREEN : l === "CASE STUDY" ? AMBERD : l === "RATIONALE" ? MID : "7C8698"); lx += 1.9; });
  s.addText("github.com/trac41799/claude-code-agentic-sdlc", { x: 8.6, y: 6.15, w: 4, h: 0.35, fontFace: B, fontSize: 12, color: "7E90C4", align: "right" });
  notes(s, "Condensed deck: rationale, workings, both diagrams, outputs, benchmarks, strengths & weaknesses.");
}

// ============ 2 · RATIONALE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Rationale");
  title(s, "Why a team-shaped framework", "Agents changed the bottleneck. The product is the process.");
  const cards = [
    ["Context loss", "Every session starts cold."],
    ["Handoff tax", "Every handoff loses fidelity."],
    ["Agents shift it", "Bottleneck is process, not code."],
  ];
  let x = 0.75;
  cards.forEach(([t, d]) => {
    card(s, x, 2.35, 3.72, 1.6, CARD, BORDER);
    s.addText(t, { x: x + 0.3, y: 2.55, w: 3.2, h: 0.45, fontFace: H, fontSize: CARD_T, bold: true, color: NAVY });
    s.addText(d, { x: x + 0.3, y: 3.05, w: 3.2, h: 0.5, fontFace: B, fontSize: BODY_SM, color: TXT });
    x += 3.94;
  });
  const stages = ["Requirements", "Design", "Implement", "Test", "Deploy", "Maintain"];
  x = 0.75;
  stages.forEach((st, i) => {
    card(s, x, 4.45, 1.78, 0.62, ICE, MID);
    s.addText(st, { x, y: 4.58, w: 1.78, h: 0.35, fontFace: B, fontSize: 11.5, bold: true, color: NAVY, align: "center", margin: 0 });
    if (i < 5) s.addText("\u2192", { x: x + 1.75, y: 4.5, w: 0.3, h: 0.4, fontFace: B, fontSize: 15, bold: true, color: AMBERD, align: "center", margin: 0 });
    x += 1.98;
  });
  s.addText("v2 principles: nothing installs globally \u00B7 no hooks \u00B7 no auto-approve \u00B7 all change via PR \u00B7 the operator gates every decision.", { x: 0.75, y: 5.5, w: 11.85, h: 0.5, fontFace: B, fontSize: BODY, bold: true, color: GREEND });
  tag(s, 0.75, 6.55, "RATIONALE");
  notes(s, "The v2 model corrects v1's pipeline assumption; v1's overnight autonomy became drift (slide 8).");
}

// ============ 3 · WORKINGS: PRINCIPLE + TEAM + COMMANDS ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Workings");
  title(s, "Principle \u00B7 team \u00B7 commands", "SDD decides, TDD proves \u2014 every gate is a human decision.");
  card(s, 0.75, 2.25, 4.15, 4.55, "FBF3E2", AMBERD);
  s.addText("PRINCIPLE", { x: 1.0, y: 2.45, w: 3.6, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: "7A5C00" });
  const prin = [
    "One request \u2192 PDCA-ish chain: spec \u2192 plan \u2192 TDD \u2192 QA \u2192 PR",
    "Spec before code \u2014 the plan is the contract",
    "Test-first: RED \u2192 GREEN \u2192 REFACTOR per task",
    "Done = gates passed with evidence",
    "Two phases: spec phase + build phase \u2014 each gated",
  ];
  let py = 2.95;
  prin.forEach((t) => {
    s.addText("\u2022 " + t, { x: 1.0, y: py, w: 3.65, h: 0.62, fontFace: B, fontSize: SMALLP, color: TXT, margin: 0 });
    py += 0.72;
  });
  card(s, 5.15, 2.25, 3.45, 4.55, "EAF5EC", GREEN);
  s.addText("TEAM \u00B7 4 AGENTS", { x: 5.4, y: 2.45, w: 2.95, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: GREEND });
  const agents = [
    ["product-manager", "specs \u00B7 epics \u00B7 status"],
    ["developer", "impl. \u00B7 publishing"],
    ["qa", "strategy \u00B7 triage"],
    ["devops", "CI/CD \u00B7 guardrails"],
  ];
  let ay = 2.95;
  agents.forEach(([n, d]) => {
    s.addText(n, { x: 5.4, y: ay, w: 2.95, h: 0.35, fontFace: H, fontSize: 17, bold: true, color: NAVY, margin: 0 });
    s.addText(d, { x: 5.4, y: ay + 0.32, w: 2.95, h: 0.32, fontFace: B, fontSize: SMALLP, color: MUT, margin: 0 });
    ay += 0.78;
  });
  s.addText("Per project \u00b7 installed by", { x: 5.4, y: 6.1, w: 2.95, h: 0.3, fontFace: B, fontSize: 12.5, italic: true, color: MUT, margin: 0 });
  s.addText("/asdlc-project  \u00B7  /asdlc-adopt", { x: 5.4, y: 6.38, w: 2.95, h: 0.3, fontFace: B, fontSize: 13, bold: true, color: GREEND, margin: 0 });
  card(s, 8.85, 2.25, 3.7, 4.55, ICE, MID);
  s.addText("COMMANDS", { x: 9.1, y: 2.45, w: 3.2, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: NAVY });
  const cmds = [
    ["/asdlc-project", "scaffold a new client project + team"],
    ["/asdlc-adopt", "install the team into an existing repo"],
    ["/asdlc-doctor", "setup check \u2014 prerequisites, layout"],
    ["/asdlc-tools", "status-first CLI + Supabase MCP installer"],
    ["/asdlc-memory-cleanup", "human-in-the-loop memory tidy"],
  ];
  let cy = 2.95;
  cmds.forEach(([c, d]) => {
    s.addText(c, { x: 9.1, y: cy, w: 3.2, h: 0.32, fontFace: MONO, fontSize: 12, bold: true, color: GREEND, margin: 0 });
    s.addText(d, { x: 9.1, y: cy + 0.3, w: 3.2, h: 0.3, fontFace: B, fontSize: 12, color: TXT, margin: 0 });
    cy += 0.7;
  });
  notes(s, "Plugin ships 5 commands; workflow skills live per project (stage-lane per the cycle diagram).");
}

// ============ 4 · DIAGRAM 1: SDLC CYCLE ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The model");
  title(s, "One SDLC cycle, two entry points", "Greenfield \u00B7 brownfield \u00B7 a skill lane per stage.");
  s.addImage({ path: __dirname + "/sdlc-cycle.png", x: 0.7, y: 2.1, w: 11.9, h: 4.32 });
  s.addText("Every stage has a skill; every entry has a command \u2014 /asdlc-project (new) \u00B7 /asdlc-adopt (existing) \u00B7 /asdlc-doctor verifies anytime.", { x: 0.7, y: 6.6, w: 11.9, h: 0.45, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "The cycle is standard SDLC; the framework only owns the lanes.");
}

// ============ 5 · DIAGRAM 2: FLOW ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "The flow");
  title(s, "One request \u2192 merged PR", "Spec gate \u00B7 plan gate \u00B7 TDD per task \u00B7 QA before merge.");
  s.addImage({ path: __dirname + "/workflow-diagram.png", x: 0.45, y: 2.0, w: 12.45, h: 4.52 });
  s.addText("Three lanes, two approvals, one PR \u2014 the human decides, the team executes, gates hold.", { x: 0.45, y: 6.7, w: 12.45, h: 0.5, fontFace: B, fontSize: NOTE, italic: true, color: MUT });
  notes(s, "The human gates are where trust is built: spec, plan, merge.");
}

// ============ 6 · OUTPUTS ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Outputs");
  title(s, "What a run leaves behind", "Same frozen task (BE SSE proxy): bare vs framework arm.");
  s.addText("B \u00B7 BARE", { x: 0.65, y: 2.0, w: 5.6, h: 0.32, fontFace: B, fontSize: 15, bold: true, color: "B91C1C" });
  s.addText("A \u00B7 ACTIVATED", { x: 6.85, y: 2.0, w: 5.6, h: 0.32, fontFace: B, fontSize: 15, bold: true, color: GREEND });
  s.addImage({ path: __dirname + "/evidence-be-b.png", x: 0.65, y: 2.4, w: 5.05, h: 3.64 });
  s.addImage({ path: __dirname + "/evidence-be-a.png", x: 6.85, y: 2.4, w: 5.05, h: 3.64 });
  s.addText("Bare: code + tests only. Framework arm: code + tests + .claude/ team + .specify/ (spec \u00B7 plan \u00B7 tasks) + docs/product + docs/qa \u2014 the traceability trail.", { x: 0.65, y: 6.2, w: 11.85, h: 0.55, fontFace: B, fontSize: NOTE, bold: true, color: NAVY });
  s.addText("All 12 projects + session JSONs + trees are in evidence/ \u00B7 python evidence/validate.py reruns every gate \u2014 12/12 claims reproduce.", { x: 0.65, y: 6.75, w: 11.85, h: 0.4, fontFace: B, fontSize: 13, italic: true, color: MUT });
  notes(s, "Point at evidence/validate.py \u2014 it reproves the whole bench.");
}
// ============ 7 · BENCHMARKS ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Benchmarks \u00B7 same model, frozen tasks");
  title(s, "Measured: bare vs passive vs activated", "R1\u2013R4 incremental + greenfield suite \u2014 metered, non-merge, one pin.");
  const rows = [
    ["R1 \u00B7 add-tests (trivial)", "$0.63 \u00B7 6 tests", "$0.62 \u00B7 7 tests", "$0.47 \u00B7 10 tests \u00B7 2.5\u00D7 turns"],
    ["R2 \u00B7 DB + RLS", "$0.22 \u00B7 11 tests", "$0.27 \u00B7 11 tests", "$0.67 \u00B7 11 tests + plan/QA"],
    ["R3 \u00B7 vertical FE+BE", "$0.94 \u00B7 4 tests", "n/a", "$0.98 \u00B7 4 tests + plan/tasks"],
    ["R4 \u00B7 fragile refactor", "refused \u00B7 restraint pass", "n/a", "guardrail advisory violated \u00B7 prod-correct when approved"],
  ];
  let y = 2.3;
  s.addText("TASK", { x: 0.9, y: 2.0, w: 2.9, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY });
  s.addText("B \u00B7 BARE", { x: 4.0, y: 2.0, w: 2.5, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY, align: "center" });
  s.addText("A\u2032 \u00B7 PASSIVE", { x: 6.6, y: 2.0, w: 2.5, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY, align: "center" });
  s.addText("A \u00B7 ACTIVATED", { x: 9.2, y: 2.0, w: 3.3, h: 0.28, fontFace: B, fontSize: 12.5, bold: true, color: NAVY, align: "center" });
  rows.forEach(([m, b, p, a]) => {
    card(s, 0.75, y, 11.85, 0.72, CARD, BORDER);
    s.addText(m, { x: 0.9, y: y + 0.14, w: 2.9, h: 0.45, fontFace: B, fontSize: 13.5, bold: true, color: NAVY });
    s.addText(b, { x: 4.0, y: y + 0.14, w: 2.5, h: 0.45, fontFace: B, fontSize: 13, color: TXT, align: "center" });
    s.addText(p, { x: 6.6, y: y + 0.14, w: 2.5, h: 0.45, fontFace: B, fontSize: 13, color: TXT, align: "center" });
    s.addText(a, { x: 9.2, y: y + 0.14, w: 3.3, h: 0.45, fontFace: B, fontSize: 13, color: "1B5E20", align: "center" });
    y += 0.82;
  });
  card(s, 0.75, 5.85, 11.85, 1.35, "EAF5EC", GREEN);
  s.addText("HARD CASE \u00B7 GREENFIELD-3 (rate-limited SSE proxy): B 27.4 min \u00B7 $2.84 \u00B7 22 tests \u2014 A 6.5 min \u00B7 $1.08 \u00B7 24 tests + spec/plan/tasks/QA. 4.2\u00D7 faster.", { x: 1.0, y: 5.98, w: 11.35, h: 0.38, fontFace: B, fontSize: BODY_SM, bold: true, color: GREEND });
  s.addText("Honest poles: passive \u2248 bare (placebo) \u00B7 N=1 per cell \u00B7 cost basis provider-unknown (GAP-ANALYSIS.md) \u00B7 devops lanes unmeasured offline.", { x: 1.0, y: 6.42, w: 11.35, h: 0.35, fontFace: B, fontSize: 13, color: TXT });
  s.addText("4 frozen cases \u00B7 E2E pipeline \u00B7 FE virtualized feed \u00B7 BE SSE proxy (hard) \u00B7 DB+ETL 1M rows \u2014 repro: bench/greenfield.py --task bench/tasks/... \u00B7 details: deck slide 13 + docs/benchmarks/BENCHMARK-SUMMARY.md", { x: 1.0, y: 6.75, w: 11.35, h: 0.35, fontFace: B, fontSize: 12.5, color: MUT });
  notes(s, "Value concentrates where difficulty lives: plan-first discipline beats churn on hard engineering; simple tasks are parity-to-small-tax.");
}

// ============ 8 · STRENGTHS & WEAKNESSES ============
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  eyebrow(s, "Honest yardsticks");
  title(s, "Strengths \u00B7 weaknesses \u00B7 deliberate cuts", "Measured first \u2014 then what we left out by design.");
  card(s, 0.75, 2.3, 5.85, 2.5, "EAF5EC", GREEN);
  s.addText("STRENGTHS (VERIFIED)", { x: 1.05, y: 2.5, w: 5.25, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: GREEND });
  const stg = [
    "Value where difficulty lives \u2014 4.2\u00D7 faster on the hard case",
    "Traceability in 8/8 A-runs; zero in bare",
    "Clean install \u00B7 marketplace updates \u00B7 CLI-first stack",
    "Reproducible: evidence/ + validate.py (12/12)",
  ];
  let sy = 2.95;
  stg.forEach((t) => { s.addText("\u2022 " + t, { x: 1.05, y: sy, w: 5.3, h: 0.4, fontFace: B, fontSize: 13.5, color: TXT, margin: 0 }); sy += 0.44; });
  card(s, 0.75, 4.95, 5.85, 1.95, "FBF3E2", AMBERD);
  s.addText("WEAKNESSES (VERIFIED)", { x: 1.05, y: 5.15, w: 5.25, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: "7A5C00" });
  const weak = [
    "Cost loop missing \u2014 no trusted metering/budgets (GAP-ANALYSIS G1)",
    "Guardrails advisory, not mechanical (R4 inversion)",
    "N=1 per bench cell \u00B7 devops lanes offline-unmeasurable",
  ];
  let wy = 5.6;
  weak.forEach((t) => { s.addText("\u2022 " + t, { x: 1.05, y: wy, w: 5.3, h: 0.4, fontFace: B, fontSize: 13.5, color: TXT, margin: 0 }); wy += 0.42; });
  card(s, 6.85, 2.3, 5.75, 4.6, ICE, MID);
  s.addText("DELIBERATELY NOT INCLUDED", { x: 7.15, y: 2.5, w: 5.15, h: 0.35, fontFace: B, fontSize: 15, bold: true, color: NAVY });
  const out = [
    "No hooks / auto-runtime / silent telemetry \u2014 v1 lesson",
    "No auto-approve \u2014 every gate is a human decision",
    "No marketing agent lanes \u2014 removed v2.6.0 (unmeasured)",
    "No permissions grants \u2014 Bash(*) killed v1",
    "No global memory \u2014 repo artifacts ARE the memory",
  ];
  let oy = 2.95;
  out.forEach((t) => { s.addText("\u2022 " + t, { x: 7.15, y: oy, w: 5.15, h: 0.4, fontFace: B, fontSize: 13.5, color: TXT, margin: 0 }); oy += 0.44; });
  s.addText("FOCUS LIST: trusted cost loop \u00B7 CI plan-vs-PR enforcement \u00B7 N\u22653 headlines \u00B7 devops staging smoke \u00B7 second-model matrix.", { x: 7.15, y: 6.35, w: 5.15, h: 0.5, fontFace: B, fontSize: 13.5, bold: true, color: NAVY });
  notes(s, "Say the cost gap first, before they ask. The exclusions are design choices, not defects.");
}

// ============ 9 · CLOSE ============
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x: -2.2, y: 4.4, w: 5.6, h: 5.6, fill: { color: "27346E" }, line: { width: 0 } });
  s.addText("WHAT WE KNOW", { x: 0.8, y: 0.85, w: 11.7, h: 0.4, fontFace: B, fontSize: 14, bold: true, color: AMBER, charSpacing: 3 });
  s.addText("Built from experience. Graded by evidence.", { x: 0.8, y: 1.3, w: 11.7, h: 0.85, fontFace: H, fontSize: 40, bold: true, color: WHITE });
  s.addText(
    [
      { text: "The framework's value concentrates on hard engineering \u2014 measured, reproducible, labeled.", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
      { text: "Gaps are shown, not hidden (cost metering, advisory guardrails, N=1 cells).", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
      { text: "Fork first: experiments live on the fork; the official ex-company repo stays read-only.", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
    ],
    { x: 0.8, y: 2.6, w: 11.7, h: 2.2, fontFace: B, fontSize: BODY, color: ICE }
  );
  s.addText("Everything ships in the repo: github.com/trac41799/claude-code-agentic-sdlc (evidence/ \u00B7 docs/demo/live-demo-guide.md \u00B7 docs/benchmarks/BENCHMARK-SUMMARY.md)", { x: 0.8, y: 5.5, w: 11.7, h: 0.5, fontFace: B, fontSize: BODY_SM, bold: true, color: AMBER });
  s.addText("Not a solved discipline \u2014 a repeatable, honest one.", { x: 0.8, y: 6.3, w: 11.7, h: 0.5, fontFace: H, fontSize: 22, italic: true, bold: true, color: WHITE });
  notes(s, "Close on honesty: we grade our own claims and show the gaps.");
}

pptx.writeFile({ fileName: process.env.PPTX_OUT || __dirname + "/Agentic-SDLC-Tech-Audience-COMPACT.pptx" }).then(f => console.log("wrote", f));