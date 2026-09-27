"""Storybooks: a printable PDF book from daily story cards.

A book folder holds `book.yaml` and the card images. Each day becomes a chapter: an opener with the
day's cover card, the story told beat by beat beside each card, a page with the lesson, a bedtime
question and new words, and an activity page (a quiz and a word search generated from the day's
words). An answer key closes the book. The book is laid out as HTML and printed to PDF by headless
Chrome, so fonts and layout are the same on every run.
"""
from __future__ import annotations

import html
import random
import re
import shutil
import subprocess
import zlib
from pathlib import Path

import yaml

BOOK_FILE = "book.yaml"
PAGE_SIZES = {"A4": ("210mm", "297mm"), "Letter": ("8.5in", "11in")}
IMAGE_MAX = 1400      # px on the long side: sharp at 150 mm printed, light to download
IMAGE_QUALITY = 84    # JPEG quality
GRID = 10
DIRECTIONS = [(0, 1), (1, 0), (1, 1)]  # right, down, diagonal down-right: easy for young readers
FONTS = ("https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800"
         "&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=block")


class BookError(Exception):
    pass


def load(folder: Path) -> dict:
    path = folder / BOOK_FILE
    if not path.is_file():
        raise BookError(f"no {BOOK_FILE} in {folder}")
    book = yaml.safe_load(path.read_text(encoding="utf-8"))
    problems = []
    if book.get("schema") != "story-book/v1":
        problems.append("schema must be story-book/v1")
    if book.get("page", "A4") not in PAGE_SIZES:
        problems.append(f"page must be one of {', '.join(PAGE_SIZES)}")
    images = [book.get("cover")] + [d.get("cover") for d in book.get("days", [])]
    images += [b.get("image") for d in book.get("days", []) for b in d.get("beats", [])]
    problems += [f"image '{i}' not found" for i in images if not i or not (folder / i).is_file()]
    for d in book.get("days", []):
        for w in d.get("search", []):
            if not w.isalpha() or len(w) > GRID:
                problems.append(f"day {d.get('day')}: search word '{w}' must be letters only, at most {GRID}")
        for q in d.get("quiz", []):
            if not 0 <= q.get("answer", -1) < len(q.get("options", [])):
                problems.append(f"day {d.get('day')}: quiz answer out of range for '{q.get('q')}'")
    if not book.get("days"):
        problems.append("the book has no days")
    if problems:
        raise BookError("; ".join(problems))
    return book


# --- word search ------------------------------------------------------------------------------

def word_search(words: list[str], seed: str) -> tuple[list[list[str]], dict[str, list[tuple[int, int]]]]:
    """A GRID×GRID puzzle hiding every word (right, down or diagonally down-right), plus where each is."""
    rnd = random.Random(zlib.crc32(seed.encode()))
    for _ in range(200):
        grid = [["" for _ in range(GRID)] for _ in range(GRID)]
        placed: dict[str, list[tuple[int, int]]] = {}
        for w in sorted((w.upper() for w in words), key=len, reverse=True):
            spots = [(r, c, dr, dc) for dr, dc in DIRECTIONS for r in range(GRID) for c in range(GRID)
                     if r + dr * (len(w) - 1) < GRID and c + dc * (len(w) - 1) < GRID
                     and all(grid[r + dr * i][c + dc * i] in ("", ch) for i, ch in enumerate(w))]
            if not spots:
                break
            r, c, dr, dc = rnd.choice(spots)
            cells = [(r + dr * i, c + dc * i) for i in range(len(w))]
            for (rr, cc), ch in zip(cells, w):
                grid[rr][cc] = ch
            placed[w] = cells
        if len(placed) == len(words):
            for row in grid:
                for i, ch in enumerate(row):
                    row[i] = ch or rnd.choice("ABCDEFGHIJKLMNOPRSTUVWY")
            return grid, placed
    raise BookError(f"could not fit the words {words} into a {GRID}×{GRID} grid")


def _grid_svg(grid, placed=None, size=100) -> str:
    """The grid as SVG (size in mm); with `placed`, each word is circled (the answer key)."""
    cell = size / GRID
    out = [f'<svg class="grid" viewBox="0 0 {size} {size}" width="{size}mm" height="{size}mm">',
           f'<rect x="0" y="0" width="{size}" height="{size}" rx="3" fill="#fffaf0" stroke="#c9a13b" stroke-width="0.6"/>']
    for cells in (placed or {}).values():
        (r0, c0), (r1, c1) = cells[0], cells[-1]
        out.append(f'<line x1="{(c0 + .5) * cell:.2f}" y1="{(r0 + .5) * cell:.2f}" x2="{(c1 + .5) * cell:.2f}" '
                   f'y2="{(r1 + .5) * cell:.2f}" stroke="#f2c14e" stroke-width="{cell * .72:.2f}" stroke-linecap="round" opacity="0.7"/>')
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            out.append(f'<text x="{(c + .5) * cell:.2f}" y="{(r + .5) * cell + cell * .18:.2f}" text-anchor="middle" '
                       f'font-size="{cell * .52:.2f}">{ch}</text>')
    out.append("</svg>")
    return "".join(out)


# --- layout -----------------------------------------------------------------------------------

CSS = """
@page { size: %(w)s %(h)s; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: 'Literata', Georgia, serif; color: #3b2a20; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: %(w)s; height: %(h)s; position: relative; overflow: hidden; page-break-after: always; break-after: page;
  background: radial-gradient(ellipse at 50%% 30%%, #fffaf0 0%%, #fbf1dc 70%%, #f3e3c0 100%%); padding: 20mm 18mm; }
.page::before { content: ''; position: absolute; inset: 7mm; border: 0.9mm double #c9a13b; border-radius: 5mm; pointer-events: none; }
h1, h2, h3, .display { font-family: 'Baloo 2', 'Trebuchet MS', sans-serif; color: #7a1f1f; margin: 0; line-height: 1.1; }
.kicker { font-family: 'Baloo 2', sans-serif; font-weight: 700; letter-spacing: 0.25em; color: #b8862b; font-size: 12pt; text-transform: uppercase; }
.center { text-align: center; }
.card { border-radius: 3mm; box-shadow: 0 1.2mm 4mm rgba(90, 60, 20, 0.28); display: block; }
.brand { position: absolute; left: 0; right: 0; bottom: 12mm; text-align: center; font-style: italic; color: #8a6a3a; font-size: 10.5pt; }
.folio { position: absolute; bottom: 10mm; left: 0; right: 0; text-align: center; font-size: 9pt; color: #a88a5a; }
/* cover */
.cover h1 { font-size: 40pt; font-weight: 800; text-align: center; margin-top: 2mm; }
.cover .sub { text-align: center; font-size: 13pt; font-style: italic; margin: 3mm 0 7mm; color: #6b4a2e; }
.cover .card { width: 138mm; margin: 0 auto; }
/* parents and contents */
.intro h2 { font-size: 22pt; margin: 4mm 0 4mm; }
.intro p { font-size: 12.5pt; line-height: 1.6; }
.toc { margin-top: 10mm; }
.toc .row { display: flex; align-items: baseline; font-size: 13pt; margin: 3.5mm 0; }
.toc .row .d { font-family: 'Baloo 2', sans-serif; color: #b8862b; font-weight: 700; width: 20mm; }
.toc .row .t { flex: 1; border-bottom: 0.3mm dotted #c9a13b; }
/* chapter opener */
.opener { display: flex; flex-direction: column; align-items: center; }
.opener h2 { font-size: 30pt; font-weight: 800; text-align: center; margin: 2mm 0 2mm; }
.opener .teaser { font-style: italic; font-size: 13pt; text-align: center; margin: 0 0 7mm; color: #6b4a2e; }
.opener .card { width: 146mm; }
/* story beats */
.beat { display: flex; gap: 8mm; align-items: center; height: 124mm; }
.beat.flip { flex-direction: row-reverse; }
.beat + .beat { margin-top: 5mm; }
.beat .card { width: 92mm; flex: none; }
.beat p { font-size: 13.4pt; line-height: 1.6; margin: 0; text-align: left; }
.beat.solo { flex-direction: column; height: auto; gap: 7mm; }
.beat.solo .card { width: 122mm; }
.beat.solo p { font-size: 14pt; max-width: 150mm; }
.beat p::first-letter { font-family: 'Baloo 2', sans-serif; font-weight: 800; color: #7a1f1f; font-size: 26pt; float: left; line-height: 0.9; margin: 1mm 1.5mm 0 0; }
/* lesson page */
.box { border: 0.6mm solid #c9a13b; border-radius: 4mm; background: rgba(255, 250, 238, 0.85); padding: 6mm 8mm; margin-bottom: 7mm; }
.box h3 { font-size: 17pt; margin-bottom: 2mm; }
.box.lesson { background: #7a1f1f; border-color: #7a1f1f; color: #fff6e0; }
.box.lesson h3 { color: #f2c14e; }
.box.lesson p { font-size: 15pt; line-height: 1.45; margin: 0; font-weight: 600; }
.box p { font-size: 12.5pt; line-height: 1.55; margin: 0; }
.words .w { margin: 1.6mm 0; font-size: 12pt; }
.words .w b { color: #7a1f1f; }
.draw { height: 70mm; border: 0.5mm dashed #c9a13b; border-radius: 4mm; position: relative; background: #fffdf6; }
.draw span { position: absolute; top: 4mm; left: 6mm; font-family: 'Baloo 2', sans-serif; color: #b8862b; font-weight: 700; }
/* activities */
.quiz .q { margin: 0 0 4.5mm; font-size: 12.5pt; }
.quiz .q b { display: block; margin-bottom: 1.5mm; }
.quiz .opt { display: inline-block; margin-right: 7mm; }
.quiz .opt::before { content: ''; display: inline-block; width: 3.6mm; height: 3.6mm; border: 0.4mm solid #7a1f1f; border-radius: 50%%; margin-right: 1.8mm; vertical-align: -0.6mm; }
.search { display: flex; gap: 8mm; align-items: center; }
.grid text { font-family: 'Baloo 2', sans-serif; font-weight: 700; fill: #3b2a20; }
.wordlist { font-family: 'Baloo 2', sans-serif; font-weight: 700; font-size: 13pt; color: #7a1f1f; line-height: 1.7; }
/* answers */
.answers .day { display: flex; gap: 8mm; margin-bottom: 8mm; align-items: flex-start; }
.answers ol { margin: 0; padding-left: 6mm; font-size: 12pt; line-height: 1.7; }
.next { font-size: 15pt; font-style: italic; text-align: center; margin-top: 60mm; line-height: 1.5; }
"""


def _smart(s: str) -> str:
    """Typographer's quotes and apostrophes for printed text."""
    s = re.sub(r'(^|[\s(\[{—-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(\w)'", "\\1\u2019", s)
    return s.replace("'", "\u2018")


def _e(s) -> str:
    return html.escape(_smart(str(s)), quote=False)


def _img(src, cls="card") -> str:
    return f'<img class="{cls}" src="{_e(_web_name(src))}"/>'


def _web_name(src: str) -> str:
    return f"images/{Path(src).stem}.jpg"


def prepare_images(book: dict, folder: Path, out_dir: Path) -> None:
    """Compressed JPEG copies of every card next to the HTML (a book of full-size PNGs is ~40 MB)."""
    from PIL import Image
    sources = {book["cover"], *(d["cover"] for d in book["days"]), *(b["image"] for d in book["days"] for b in d["beats"])}
    for src in sorted(sources):
        dest = out_dir / _web_name(src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file() and dest.stat().st_mtime >= (folder / src).stat().st_mtime:
            continue
        with Image.open(folder / src) as im:
            im = im.convert("RGB")
            im.thumbnail((IMAGE_MAX, IMAGE_MAX), Image.LANCZOS)
            im.save(dest, "JPEG", quality=IMAGE_QUALITY, optimize=True, progressive=True)


def render_html(book: dict) -> str:
    w, h = PAGE_SIZES[book.get("page", "A4")]
    pages, folio = [], [0]

    def page(body: str, cls: str = "", number: bool = True) -> None:
        folio[0] += 1
        num = f'<div class="folio">{folio[0]}</div>' if number else ""
        pages.append(f'<section class="page {cls}">{body}{num}</section>')

    brand = _e(book.get("brand", ""))
    page(f'<div class="kicker center">{brand}</div><h1>{_e(book["title"])}</h1>'
         f'<div class="sub">{_e(book.get("subtitle", ""))}</div>{_img(book["cover"])}', "cover", number=False)
    toc = "".join(f'<div class="row"><span class="d">Day {d["day"]}</span><span class="t">{_e(d["title"])}</span></div>'
                  for d in book["days"])
    page(f'<div class="intro"><div class="kicker">For parents</div><h2>How to use this book</h2>'
         f'<p>{_e(book.get("for_parents", ""))}</p><div class="toc"><h2>Inside</h2>{toc}</div></div>'
         f'<div class="brand">{brand}</div>', "intro")
    keys = []
    for d in book["days"]:
        page(f'<div class="opener"><div class="kicker">Day {d["day"]}</div><h2>{_e(d["title"])}</h2>'
             f'<div class="teaser">{_e(d.get("teaser", ""))}</div>{_img(d["cover"])}</div>')
        beats = d.get("beats", [])
        for i in range(0, len(beats), 2):
            pair = beats[i:i + 2]
            solo = len(pair) == 1  # a lone last beat gets a feature layout: big picture, text beneath
            rows = "".join(f'<div class="beat{" solo" if solo else " flip" if (i + j) % 2 else ""}">{_img(b["image"])}<p>{_e(b["text"])}</p></div>'
                           for j, b in enumerate(pair))
            page(rows)
        words = "".join(f'<div class="w"><b>{_e(x["word"])}</b>: {_e(x["meaning"])}</div>' for x in d.get("words", []))
        page(f'<div class="box lesson"><h3>Tonight\'s Lesson</h3><p>{_e(d.get("lesson", ""))}</p></div>'
             f'<div class="box"><h3>Bedtime Question</h3><p>{_e(d.get("question", ""))}</p></div>'
             + (f'<div class="box words"><h3>New Words</h3>{words}</div>' if words else "")
             + '<div class="draw"><span>Draw your favourite moment from today\'s story</span></div>')
        quiz = "".join(f'<div class="q"><b>{n + 1}. {_e(q["q"])}</b>'
                       + "".join(f'<span class="opt">{_e(o)}</span>' for o in q["options"]) + "</div>"
                       for n, q in enumerate(d.get("quiz", [])))
        grid, placed = word_search(d.get("search", []), f'{book["id"]}-day{d["day"]}')
        page(f'<div class="kicker">Day {d["day"]} · Activities</div><h2 style="font-size:24pt;margin:1mm 0 6mm">Fun Time!</h2>'
             f'<div class="box quiz"><h3>Quiz</h3>{quiz}</div>'
             f'<div class="box"><h3>Word Search</h3><div class="search">{_grid_svg(grid, size=100)}'
             f'<div class="wordlist">{"<br/>".join(sorted(placed))}</div></div></div>')
        keys.append((d, grid, placed))
    rows = "".join(
        f'<div class="day"><div><h3>Day {d["day"]}</h3><ol>'
        + "".join(f'<li>{_e(q["options"][q["answer"]])}</li>' for q in d.get("quiz", []))
        + f'</ol></div>{_grid_svg(grid, placed, size=62)}</div>' for d, grid, placed in keys)
    page(f'<div class="answers"><div class="kicker">Answer key</div><h2 style="font-size:24pt;margin:1mm 0 6mm">Answers</h2>{rows}</div>')
    page(f'<div class="kicker center" style="margin-top:40mm">Coming next</div>'
         f'<div class="next">{_e(book.get("coming_next", ""))}</div><div class="brand">{brand}</div>', number=False)
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{_e(book["title"])}</title>'
            f'<link rel="stylesheet" href="{FONTS}"><style>{CSS % {"w": w, "h": h}}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


# --- printing ---------------------------------------------------------------------------------

def _chrome(root: Path) -> str:
    local = sorted((root / "render" / "node_modules" / ".remotion" / "chrome-headless-shell").glob("*/chrome-headless-shell-*/chrome-headless-shell"))
    for c in [*map(str, local), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome") or ""]:
        if c and Path(c).exists():
            return c
    raise BookError("no Chrome found to print the PDF (run `npm install` in render/, or install Google Chrome)")


def build(root: Path, folder: Path, log=print) -> Path:
    book = load(folder)
    out_dir = folder / "build"
    out_dir.mkdir(parents=True, exist_ok=True)
    prepare_images(book, folder, out_dir)
    page_html = out_dir / "book.html"
    page_html.write_text(render_html(book), encoding="utf-8")
    pdf = out_dir / f'{book["id"]}.pdf'
    subprocess.run([_chrome(root), "--headless", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=20000", f"--print-to-pdf={pdf.resolve()}", page_html.resolve().as_uri()],
                   check=True, capture_output=True)
    log(f"wrote {pdf} ({pdf.stat().st_size // 1024} KB)")
    return pdf
