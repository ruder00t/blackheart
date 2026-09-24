#!/usr/bin/env python3
"""
CPTS-style pentest report builder.

    report.md  ->  pandoc  ->  HTML + CSS  ->  WeasyPrint  ->  out/report.pdf

Everything the report references (logo, screenshots) is embedded in the PDF,
so the resulting file is standalone and safe to share on its own.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: python3-yaml  (apt install python3-yaml)")

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "assets" / "report.html"
STYLESHEET = ROOT / "assets" / "style.css"

# CVSS 3.1 severity bands, as documented in Appendix A.1 of the report.
SEVERITY_BANDS = [
    ("Critical", 9.0, 10.0),
    ("High", 7.0, 8.9),
    ("Medium", 4.0, 6.9),
    ("Low", 0.1, 3.9),
    ("Info", 0.0, 0.0),
]
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]


# --------------------------------------------------------------------------
# Source preparation
# --------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 2)
    if len(parts) < 2:
        return {}, text
    meta = yaml.safe_load(parts[0].lstrip("-\n")) or {}
    body = parts[1].lstrip("\n")
    if len(parts) == 3:
        body = parts[2].lstrip("\n")
    return meta, body


def strip_comments(text: str) -> str:
    """Drop `//` comment lines, leaving fenced code blocks untouched."""
    out, fence = [], None
    for line in text.split("\n"):
        stripped = line.strip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            out.append(line)
            continue
        match = re.match(r"^(```+|~~~+)", stripped)
        if match:
            fence = match.group(1)[:3]
            out.append(line)
            continue
        if stripped.startswith("//"):
            continue
        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------

@dataclass
class Finding:
    number: int
    title: str = "Untitled Finding"
    severity: str = "Info"
    cvss: str = ""
    vector: str = ""
    cwe: str = ""
    affected: str = ""
    sections: list[tuple[str, str]] = field(default_factory=list)

    @property
    def anchor(self) -> str:
        return f"finding-{self.number}"

    @property
    def score_label(self) -> str:
        return f"{self.cvss} ({self.severity})" if self.cvss else self.severity


def severity_from_score(score: float) -> str:
    for name, low, high in SEVERITY_BANDS:
        if low <= score <= high:
            return name
    return "Info"


def parse_finding(block: str, number: int) -> Finding:
    """Parse one `::: finding` block: key/value header, then `## Label` parts."""
    finding = Finding(number=number)
    lines = block.split("\n")
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if line.strip().startswith("##") or (not line.strip() and idx > 0):
            if line.strip().startswith("##"):
                break
        match = re.match(r"^\s*([A-Za-z][\w-]*)\s*:\s*(.*)$", line)
        if match and not line.startswith(" " * 4):
            key, value = match.group(1).lower(), match.group(2).strip()
            if key == "title":
                finding.title = value
            elif key == "severity":
                finding.severity = value.capitalize()
            elif key == "cvss":
                finding.cvss = value
            elif key in ("vector", "cvss-vector", "cvss_vector"):
                finding.vector = value
            elif key == "cwe":
                finding.cwe = value
            elif key in ("affected", "affected-hosts", "host", "hosts"):
                finding.affected = value
        elif line.strip():
            break
        idx += 1

    # Severity is derived from the CVSS score when one is supplied.
    if finding.cvss:
        try:
            finding.severity = severity_from_score(float(finding.cvss))
        except ValueError:
            pass

    rest = "\n".join(lines[idx:])
    chunks = re.split(r"^##\s+(.+?)\s*$", rest, flags=re.MULTILINE)
    if chunks[0].strip():
        finding.sections.append(("Description", chunks[0].strip()))
    for label, body in zip(chunks[1::2], chunks[2::2]):
        finding.sections.append((label.strip(), body.strip()))
    return finding


def render_finding(finding: Finding) -> str:
    """Emit the finding as raw HTML with Markdown left intact between blocks.

    Pandoc ends a raw HTML block at a blank line, so the section bodies
    surrounded by blank lines are still parsed as Markdown.
    """
    sev_class = f"sev-{finding.severity.lower()}"
    esc = html.escape

    meta_rows = []
    if finding.cwe:
        meta_rows.append(f"<tr><th>CWE</th><td>{esc(finding.cwe)}</td></tr>")
    score = esc(finding.cvss) if finding.cvss else "N/A"
    if finding.vector:
        score += f' <span class="vector">{esc(finding.vector)}</span>'
    meta_rows.append(f"<tr><th>CVSS 3.1</th><td>{score}</td></tr>")
    if finding.affected:
        meta_rows.append(
            f"<tr><th>Affected</th><td>{esc(finding.affected)}</td></tr>"
        )

    parts = [
        f'<div class="finding {sev_class}" id="{finding.anchor}">',
        '<div class="finding-head">',
        f'<span class="finding-num">{finding.number}.</span>'
        f'<span class="finding-title">{esc(finding.title)}</span>'
        f'<span class="sev-badge {sev_class}">{esc(finding.severity)}</span>',
        "</div>",
        '<table class="finding-meta">',
        "".join(meta_rows),
        "</table>",
        "",
    ]
    for label, body in finding.sections:
        parts.append(f'<div class="finding-part"><h4>{esc(label)}</h4>')
        parts.append("")
        parts.append(body)
        parts.append("")
        parts.append("</div>")
        parts.append("")
    parts.append("</div>")
    return "\n".join(parts)


def extract_findings(text: str) -> tuple[str, list[Finding]]:
    findings: list[Finding] = []
    pattern = re.compile(
        r"^:::+\s*(?:\{?\.?finding\}?)\s*$(.*?)^:::+\s*$",
        re.DOTALL | re.MULTILINE,
    )

    def replace(match: re.Match) -> str:
        finding = parse_finding(match.group(1).strip("\n"), len(findings) + 1)
        findings.append(finding)
        return render_finding(finding)

    return pattern.sub(replace, text), findings


# --------------------------------------------------------------------------
# Generated content
# --------------------------------------------------------------------------

def findings_table(findings: list[Finding]) -> str:
    if not findings:
        return '<p class="empty-note">No findings recorded.</p>'
    rows = []
    for f in findings:
        rows.append(
            f"<tr><td>{f.number}</td>"
            f'<td><span class="sev-pill sev-{f.severity.lower()}">'
            f"{html.escape(f.score_label)}</span></td>"
            f'<td><a href="#{f.anchor}">{html.escape(f.title)}</a></td>'
            f'<td class="pageref"><a href="#{f.anchor}"></a></td></tr>'
        )
    return (
        '<table class="findings-summary">\n'
        "<thead><tr><th>#</th><th>Severity Level</th>"
        "<th>Finding Name</th><th>Page</th></tr></thead>\n"
        f"<tbody>{''.join(rows)}</tbody>\n</table>"
    )


# Colours are written as SVG presentation attributes: WeasyPrint renders inline
# SVG with its own engine, so the page stylesheet does not cascade into it.
CHART_COLOURS = {
    "Critical": "#9e1b28",
    "High": "#e03131",
    "Medium": "#ffb224",
    "Low": "#4899e8",
    "Info": "#8b949e",
}
CHART_TRACK = "#2a2e34"   # empty portion of each bar
CHART_LABEL = "#e6e8ea"   # severity names
CHART_COUNT = "#99a2ad"   # counts


def severity_chart(counts: dict[str, int], colours: dict | None = None) -> str:
    """Horizontal bar chart as inline SVG - no external chart dependency."""
    if not sum(counts.values()):
        return '<p class="empty-note">No findings to chart.</p>'
    row_h, gap, label_w, bar_max = 24, 10, 70, 300
    height = len(SEVERITY_ORDER) * (row_h + gap)
    peak = max(counts.values()) or 1
    parts = []
    for i, name in enumerate(SEVERITY_ORDER):
        count = counts.get(name, 0)
        y = i * (row_h + gap)
        width = (count / peak) * bar_max
        baseline = y + row_h * 0.72
        parts.append(
            f'<text x="{label_w - 10}" y="{baseline}" text-anchor="end" '
            f'font-family="sans-serif" font-size="12" font-weight="600" '
            f'fill="{CHART_LABEL}">{name}</text>'
            f'<rect x="{label_w}" y="{y}" width="{bar_max}" height="{row_h}" '
            f'fill="{CHART_TRACK}" rx="2"/>'
        )
        if count:
            parts.append(
                f'<rect x="{label_w}" y="{y}" width="{width:.1f}" '
                f'height="{row_h}" fill="{(colours or CHART_COLOURS).get(name, CHART_COLOURS[name])}" rx="2"/>'
            )
        parts.append(
            f'<text x="{label_w + bar_max + 10}" y="{baseline}" '
            f'font-family="sans-serif" font-size="12" font-weight="700" '
            f'fill="{CHART_COUNT}">{count}</text>'
        )
    return (
        f'<div class="chart"><svg viewBox="0 0 {label_w + bar_max + 40} {height}" '
        f'width="100%" role="img" '
        f'aria-label="Distribution of identified vulnerabilities by severity">'
        f'{"".join(parts)}</svg>'
        f'<p class="figure-caption">Distribution of identified vulnerabilities</p>'
        f"</div>"
    )


def breakdown_sentence(counts: dict[str, int]) -> str:
    parts = [f"{counts.get(n, 0)} {n.lower()}-risk" for n in SEVERITY_ORDER[:4]]
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def apply_tokens(text: str, findings: list[Finding], colours: dict | None = None) -> str:
    counts = {n: 0 for n in SEVERITY_ORDER}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    risk = sum(v for k, v in counts.items() if k != "Info")
    tokens = {
        "FINDINGS_TABLE": findings_table(findings),
        "SEVERITY_CHART": severity_chart(counts, colours),
        "SEVERITY_BREAKDOWN": breakdown_sentence(counts),
        "TOTAL_FINDINGS": str(len(findings)),
        "RISK_FINDINGS": str(risk),
        "CRITICAL_COUNT": str(counts["Critical"]),
        "HIGH_COUNT": str(counts["High"]),
        "MEDIUM_COUNT": str(counts["Medium"]),
        "LOW_COUNT": str(counts["Low"]),
        "INFO_COUNT": str(counts["Info"]),
    }
    for key, value in tokens.items():
        text = text.replace("{{" + key + "}}", value)
    return text


# --------------------------------------------------------------------------
# Headings, numbering and table of contents
# --------------------------------------------------------------------------

def number_headings(text: str, findings: list[Finding]) -> tuple[str, str]:
    """Prefix headings with CPTS numbering and build the TOC markup."""
    out, toc = [], []
    fence = None
    section = 0
    appendix_idx = -1
    in_appendix = False
    sub = 0
    top_label = ""
    findings_emitted = False

    for line in text.split("\n"):
        stripped = line.strip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            out.append(line)
            continue
        match = re.match(r"^(```+|~~~+)", stripped)
        if match:
            fence = match.group(1)[:3]
            out.append(line)
            continue

        heading = re.match(r"^(#{1,2})\s+(.*?)\s*$", line)
        if not heading:
            out.append(line)
            continue

        level, title = len(heading.group(1)), heading.group(2)
        is_appendix = bool(re.search(r"\{\.appendix\}", title))
        title = re.sub(r"\s*\{\.appendix\}", "", title).strip()

        if level == 1:
            if is_appendix:
                in_appendix = True
                appendix_idx += 1
                top_label = chr(ord("A") + appendix_idx)
            else:
                section += 1
                top_label = str(section)
            sub = 0
            anchor = f"sec-{top_label}"
        else:
            sub += 1
            top_label_current = top_label or str(section)
            anchor = f"sec-{top_label_current}-{sub}"

        label = top_label if level == 1 else f"{top_label}.{sub}"
        out.append(f"{'#' * level} {label} {title} {{#{anchor}}}")
        toc.append(
            f'<li class="toc-l{level}"><a href="#{anchor}">'
            f'<span class="toc-num">{label}</span>'
            f'<span class="toc-text">{html.escape(title)}</span></a></li>'
        )

        # Findings live under the "Technical Findings Details" section.
        if level == 1 and not findings_emitted and "finding" in title.lower():
            findings_emitted = True
            for f in findings:
                toc.append(
                    f'<li class="toc-l3"><a href="#{f.anchor}">'
                    f'<span class="toc-num">{f.number}.</span>'
                    f'<span class="toc-text">{html.escape(f.title)}</span></a></li>'
                )

    return "\n".join(out), f'<ul class="toc-list">{"".join(toc)}</ul>'


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

_HELP_CACHE: str | None = None


def _pandoc_help() -> str:
    global _HELP_CACHE
    if _HELP_CACHE is None:
        _HELP_CACHE = subprocess.run(
            ["pandoc", "--help"], capture_output=True, text=True
        ).stdout
    return _HELP_CACHE


def run_pandoc(markdown: str, resource_dir: Path) -> str:
    extensions = (
        "markdown+pipe_tables+grid_tables+fenced_divs+bracketed_spans"
        "+raw_html+implicit_figures+header_attributes+backtick_code_blocks"
        "+fenced_code_attributes+auto_identifiers+table_captions"
    )
    # --highlight-style was renamed in newer pandoc releases.
    highlight = (
        "--syntax-highlighting"
        if "--syntax-highlighting" in _pandoc_help()
        else "--highlight-style"
    )
    cmd = [
        "pandoc",
        "--from", extensions,
        "--to", "html5",
        "--strip-comments",
        highlight, "tango",
        "--wrap", "preserve",
        "--resource-path", str(resource_dir),
    ]
    result = subprocess.run(
        cmd, input=markdown, capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"pandoc failed:\n{result.stderr}")
    if result.stderr.strip():
        print(f"  pandoc: {result.stderr.strip()}", file=sys.stderr)
    return result.stdout


def cover_fields(meta: dict) -> dict:
    today = time.strftime("%d %B %Y")
    return {
        "TITLE": meta.get("title", "Penetration Test Report"),
        "SUBTITLE": meta.get("subtitle", "Report of Findings"),
        "DOCTYPE": meta.get("document_type", "Penetration Test"),
        "CLIENT": meta.get("client", ""),
        "CANDIDATE": meta.get("candidate", meta.get("author", "")),
        "CANDIDATE_TITLE": meta.get("candidate_title", ""),
        "CANDIDATE_EMAIL": meta.get("candidate_email", ""),
        "VERSION": str(meta.get("version", "1.0")),
        "DATE": str(meta.get("date", today)),
        "CLASSIFICATION": meta.get("classification", "CONFIDENTIAL"),
        "LOGO": meta.get("logo", "assets/logo.png"),
    }


def build(source: Path, output: Path, keep_html: bool = False,
          base_dir: Path | None = None, style_override: str = "",
          chart_colours: dict | None = None,
          logo_override: Path | None = None) -> Path:
    raw = source.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)

    # where images (relative and absolute) resolve from
    base = Path(base_dir).resolve() if base_dir else source.parent.resolve()

    body = strip_comments(body)
    body, findings = extract_findings(body)
    body = apply_tokens(body, findings, chart_colours)
    body, toc = number_headings(body, findings)

    content = run_pandoc(body, base)

    fields = cover_fields(meta)
    if logo_override and Path(logo_override).exists():
        logo_path = Path(logo_override).resolve()
    else:
        logo_path = base / fields["LOGO"]
        if not logo_path.exists():
            logo_path = ROOT / "assets" / "logo.png"

    template = TEMPLATE.read_text(encoding="utf-8")
    page = template.replace("{{CONTENT}}", content).replace("{{TOC}}", toc)
    page = page.replace("{{STYLESHEET}}", STYLESHEET.as_uri())
    page = page.replace("{{STYLE_OVERRIDE}}", style_override or "")
    page = page.replace("{{LOGO_PATH}}", logo_path.as_uri())
    for key, value in fields.items():
        page = page.replace("{{" + key + "}}", html.escape(str(value)))

    html_path = output.with_suffix(".html")
    output.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(page, encoding="utf-8")

    from weasyprint import HTML  # imported late; it is slow to load

    HTML(string=page, base_url=str(base) + "/").write_pdf(str(output))
    if not keep_html:
        html_path.unlink(missing_ok=True)

    counts: dict[str, int] = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    summary = ", ".join(
        f"{counts[s]} {s}" for s in SEVERITY_ORDER if counts.get(s)
    )
    size_kb = output.stat().st_size / 1024
    print(
        f"  {output}  ({size_kb:.0f} KB, {len(findings)} findings"
        + (f": {summary}" if summary else "")
        + ")"
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a pentest report PDF.")
    parser.add_argument("source", nargs="?", default="report.md",
                        help="Markdown source (default: report.md)")
    parser.add_argument("-o", "--output", help="Output PDF path")
    parser.add_argument("--html", action="store_true",
                        help="Keep the intermediate HTML for debugging")
    parser.add_argument("--watch", action="store_true",
                        help="Rebuild whenever the source or assets change")
    args = parser.parse_args()

    if not shutil.which("pandoc"):
        sys.exit("pandoc is not installed (apt install pandoc)")

    source = Path(args.source).resolve()
    if not source.exists():
        sys.exit(f"No such file: {source}")
    output = (
        Path(args.output).resolve()
        if args.output
        else ROOT / "out" / f"{source.stem}.pdf"
    )

    if not args.watch:
        build(source, output, args.html)
        return

    watched = [source, STYLESHEET, TEMPLATE]
    print(f"Watching {source.name}, style.css and report.html - Ctrl-C to stop")
    last: float = 0
    while True:
        newest = max(
            (p.stat().st_mtime for p in watched if p.exists()), default=0
        )
        if newest > last:
            last = newest
            try:
                build(source, output, args.html)
            except SystemExit as exc:
                print(f"  build failed: {exc}", file=sys.stderr)
            except Exception as exc:  # keep the watcher alive on any error
                print(f"  build failed: {exc}", file=sys.stderr)
        time.sleep(1)


if __name__ == "__main__":
    main()
