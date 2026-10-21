"""Build the SSANZ trial tools site: a front page (index.html) plus one linked page per tool.

Each tool is written as a standalone page in src/ (e.g. src/Trial-Entry-Trial-Lists.html). The build
copies it to the site with the shared extras added:
  - a "← All trial tools · Step N of 5" bar at the top,
  - a "Next step" box before the "Good to know" section,
  - the "Report a problem" section after it (see report_section.py; REPORT_TO = "" leaves it off).
It also writes index.html with one card per tool, in the order of TOOLS.

Usage (from the repository's top folder):
  python3 build/build-toolkit.py build src .     rebuild the site pages from src/
  python3 build/build-toolkit.py strip . src     recover src/ from the site pages (the reverse)
  python3 build/build-toolkit.py check src .     rebuild into a temporary folder and compare with the site

Always edit the page in src/ and rebuild; don't edit the built pages by hand.
To add a tool: put its page in src/ and add an entry to TOOLS below (list order = order of use).
"""
import filecmp, html, pathlib, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from report_section import add_report, strip_report  # noqa: E402

TOOLS = [
    dict(src="Trial-Entry-Payment-Split.html", out="payment-split.html", title="Payment Split",
         does="Splits entries into Paid, Part Paid and Not Paid tabs and shows who still owes, and how much.",
         gives="Paid · Part Paid · Not Paid tabs"),
    dict(src="Trial-Entry-Email-List.html", out="email-list.html", title="Email List",
         does="Makes one email address per person, ready to paste into BCC. Run it on a Payment Split file to email just one group, or on your selection of trial groups. After a ballot it lists who has a place and who is on the waitlist.",
         gives="Emails tab · BCC list"),
    dict(src="Trial-Entry-Trial-Lists.html", out="trial-lists.html", title="Trial Lists",
         does="Makes a randomly ordered running list for each trial (e.g. NWAdv1), with D / H reactivity flags and a check for handlers with two dogs in one trial. For an oversubscribed trial it can run the SSANZ ballot and keep a numbered waitlist.",
         gives="One tab per trial"),
    dict(src="Trial-Entry-Documents.html", out="trial-documents.html", title="Trial Documents",
         does="Turns the trial tabs into Word documents (A4): running orders for the catalogue, callboards, and time stewards' and judges' sheets with one element and judge per sheet. It also prints the judging sheets as a PDF, one per dog for each search, with the date, host, judge, element, search time and running-order number filled in. And it prints the certificates onto the pre-printed SSANZ cards. Wherever possible data need only be entered once, however there are plenty of customisation options too, including the possibility of adding your logo.",
         gives="Running orders · Callboards · Time stewards · Judges (.docx) · Judging sheets · Certificates (.pdf)", label="Makes"),
    dict(src="Trial-Entry-Results-Sheets.html", out="results-sheets.html", title="Results Sheets",
         does="Fills in the official SSANZ results spreadsheet for each class: organisation, Org Ref ID, date, venue, Trial #, judges and every dog in alphabetical order of handler, so the admin team only types the points and times. The SSANZ sheet keeps its lock and formulas, and extra rows are added for big classes.",
         gives="one SSANZ results sheet per class (.xlsx)", label="Makes",
         # Shown in the previous tool's "Next step" box, instead of the usual wording.
         arrive="After Save progress, drop the file that downloads into it, with the SSANZ results files zip."),
]
TITLES = [t["title"] for t in TOOLS]

ARRIVE = "Drop the file you just downloaded into it."
LAST_STEP = ("That's the last step.", "Open each results sheet in Excel to check it, then the admin team types in the points and times on the day. Send the finished sheet to SSANZ.")
FRONT_NOTE = "You don't have to use every tool. Steps 1–3 each work on their own with an entries download; Trial Documents needs the file from Trial Lists, and Results Sheets needs the file saved from Trial Documents plus the SSANZ results files zip."

NAV_CSS = """
.crumbs { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 6px 16px; font-size: 14px; margin-bottom: -12px; }
.crumbs a { color: var(--accent); font-weight: 700; text-decoration: none; }
.crumbs a:hover { text-decoration: underline; }
.crumbs span { color: var(--muted); }
.nextstep { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px 20px; padding: 16px 18px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); }
.nextstep p { margin: 0; font-size: 15px; color: var(--muted); max-width: 52ch; }
.nextstep p b { color: var(--ink); }
.nextstep a { font-weight: 700; color: var(--accent-ink); background: var(--accent); border-radius: 10px; padding: 10px 16px; text-decoration: none; white-space: nowrap; }
.nextstep a:focus-visible, .crumbs a:focus-visible { outline: 3px solid var(--ink); outline-offset: 2px; }
"""
HELP = '  <section class="help">'


def nav(i):
    return (f'  <nav class="crumbs" aria-label="Trial tools">'
            f'<a href="index.html">← All trial tools</a>'
            f'<span>Step {i + 1} of {len(TOOLS)}</span></nav>\n')


def next_step(i):
    if i + 1 < len(TOOLS):
        n = TOOLS[i + 1]
        return (f'  <aside class="nextstep">\n'
                f'    <p><b>Next step: {html.escape(n["title"])}.</b> {html.escape(n.get("arrive", ARRIVE), quote=False)}</p>\n'
                f'    <a href="{n["out"]}">Open {html.escape(n["title"])} →</a>\n'
                f'  </aside>\n')
    return ('  <aside class="nextstep">\n'
            f'    <p><b>{html.escape(LAST_STEP[0], quote=False)}</b> {html.escape(LAST_STEP[1], quote=False)}</p>\n'
            '    <a href="index.html">Back to all trial tools</a>\n'
            '  </aside>\n')


def build_tool(text, i):
    """A tool's source page → the page on the site."""
    assert text.count("</style>") == 1 and text.count('<div class="wrap">') == 1 and text.count(HELP) == 1
    text = text.replace("</style>", NAV_CSS + "</style>", 1)
    text = text.replace('<div class="wrap">\n', '<div class="wrap">\n' + nav(i), 1)
    text = text.replace(HELP, next_step(i) + "\n" + HELP, 1)
    return add_report(text, TOOLS[i]["title"], TITLES)


def strip_tool(text, i):
    """The reverse of build_tool: a page from the site → its source page."""
    text = strip_report(text)
    for part, by in ((NAV_CSS + "</style>", "</style>"), (nav(i), ""), (next_step(i) + "\n" + HELP, HELP)):
        if part not in text:
            raise SystemExit(f"{TOOLS[i]['out']}: the {'step bar' if part == nav(i) else 'next-step box' if HELP in part else 'styles'} "
                             "don't match TOOLS. Update TOOLS to match the site first.")
        text = text.replace(part, by, 1)
    return text


def card(i, t):
    return f"""      <li class="tool">
        <span class="num" aria-hidden="true">{i + 1}</span>
        <div class="body">
          <h3><a href="{t['out']}">{html.escape(t['title'])}</a></h3>
          <p>{html.escape(t['does'])}</p>
          <p class="gives">{t.get('label', 'Adds')}: {html.escape(t['gives'])}</p>
        </div>
        <a class="open" href="{t['out']}" aria-label="Open {html.escape(t['title'])}">Open →</a>
      </li>"""


INDEX = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SSANZ Trial Tools</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {
  --bg: #f5f6f2; --surface: #ffffff; --ink: #1d2420; --muted: #5d6a62; --line: #d9ded7;
  --accent: #2f6b4f; --accent-ink: #ffffff; --accent-soft: #e3efe8; --warn: #8a5a12;
  --font-display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --font-body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #141916; --surface: #1c2320; --ink: #e6ebe7; --muted: #9aa8a0; --line: #2f3933;
    --accent: #6fbf95; --accent-ink: #0f1a14; --accent-soft: #213229; --warn: #e0b060; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #141916; --surface: #1c2320; --ink: #e6ebe7; --muted: #9aa8a0; --line: #2f3933;
  --accent: #6fbf95; --accent-ink: #0f1a14; --accent-soft: #213229; --warn: #e0b060; color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.55; }
.wrap { max-width: 760px; margin: 0 auto; padding-inline: 16px; padding-block: 48px 64px; display: grid; gap: 32px; }
header { display: grid; gap: 10px; }
.eyebrow { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin: 0; }
h1 { font-family: var(--font-display); font-size: clamp(32px, 7vw, 48px); line-height: 1.05; margin: 0; text-wrap: balance; }
.lede { margin: 0; color: var(--muted); max-width: 60ch; font-size: 17px; }
.important { margin: 6px 0 0; max-width: 60ch; font-size: 16px; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--warn); border-radius: 10px; padding: 12px 16px; }
.important b { color: var(--warn); letter-spacing: .04em; }
h2 { font-family: var(--font-display); font-size: 20px; margin: 0 0 12px; }
.steps { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.tool { display: grid; grid-template-columns: auto 1fr auto; gap: 4px 16px; align-items: center; padding: 18px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); transition: border-color .15s; }
.tool:hover { border-color: var(--accent); }
.num { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; background: var(--accent-soft); color: var(--accent); font-family: var(--font-display); font-weight: 700; font-size: 18px; align-self: start; }
.body { display: grid; gap: 4px; min-width: 0; }
.body h3 { font-family: var(--font-display); font-size: 20px; margin: 0; }
.body h3 a { color: var(--ink); text-decoration: none; }
.body h3 a:hover { color: var(--accent); }
.body p { margin: 0; color: var(--muted); font-size: 15px; }
.body .gives { font-family: var(--font-mono); font-size: 13px; color: var(--accent); }
.open { font-weight: 700; color: var(--accent-ink); background: var(--accent); border-radius: 10px; padding: 10px 16px; text-decoration: none; white-space: nowrap; }
a:focus-visible { outline: 3px solid var(--ink); outline-offset: 2px; }
@media (max-width: 560px) {
  .tool { grid-template-columns: auto 1fr; }
  .open { grid-column: 2; justify-self: start; margin-top: 8px; }
}
.note { margin: 10px 0 0; font-size: 14px; color: var(--muted); }
.facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.fact { padding: 16px; border-radius: 12px; background: var(--accent-soft); display: grid; gap: 4px; }
.fact b { font-family: var(--font-display); font-size: 17px; }
.fact span { font-size: 14px; color: var(--muted); }
@media (max-width: 640px) { .facts { grid-template-columns: 1fr; } }
.help { border-top: 1px solid var(--line); padding-top: 20px; display: grid; gap: 10px; font-size: 15px; }
.help h3 { font-family: var(--font-display); font-size: 17px; margin: 0; }
.help ul { margin: 0; padding-left: 20px; display: grid; gap: 6px; color: var(--muted); max-width: 66ch; }
.help li b { color: var(--ink); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">SSANZ</p>
    <h1>Trial entry tools</h1>
    <p class="lede">The interfaces on this page automate and simplify the process of taking your downloaded trial entries, extracting the data you need, and reformatting into various different forms that you may want to use for your trial. At each step the spreadsheet tools give your file back with new tabs added, so none of your original data is lost. The Trial Documents step produces the various formats of running orders in Word, judging sheets as a PDF, and will also print certificates.</p>
    <p class="important"><b>IMPORTANT</b> - trial lists are produced in a random order. If you wish to move people around, you should do that manually before proceeding to step 4. Remember to move the entire line. Also, if you want to change the running order for different elements, duplicate the entire tab and reorder them there.</p>
  </header>

  <section>
    <h2>The tools, in the usual order</h2>
    <ol class="steps">
__CARDS__
    </ol>
    <p class="note">__NOTE__</p>
  </section>

  <section class="facts" aria-label="How the tools work">
    <div class="fact"><b>Private</b><span>Your file never leaves your computer. Nothing is uploaded or saved.</span></div>
    <div class="fact"><b>Nothing to install</b><span>Works in any web browser. No account or login needed.</span></div>
    <div class="fact"><b>Excel or CSV</b><span>Drop in an .xlsx or .csv entries download.</span></div>
  </section>

  <section class="help">
    <h3>Good to know</h3>
    <ul>
      <li><b>Using Google Sheets?</b> Choose File → Download → Microsoft Excel (.xlsx), drop that into a tool, then bring the result back with File → Import.</li>
      <li><b>Old .xls files</b> aren't supported. Open them in Excel and use Save As → Excel Workbook (.xlsx) first.</li>
      <li><b>Chaining tools:</b> each tool's download keeps all your tabs, so drop it straight into the next tool.</li>
      <li><b>Needs internet</b> to load the page. The work itself happens on your computer.</li>
    </ul>
  </section>
</div>
</body>
</html>
"""


def front_page():
    cards = "\n".join(card(i, t) for i, t in enumerate(TOOLS))
    return add_report(INDEX.replace("__CARDS__", cards).replace("__NOTE__", html.escape(FRONT_NOTE, quote=False)), "", TITLES)


def build(src, out):
    src, out = pathlib.Path(src), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(TOOLS):
        text = (src / t["src"]).read_text(encoding="utf-8")
        (out / t["out"]).write_text(build_tool(text, i), encoding="utf-8", newline="\n")
    (out / "index.html").write_text(front_page(), encoding="utf-8", newline="\n")


def strip(site, src):
    site, src = pathlib.Path(site), pathlib.Path(src)
    src.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(TOOLS):
        text = (site / t["out"]).read_text(encoding="utf-8")
        (src / t["src"]).write_text(strip_tool(text, i), encoding="utf-8", newline="\n")


def check(src, site):
    """Rebuild into a temporary folder and list any page that differs from the site."""
    with tempfile.TemporaryDirectory() as tmp:
        build(src, tmp)
        names = ["index.html"] + [t["out"] for t in TOOLS]
        bad = [n for n in names if not filecmp.cmp(pathlib.Path(tmp) / n, pathlib.Path(site) / n, shallow=False)]
    print("All pages match the sources." if not bad else "These pages differ from a fresh build: " + ", ".join(bad))
    return not bad


if __name__ == "__main__":
    cmd, a, b = (sys.argv[1:4] + [None] * 3)[:3]
    if cmd == "build" and a and b:
        build(a, b)
    elif cmd == "strip" and a and b:
        strip(a, b)
    elif cmd == "check" and a and b:
        sys.exit(0 if check(a, b) else 1)
    else:
        sys.exit(__doc__)
