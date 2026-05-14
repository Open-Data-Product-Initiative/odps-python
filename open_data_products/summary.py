"""Lightweight artifact-reference summaries for ODP documents.

Returns metadata only — never the parsed body — so agents can pass references
through their context window without paying the token cost of the full file.
Aligns with the artifact-driven design rule from agenticpatterns.veso.ai/context-management.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Union

import yaml

from .agent import detect_document


def load_summary(path: Union[str, Path]) -> Dict[str, Any]:
    """Return a fixed-shape, document-body-free reference for ``path``.

    Keys: ``path``, ``byte_size``, ``line_count``, ``sha256``, ``spec``,
    ``kind``, ``id``. ``spec`` falls back to ``"unknown"`` when detection
    cannot resolve the document.
    """
    p = Path(path)
    raw = p.read_bytes()
    text = raw.decode("utf-8", errors="replace")

    spec = "unknown"
    kind = ""
    doc_id = ""
    try:
        if p.suffix.lower() == ".json":
            import json

            data = json.loads(text)
        else:
            data = yaml.safe_load(text)
        if isinstance(data, dict):
            spec, kind = detect_document(data)
            doc_id = _extract_id(data)
    except Exception:
        pass

    return {
        "path": str(p),
        "byte_size": len(raw),
        "line_count": text.count("\n") + (0 if text.endswith("\n") else 1),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "spec": spec,
        "kind": kind,
        "id": doc_id,
    }


def _extract_id(data: Dict[str, Any]) -> str:
    for key in ("id", "productID"):
        if isinstance(data.get(key), str):
            return data[key]
    product = data.get("product")
    if isinstance(product, dict):
        for key in ("productID", "id"):
            if isinstance(product.get(key), str):
                return product[key]
    catalog = data.get("catalog")
    if isinstance(catalog, dict):
        meta = catalog.get("metadata")
        if isinstance(meta, dict) and isinstance(meta.get("id"), str):
            return meta["id"]
    return ""
