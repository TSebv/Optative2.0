from __future__ import annotations
import json
import os
import faiss
import pandas as pd
from django.conf import settings
from sentence_transformers import SentenceTransformer

ARTEFACTS_DIR = os.path.join(settings.BASE_DIR, "core", "ia", "artefactos")

with open(os.path.join(ARTEFACTS_DIR, "config.json"), encoding="utf-8") as cfg_file:
    CONFIG = json.load(cfg_file)

MODEL = SentenceTransformer(CONFIG["model_name"])
INDEX = faiss.read_index(os.path.join(ARTEFACTS_DIR, "faiss.index"))
CATALOGO = pd.read_csv(os.path.join(ARTEFACTS_DIR, "productos.csv"))

def buscar_productos(query: str, k: int=5) -> list[dict]:
    # Normalizar la consulta
    query = (query or "").strip()
    if not query:
        return[]
    
    emb = MODEL.encode([query], normalize_embeddings=True).astype("float32")
    distancia, indices = INDEX.search(emb, k)

    resultados: list[dict] = []

    for score, idx in zip(distancia[0], indices[0]):
        if idx < 0:
            continue
        fila = CATALOGO.iloc[int(idx)].to_dict()
        fila["score"] = float(score)
        resultados.append(fila)

    return resultados

