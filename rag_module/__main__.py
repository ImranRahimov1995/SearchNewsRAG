"""RAG module CLI interface."""

import argparse
import sys

from settings import get_logger

from .services import VectorizationService

logger = get_logger("rag_cli")


def vectorize_command(args: argparse.Namespace) -> int:
    """Execute vectorization command.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info(
            f"Vectorization started: source={args.source}, "
            f"collection={args.collection}, mode={args.analyzer_mode}"
        )

        service = VectorizationService.create_default(
            collection_name=args.collection,
            persist_directory=args.persist_dir,
            analyzer_mode=args.analyzer_mode,
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            max_concurrent=args.max_concurrent,
        )

        result = service.vectorize(
            source=args.source,
            source_name=args.source_name,
            start_index=args.start_index,
            end_index=args.end_index,
        )

        logger.info(
            f"✅ Vectorization complete!\n"
            f"  Source: {result.source_name}\n"
            f"  Documents: {result.total_documents}\n"
            f"  Chunks: {result.total_chunks}\n"
            f"  Vectorized: {result.vectorized_count}\n"
            f"  Failed: {result.failed_count}"
        )

        print(f"\n✅ Successfully vectorized {result.total_chunks} chunks")
        print(f"   from {result.total_documents} documents")
        print(f"   Source: {result.source_name}")
        print(f"   Collection: {args.collection}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception("Unexpected error during vectorization")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="RAG module CLI for document processing and vectorization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Vectorize all documents
  python -m rag_module vectorize --source data/news.json --source-name news_2024

  # Vectorize with slicing (first 100 documents)
  python -m rag_module vectorize --source data/news.json --source-name news_2024 --end-index 100

  # Use sync mode instead of async
  python -m rag_module vectorize --source data/news.json --source-name news_2024 --sync

  # Custom chunk size and overlap
  python -m rag_module vectorize --source data/news.json --source-name news_2024 \\
    --chunk-size 800 --overlap 150
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    vectorize_parser = subparsers.add_parser(
        "vectorize",
        help="Process and vectorize documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    vectorize_parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to source data file (JSON)",
    )

    vectorize_parser.add_argument(
        "--source-name",
        type=str,
        required=True,
        help="Name/identifier for the source (used in document IDs)",
    )

    vectorize_parser.add_argument(
        "--collection",
        type=str,
        default="news",
        help="ChromaDB collection name (default: news)",
    )

    vectorize_parser.add_argument(
        "--persist-dir",
        type=str,
        default="./chroma_db",
        help="ChromaDB persistence directory (default: ./chroma_db)",
    )

    vectorize_parser.add_argument(
        "--start-index",
        type=int,
        default=None,
        help="Start index for slicing source data (optional)",
    )

    vectorize_parser.add_argument(
        "--end-index",
        type=int,
        default=None,
        help="End index for slicing source data (optional)",
    )

    vectorize_parser.add_argument(
        "--analyzer-mode",
        type=str,
        choices=["async", "sync", "none"],
        default="async",
        help="Analyzer mode: async (concurrent LLM), sync (sequential), or none (no LLM)",
    )

    vectorize_parser.add_argument(
        "--sync",
        action="store_const",
        const="sync",
        dest="analyzer_mode",
        help="Shortcut for --analyzer-mode sync",
    )

    vectorize_parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (uses OPENAI_API_KEY env var if not provided)",
    )

    vectorize_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model name (default: gpt-4o-mini)",
    )

    vectorize_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Generation temperature (default: 0.1)",
    )

    vectorize_parser.add_argument(
        "--chunk-size",
        type=int,
        default=600,
        help="Target chunk size in characters (default: 600)",
    )

    vectorize_parser.add_argument(
        "--overlap",
        type=int,
        default=100,
        help="Overlap between chunks (default: 100)",
    )

    vectorize_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=50,
        help="Max concurrent requests for async mode (default: 50)",
    )

    return parser


def main() -> int:
    """Execute main CLI workflow.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "vectorize":
        return vectorize_command(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
