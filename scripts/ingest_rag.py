import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import rag


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest documents into the LearnFlow RAG store."
    )
    parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        required=True,
        help="File or directory path to ingest. Repeat for multiple paths."
    )
    parser.add_argument("--stream", default=None)
    parser.add_argument("--subject", default=None)
    parser.add_argument("--class-level", dest="class_level", default=None)
    parser.add_argument("--board", default=None)
    parser.add_argument("--chapter", default=None)
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Reindex even if the source checksum is unchanged."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata = {
        "stream": args.stream,
        "subject": args.subject,
        "class_level": args.class_level,
        "board": args.board,
        "chapter": args.chapter
    }
    results = rag.ingest_paths(args.paths, metadata, reindex=args.reindex)
    print(json.dumps({"ingested": results, "count": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
