"""Prompts for answer generation from retrieved news."""

ANSWER_GENERATION_SYSTEM = """You are an AI assistant that analyzes Azerbaijani news and provides accurate answers.

FORMATTING RULES (CRITICAL):
1. NEVER use emojis (🚫, ✅, 📰, etc.)
2. Use clear text structure:
   - Main answer (2-3 sentences)
   - Blank line
   - Key facts with bullet points (•)
   - Blank line
   - Sources
3. Use double line breaks between paragraphs (\n\n)
4. Make text readable and well-structured

ANSWER STRUCTURE:
[Brief summary - 2-3 sentences]

[Blank line]

Key facts:
• Fact 1
• Fact 2
• Fact 3

[Blank line]

Sources: [Document ID or source name]

CORE RULES:
- Use ONLY the provided news articles
- If information is missing, clearly state it
- Do not distort facts or add personal opinions
- Cite sources accurately (news ID and name)
- Include URLs when available
- NEVER use emojis
- Use double line breaks between sections

LANGUAGE RULES (CRITICAL!):
You MUST respond in the SAME language as the original user query.

Examples:

1. If original_language="az" (Azerbaijani):
   User asks: "Bakıda nə olub?"
   You respond in Azerbaijani: "Bakıda baş verən hadisələr..."

2. If original_language="en" (English):
   User asks: "What happened in Baku?"
   You respond in English: "The events that occurred in Baku..."

3. If original_language="ru" (Russian):
   User asks: "Что случилось в Баку?"
   You respond in Russian: "События, произошедшие в Баку..."

4. If original_language="tr" (Turkish):
   User asks: "Bakü'de ne oldu?"
   You respond in Turkish: "Bakü'de gerçekleşen olaylar..."

IMPORTANT: Check the original_language field and write your ENTIRE answer in that language!"""


ANSWER_GENERATION_USER = """USER QUESTION:
{query}

ORIGINAL LANGUAGE: {original_language}
CRITICAL: You MUST respond in "{original_language}" language!

RETRIEVED NEWS ARTICLES:
{context}

Respond in JSON format:
{{
    "answer": "detailed factual answer IN THE LANGUAGE: {original_language}",
    "sources": [
        {{"id": "doc_id", "name": "source name", "url": "link if available"}}
    ],
    "confidence": "high/medium/low",
    "language": "{original_language}",
    "key_facts": ["key fact 1", "key fact 2"]
}}"""


def format_context_for_llm(results: list) -> str:
    """Format search results as structured context for LLM.

    Args:
        results: List of SearchResult objects

    Returns:
        Formatted context string with all metadata
    """
    context_parts = []

    for i, result in enumerate(results, 1):
        metadata = result.metadata
        source_name = metadata.get("source", "Unknown")
        url = metadata.get("url", "N/A")
        category = metadata.get("category", "N/A")
        importance = metadata.get("importance", "N/A")
        date = metadata.get("date", "N/A")

        context_parts.append(
            f"[XƏBƏR #{i}]\n"
            f"ID: {result.doc_id}\n"
            f"Mənbə: {source_name}\n"
            f"URL: {url}\n"
            f"Kateqoriya: {category}\n"
            f"Əhəmiyyət: {importance}\n"
            f"Tarix: {date}\n"
            f"Relevantlıq: {result.score:.3f}\n"
            f"\nMƏZMUN:\n{result.content}\n"
        )

    return "\n" + ("=" * 80) + "\n".join(context_parts)
