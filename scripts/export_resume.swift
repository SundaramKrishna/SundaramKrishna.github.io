// macOS PDF export without third-party packages.
// Run from the repository root: swift scripts/export_resume.swift
import AppKit
import CoreGraphics
import PDFKit

struct Job: Decodable { let company: String; let role: String; let dates: String; let bullets: [String] }
struct Skill: Decodable { let category: String; let items: [String] }
struct Education: Decodable { let institution: String; let degree: String; let dates: String }
struct Profile: Decodable {
    let name: String; let role: String; let location: String; let email: String
    let phone: String; let website: String; let linkedin: String; let github: String
    let summary: String; let experience: [Job]; let skills: [Skill]; let education: Education
}

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let profile = try JSONDecoder().decode(Profile.self, from: Data(contentsOf: root.appendingPathComponent("data/profile.json")))
let directory = root.appendingPathComponent("downloads")
try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
let output = directory.appendingPathComponent("Sundaram-Krishnan-Resume.pdf")
let pageWidth: CGFloat = 595.28
let pageHeight: CGFloat = 841.89
var bounds = CGRect(x: 0, y: 0, width: pageWidth, height: pageHeight)
let metadata: [CFString: Any] = [kCGPDFContextTitle: "\(profile.name) - Resume", kCGPDFContextAuthor: profile.name]
guard let context = CGContext(output as CFURL, mediaBox: &bounds, metadata as CFDictionary) else { fatalError("Cannot create PDF") }
context.beginPDFPage(nil)
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)
let ink = NSColor(calibratedRed: 0.08, green: 0.17, blue: 0.15, alpha: 1)
let muted = NSColor(calibratedRed: 0.31, green: 0.36, blue: 0.33, alpha: 1)
let accent = NSColor(calibratedRed: 0.21, green: 0.37, blue: 0.29, alpha: 1)
var cursor: CGFloat = 38
let margin: CGFloat = 44
let contentWidth = pageWidth - margin * 2

@discardableResult
func text(_ value: String, size: CGFloat = 10, bold: Bool = false, color: NSColor = ink, after: CGFloat = 0, indent: CGFloat = 0) -> CGRect {
    let font = NSFont(name: bold ? "Helvetica-Bold" : "Helvetica", size: size)!
    let paragraph = NSMutableParagraphStyle()
    paragraph.lineSpacing = size * 0.24
    paragraph.lineBreakMode = .byWordWrapping
    let styled = NSAttributedString(string: value, attributes: [.font: font, .foregroundColor: color, .paragraphStyle: paragraph])
    let width = contentWidth - indent
    let measured = styled.boundingRect(with: NSSize(width: width, height: 1000), options: [.usesLineFragmentOrigin, .usesFontLeading])
    let height = ceil(measured.height) + 2
    let rect = CGRect(x: margin + indent, y: pageHeight - cursor - height, width: width, height: height)
    styled.draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
    cursor += height + after
    return rect
}
func heading(_ value: String) {
    cursor += 15
    text(value.uppercased(), size: 10, bold: true, color: accent, after: 6)
}
text(profile.name, size: 25, bold: true, after: 4)
text(profile.role, size: 12, color: accent, after: 8)
text("\(profile.location) | \(profile.phone) | \(profile.email)", size: 9, color: muted, after: 2)
for url in [profile.linkedin, profile.github, profile.website] {
    let rect = text(url, size: 9, color: accent)
    context.setURL(URL(string: url)! as CFURL, for: rect)
}
heading("Professional Summary")
text(profile.summary)
heading("Work Experience")
for (index, job) in profile.experience.enumerated() {
    text(job.role, size: 10.5, bold: true, after: 2)
    text(job.company, size: 9, color: muted, after: 1)
    text(job.dates, size: 9, color: muted, after: 5)
    for bullet in job.bullets { text("- " + bullet, after: 3, indent: 3) }
    if index < profile.experience.count - 1 { cursor += 7 }
}
heading("Technical skills")
for group in profile.skills { text("\(group.category): \(group.items.joined(separator: ", "))") }
heading("Education")
text(profile.education.degree, size: 10.5, bold: true, after: 2)
text("\(profile.education.institution) | \(profile.education.dates)", size: 10)
precondition(cursor < pageHeight - 35, "Resume exceeds one page: adjust layout before delivery")
NSGraphicsContext.restoreGraphicsState()
context.endPDFPage()
context.closePDF()

// Verify the exported page and render a PNG for visual inspection.
guard let pdf = PDFDocument(url: output), pdf.pageCount == 1, let page = pdf.page(at: 0) else { fatalError("Expected a one-page PDF") }
guard let extracted = pdf.string, extracted.contains(profile.name), extracted.contains(profile.education.institution) else { fatalError("PDF text verification failed") }
let preview = page.thumbnail(of: NSSize(width: 1190, height: 1684), for: .mediaBox)
let bitmap = NSBitmapImageRep(data: preview.tiffRepresentation!)!
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "/tmp/sundaram-resume-preview.png"))
print("Created \(output.path); 1 page; content ends at \(Int(cursor))pt; text extraction verified.")
