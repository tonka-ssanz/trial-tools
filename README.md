# SSANZ trial tools

Web pages that turn an SSANZ trial entries download (Excel or CSV) into the lists, documents and results sheets a trial needs. Trial organisers ("users") open a page in their browser, drop in their spreadsheet and download the result. Nothing is installed and nothing is uploaded.

This repository is the test site, served by GitHub Pages while the tools are tried out by several people. The plan is to host the finished tools on the SSANZ organisation website.

Last updated: October 2026.

## The tools

| Step | Page | What it does | Output |
|---|---|---|---|
| – | `index.html` | Front page: lists the tools in order of use | – |
| 1 | `payment-split.html` | Splits entries into Paid, Part Paid and Not Paid, and shows who still owes | Same spreadsheet + 3 tabs |
| 2 | `email-list.html` | One email per person (all entries, or only chosen trials), ready for BCC | Same spreadsheet + Emails tab |
| 3 | `trial-lists.html` | Starts the trial spreadsheet: locked copy of the download, a Master List for late entries and withdrawals, and one randomly ordered tab per trial. Dropped in again later, it applies changes to the trial tabs | The trial spreadsheet (.xlsx) |
| 4 | `trial-documents.html` | Running orders, callboards, timekeepers' and judges' sheets (Word), judging sheets and certificates (PDF) | .docx and .pdf files, plus the trial spreadsheet with its settings saved |
| 5 | `results-sheets.html` | Fills in the official SSANZ results spreadsheet for each class (organisation, date, venue, Trial #, judges, dogs) | One .xlsx per class |

Steps 1 and 2 can be used at any time on an entries download. Steps 3 to 5 work on one growing trial spreadsheet, which the user keeps and drops back into the next tool.

## How it works

- **Static pages only.** Each page is a single HTML file with its styles and script inline. There is no server code, database, build step on the server, login, cookies, browser storage or analytics.
- **All processing happens in the visitor's browser.** Files are read with the File API and results are downloaded as files the page creates (`blob:` links). No data leaves the computer, so the pages never see or keep anyone's entries.
- **Saving progress lives in the user's own spreadsheet**, not on a server. Trial Lists adds a "Tool Settings" tab holding the tools' settings as JSON (with a check value, so edits made outside the tools are noticed). Later tools read it back, so users can stop between steps and carry on later.
- **Libraries** are loaded from cdnjs, pinned to these versions:
  - ExcelJS 4.4.0 (reading and writing .xlsx): Payment Split, Email List, Trial Lists, Trial Documents
  - PapaParse 5.4.1 (reading CSV): Payment Split, Email List, Trial Lists
  - JSZip 3.10.1 (building Word files; editing the SSANZ results sheet without re-saving it through a library): Trial Documents, Results Sheets
- **Fonts** come from Google Fonts (Bricolage Grotesque, Atkinson Hyperlegible, IBM Plex Mono). The handwriting-style font printed on certificates (Kalam, SIL Open Font Licence) is embedded in `trial-documents.html`.
- The pages need an internet connection to load the libraries and fonts. They're written for current versions of Chrome, Edge, Firefox and Safari, on computers and phones; so far they've been checked mainly in Chrome.

## Hosting the tools on another website

1. Copy the six `.html` files at the top of this repository (`index.html` and the five tool pages) into one folder on the site. They link to each other with relative links, so keep them together and keep the file names.
2. Serve them as ordinary `text/html` over HTTPS. Nothing else is needed: no server settings, redirects or other file types.
3. If the site sends a **Content Security Policy**, it must allow:

   | Directive | Allow |
   |---|---|
   | `script-src` | `https://cdnjs.cloudflare.com` and `'unsafe-inline'` (every page has inline scripts) |
   | `style-src` | `https://fonts.googleapis.com` and `'unsafe-inline'` (inline styles) |
   | `font-src` | `https://fonts.gstatic.com` |
   | `img-src` | `'self' blob:` (the logo preview in Trial Documents) |
   | `frame-src` | `blob:` (the PDF preview in Trial Documents) |

   If the site's policy can't allow inline scripts, the simplest option is to relax the policy for this one folder.
4. Open each page once after copying it and drop in a test file (see "Testing" below) to check the libraries load.

The folders `src/` and `build/` are only needed to change the tools. They don't need to be on the live site.

## What's in this repository

```
index.html, *-*.html   The site: built pages, served by GitHub Pages
src/                   The source page for each tool (the page without the shared site extras)
build/                 The build script that turns src/ into the site pages
README.md              This file
```

### The site extras added by the build

Each tool is written as a standalone page in `src/`. The build (`build/build-toolkit.py`) copies it to the site and adds:

- a bar at the top: "← All trial tools" and "Step N of 5";
- a "Next step" box before the "Good to know" section, pointing to the next tool;
- a "Found a problem? Report it" section at the bottom (from `build/report_section.py`). It opens the visitor's own email app with a report addressed to the test coordinator, filled in from what they typed. Nothing is sent by the page itself. To remove it once testing is over, set `REPORT_TO = ""` in `report_section.py` and rebuild.

It also writes `index.html`, with one card per tool in the order of the `TOOLS` list.

### Changing a tool

Edit the page in `src/` and rebuild. Don't edit the built pages at the top of the repository by hand: the next build overwrites them.

From the repository's top folder (needs Python 3.10 or later; no packages to install):

```
python3 build/build-toolkit.py build src .     # rebuild every page from src/
python3 build/build-toolkit.py check src .     # confirm the site pages match a fresh build
python3 build/build-toolkit.py strip . src     # the reverse: recover src/ from the site pages
```

- To change a tool's card on the front page, the step order or the "Next step" wording, edit `TOOLS` (and `LAST_STEP`, `FRONT_NOTE`) at the top of `build-toolkit.py`.
- To add a tool, put its page in `src/` and add an entry to `TOOLS` (list order = order of use). Its page needs exactly one `<style>` block, one `<div class="wrap">` and one `<section class="help">`, which is where the build adds the extras.
- Settings that change from time to time are near the top of each tool's script, for example the list of SSANZ organisations and their Org Ref IDs (in both Trial Documents and Results Sheets; keep the two lists the same), regulation search times, and the layout of each printed document.

## Data and privacy

The entries download contains personal details (names, email addresses, dog details and payment status). The tools are designed so that this never leaves the user's computer: no upload, no server, no storage in the browser. Users are told to keep the trial spreadsheet for at least 12 months, stored securely and not on a shared computer.

The example data shown on each page before a file is dropped is made up.

## Testing

Each page shows a made-up example as soon as it opens, so it can be checked without real data. To test properly, use an entries download from a past trial (not shared outside the trial's organisers), and follow the steps on the front page in order. Problems found while testing go through the "Report a problem" section on each page.

Status in October 2026: being tested by several users. Still to be checked: the spreadsheets in every program users have (Windows Excel, Excel for Mac, Excel for the web, Google Sheets), the Word files in Microsoft Word, the results sheets in Excel, and certificates printed on the real SSANZ cards.
