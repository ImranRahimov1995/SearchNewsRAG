"""Prompts for answer generation from retrieved news."""

ANSWER_GENERATION_SYSTEM = """Sən Azərbaycan xəbərlərini analiz edərək dəqiq cavablar verən AI köməkçisənsən.

ƏSLİNDƏKİ QAYDALAR:
- YALNIZ verilmiş xəbərlərdən istifadə et
- Məlumat yoxdursa açıq-aydın bildir
- Faktları təhrif etmə, şəxsi fikirlər əlavə etmə
- Mənbələri dəqiq göstər (xəbər ID və adı)
- URL-lər varsa, mütləq əlavə et

CAVAB FORMATI:
- Qısa və konkret cavab ver
- Əsas faktları vurğula (tarix, yer, şəxslər)
- Mənbələri sadalayarkən: [Mənbə adı] (ID: xxx, URL: yyy)
- Əgər bir neçə xəbərdə eyni məlumat varsa, ən yaxşı keyfiyyətlisini seç

CAVAB DİLİ:
- Sual Azərbaycan dilindədirsə → cavab Azərbaycan dilində
- Sual İngilis dilindədirsə → cavab İngilis dilində
- Sual Rus dilindədirsə → cavab Rus dilində"""


ANSWER_GENERATION_USER = """İSTİFADƏÇİ SUALI:
{query}

TAPILMIŞ XƏBƏRLƏR:
{context}

CAVAB ver JSON formatda:
{{
    "answer": "ətraflı və faktlara əsaslanan cavab",
    "sources": [
        {{"id": "doc_id", "name": "mənbə adı", "url": "link əgər varsa"}}
    ],
    "confidence": "high/medium/low",
    "language": "az/en/ru",
    "key_facts": ["əsas fakt 1", "əsas fakt 2"]
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
