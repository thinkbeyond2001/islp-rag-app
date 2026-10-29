"""Text-cleaning helpers for documents that will be embedded."""

from __future__ import annotations

import html
import re
import unicodedata


_PAGE_HEADINGS = (
    "What becomes possible",
    "Why trust Matt?",
    "Implementation pack",
    "Schedule of Live Events",
    "Time Commitment",
    "Clinic Schedule",
    "Weekly Builder Breakdown",
    "Tools & Techniques You'll Use",
    "Tools & Techniques You’ll Use",
    "Core AI Tools",
    "Production & Deployment",
    "Here's What You'll Build",
    "Here’s What You’ll Build",
    "Everything You Build Is Backed by the Implementation Pack",
    "Designed for professionals with full-time jobs",
    "The 8-Week Generative AI Bootcamp",
    "Cohort Size & Enrollment Timing",
    "Cohort Transfer Guarantee",
    "Refund Policy",
    "Frequently Asked Questions (FAQs)",
)


def text_cleaner_1(text: str) -> str:
    """Clean scraped sales-page text before adding it to a vector store.

    The cleaner is intentionally conservative: it normalizes characters and
    whitespace, removes repeated calls-to-action and checkout/footer boilerplate,
    and restores useful boundaries around headings and sentences. It does not
    select content using keywords, so relevant information is not silently lost.

    Parameters
    ----------
    text:
        Raw text extracted from a webpage.

    Returns
    -------
    str
        Clean text with paragraphs separated by a single newline.
    """
    if not isinstance(text, str):
        raise TypeError("text_cleaner_1() expects text to be a string")

    # Decode HTML entities, standardize Unicode, and fix common scrape artifacts.
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("ðŸŽ‰", "🎉").replace("â€™", "’")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove navigation and purchase-form text that does not help retrieval.
    text = re.sub(
        r"Toggle navigation.*?Business Science",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(
        r"Your Account\s*Who is Enrolling Today\?.*?"
        r"Continue to secure your seat",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # These blocks occur many times on the sample page and add embedding noise.
    text = re.sub(
        r"(?:👉\s*)?Enroll in Cohort\s+\d+\s*"
        r"\(Limited to\s+\d+\s+seats to preserve live support quality\)",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Get Instant Access\s*"
        r"\(Limited to\s+\d+\s+seats to preserve live support quality\)",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # Remove the site footer, but retain all useful material that precedes it.
    text = re.sub(
        r"(?:©|Copyright)\s+Business Science(?: University)?(?:\s+\d{4})?.*$",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Flatten arbitrary scrape whitespace first, then introduce stable boundaries.
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(?<=[.!?])(?=[A-Z0-9🎓👉✔🔹⏱🎥🧱☁️])", "\n", text)
    text = re.sub(r"\s*(?=[✔🔹⏱🎥🧱📊💬🎓☁️🧭])", "\n", text)
    text = re.sub(r"\s*(?=Week\s+\d+\s*[—-])", "\n", text)
    text = re.sub(r"\s*(?=Live Clinic\s+#?\d+\s*:)", "\n", text)
    text = re.sub(r"\s*(?=\d+\)\s+)", "\n", text)

    if _PAGE_HEADINGS:
        heading_pattern = "|".join(
            re.escape(heading) for heading in sorted(_PAGE_HEADINGS, key=len, reverse=True)
        )
        text = re.sub(rf"\s*(?=(?:{heading_pattern}))", "\n", text)

    # Trim every line and remove empty or immediately duplicated lines.
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line and (not cleaned_lines or line != cleaned_lines[-1]):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
