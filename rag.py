import hashlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional, Dict, Any

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import database as db

BASE_DIR = Path(__file__).resolve().parent
RAG_STORE_DIR = Path(os.getenv("RAG_STORE_DIR", BASE_DIR / "rag_store"))
RAG_SOURCE_DIR = Path(os.getenv("RAG_SOURCE_DIR", BASE_DIR / "rag_sources"))
RAG_EMBED_MODEL = os.getenv(
    "RAG_EMBED_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "800"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))
RAG_COLLECTION = "learnflow"


def _validate_source_path(path: Path) -> Path:
    resolved = path.resolve()
    base = RAG_SOURCE_DIR.resolve()
    base.mkdir(parents=True, exist_ok=True)
    if base not in resolved.parents and resolved != base:
        raise ValueError(
            f"Source path {resolved} must be within {base}."
        )
    return resolved


def _collect_files(paths: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for raw_path in paths:
        resolved = _validate_source_path(Path(raw_path))
        if resolved.is_dir():
            for ext in ("*.pdf", "*.txt", "*.md"):
                files.extend(resolved.rglob(ext))
        elif resolved.is_file():
            files.append(resolved)
    unique_files = sorted({f for f in files if f.exists()})
    return unique_files


def _loader_for_file(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path))
    return TextLoader(str(path), encoding="utf-8")


def _checksum(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@lru_cache
def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=RAG_EMBED_MODEL)


def get_vectorstore() -> Chroma:
    RAG_STORE_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=RAG_COLLECTION,
        persist_directory=str(RAG_STORE_DIR),
        embedding_function=_get_embeddings()
    )


def _split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP
    )
    return splitter.split_documents(documents)


def _apply_metadata(documents: List[Document],
                    metadata: Dict[str, Optional[str]],
                    source_path: Path) -> List[Document]:
    source_name = source_path.name
    for doc in documents:
        doc.metadata.update({
            "source_path": str(source_path),
            "source_name": source_name,
            **{k: v for k, v in metadata.items() if v}
        })
    return documents


def ingest_paths(paths: Iterable[str],
                 metadata: Dict[str, Optional[str]],
                 reindex: bool = False) -> List[Dict[str, Any]]:
    files = _collect_files(paths)
    vectorstore = get_vectorstore()
    results: List[Dict[str, Any]] = []

    for file_path in files:
        checksum = _checksum(file_path)
        existing = db.get_rag_source(str(file_path))

        if existing and existing["checksum"] == checksum and not reindex:
            results.append({
                "source_path": str(file_path),
                "status": "skipped",
                "reason": "unchanged"
            })
            continue

        if existing:
            vectorstore.delete(where={"source_path": str(file_path)})

        loader = _loader_for_file(file_path)
        raw_docs = loader.load()
        tagged_docs = _apply_metadata(raw_docs, metadata, file_path)
        split_docs = _split_documents(tagged_docs)

        if split_docs:
            vectorstore.add_documents(split_docs)

        db.upsert_rag_source(
            source_path=str(file_path),
            checksum=checksum,
            stream=metadata.get("stream"),
            subject=metadata.get("subject"),
            class_level=metadata.get("class_level"),
            board=metadata.get("board"),
            chapter=metadata.get("chapter"),
            chunk_count=len(split_docs)
        )

        results.append({
            "source_path": str(file_path),
            "status": "indexed",
            "chunk_count": len(split_docs)
        })

    vectorstore.persist()
    return results


def _build_filters(stream: Optional[str],
                   subjects: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    clauses: List[Dict[str, Any]] = []
    if stream:
        clauses.append({"stream": stream})
    if subjects:
        clauses.append({"$or": [{"subject": s} for s in subjects]})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def retrieve_documents(query: str,
                       stream: Optional[str] = None,
                       subjects: Optional[List[str]] = None,
                       top_k: Optional[int] = None) -> List[Document]:
    vectorstore = get_vectorstore()
    filters = _build_filters(stream, subjects)
    return vectorstore.similarity_search(
        query=query,
        k=top_k or RAG_TOP_K,
        filter=filters
    )


def format_rag_context(documents: List[Document]) -> str:
    if not documents:
        return "<RAG_CONTEXT>\nNo relevant documents found.\n</RAG_CONTEXT>"

    lines = ["<RAG_CONTEXT>"]
    for idx, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source_name") or doc.metadata.get("source_path", "unknown")
        content = doc.page_content.strip()
        lines.append(f"[{idx}] Source: {source}")
        lines.append(content)
        lines.append("---")
    lines.append("</RAG_CONTEXT>")
    return "\n".join(lines)


def serialize_document(doc: Document, max_chars: int = 400) -> Dict[str, Any]:
    content = doc.page_content.strip()
    if len(content) > max_chars:
        content = content[:max_chars].rstrip() + "..."
    return {
        "content": content,
        "metadata": doc.metadata
    }
