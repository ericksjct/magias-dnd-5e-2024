"""
parse_spells.py
Extrai descrições de magias de um PDF estruturado (D&D 5e PTBR).
Retorna lista de dicts e string markdown.

Baseado em data/temp/pdf_docling.py, refatorado como módulo reutilizável.
"""

import re
import os
from pypdf import PdfReader, PdfWriter
from docling.document_converter import DocumentConverter

BATCH_SIZE = 5
OVERLAP = 2
STEP = BATCH_SIZE - OVERLAP

FIELD_NAMES = r"(Tempo de Conjura[cç][aã]o|Alcance|Componentes|Dura[cç][aã]o)"


# ── Normalização de campos ───────────────────────────────────────────────────

def _normalize_fields(text: str) -> str:
    text = re.sub(
        rf"{FIELD_NAMES}\s*\n+\s*:\s*",
        lambda m: m.group(1) + ": ",
        text, flags=re.IGNORECASE,
    )
    text = re.sub(
        rf"{FIELD_NAMES}\s+:\s*",
        lambda m: m.group(1) + ": ",
        text, flags=re.IGNORECASE,
    )
    text = re.sub(
        rf"\s+({FIELD_NAMES[1:-1]}):",
        lambda m: "\n" + m.group(1) + ":",
        text, flags=re.IGNORECASE,
    )
    return text


# ── Parse de um bloco de magia ───────────────────────────────────────────────

def _parse_spell_block(block: str) -> dict | None:
    block = _normalize_fields(block)
    lines = [l.rstrip() for l in block.split("\n")]

    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines or not lines[0].startswith("## "):
        return None

    spell = {
        "name": lines[0][3:].strip(),
        "level": None,
        "school": "",
        "ritual": False,
        "castTime": "",
        "range": "",
        "components": "",
        "material": None,
        "concentration": False,
        "duration": "",
        "description": "",
    }

    level_found = False
    in_description = False
    desc_lines = []
    i = 1

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            if in_description:
                desc_lines.append("")
            i += 1
            continue

        if not level_found:
            level_m = re.match(r"(\d+)[°º]\s*nível de\s+(.+?)(?:\s*\(ritual\))?$", line, re.IGNORECASE)
            truque_m = re.match(r"truque de\s+(.+?)(?:\s*\(ritual\))?$", line, re.IGNORECASE)
            if level_m:
                spell["level"] = int(level_m.group(1))
                spell["school"] = level_m.group(2).strip().lower()
                spell["ritual"] = bool(re.search(r"\(ritual\)", line, re.IGNORECASE))
                level_found = True
                i += 1
                continue
            elif truque_m:
                spell["level"] = 0
                spell["school"] = truque_m.group(1).strip().lower()
                spell["ritual"] = bool(re.search(r"\(ritual\)", line, re.IGNORECASE))
                level_found = True
                i += 1
                continue

        if in_description:
            desc_lines.append(line)
            i += 1
            continue

        cast_m = re.match(r"Tempo de Conjura[cç][aã]o:\s*(.+)", line, re.IGNORECASE)
        range_m = re.match(r"Alcance:\s*(.+)", line, re.IGNORECASE)
        comp_m = re.match(r"Componentes:\s*(.+)", line, re.IGNORECASE)
        dur_m = re.match(r"Dura[cç][aã]o:\s*(.+)", line, re.IGNORECASE)

        if cast_m:
            spell["castTime"] = cast_m.group(1).strip()
        elif range_m:
            spell["range"] = range_m.group(1).strip()
        elif comp_m:
            comp_str = comp_m.group(1).strip()
            j = i + 1
            while j < len(lines) and comp_str.count("(") > comp_str.count(")"):
                next_line = lines[j].strip()
                if next_line:
                    comp_str += " " + next_line
                j += 1
            i = j - 1

            mat_m = re.match(r"([VSM,\s]+?)\s*\((.+)\)\s*$", comp_str)
            if mat_m:
                spell["components"] = mat_m.group(1).strip().rstrip(",").strip()
                spell["material"] = mat_m.group(2).strip()
            else:
                spell["components"] = comp_str.strip()
        elif dur_m:
            dur_str = dur_m.group(1).strip()
            if re.search(r"concentra[cç][aã]o", dur_str, re.IGNORECASE):
                spell["concentration"] = True
                dur_str = re.sub(r"concentra[cç][aã]o,?\s*", "", dur_str, flags=re.IGNORECASE).strip()
            spell["duration"] = dur_str
            in_description = True

        i += 1

    while desc_lines and not desc_lines[0].strip():
        desc_lines.pop(0)
    while desc_lines and not desc_lines[-1].strip():
        desc_lines.pop()

    spell["description"] = _postprocess_description("\n".join(desc_lines))
    return spell


# ── Pós-processamento da descrição ───────────────────────────────────────────

def _postprocess_description(text: str) -> str:
    text = re.sub(r"  +", " ", text)

    paragraphs = text.split("\n\n")
    merged = []
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i].strip()
        while (
            para
            and i + 1 < len(paragraphs)
            and para[-1] not in ".!?:"
            and paragraphs[i + 1].strip()
        ):
            i += 1
            para = para + " " + paragraphs[i].strip()
        merged.append(para)
        i += 1
    text = "\n\n".join(merged)

    text = re.sub(
        r"^([A-ZÁÉÍÓÚÃÕÂÊÎÔÛÀÈÌÒÙÇ][A-Za-záéíóúãõâêîôûàèìòùçÁÉÍÓÚÃÕÂÊÎÔÛÀÈÌÒÙÇ\s]+?)\s+\.\s+",
        lambda m: f"**{m.group(1).strip()}.** ",
        text, flags=re.MULTILINE,
    )
    text = re.sub(r"^Material:", "**Material:**", text, flags=re.MULTILINE)
    return text


# ── Formatadores de saída ────────────────────────────────────────────────────

def _md_to_html(text: str) -> str:
    parts = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", para)
        parts.append(f"<p>{para}</p>")
    return "\n".join(parts)


def _format_spell(spell: dict, classes: list[str]) -> tuple[str, dict]:
    name_lower = spell["name"].lower()
    name_title = spell["name"].title()

    desc_parts = []
    if spell["material"]:
        desc_parts.append(f"**Material:** {spell['material']}.")
        desc_parts.append("")
    if spell["description"]:
        desc_parts.append(spell["description"])
    description_md = "\n".join(desc_parts)

    classes_str = ", ".join(classes) if classes else ""

    md = "\n".join([
        f"## {name_title}",
        "",
        f"- name: {name_lower}",
        f"- classe: {classes_str}",
        f"- level: {spell['level']}",
        f"- school: {spell['school']}",
        f"- ritual: {'true' if spell['ritual'] else 'false'}",
        f"- castTime: {spell['castTime']}",
        f"- range: {spell['range']}",
        f"- components: {spell['components']}",
        f"- concentration: {'true' if spell['concentration'] else 'false'}",
        f"- duration: {spell['duration']}",
        "",
        "### Descrição",
        "",
        description_md,
        "",
        "---",
    ])

    data = {
        "name": name_lower,
        "displayName": name_title,
        "classe": classes,
        "level": spell["level"],
        "school": spell["school"],
        "ritual": spell["ritual"],
        "castTime": spell["castTime"],
        "range": spell["range"],
        "components": spell["components"],
        "concentration": spell["concentration"],
        "duration": spell["duration"],
        "description": _md_to_html(description_md),
    }

    return md, data


# ── Extração principal ───────────────────────────────────────────────────────

NON_SPELL_HEADERS = {"DESCRIÇÕES DAS MAGIAS", "LISTA DE MAGIAS"}


def extract(
    pdf_path: str,
    classes_map: dict[str, list[str]],
    temp_dir: str = "temp_chunks",
) -> tuple[str, list[dict], list[str]]:
    """
    Extrai magias do PDF de descrições e injeta classes do classes_map.

    Retorna:
      - markdown (str)
      - spells (list[dict])
      - sem_classe (list[str])  — nomes de magias sem dados de classe
    """
    print(f"  [parse_spells] Convertendo: {pdf_path}")
    os.makedirs(temp_dir, exist_ok=True)

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"  [parse_spells] {total_pages} páginas")

    converter = DocumentConverter()
    raw_text = ""

    for i in range(0, total_pages, STEP):
        start = i
        end = min(i + BATCH_SIZE, total_pages)
        pages = list(range(start, end))
        print(f"    Processando páginas: {pages}")

        writer = PdfWriter()
        for j in pages:
            writer.add_page(reader.pages[j])

        chunk_path = os.path.join(temp_dir, f"chunk_{start}_{end}.pdf")
        with open(chunk_path, "wb") as f:
            writer.write(f)

        try:
            doc = converter.convert(chunk_path).document
            md = doc.export_to_markdown()
            if md.strip():
                raw_text += md + "\n\n"
            else:
                print(f"    Chunk vazio: {chunk_path}")
        except Exception as e:
            print(f"    Erro no chunk {chunk_path}: {e}")

    # Divide em blocos por magia
    spell_blocks = re.split(r"\n(?=## [^\n]+\n)", raw_text)

    seen = set()
    output_parts = []
    output_json = []
    sem_classe = []

    def lookup_classes(name: str) -> list[str]:
        key = name.lower()
        if key in classes_map:
            return classes_map[key]
        # Fallback: normalização sem acento
        import unicodedata
        def norm(s):
            nfkd = unicodedata.normalize("NFKD", s.lower())
            return "".join(c for c in nfkd if not unicodedata.combining(c))
        target = norm(key)
        for k, v in classes_map.items():
            if norm(k) == target:
                return v
        return []

    for block in spell_blocks:
        block = block.strip()
        if not block:
            continue

        header_m = re.match(r"## ([^\n]+)", block)
        if not header_m:
            continue

        header = header_m.group(1).strip()
        if header.upper() in NON_SPELL_HEADERS or re.match(r"Páginas \d+", header):
            continue

        name_key = header.lower()
        if name_key in seen:
            continue
        seen.add(name_key)

        spell = _parse_spell_block(block)
        if spell and spell["level"] is not None and spell["castTime"]:
            classes = lookup_classes(spell["name"])
            if not classes:
                sem_classe.append(spell["name"].lower())
            md, data = _format_spell(spell, classes)
            output_parts.append(md)
            output_json.append(data)
        else:
            print(f"    Magia ignorada/incompleta: {header}")

    markdown = "\n\n".join(output_parts)
    return markdown, output_json, sem_classe
