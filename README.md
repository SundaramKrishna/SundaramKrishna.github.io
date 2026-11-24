# Sundaram Krishnan Portfolio

A responsive, static portfolio and one-page resume for GitHub Pages. The live pages use plain HTML, CSS and JavaScript, system fonts and local assets; there are no runtime packages or external font requests.

## Update content

Edit `data/profile.json` for contact information, experience, skills and education. Update `templates/index.html` for the introductory copy and selected-work narrative. Do not edit the generated `index.html` or `resume.html` directly.

Generate both HTML pages and the downloadable contact card:

```sh
python3 scripts/build.py
```

Regenerate the PDF and its QR code after resume or website URL changes:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-resume.txt
.venv/bin/python scripts/build.py --pdf
```

The PDF and vCard are written to `downloads/`. The QR code at `img/resume-qr.png` points to the public PDF URL. Commit the generated pages and updated assets alongside source edits so GitHub Pages serves them. No server-side build is required.

On macOS, an alternative exporter uses the built-in Swift and PDFKit frameworks without third-party packages:

```sh
swift scripts/export_resume.swift
```

This export also checks the PDF page count and text, and writes a temporary PNG preview to `/tmp/sundaram-resume-preview.png` for visual inspection.

## Preview

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Check desktop and mobile widths, keyboard navigation, the mobile menu, resume download and resume printing. Navigation and content remain usable without JavaScript.

## Content review

The initial rewrite preserves the previous portfolio's job titles, dates, education and listed skills. Before using the resume for applications, confirm the current title and dates, then add specific project ownership, team scope and measurable outcomes where available. No performance metrics or additional technologies have been assumed.

The prior Bootstrap, jQuery, SCSS and icon-font assets are retained for reference but are no longer loaded by either page. The active styles are `css/portfolio.css` and `css/resume-page.css`.
