"""Render compact terminal-style trees of the evidence projects (for the deck
screenshots) — deterministic, correct connectors, file-groups squashed inline."""
import os
import sys

GF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "evidence", "greenfield"))
SKIP = {".pytest_cache", "__pycache__", ".git", "node_modules", ".venv"}


def entries(d):
    return sorted((e for e in os.scandir(d)
                   if e.name not in SKIP and not e.name.endswith(".pyc")),
                  key=lambda e: (e.is_dir(), e.name.lower()))


def walk(d, depth, accents, rows, maxdepth=5):
    es = entries(d)
    for i, e in enumerate(es):
        last = i == len(es) - 1
        branch = ("\\--- " if last else "+--- ") if depth > 0 else "|   "
        pref = "".join(accents) + branch
        is_dir = e.is_dir()
        rows.append([pref, e.name + ("/" if is_dir else ""), depth, last])
        if is_dir:
            if depth >= maxdepth:
                rows.append([pref + "    ", "... (deeper \u2014 see evidence/tree/)\u00a7", depth + 1, False])
                continue
            if e.name == "skills":
                n = sum(1 for x in os.scandir(e.path) if x.is_dir())
                rows.append([pref + "    ", f"({n} skill dirs \u00b7 SKILL.md each \u2014 list: evidence/tree/install-payload.txt)", depth + 1, False])
                continue
            walk(e.path, depth + 1, accents + [("    " if last else "|   ")], rows, maxdepth)


def compact(rows):
    """Squash consecutive file lines at the same depth into one line, wrapping
    at a character budget so no list exceeds the panel width."""
    budget = 88
    out, i = [], 0
    while i < len(rows):
        pref, name, depth, last = rows[i]
        is_dir = name.endswith("/") and not name.startswith("...")
        j = i + 1
        names = []
        while j < len(rows):
            p2, n2, d2, _ = rows[j]
            if d2 == depth + 1 and not n2.endswith("/") and not n2.startswith("..."):
                names.append(n2)
                j += 1
            else:
                break
        if names and is_dir:
            line = pref + name + "  ("
            for n in names:
                piece = (" \u00b7 " if line.split("(", 1)[-1] else "") + n
                if len(line) + len(piece) > budget:
                    out.append([line.rstrip() + "\u00a7", "", 0, False])
                    line = pref + "            " + n
                else:
                    line += piece
            out.append([line + ")", "", 0, False])
            i = j
        else:
            out.append(rows[i])
            i += 1
    return out


def build(sub):
    rows = []
    walk(os.path.join(GF, sub), 0, [], rows)
    return [p + n for p, n, _, _ in compact(rows)]


if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        Image = None
    font_b = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
    font_t = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 14)
    W, H = 860, 620
    titles = {
        "be-a": "tree /F /A greenfield\\be-a  \u00b7  A \u00b7 activated (framework arm)",
        "be-b": "tree /F /A greenfield\\be-b  \u00b7  B \u00b7 bare",
    }
    for sub in sys.argv[1:]:
        lines = build(sub)
        img = Image.new("RGB", (W, H), (11, 18, 32))
        d = ImageDraw.Draw(img)
        d.text((24, 30), "$ " + titles[sub], font=font_t, fill=(244, 180, 0))
        y = 60
        for l in lines[:24]:
            d.text((24, y), l, font=font_b, fill=(198, 208, 224))
            y += 21
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "evidence-" + sub + ".png")
        img.save(out)
        print("wrote", out, len(lines), "lines")