import re
from typing import List, Pattern

REF_HEADERS: List[Pattern[str]] = [
    re.compile(r"^\s*references\s*$", re.IGNORECASE),
    re.compile(r"^\s*\*\*references\*\*\s*$", re.IGNORECASE),
    re.compile(r"^\s*_?\*\*references\*\*_?\s*$", re.IGNORECASE),
    re.compile(r"^\s*bibliography\s*$", re.IGNORECASE),
    re.compile(r"^\s*works\s+cited\s*$", re.IGNORECASE),
    re.compile(r"^\s*literature\s+cited\s*$", re.IGNORECASE),
    re.compile(r"^\s*reference\s+list\s*$", re.IGNORECASE),
    re.compile(r"^\s*cited\s+literature\s*$", re.IGNORECASE),
]

END_HEADER = re.compile(
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

LICENSE_TEXT = (
    "creative commons",
    "the internal medicine is an open access article",
    "naika.or.jp",
    "by-nc-nd/4.0",
)

HEADER_JUNK = (
    "intern med",
    "received for publication",
    "accepted for publication",
    "correspondence to",
    "japanese society of internal medicine",
    "correspondence:",
    "email:",
    "e-mail:",
    "these authors contributed equally",
    "frontiers in",
    "frontiersin.org",
    "pubmed",
    "pmc",
    "pmcid",
    "nihms",
    "advance access publication",
)

CONTINUATION_WORDS = "in which|and|but|or|so|yet|because|while|whereas|although|however"

PAGE_MARKER = re.compile(r"<!--\s*page:\s*\d+\s*-->", re.IGNORECASE)

DROP_LINE_PATTERNS: List[Pattern[str]] = [
    re.compile(r"^\s*\*\*correspondence:.*$", re.IGNORECASE),
    re.compile(r"^\s*\[email:.*$", re.IGNORECASE),
    re.compile(r"^\s*.*mailto:.*$", re.IGNORECASE),
    re.compile(r"^\s*these authors contributed equally.*$", re.IGNORECASE),
    re.compile(r"^\s*this article is part of the topical collection.*$", re.IGNORECASE),
    re.compile(r"^\s*keywords\b.*$", re.IGNORECASE),
    re.compile(r"^\s*-\s+[A-Z][A-Za-z .,&'\-]{2,}.*$"),
    re.compile(r"^\s*\d+\s+Page\s+\d+\s+of\s+\d+.*$", re.IGNORECASE),
    re.compile(r"^\s*School of Medicine,.*$", re.IGNORECASE),
    re.compile(
        r"^\s*\d+.*(?:university|hospital|department|school|institute|college|medical center).*$",
        re.IGNORECASE,
    ),
    re.compile(r"^\s*\*\*[A-Z][^\n]*\*\*\s*(?:\*\*[^\n]+\*\*\s*){2,}$"),
    re.compile(r"^\s*https?://\S+\s*$", re.IGNORECASE),
    re.compile(r"^\s*\[https?://[^\]]+\]\([^)]+\)\s*$", re.IGNORECASE),
    re.compile(r"^\s*frontiers in .*?$", re.IGNORECASE),
    re.compile(r"^\s*.*frontiersin\.org.*$", re.IGNORECASE),
    re.compile(r"^\s*[A-Z][A-Za-z .,&'\-]{2,}\bet al\.?\s*$"),
    re.compile(r"^\s*copyright\s*$", re.IGNORECASE),
    re.compile(r"^\s*published\s+online:.*$", re.IGNORECASE),
    re.compile(r"^\s*received:?\s+.*$", re.IGNORECASE),
    re.compile(r"^\s*accepted:?\s+.*$", re.IGNORECASE),
    re.compile(r"^\s*editorial decision:?\s+.*$", re.IGNORECASE),
    re.compile(r"^\s*corrected and typeset:?\s+.*$", re.IGNORECASE),
    re.compile(r"^\s*curr diab rep.*$", re.IGNORECASE),
    re.compile(r"^\s*doi[:\s].*$", re.IGNORECASE),
    re.compile(r"^\s*.*section editor.*$", re.IGNORECASE),
    re.compile(r"^\s*the author\(s\).*$", re.IGNORECASE),
    re.compile(r"^\s*.*springerlink\.com.*$", re.IGNORECASE),
    re.compile(r"^\*\*\(Intern.*?\)\*\*\s*$"),
    re.compile(r"^\*\*\(DOI:.*?\)\*\*\s*$", re.IGNORECASE),
    re.compile(r"^\*\*The\*\* \*\*authors\*\* .*?COI\)\.\s*$", re.IGNORECASE),
]

CITE_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\[(\d{1,3}(?:\s*[-,•*]\s*\d{1,3}|\s*[•*]+)*)\]"),
    re.compile(r"\((\d{1,3}(?:\s*[-,•*]\s*\d{1,3}|\s*[•*]+)*)\)"),
    re.compile(r"\[(\d{1,3}[•*]+(?:\s*[-,]\s*\d{1,3}[•*]+)*)\]"),
]


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    if not text.strip():
        return ""

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def find_refs_start(text: str) -> int | None:
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        stripped = line.strip()
        for pattern in REF_HEADERS:
            if pattern.match(stripped):
                return idx
    return None


def find_end_start(text: str) -> int | None:
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        if END_HEADER.match(line.strip()):
            return idx
    return None


def find_numbered_refs_start(text: str) -> int | None:
    lines = text.split("\n")

    def looks_like_reference_entry(line: str) -> bool:
        stripped = line.strip()
        return bool(
            re.match(r"^\d{1,3}[.)]\s+", stripped)
            or re.match(r"^\[\d{1,3}\]\s+", stripped)
            or re.match(
                r"^[A-Z][A-Za-z'`.-]+(?:\s+[A-Z][A-Za-z'`.-]+){0,5},\s*(?:et al\.?|[A-Z])",
                stripped,
            )
            or re.match(
                r"^[A-Z][A-Za-z'`.-]+\s+[A-Z][A-Za-z'`.-]+.*\b(?:J\.|N Engl J Med|Lancet|BMJ|Radiology|Clin Endocrinol|Endocrinol|Horm Res|QJM)\b",
                stripped,
            )
        )

    for idx in range(len(lines)):
        window = [ln.strip() for ln in lines[idx : idx + 10] if ln.strip()]
        if len(window) < 3:
            continue
        hits = sum(1 for ln in window[:8] if looks_like_reference_entry(ln))
        if hits >= 3:
            return idx

    return None


def _merge_page_marker_mid_sentence(text: str) -> str:
    return re.sub(
        r"(?<=[a-z,;])\s*\n\s*(<!--\s*page:\s*\d+\s*-->)\s*\n\s*(?=[a-z])",
        r" \1 ",
        text,
        flags=re.IGNORECASE,
    )


def _drop_bad_replacement_chars(text: str) -> str:
    return text.replace("�", "")


def dedupe_paragraphs(text: str) -> str:
    t = normalize_text(text)
    paras = [p.strip() for p in t.split("\n\n")]
    out: List[str] = []
    prev: str | None = None

    for paragraph in paras:
        if not paragraph:
            continue
        if prev is not None and paragraph == prev:
            continue
        out.append(paragraph)
        prev = paragraph

    return "\n\n".join(out).strip() + "\n"


def drop_matching_lines(text: str, patterns: List[Pattern[str]]) -> str:
    lines = text.split("\n")
    kept_lines = [line for line in lines if not any(pattern.match(line) for pattern in patterns)]
    return "\n".join(kept_lines)


def drop_inline_citations(text: str) -> str:
    for pattern in CITE_PATTERNS:
        text = pattern.sub("", text)
    return text

def strip_heading_author(line: str) -> str:
    if not line.lstrip().startswith("#"):
        return line

    cleaned = re.sub(
        r"^(#{1,6}\s+.*?)(?:\s+[A-Z][A-Za-z'`.-]+(?:\s+[A-Z][A-Za-z'`.-]+){1,3})\s*$",
        r"\1",
        line.strip(),
    )
    return cleaned

def drop_top_meta_line(
    stripped: str,
    lower: str,
    *,
    in_top_window: bool,
    skipping_affiliations: bool,
) -> bool:
    if not in_top_window or not stripped:
        return False

    if lower.startswith(("correspondence:", "email:", "e-mail:")):
        return True

    if "these authors contributed equally" in lower:
        return True

    if "mailto:" in lower:
        return True

    if re.match(r"^\d+[A-Za-z].*", stripped):
        return True

    if re.match(r"^\d+[A-Za-z].*university|^\d+.*hospital|^\d+.*department", stripped, flags=re.IGNORECASE):
        return True

    if re.match(r"^[A-Z][A-Za-z'`.-]+(\s+[A-Z][A-Za-z'`.-]+){1,8}(\s*[,*&]\s*)?$", stripped):
        return True

    if re.match(r"^\*\*[^*]+\*\*(\s*\*\*[^*]+\*\*)+$", stripped):
        return True

    if skipping_affiliations and (
        "university" in lower
        or "hospital" in lower
        or "department of" in lower
        or "school of" in lower
        or "institute of" in lower
        or "college of" in lower
        or "medical center" in lower
        or "correspondence" in lower
        or "@" in stripped
    ):
        return True

    if stripped.startswith("Received:") or stripped.startswith("©"):
        return True

    if lower.startswith("published online:"):
        return True

    if lower.startswith("curr diab rep"):
        return True

    if lower.startswith("doi ") or lower.startswith("doi:"):
        return True

    if "section editor" in lower:
        return True

    if lower.startswith("the author(s)"):
        return True

    if "springerlink.com" in lower:
        return True

    return False


def drop_top_author_block(text: str) -> str:
    lines = text.split("\n")
    cleaned: List[str] = []

    top_window = min(len(lines), 40)
    skipping_affiliations = True

    for idx, line in enumerate(lines):
        stripped = line.strip()
        lower = stripped.lower()

        if idx < top_window:
            if not stripped:
                continue

            if PAGE_MARKER.fullmatch(stripped):
                cleaned.append(stripped)
                continue

            if drop_top_meta_line(
                stripped,
                lower,
                in_top_window=True,
                skipping_affiliations=skipping_affiliations,
            ):
                continue

        skipping_affiliations = False
        cleaned.append(line)

    cleaned_text = "\n".join(cleaned)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text.strip() + "\n" if cleaned_text.strip() else ""


def is_license_start(lower_line: str) -> bool:
    return any(token in lower_line for token in LICENSE_TEXT)


def is_header_junk(lower_line: str) -> bool:
    return any(token in lower_line for token in HEADER_JUNK)


def is_junk_line(stripped: str) -> bool:
    if PAGE_MARKER.fullmatch(stripped):
        return False

    if re.fullmatch(r"https?://\S+", stripped, flags=re.IGNORECASE):
        return True

    if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", stripped):
        return True

    if re.fullmatch(r"[A-Z][A-Za-z .,&'-]{2,}\bet al\.?", stripped):
        return True

    return any(
        (
            stripped.isdigit(),
            re.fullmatch(r"\d+(\.\d+)?", stripped) is not None,
            re.fullmatch(r"[#*\-_\s]+", stripped) is not None,
            re.fullmatch(r"#+\s*[A-Z]$", stripped) is not None,
        )
    )


def repair_text(text: str) -> str:
    text = _drop_bad_replacement_chars(text)
    text = _merge_page_marker_mid_sentence(text)
    text = re.sub(r"\bIgG\s*\n\s*4-related\b", "IgG4-related", text)
    text = re.sub(r"\bIgG\s+4\b", "IgG4", text)
    text = re.sub(r"\bre\s*\n\s*turned\b", "returned", text)
    text = re.sub(r"\bpost\s*\n\s*obstructive\b", "post-obstructive", text)
    text = re.sub(r"([A-Za-z])-\n([A-Za-z])", r"\1\2", text)
    text = re.sub(r"\*\*([^*]+)\*\*\s+\*\*([^*]+)\*\*", r"**\1 \2**", text)
    text = re.sub(
        r"incidence rates of\s+of retroperitoneal fibrosis",
        "incidence rates of retroperitoneal fibrosis",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"IgG4related", "IgG4-related", text)
    text = re.sub(r"\b4-related\b", "IgG4-related", text)
    text = re.sub(r"\bIG4\b", "IgG4", text)
    text = re.sub(r"postobstructive", "post-obstructive", text, flags=re.IGNORECASE)
    text = re.sub(r"IgG4RD", "IgG4-RD", text)
    text = re.sub(r"(?<!\n\n)(?<=[a-z,;])\n(?=[a-zA-Z])", " ", text)
    text = re.sub(rf"\n({CONTINUATION_WORDS})\b", r" \1", text)
    text = re.sub(r"\s+(<!--\s*page:\s*\d+\s*-->)", r"\n\1", text, flags=re.IGNORECASE)
    text = re.sub(
        r"(<!--\s*page:\s*\d+\s*-->)\s+(?=#+\s|\*\*|[A-Z])",
        r"\1\n\n",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\*\*([^*]+)\*\*\s*\n\s*\*\*([^*]+)\*\*", r"**\1 \2**", text)
    text = re.sub(r"([a-zA-Z])\n\s*(\d+-[a-zA-Z])", r"\1 \2", text)
    text = re.sub(r"/\s+([a-z])", r"/ \1", text)
    text = re.sub(r"\b[A-Z][A-Za-z .,&'\-]{2,}\bet al\.?\b", "", text)
    text = re.sub(r"\[[^\]]*doi\.org/[^\]]*\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[[^\]]*frontiersin\.org[^\]]*\]", "", text, flags=re.IGNORECASE)
    return text


def find_cutoff(text: str) -> int | None:
    bib_idx = find_refs_start(text)
    end_idx = find_end_start(text)
    numbered_ref_idx = find_numbered_refs_start(text)

    coi_match = re.search(
        r"^\s*\*\*The\*\*\s+\*\*authors\*\*.*COI.*$",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    references_match = re.search(
        r"(?im)^\s*(?:#{1,6}\s*)?_?\*\*?references\*\*?_?\s*$|^\s*references\s*$|^\s*bibliography\s*$|^\s*works\s+cited\s*$|^\s*literature\s+cited\s*$",
        text,
    )
    extra_endmatter_match = re.search(
        r"(?im)^\s*(?:#{1,6}\s*)?(acknowledg(?:e)?ments|conflict of interest|compliance with ethical standards|funding|author contributions|data availability|ethics statement|supplementary material|open access|copyright)",
        text,
    )

    extra_cut_lines: List[int] = []
    if coi_match:
        extra_cut_lines.append(text[:coi_match.start()].count("\n"))
    if references_match:
        extra_cut_lines.append(text[:references_match.start()].count("\n"))
    if extra_endmatter_match:
        extra_cut_lines.append(text[:extra_endmatter_match.start()].count("\n"))
    if numbered_ref_idx is not None:
        extra_cut_lines.append(numbered_ref_idx)

    cut_candidates = [idx for idx in (bib_idx, end_idx) if idx is not None] + extra_cut_lines
    if not cut_candidates:
        return None

    return min(cut_candidates)


def clean_document_text(text: str, *, remove_tables: bool = False) -> str:
    if not text:
        return ""

    text = normalize_text(text)
    text = drop_top_author_block(text)

    lines = text.split("\n")
    cleaned_lines: List[str] = []

    skip_license_block = False
    skip_caption_block = False

    for line in lines:
        line = strip_heading_author(line)
        stripped = line.strip()
        lower = stripped.lower()

        if not stripped:
            if not skip_license_block and not skip_caption_block:
                cleaned_lines.append("")
            continue

        if is_license_start(lower):
            skip_license_block = True
            continue

        if skip_license_block:
            continue

        if is_header_junk(lower) and not PAGE_MARKER.fullmatch(stripped):
            continue

        if is_junk_line(stripped):
            continue

        if lower.startswith("**figure") or lower.startswith("figure "):
            skip_caption_block = True
            continue
        if lower.startswith("**table") or lower.startswith("table "):
            skip_caption_block = True
            continue

        if skip_caption_block:
            if PAGE_MARKER.fullmatch(stripped):
                cleaned_lines.append(stripped)
                continue
            if len(stripped) > 60 and stripped[0].isalpha():
                skip_caption_block = False
            else:
                continue

        if remove_tables:
            if stripped.count("|") >= 2:
                continue
            if re.fullmatch(r"[\-:|\s]+", stripped):
                continue

        cleaned_lines.append(line.rstrip())

    cleaned = "\n".join(cleaned_lines)
    cleaned = drop_matching_lines(cleaned, DROP_LINE_PATTERNS)
    cleaned = drop_inline_citations(cleaned)
    cleaned = dedupe_paragraphs(cleaned).strip()

    cut_idx = find_cutoff(cleaned)
    if cut_idx is not None:
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[:cut_idx]).strip()

    cleaned = repair_text(cleaned)
    cleaned = drop_matching_lines(cleaned, DROP_LINE_PATTERNS)
    cleaned = normalize_text(cleaned).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned + "\n" if cleaned else ""