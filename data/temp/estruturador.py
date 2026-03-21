import re

INPUT_FILE = "output.md"
OUTPUT_FILE = "spells-5e.md"

def is_spell_title(line):
    # heurística simples: linha curta, sem ":" e com palavras capitalizadas
    return (
        line.strip()
        and len(line.split()) <= 5
        and ":" not in line
        and line[0].isupper()
    )

def format_spell_block(lines):
    title = lines[0].strip()
    body = lines[1:]

    formatted = []
    formatted.append(f"## {title}")

    for line in body:
        line = line.strip()

        if line.lower().startswith("casting time"):
            formatted.append(f"- **Casting Time:** {line.split(':',1)[1].strip()}")
        elif line.lower().startswith("range"):
            formatted.append(f"- **Range:** {line.split(':',1)[1].strip()}")
        elif line.lower().startswith("components"):
            formatted.append(f"- **Components:** {line.split(':',1)[1].strip()}")
        elif line.lower().startswith("duration"):
            formatted.append(f"- **Duration:** {line.split(':',1)[1].strip()}")
        else:
            formatted.append(line)

    return "\n".join(formatted)


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

spells = []
current_spell = []

for line in lines:
    if is_spell_title(line):
        if current_spell:
            spells.append(current_spell)
        current_spell = [line]
    else:
        current_spell.append(line)

if current_spell:
    spells.append(current_spell)

# formata tudo
formatted_spells = []

for spell in spells:
    formatted_spells.append(format_spell_block(spell))

# salva
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n\n---\n\n".join(formatted_spells))

print(f"✅ Arquivo gerado: {OUTPUT_FILE}")