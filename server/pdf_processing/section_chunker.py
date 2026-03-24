import re
from typing import List


def normalize_section_name(name: str) -> str:
    n = re.sub(r"\s+", " ", name.strip())
    n = n.strip(" :.-\t")

    low = n.lower()
    mapping = {
        "materials and methods": "Methods",
        "material and methods": "Methods",
        "patients and methods": "Methods",
        "methods": "Methods",
        "method": "Methods",
        "materials": "Methods",
        "research design and methods": "Methods",
        "results": "Results",
        "discussion": "Discussion",
        "conclusion": "Conclusion",
        "conclusions": "Conclusion",
        "introduction": "Introduction",
        "background": "Introduction",
        "abstract": "Abstract",
        "aim": "Aim",
        "aims": "Aim",
        "objectives": "Aim",
        "objective": "Aim",
        "limitations": "Limitations",
        "references": "References",
        "bibliography": "References",
        "acknowledgements": "EndMatter",
        "acknowledgments": "EndMatter",
        "author contributions": "EndMatter",
        "funding": "EndMatter",
        "declarations": "EndMatter",
        "declaration": "EndMatter",
        "conflict of interest": "EndMatter",
        "conflicts of interest": "EndMatter",
        "competing interests": "EndMatter",
        "ethics approval": "EndMatter",
        "consent to participate": "EndMatter",
        "consent for publication": "EndMatter",
        "data availability": "EndMatter",
        "code availability": "EndMatter",
        "abbreviations": "EndMatter",
        "list of abbreviations": "EndMatter",
        "glossary": "EndMatter",
        "supplementary material": "EndMatter",
        "supplementary information": "EndMatter",
        "supplemental material": "EndMatter",
        "supplemental information": "EndMatter",
        "appendix": "EndMatter",
        "annex": "EndMatter",
    }
    return mapping.get(low, n.title() if n.islower() else n)


def is_probable_section_heading(line: str) -> str | None:
    """Return normalized section name if the line looks like a real section heading."""
    s = line.strip()
    if not s:
        return None

    if len(s) > 80:
        return None

    s2 = re.sub(r"^\s*(\d+(?:\.\d+)*|[IVXLC]+)\s*[.)-]?\s+", "", s, flags=re.IGNORECASE)

    if re.fullmatch(r"[IVXLC]+", s2.strip(), flags=re.IGNORECASE):
        return None

    s2 = s2.rstrip(":")

    if re.fullmatch(r"page", s2.strip(), flags=re.IGNORECASE) or re.fullmatch(
        r"page\s*\d+", s2.strip(), flags=re.IGNORECASE
    ):
        return None

    if s2.strip().upper() in {
        "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
        "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
    }:
        return None

    if re.search(
        r"\b(inc|ltd|llc|corp|corporation|gmbh|s\.a\.|sa|plc|co\.|company|"
        r"dublin|paris|london|berlin|montpellier|li[eè]ge|france|belgium|germany|china|"
        r"ca|ny|tx|usa|u\.s\.|united\s+states)\b",
        s2,
        re.IGNORECASE,
    ):
        return None

    common = re.compile(
        r"^((?:abstract|introduction|background|aims?|objectives?|methods?|materials\s+and\s+methods|research\s+design\s+and\s+methods|"
        r"patients\s+and\s+methods|results?|discussion|conclusions?|limitations|"
        r"references|bibliography|abbreviations?|list\s+of\s+abbreviations?|glossary|"
        r"acknowledg(e)?ments?|author\s+contributions?|funding|declarations?|"
        r"conflicts?\s+of\s+interest|competing\s+interests?|ethics\s+approval|"
        r"data\s+availability|code\s+availability|supplementary\s+(?:material|information)|"
        r"supplemental\s+(?:material|information)|appendix|annex))\b",
        re.IGNORECASE,
    )
    m = common.match(s2)
    if m:
        rest = s2[m.end():].strip()
        rest = rest.strip(" :.-\t")
        if rest:
            return None
        return normalize_section_name(m.group(1))

    low2 = s2.strip().lower()
    if low2 in {"no", "yes", "mri", "ct", "mra", "pet", "eeg", "ecg", "us", "usa"}:
        return None

    if re.fullmatch(r"[A-Za-z]{1,3}", s2.strip()):
        return None

    letters = sum(ch.isalpha() for ch in s2)
    if letters == 0:
        return None
    if letters / max(1, len(s2)) < 0.6:
        return None

    words = re.findall(r"[A-Za-z]+", s2)
    if not (1 <= len(words) <= 6):
        return None

    if s2.isupper() and len(s2) <= 50:
        if len(words) == 1 and len(words[0]) <= 4:
            return None
        return normalize_section_name(" ".join(words[:6]))

    if 1 <= len(words) <= 4 and s2[:1].isupper() and sum(w[0].isupper() for w in words) >= len(words):
        return normalize_section_name(" ".join(words))

    return None


def chunk_pages_by_sections(
    cleaned_pages: List[tuple[int, str]],
    *,
    max_chars: int,
    max_words: int,
) -> List[tuple[int, int, int, str, str]]:
    """Given cleaned per-page text, create section-aware chunks across pages.

    Returns (chunk_no, page_start, page_end, text, section).
    """
    chunks_out: List[tuple[int, int, int, str, str]] = []

    MIN_CHUNK_CHARS = 250
    MIN_CHUNK_WORDS = 50

    current_section = "Abstract"
    buf_lines: List[str] = []
    page_start: int | None = None
    page_end: int | None = None

    STOP_SECTIONS = {"References", "EndMatter"}

    def flush() -> None:
        nonlocal buf_lines, page_start, page_end, current_section, chunks_out
        text = "\n".join(buf_lines).strip()
        if not text or page_start is None or page_end is None:
            buf_lines = []
            page_start = None
            page_end = None
            return

        word_count = len(re.findall(r"\S+", text))
        if (len(text) < MIN_CHUNK_CHARS) or (word_count < MIN_CHUNK_WORDS):
            if chunks_out:
                prev_no, prev_ps, prev_pe, prev_text, prev_sec = chunks_out[-1]
                merged_text = (prev_text.rstrip() + "\n\n" + text).rstrip() + "\n"
                chunks_out[-1] = (prev_no, prev_ps, max(prev_pe, page_end), merged_text, prev_sec)
            else:
                chunks_out.append((len(chunks_out) + 1, page_start, page_end, text + "\n", current_section))
        else:
            chunks_out.append((len(chunks_out) + 1, page_start, page_end, text + "\n", current_section))

        buf_lines = []
        page_start = None
        page_end = None

    def buf_too_big() -> bool:
        joined = "\n".join(buf_lines)
        if max_chars > 0 and len(joined) > max_chars:
            return True
        if max_words > 0 and len(re.findall(r"\S+", joined)) > max_words:
            return True
        return False

    for page_no, page_text in cleaned_pages:
        lines = page_text.split("\n")
        for ln in lines:
            sec = is_probable_section_heading(ln)
            if sec is not None:
                if buf_lines:
                    flush()

                if sec in STOP_SECTIONS:
                    return chunks_out

                current_section = sec
                continue

            if page_start is None:
                page_start = page_no
            page_end = page_no
            if ln.strip() or (buf_lines and buf_lines[-1].strip()):
                buf_lines.append(ln)

            if buf_lines and buf_too_big():
                last_line = buf_lines.pop() if buf_lines else ""

                if buf_lines:
                    flush()
                    if last_line.strip():
                        if page_start is None:
                            page_start = page_no
                        page_end = page_no
                        buf_lines.append(last_line)
                else:
                    buf_lines.append(last_line)
                    flush()

    if buf_lines:
        flush()

    return chunks_out