"""Statistics handler - SQL-based analytics using LangChain."""

import logging
import os

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from ..protocols import SearchResult

logger = logging.getLogger(__name__)


STATISTICS_PROMPT_TEXT = """You are an expert data analyst for an Azerbaijani news database.

Database Schema:
{table_info}

User Question: {question}

Task:
1. Analyze the user's question
2. Generate a SQL query to answer it
3. Focus on: news_articles table with fields: date, category, importance, sentiment, summary
4. Use aggregations (COUNT, AVG, MAX, MIN) when appropriate
5. ORDER BY importance DESC LIMIT 30 for important news
6. Return ONLY executable PostgreSQL query

Example Queries:
{examples}

SQL Query (PostgreSQL format):"""


SQL_EXAMPLES = """
-- Most important news in 2025
SELECT summary, date, category, importance
FROM news_articles
WHERE EXTRACT(YEAR FROM date) = 2025 AND importance >= 7
ORDER BY importance DESC
LIMIT 30;

-- News count by category
SELECT category, COUNT(*) as count
FROM news_articles
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category
ORDER BY count DESC;

-- Top positive news this week
SELECT summary, date, importance, sentiment_score
FROM news_articles
WHERE date >= CURRENT_DATE - INTERVAL '7 days' AND sentiment = 'positive'
ORDER BY importance DESC, sentiment_score DESC
LIMIT 30;
"""


class StatisticsHandler:
    """Handle statistical queries using SQL database.

    Uses LangChain SQL utilities to analyze news database and return top results.
    """

    def __init__(self, database_url: str | None = None):
        """Initialize statistics handler.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://newsapp:newsapp@postgres:5432/newsapp",
        )

        self.db = SQLDatabase.from_uri(self.database_url)
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

        self.prompt = PromptTemplate(
            input_variables=["question", "table_info", "examples"],
            template=STATISTICS_PROMPT_TEXT,
        )

        self.chain = self.prompt | self.llm | StrOutputParser()

        logger.info("Initialized StatisticsHandler with SQL database")

    def retrieve(
        self, query: str, entities: list, top_k: int = 30
    ) -> list[SearchResult]:
        """Execute statistical query and return results.

        Args:
            query: User's analytical question
            entities: Extracted entities (dates, categories, etc.)
            top_k: Maximum number of results

        Returns:
            List of search results from database query
        """
        logger.info(f"Statistics query: '{query[:100]}...'")

        try:
            table_info = self.db.get_table_info(
                table_names=["news_articles"]
            )

            sql_query = self.chain.invoke(
                {
                    "question": query,
                    "table_info": table_info,
                    "examples": SQL_EXAMPLES,
                }
            )

            sql_query = sql_query.strip().strip("`").strip()
            if sql_query.lower().startswith("sql"):
                sql_query = sql_query[3:].strip()

            logger.info(f"Generated SQL: {sql_query}")

            results = self.db.run(sql_query)

            search_results = []
            if isinstance(results, str):
                # If results are empty or show "no rows", return user-friendly message
                if not results.strip() or "no rows" in results.lower() or results == "[]":
                    from rag_module.message_templates import NO_RESULTS_MESSAGES
                    
                    message = NO_RESULTS_MESSAGES.get("az", NO_RESULTS_MESSAGES["en"])
                    search_results.append(
                        SearchResult(
                            doc_id="no_results",
                            content=message,
                            score=0.0,
                            metadata={
                                "source": "sql_query",
                                "query": sql_query,
                                "type": "statistics",
                                "no_results": True,
                            },
                        )
                    )
                else:
                    search_results.append(
                        SearchResult(
                            doc_id="statistics_result",
                            content=results,
                            score=1.0,
                            metadata={
                                "source": "sql_query",
                                "query": sql_query,
                                "type": "statistics",
                            },
                        )
                    )

            logger.info(f"Statistics query returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Statistics query failed: {e}")
            return [
                SearchResult(
                    doc_id="error",
                    content=f"Statistik sorğu alınarkən xəta baş verdi: {str(e)}",
                    score=0.0,
                    metadata={"error": True},
                )
            ]
