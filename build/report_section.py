"""The "Report a problem" (snagging) section added to every page of the trial tools site.

Reports open in the tester's own email app, addressed to REPORT_TO, with what they typed filled in.
Nothing is sent or stored by the page itself. Set REPORT_TO = "" to leave the section off (e.g. once
testing is over).
"""
import html, json

REPORT_TO = "tonka.watson@gmail.com"

REPORT_CSS = """
.report details { border: 1px solid var(--line); border-radius: 14px; background: var(--surface); }
.report summary { cursor: pointer; padding: 14px 18px; font-family: var(--font-display); font-size: 17px; font-weight: 700; list-style: none; display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.report summary::-webkit-details-marker { display: none; }
.report summary::after { content: "+"; font-size: 22px; line-height: 1; color: var(--accent); }
.report details[open] summary::after { content: "–"; }
.report summary:focus-visible { outline: 3px solid var(--ink); outline-offset: 2px; border-radius: 14px; }
.report .rbody { display: grid; gap: 12px; padding: 0 18px 18px; }
.report .rbody > p { margin: 0; font-size: 15px; color: var(--muted); max-width: 66ch; }
.report .rprivacy { padding: 10px 14px; border-radius: 10px; border-left: 4px solid var(--warn); background: var(--bg); color: var(--ink) !important; }
.report .rgrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 16px; }
.report .rgrid .wide { grid-column: 1 / -1; }
.report label { display: grid; gap: 4px; font-size: 14px; color: var(--muted); min-width: 0; }
.report label b { color: var(--ink); }
.report input, .report select, .report textarea { font: inherit; font-size: 15px; color: var(--ink); background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 7px 9px; width: 100%; min-width: 0; }
.report textarea { min-height: 72px; resize: vertical; }
.report input:focus-visible, .report select:focus-visible, .report textarea:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.report .ractions { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.report .ractions a, .report .ractions button { font: inherit; font-weight: 700; font-size: 15px; border-radius: 10px; padding: 10px 16px; cursor: pointer; text-decoration: none; }
.report .rsend { background: var(--accent); color: var(--accent-ink); border: 1px solid var(--accent); }
.report .rcopy { background: transparent; color: var(--accent); border: 1px solid var(--accent); }
.report .rnote { font-size: 14px; color: var(--muted); margin: 0; }
.report .rnote.err { color: var(--warn); font-weight: 700; }
@media (max-width: 560px) { .report .rgrid { grid-template-columns: 1fr; } }
"""


def report_html(tool_title, tool_titles):
    """The section's HTML and script. tool_title: this page's tool ("" on the front page)."""
    if not REPORT_TO:
        return ""
    options = ["Not sure"] + tool_titles + ["Front page"]
    chosen = tool_title or "Not sure"
    opts = "".join(f'<option{" selected" if o == chosen else ""}>{html.escape(o)}</option>' for o in options)
    return f"""
  <section class="report" aria-label="Report a problem">
    <details id="report">
      <summary>Found a problem? Report it</summary>
      <div class="rbody">
        <p>These tools are being tested. If something goes wrong, looks odd or is confusing, tell us here. Your report opens in your email app, ready to send. Nothing is sent until you press Send there.</p>
        <p class="rprivacy"><b>Please don't attach your entries file</b> or type anyone's name, email or other details. Describe the problem instead, for example “row 14 of NWAdv1” or “the third dog on the Judges sheet”.</p>
        <div class="rgrid">
          <label>Which tool?<select id="rTool">{opts}</select></label>
          <label>Your name (optional, so we can ask you more)<input type="text" id="rName" autocomplete="name" maxlength="60"></label>
          <label class="wide"><span><b>What went wrong?</b> What you saw, any message on the screen, and which step you were on</span><textarea id="rWhat" maxlength="1200"></textarea></label>
          <label class="wide">What did you expect to happen? (optional)<textarea id="rExpect" maxlength="600"></textarea></label>
          <label>Your computer<select id="rDevice"><option value="">Choose…</option><option>Windows</option><option>Mac</option><option>iPad or tablet</option><option>Phone</option><option>Other</option></select></label>
          <label>Spreadsheet program you used<select id="rSheet"><option value="">Choose…</option><option>Excel (installed)</option><option>Excel for the web</option><option>Google Sheets</option><option>Numbers</option><option>Other</option><option>None yet</option></select></label>
          <label class="wide">Web browser (filled in for you)<input type="text" id="rBrowser" maxlength="80"></label>
        </div>
        <div class="ractions">
          <a class="rsend" id="rSend" href="mailto:{REPORT_TO}">Open email to send</a>
          <button class="rcopy" type="button" id="rCopy">Copy report</button>
        </div>
        <p class="rnote" id="rNote">No email app opens? Copy the report and email it to {html.escape(REPORT_TO)}.</p>
      </div>
    </details>
  </section>
<script>
(() => {{
  const TO = {json.dumps(REPORT_TO)};
  const $ = id => document.getElementById(id);
  const ua = navigator.userAgent, pick = (re, name) => {{ const m = re.exec(ua); return m ? `${{name}} ${{m[1]}}` : ""; }};
  $("rBrowser").value = pick(/Edg\\/(\\d+)/, "Edge") || pick(/OPR\\/(\\d+)/, "Opera") || pick(/Firefox\\/(\\d+)/, "Firefox")
    || pick(/(?:Chrome|CriOS)\\/(\\d+)/, "Chrome") || pick(/Version\\/(\\d+)[\\d.]* .*Safari/, "Safari") || "";
  const pad = n => String(n).padStart(2, "0"), now = () => {{ const d = new Date(); return `${{d.getFullYear()}}-${{pad(d.getMonth() + 1)}}-${{pad(d.getDate())}} ${{pad(d.getHours())}}:${{pad(d.getMinutes())}}`; }};
  function report() {{
    const v = id => $(id).value.trim();
    return {{
      subject: `Trial tools problem: ${{v("rTool")}}`,
      body: [
        `Tool: ${{v("rTool")}}`,
        `Page: ${{document.title}} (${{location.pathname.split("/").pop() || "index.html"}})`,
        `When: ${{now()}}`,
        `Computer: ${{v("rDevice") || "not given"}}`,
        `Spreadsheet program: ${{v("rSheet") || "not given"}}`,
        `Browser: ${{v("rBrowser") || "not given"}}`,
        `Screen: ${{window.innerWidth}} x ${{window.innerHeight}}`,
        v("rName") ? `From: ${{v("rName")}}` : "",
        "", "WHAT WENT WRONG", v("rWhat") || "(not filled in)",
        "", "WHAT I EXPECTED", v("rExpect") || "(not filled in)",
      ].filter((l, i, a) => l !== "" || a[i - 1] !== "").join("\\n"),
    }};
  }}
  function check() {{
    if ($("rWhat").value.trim()) return true;
    $("rNote").textContent = "Please say what went wrong first.";
    $("rNote").className = "rnote err";
    $("rWhat").focus();
    return false;
  }}
  $("rSend").addEventListener("click", e => {{
    if (!check()) {{ e.preventDefault(); return; }}
    const r = report();
    window.mailtoOpening = true; setTimeout(() => {{ window.mailtoOpening = false; }}, 1500);   // opening email isn't leaving the page
    $("rSend").href = `mailto:${{TO}}?subject=${{encodeURIComponent(r.subject)}}&body=${{encodeURIComponent(r.body)}}`;
    $("rNote").textContent = `Your email app should open with the report. Check it and press Send. If nothing opens, use Copy report and email it to ${{TO}}.`;
    $("rNote").className = "rnote";
  }});
  $("rCopy").addEventListener("click", async () => {{
    if (!check()) return;
    const r = report(), text = `To: ${{TO}}\\nSubject: ${{r.subject}}\\n\\n${{r.body}}`;
    try {{ await navigator.clipboard.writeText(text); $("rNote").textContent = `Copied. Paste it into an email to ${{TO}}.`; $("rNote").className = "rnote"; }}
    catch (err) {{ $("rNote").textContent = `Copying didn't work here. Please select and copy what you typed, and email it to ${{TO}}.`; $("rNote").className = "rnote err"; }}
  }});
}})();
</script>
"""


def add_report(text, tool_title, tool_titles):
    """Put the section's styles in the page and the section after its "Good to know" box."""
    section = report_html(tool_title, tool_titles)
    if not section:
        return text
    assert text.count("</style>") == 1
    text = text.replace("</style>", REPORT_CSS + "</style>", 1)
    start = text.index('<section class="help">')
    end = text.index("  </section>\n", start) + len("  </section>\n")
    return text[:end] + section + text[end:]


def strip_report(text):
    """The reverse of add_report: take the section and its styles out of a built page."""
    if REPORT_CSS + "</style>" not in text:
        return text
    text = text.replace(REPORT_CSS + "</style>", "</style>", 1)
    start = text.index('\n  <section class="report"')
    end = text.index("</script>\n", start) + len("</script>\n")
    return text[:start] + text[end:]
