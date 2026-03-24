import re
from typing import List


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text


def remove_consecutive_duplicate_paragraphs(text: str) -> str:
    """Remove consecutive duplicate paragraphs (common PDF extraction artifact)."""
    t = normalize_text(text)
    paras = [p.strip() for p in t.split("\n\n")]
    out: List[str] = []
    prev: str | None = None

    for p in paras:
        if not p:
            continue
        if prev is not None and p == prev:
            continue
        out.append(p)
        prev = p

    return "\n\n".join(out).strip() + "\n"


def clean_chunk_text(text: str, *, remove_tables: bool) -> str:
    """Extra cleaning: remove figure/image artifacts; optionally drop table-like blocks."""
    t = text

    # Normalize unicode non-breaking spaces and normalize newlines.
    t = t.replace("\u00a0", " ")
    t = normalize_text(t)

    lines = t.split("\n")
    out: List[str] = []

    # Regexes for figure / image artifacts
    fig_heading = re.compile(
        r"^\s*(figure|fig\.?|image|photo|illustration|chart)\s*\d+\s*[:.-]?\s*.*$",
        re.IGNORECASE,
    )
    fig_ref_inline = re.compile(
        r"\((see\s+)?(figure|fig\.?|table)\s*\d+[^)]*\)",
        re.IGNORECASE,
    )
    fig_only_line = re.compile(
        r"^\s*(see\s+)?(figure|fig\.?|table)\s*\d+\s*(on\s+page\s*\d+)?\s*\.?\s*$",
        re.IGNORECASE,
    )

    # A loose copyright / credit line often attached to images
    credit_line = re.compile(
        r"^\s*(copyright|\u00a9|reprinted\s+with\s+permission|source\s*:)\b.*$",
        re.IGNORECASE,
    )

    # PyMuPDF-Layout picture placeholders
    picture_placeholder = re.compile(
        r"^\s*==>\s*picture\s*\[\s*\d+\s*x\s*\d+\s*\]\s*<==\s*$",
        re.IGNORECASE,
    )

    # Some extractions include explicit picture-text blocks
    picture_text_start = re.compile(
        r"^\s*-{2,}\s*start\s+of\s+picture\s+text\s*-{2,}\s*$",
        re.IGNORECASE,
    )
    picture_text_end = re.compile(
        r"^\s*-{2,}\s*end\s+of\s+picture\s+text\s*-{2,}\s*$",
        re.IGNORECASE,
    )

    # Common scholarly front-matter / boilerplate lines
    doi_line = re.compile(r"\b(doi\s*:|doi\.org/|https?://\S+|www\.)\b", re.IGNORECASE)
    received_line = re.compile(
        r"^\s*(received|accepted|published\s+online|available\s+online|revised)\s*:\s*.*$",
        re.IGNORECASE,
    )
    dates_inline = re.compile(r"\b(received|accepted|published\s+online)\b", re.IGNORECASE)
    author_copyright = re.compile(
        r"\b(the\s+author\(s\)|springer|elsevier|wiley|copyright|\u00a9)\b",
        re.IGNORECASE,
    )

    # Front-matter banner and copyright/author list regexes
    copyright_line2 = re.compile(
        r"^\s*(?:©|\(c\))\s*.*$|^\s*the\s+author\(s\)\s+\d{4}\s*$",
        re.IGNORECASE,
    )

    # Long author lists often contain many commas, affiliation markers, and correspondence symbols
    author_list_line = re.compile(r"^(?=.{25,}).*(?:,|\u2709|\*|\[\d+\]|\d+){3,}.*$")

    # Affiliations / contact / editorial / journal branding junk
    email_line = re.compile(r"\bemail\s*:\s*\S+@\S+|\b\S+@\S+\b", re.IGNORECASE)
    edited_by_line = re.compile(r"^\s*edited\s+by\b.*$", re.IGNORECASE)
    official_journal_line = re.compile(r"^\s*official\s+journal\s+of\b.*$", re.IGNORECASE)
    contributed_equally_line = re.compile(
        r"^\s*(these\s+authors\s+contributed\s+equally|contributed\s+equally)\b.*$",
        re.IGNORECASE,
    )

    # Affiliation lines often contain institution keywords and locations; remove near the top
    affiliation_keywords = re.compile(
        r"\b(univ(ersity)?|ins?erm|ephe|cnrs|department|laboratoire|laboratory|hospital|center|centre|"
        r"montpellier|france|belgique|belgium|li[eè]ge|paris|london|berlin|usa|u\.s\.|uk)\b",
        re.IGNORECASE,
    )

    # Running headers like "E.M. Richard et al." or "Hilson et al."
    author_running_header = re.compile(
        r"^\s*(?:[A-Z](?:\.[A-Z])?\.?\s*)?[A-Z][a-z]+\s+et\s+al\.?\s*$"
    )

    # Journal citation header-like lines
    journal_citation = re.compile(
        r"^\s*[A-Z][A-Za-z&()\-\u2013\u2014\s]{8,}\(\d{4}\)\s*[0-9]{1,4}[^A-Za-z]*[0-9]{1,6}.*$"
    )

    # Heuristic: table-like line
    table_like = re.compile(r"(\t|\s{2,}).*(\t|\s{2,})")
    sep_like = re.compile(r"^\s*[-_=]{3,}\s*$")

    in_table_block = False
    non_empty_seen = 0
    in_picture_text = False
    picture_text_lines_skipped = 0

    for ln in lines:
        s = ln.strip()
        if s:
            non_empty_seen += 1

        # Remove leading Markdown quote marker for matching
        ln_match = re.sub(r"^\s*>\s*", "", ln)
        s_match = ln_match.strip()

        # Skip explicit picture-text blocks
        if picture_text_start.match(ln_match):
            in_picture_text = True
            picture_text_lines_skipped = 0
            continue

        if in_picture_text:
            picture_text_lines_skipped += 1
            if (
                picture_text_end.match(ln_match)
                or not s_match
                or picture_text_lines_skipped >= 40
            ):
                in_picture_text = False
            continue

        # Drop common footer artifacts like "1 3"
        if re.match(r"^\s*\d+\s+\d+\s*$", ln_match):
            continue

        # Drop standalone page numbers like "702"
        if re.match(r"^\s*\d{1,4}\s*$", ln_match) and len(s_match) <= 4:
            continue

        # Hard-drop known repeating journal header line
        if re.search(
            r"\bArchives\s+of\s+Gynecology\s+and\s+Obstetrics\b",
            ln_match,
            flags=re.IGNORECASE,
        ):
            continue

        # Drop editorial / journal branding / contact blocks near the top
        if non_empty_seen <= 120:
            if (
                edited_by_line.match(ln_match)
                or official_journal_line.match(ln_match)
                or contributed_equally_line.match(ln_match)
            ):
                continue
            if email_line.search(ln_match):
                continue
            if author_running_header.match(ln_match):
                continue
            if copyright_line2.match(ln_match):
                continue
            if author_list_line.match(ln_match):
                continue

            if affiliation_keywords.search(ln_match) and len(s_match) < 220:
                if re.match(r"^\s*\d+\b", ln_match) or "," in ln_match or ";" in ln_match:
                    continue

        # Drop PyMuPDF-Layout picture placeholders
        if picture_placeholder.match(ln_match):
            continue

        # Drop obvious OCR/image-gibberish lines
        if s_match:
            letters = sum(ch.isalpha() for ch in s_match)
            alpha_ratio = letters / max(1, len(s_match))
            if len(s_match) >= 25 and alpha_ratio < 0.25:
                if re.search(r"\d", s_match) and re.search(r"[=*_\[\]{}<>|]", s_match):
                    continue

        # Drop DOI / URL lines
        if doi_line.search(ln_match):
            continue

        # Drop common publication history lines
        if received_line.match(ln_match) or dates_inline.search(ln_match):
            if len(s_match) < 160:
                continue

        # Drop copyright/boilerplate lines
        if author_copyright.search(ln_match) and len(s_match) < 160:
            continue

        # Drop journal citation header lines near the top only
        if non_empty_seen <= 120 and journal_citation.match(ln_match) and len(s_match) < 220:
            continue

        # Keep figure captions, but strip the label
        if fig_heading.match(ln_match):
            cap = re.sub(
                r"^\s*(figure|fig\.?|image|photo|illustration|chart)\s*\d+\s*[:.-]?\s*",
                "",
                ln_match,
                flags=re.IGNORECASE,
            ).strip()

            if cap and not credit_line.match(cap) and len(cap) >= 8:
                out.append(f"[FIGURE_CAPTION] {cap}")
            continue

        # Drop standalone refs and credit lines
        if fig_only_line.match(ln_match) or credit_line.match(ln_match):
            continue

        # Remove inline references like "(see Fig. 2)"
        ln = fig_ref_inline.sub("", ln_match)

        if remove_tables:
            is_tabley = bool(table_like.search(ln)) or ("|" in ln) or ("\t" in ln)
            is_sep = bool(sep_like.match(ln))
            if is_sep:
                is_tabley = True

            if is_tabley and s_match:
                in_table_block = True
                continue

            if in_table_block:
                in_table_block = False

        out.append(ln.rstrip())

    cleaned = "\n".join(out)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip() + "\n"


def find_bibliography_start_line_index(text: str) -> int | None:
    """Return the line index where bibliography/references heading starts, else None."""
    lines = text.split("\n")
    pat = re.compile(
        r"^\s*(references|bibliography|works\s+cited|literature\s+cited|"
        r"reference\s+list|cited\s+literature)\s*$",
        re.IGNORECASE,
    )
    for idx, ln in enumerate(lines):
        if pat.match(ln):
            return idx
    return None


def find_endmatter_start_line_index(text: str) -> int | None:
    """Return the line index where common end-matter starts, else None."""
    lines = text.split("\n")

    pat = re.compile(
        r"^\s*(acknowledg(e)?ments?|author\s+contributions?|funding|"
        r"abbreviations?|list\s+of\s+abbreviations?|glossary|"
        r"availability\s+of\s+data(\s+and\s+material(s)?)?|data\s+availability|"
        r"code\s+availability|declarations?|conflicts?\s+of\s+interest|"
        r"competing\s+interests?|ethics\s+approval|consent\s+to\s+participate|"
        r"consent\s+for\s+publication|patient\s+consent|open\s+access|"
        r"creative\s+commons|publisher'?s\s+note|"
        r"supplementary\s+(material|information)|supplemental\s+(material|information)|"
        r"appendix|annex)\s*$",
        re.IGNORECASE,
    )

    for idx, ln in enumerate(lines):
        if pat.match(ln.strip()):
            return idx
    return None


def remove_author_lines_near_top(text: str) -> str:
    """Heuristically remove author name lines near the top while keeping the title line."""
    lines = text.split("\n")

    title_idx = None
    for i, ln in enumerate(lines):
        if ln.strip():
            title_idx = i
            break

    def looks_like_author_line(ln: str) -> bool:
        s = ln.strip()
        if not s:
            return False
        if re.match(r"^by\s+", s, flags=re.IGNORECASE):
            return True

        tokens = re.findall(r"[A-Za-z]+", s)
        if not (2 <= len(tokens) <= 12):
            return False

        alpha_ratio = sum(ch.isalpha() for ch in s) / max(1, len(s))
        if alpha_ratio < 0.55:
            return False

        has_commas = "," in s
        has_and = re.search(r"\b(and|&)\b", s, flags=re.IGNORECASE) is not None
        if not (has_commas or has_and):
            return False

        if re.search(
            r"\b(university|department|school|college|email|@)\b",
            s,
            flags=re.IGNORECASE,
        ):
            return False

        return True

    non_empty_seen = 0
    for i, ln in enumerate(lines):
        if ln.strip():
            non_empty_seen += 1
        if non_empty_seen > 40:
            break

        if title_idx is not None and i == title_idx:
            continue

        if looks_like_author_line(ln):
            lines[i] = ""

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip() + "\n"