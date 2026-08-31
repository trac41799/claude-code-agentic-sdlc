import pathlib
import shutil
import subprocess
import sys
import pytest

GIT_BASH = r"C:\Program Files\Git\bin\bash.exe"
BUNDLE = pathlib.Path(__file__).resolve().parent.parent
REPO = BUNDLE.parent.parent
WAVE_SKILLS = ["dev-multi-agent", "asdlc-wave-on", "asdlc-wave-off"]


def bash(*args: str, cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    posix = lambda a: "'" + a.replace("\\", "/") + "'"
    return subprocess.run(
        [GIT_BASH, "-c", " ".join(posix(str(a)) for a in args)],
        cwd=cwd, capture_output=True, text=True,
    )


def make_project(root: pathlib.Path, n_canonical: int = 17) -> pathlib.Path:
    proj = root / "proj"
    skills = proj / ".claude" / "skills"
    skills.mkdir(parents=True)
    for i in range(n_canonical):
        d = skills / f"skill-{i:02d}"
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\nname: skill-{i:02d}\ndescription: stub\n---\n", encoding="utf-8")
    return proj


def canonical_hashes(proj: pathlib.Path) -> dict:
    out = {}
    for f in (proj / ".claude" / "skills").glob("*/SKILL.md"):
        out[f.parent.name] = f.read_bytes()
    return out


def test_install_adds_three_and_preserves_canonical(tmp_path):
    proj = make_project(tmp_path)
    before = canonical_hashes(proj)
    r = bash(str(BUNDLE / "scripts" / "wave-install.sh"), str(BUNDLE), str(proj))
    assert r.returncode == 0, r.stderr
    after = canonical_hashes(proj)
    assert len(after) == 20
    assert set(WAVE_SKILLS) <= set(after)
    for name, content in before.items():
        assert after[name] == content, f"canonical skill {name} was modified"
    for name in WAVE_SKILLS:
        assert (proj / ".claude" / "skills" / name / "SKILL.md").exists()


def test_remove_restores_17_and_idempotent(tmp_path):
    proj = make_project(tmp_path)
    bash(str(BUNDLE / "scripts" / "wave-install.sh"), str(BUNDLE), str(proj))
    artifact = proj / ".specify" / "features" / "demo" / "wave-report.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("wave report", encoding="utf-8")
    r = bash(str(BUNDLE / "scripts" / "wave-remove.sh"), str(proj))
    assert r.returncode == 0, r.stderr
    assert len(canonical_hashes(proj)) == 17
    assert not artifact.exists()
    for name in WAVE_SKILLS:
        assert not (proj / ".claude" / "skills" / name).exists()
    r2 = bash(str(BUNDLE / "scripts" / "wave-remove.sh"), str(proj))
    assert r2.returncode == 0
    assert len(canonical_hashes(proj)) == 17


def test_remove_handles_partial_install(tmp_path):
    proj = make_project(tmp_path)
    bash(str(BUNDLE / "scripts" / "wave-install.sh"), str(BUNDLE), str(proj))
    removed = proj / ".claude" / "skills" / "asdlc-wave-on"
    (removed / "SKILL.md").unlink()
    r = bash(str(BUNDLE / "scripts" / "wave-remove.sh"), str(proj))
    assert r.returncode == 0, r.stderr
    assert len(canonical_hashes(proj)) == 17
    assert not (proj / ".claude" / "skills" / "dev-multi-agent").exists()
    assert not (proj / ".claude" / "skills" / "asdlc-wave-off").exists()


V1_REQUIRED = [
    "Wave Execution Model",
    "Wave 1: [Agent A] [Agent B] [Agent C]",
    "Sub-Agent Prompt Template",
    "Tasks share state or depend on each other",
    "Agents would edit the same files",
    "Coordinator Responsibilities",
    "Integration Check",
    "Conflicts found: none / [list]",
    "Follow-up waves needed: none / [describe]",
]

GAP_MARKERS = {
    "R4": ["[V2-REINTRO R4]", "tasks.md", "disjoint", "operator"],
    "R5": ["[V2-REINTRO R5]", "git status", "scope"],
    "R6": ["[V2-REINTRO R6]", "sequentially", "abort"],
    "R7": ["[V2-REINTRO R7]", "wave-report.md"],
    "R8": ["[V2-REINTRO R8]", "test suite", "before the next wave"],
}


def wave_skill() -> str:
    return (BUNDLE / "skills" / "dev-multi-agent" / "SKILL.md").read_text(encoding="utf-8")


def test_v1_sections_verbatim():
    t = wave_skill()
    for frag in V1_REQUIRED:
        assert frag in t, f"v1 section missing: {frag}"


def test_gaps_present():
    import re
    t = re.sub(r"\s+", " ", wave_skill()).lower()
    for tag, frags in GAP_MARKERS.items():
        for f in frags:
            assert f.lower() in t, f"gap {tag} missing marker/phrase: {f}"


def test_toggle_frontmatter():
    for name in ("dev-multi-agent", "asdlc-wave-on", "asdlc-wave-off"):
        p = BUNDLE / "skills" / name / "SKILL.md"
        t = p.read_text(encoding="utf-8")
        assert t.startswith("---\n"), f"{name}: no frontmatter"
        fm = t.split("---\n", 2)[1]
        assert f"name: {name}" in fm, f"{name}: name mismatch"
        assert "description:" in fm, f"{name}: no description"


def test_no_global_install_regression():
    import re
    bad = []
    for f in list((BUNDLE / "skills").rglob("*")) + list((BUNDLE / "scripts").rglob("*")):
        if not f.is_file():
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"(cp|mv|mkdir|touch|tee|rm|ln|install)[^|;&]*(~/\.claude|\$HOME/\.claude)", t):
            bad.append(f"{f}: writes into ~/.claude")
        if re.search(r'>\s*"?(~/\.claude|\$HOME/\.claude)', t):
            bad.append(f"{f}: redirects into ~/.claude")
    assert not bad, "\n".join(bad)


def test_benchkit_install_wave_and_activation(tmp_path):
    sys.path.insert(0, str(REPO / "bench"))
    import benchkit
    proj_wave = tmp_path / "wave-proj"
    proj_plain = tmp_path / "plain-proj"
    for p in (proj_wave, proj_plain):
        p.mkdir()
    benchkit.install_framework(str(proj_wave), str(REPO), wave=True)
    benchkit.install_framework(str(proj_plain), str(REPO), wave=False)
    skills_wave = {d.name for d in (proj_wave / ".claude" / "skills").iterdir() if d.is_dir()}
    skills_plain = {d.name for d in (proj_plain / ".claude" / "skills").iterdir() if d.is_dir()}
    assert len(skills_plain) == 17
    assert len(skills_wave) == 20
    assert set(WAVE_SKILLS) <= skills_wave
    assert set(WAVE_SKILLS).isdisjoint(skills_plain)
    assert "dev-multi-agent" in benchkit.activation_text(True, True)
    assert "dev-multi-agent" not in benchkit.activation_text(True, False)


def test_greenfield_wave_flag(tmp_path):
    r = subprocess.run(
        [sys.executable, str(REPO / "bench" / "greenfield.py"), "--help"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "--wave" in r.stdout