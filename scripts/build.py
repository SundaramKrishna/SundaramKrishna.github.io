#!/usr/bin/env python3
"""Build the static portfolio and resume from data/profile.json.

Usage: python3 scripts/build.py [--pdf]
The optional PDF and QR exports require ReportLab. HTML and vCard use the standard library.
"""
import argparse
import json
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
PDF_NAME = "Sundaram-Krishnan-Resume.pdf"
PDF_PATH = f"downloads/{PDF_NAME}"
VCARD_PATH = "downloads/Sundaram-Krishnan.vcf"


def bullet_list(items):
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def build_html(profile):
    fields = {key: escape(value, quote=True) for key, value in profile.items() if isinstance(value, str)}
    fields["description"] = fields["summary"]
    fields.update(pdf_path=PDF_PATH, vcard_path=VCARD_PATH)
    experience = []
    resume_experience = []
    for job in profile["experience"]:
        dates = escape(job["dates"])
        current = '<span class="current-label">Current role</span>' if job["dates"].endswith("Present") else ""
        experience.append(f'''<article class="experience-item"><div class="experience-meta"><span>{dates}</span>{current}</div><h3>{escape(job["short_name"])}</h3><p class="experience-role">{escape(job["role"])}</p>{bullet_list(job["bullets"])}</article>''')
        resume_experience.append(f'''<article><h3>{escape(job["role"])}</h3><p class="company">{escape(job["company"])}</p><p class="dates">{dates}</p>{bullet_list(job["bullets"])}</article>''')
    fields["experience_html"] = "\n".join(experience)
    fields["skills_html"] = "\n".join(f'''<div class="skill-group"><h3>{escape(group["category"])}</h3><p>{"<br>".join(escape(item) for item in group["items"])}</p></div>''' for group in profile["skills"])
    education = profile["education"]
    fields.update(degree=escape(education["degree"]), institution=escape(education["institution"]), education_dates=escape(education["dates"]))
    template = Template((ROOT / "templates/index.html").read_text())
    (ROOT / "index.html").write_text(template.substitute(fields))
    skills = "".join(f'<p><strong>{escape(group["category"])}:</strong> {escape(", ".join(group["items"]))}</p>' for group in profile["skills"])
    resume = Template('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="$description"><meta name="robots" content="noindex"><title>$name | Resume</title><link rel="icon" href="img/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="css/resume-page.css"><script src="js/resume-page.js" defer></script></head>
<body><nav class="resume-toolbar" aria-label="Resume actions"><a href="index.html">Back to portfolio</a><div><button type="button" id="print-resume" hidden>Print resume</button><a class="download" href="$pdf_path" download>Download PDF</a></div></nav>
<main class="resume"><header><h1>$name</h1><p class="role">$role</p><p class="contact">$location | <a href="tel:$phone_href">$phone</a> | <a href="mailto:$email">$email</a></p><p class="profile-links"><a href="$linkedin">$linkedin</a> | <a href="$github">$github</a> | <a href="$website">$website</a></p></header>
<section><h2>Professional Summary</h2><p>$summary</p></section><section><h2>Work Experience</h2>$resume_experience</section><section><h2>Technical skills</h2>$resume_skills</section><section><h2>Education</h2><h3>$degree</h3><p>$institution</p><p class="dates">$education_dates</p></section></main></body></html>''')
    (ROOT / "resume.html").write_text(resume.substitute(fields, resume_experience="".join(resume_experience), resume_skills=skills))
    print("Built index.html and resume.html")


def build_vcard(profile):
    def vcard_text(key):
        value = profile[key].replace("\r\n", "\n").replace("\r", "\n")
        return value.replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f'N:{vcard_text("family_name")};{vcard_text("given_name")};;;',
        f'FN:{vcard_text("name")}',
        f'TITLE:{vcard_text("role")}',
        f'TEL;TYPE=CELL:{profile["phone_href"]}',
        f'EMAIL;TYPE=INTERNET:{vcard_text("email")}',
        f'URL:{profile["website"]}',
        "END:VCARD",
    ]
    output = ROOT / VCARD_PATH
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    print(f"Built {VCARD_PATH}")


def build_resume_qr(profile):
    from PIL import Image
    from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

    code = QRCode(None, QRErrorCorrectLevel.M)
    code.addData(urljoin(profile["website"], PDF_PATH))
    code.make()
    quiet_zone = 4  # QR codes require a clear border four modules wide.
    side = code.getModuleCount() + 2 * quiet_zone
    qr_image = Image.new("1", (side, side), 1)
    for row, modules in enumerate(code.modules, start=quiet_zone):
        for column, dark in enumerate(modules, start=quiet_zone):
            if dark:
                qr_image.putpixel((column, row), 0)
    output = ROOT / "img/resume-qr.png"
    qr_image.resize((side * 8, side * 8), Image.Resampling.NEAREST).save(output)
    print(f"Built {output.relative_to(ROOT)}")


def build_pdf(profile):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

    output = ROOT / PDF_PATH
    output.parent.mkdir(exist_ok=True)
    ink, accent, muted = "#152B27", "#355F49", "#4F5B55"
    styles = {
        "name": ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=colors.HexColor(ink), spaceAfter=5),
        "role": ParagraphStyle("Role", fontName="Helvetica", fontSize=12, leading=16, textColor=colors.HexColor(accent), spaceAfter=9),
        "contact": ParagraphStyle("Contact", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor(muted)),
        "section": ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=10, leading=13, spaceBefore=17, spaceAfter=8, textColor=colors.HexColor(accent), keepWithNext=True),
        "body": ParagraphStyle("Body", fontName="Helvetica", fontSize=10, leading=14.5, textColor=colors.HexColor(ink), alignment=TA_LEFT),
        "job": ParagraphStyle("Job", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=colors.HexColor(ink), spaceAfter=2, keepWithNext=True),
        "meta": ParagraphStyle("Meta", fontName="Helvetica", fontSize=9, leading=12.5, textColor=colors.HexColor(muted), spaceAfter=5, keepWithNext=True),
        "bullet": ParagraphStyle("Bullet", fontName="Helvetica", fontSize=10, leading=14.5, leftIndent=11, firstLineIndent=-9, spaceAfter=4, textColor=colors.HexColor(ink)),
    }
    def para(text, kind="body"):
        return Paragraph(text, styles[kind])
    def link(url, label):
        return f'<link href="{escape(url, quote=True)}" color="{accent}">{escape(label)}</link>'
    story = [para(escape(profile["name"]), "name"), para(escape(profile["role"]), "role")]
    story.append(para(f'{escape(profile["location"])} | {escape(profile["phone"])} | {link("mailto:" + profile["email"], profile["email"])}', "contact"))
    story.append(para(" | ".join(link(url, url) for url in (profile["linkedin"], profile["github"], profile["website"])), "contact"))
    story.extend([para("PROFESSIONAL SUMMARY", "section"), para(escape(profile["summary"]))])
    story.append(para("WORK EXPERIENCE", "section"))
    for index, job in enumerate(profile["experience"]):
        block = [para(escape(job["role"]), "job"), para(f'{escape(job["company"])}<br/>{escape(job["dates"])}', "meta")]
        block.extend(para("- " + escape(item), "bullet") for item in job["bullets"])
        story.append(KeepTogether(block))
        if index < len(profile["experience"]) - 1:
            story.append(Spacer(1, 8))
    story.append(para("TECHNICAL SKILLS", "section"))
    for group in profile["skills"]:
        story.append(para(f'<b>{escape(group["category"])}:</b> {escape(", ".join(group["items"]))}'))
    education = profile["education"]
    story.extend([para("EDUCATION", "section"), para(escape(education["degree"]), "job"), para(f'{escape(education["institution"])} | {escape(education["dates"])}', "body")])
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=44, leftMargin=44, topMargin=37, bottomMargin=37, title=f'{profile["name"]} - Resume', author=profile["name"], pageCompression=1).build(story)
    print(f"Built {output.relative_to(ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", action="store_true", help="Also export the PDF resume and its QR code (requires ReportLab)")
    args = parser.parse_args()
    profile = json.loads((ROOT / "data/profile.json").read_text())
    build_html(profile)
    build_vcard(profile)
    if args.pdf:
        build_pdf(profile)
        build_resume_qr(profile)
