"""
parse_classes.py
Extrai mapeamento magia → classes a partir de um PDF estruturado como:

  ## MAGIAS DE BARDO
  ## TRUQUES (NÍVEL 0)
  Nome da Magia (escola)
  Outra Magia (escola, ritual)

Retorna: dict  { "nome da magia": ["Bardo", "Clérigo", ...] }
"""

import re
import unicodedata
from docling.document_converter import DocumentConverter


# Regex para cabeçalho de classe: "MAGIAS DE BARDO", "MAGIAS DO DRUIDA", etc.
RE_CLASS_HEADER = re.compile(
    r"^magias\s+d[oae]s?\s+(.+)$", re.IGNORECASE
)

# Regex para sub-cabeçalho de nível (ignora)
RE_LEVEL_HEADER = re.compile(
    r"^(truques?|(\d+)[°º]\s*n[íi]vel)", re.IGNORECASE
)

# Regex para remover anotação de escola no final: "(encantamento)" ou "(ilusão, ritual)"
RE_SCHOOL_SUFFIX = re.compile(r"\s*\([^)]+\)\s*$")

# Linhas que definitivamente são anotações de escola soltas (ex: "(adivinhação, ritual)")
RE_SCHOOL_ONLY = re.compile(r"^\([^)]+\)\s*$")


def _norm(s: str) -> str:
    """Lowercase sem acentos para comparação fuzzy."""
    nfkd = unicodedata.normalize("NFKD", s.lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _extract_class_name(header_text: str) -> str | None:
    """'MAGIAS DE BARDO' → 'Bardo'"""
    m = RE_CLASS_HEADER.match(header_text.strip())
    if not m:
        return None
    raw = m.group(1).strip()
    # Capitaliza cada palavra mas mantém acentos
    return raw.title()


def extract(pdf_path: str) -> dict[str, list[str]]:
    """
    Processa o PDF e retorna { "nome magia lower": ["Classe1", ...] }
    """
    print(f"  [parse_classes] Convertendo: {pdf_path}")
    converter = DocumentConverter()
    doc = converter.convert(pdf_path).document
    raw_md = doc.export_to_markdown()

    mapping: dict[str, list[str]] = {}
    current_class: str | None = None
    pending_name: str | None = None  # nome parcial aguardando continuação

    lines = raw_md.split("\n")

    for raw_line in lines:
        line = raw_line.strip("# ").strip()

        # ── Ignora linhas vazias ────────────────────────────────────────────
        if not line or line.startswith("<!--"):
            pending_name = None
            continue

        # ── Detecta cabeçalho de classe ────────────────────────────────────
        class_name = _extract_class_name(line)
        if class_name:
            current_class = class_name
            pending_name = None
            print(f"    [CLASSE] {current_class}")
            continue

        # ── Detecta sub-cabeçalho de nível (ignora) ────────────────────────
        if RE_LEVEL_HEADER.match(line):
            pending_name = None
            continue

        # Sem classe ativa, ignora
        if not current_class:
            continue

        # ── Linha só com anotação de escola → finaliza nome pendente ───────
        if RE_SCHOOL_ONLY.match(line):
            if pending_name:
                _register(mapping, pending_name, current_class)
                pending_name = None
            continue

        # ── Linha com nome de magia (+ possível escola inline) ─────────────
        # Remove anotação de escola inline: "Falar com Animais (adivinhação, ritual)"
        name_candidate = RE_SCHOOL_SUFFIX.sub("", line).strip()

        # Se ainda tem parêntese aberto → magia tem nome longo que quebrou:
        # ex: "Localizar Animais ou Plantas" ficou separado de "(adivinhação, ritual)"
        if "(" in name_candidate and ")" not in name_candidate:
            # Anotação ainda não fechada — aguarda próxima linha
            pending_name = (pending_name + " " + name_candidate).strip() if pending_name else name_candidate
            continue

        # Se havia nome pendente, esse é a continuação do nome (não a anotação)
        if pending_name and not RE_SCHOOL_ONLY.match(line):
            # Verifica se esta linha é continuação do nome ou já é nova magia
            full = pending_name + " " + name_candidate
            _register(mapping, full.strip(), current_class)
            pending_name = None
            continue

        if name_candidate:
            _register(mapping, name_candidate, current_class)
            pending_name = None

    # Garante ordenação das classes por magia
    for k in mapping:
        mapping[k] = sorted(set(mapping[k]))

    print(f"  [parse_classes] {len(mapping)} magias encontradas")
    return mapping


def _register(mapping: dict, name: str, classe: str) -> None:
    key = name.lower()
    if key not in mapping:
        mapping[key] = []
    if classe not in mapping[key]:
        mapping[key].append(classe)
