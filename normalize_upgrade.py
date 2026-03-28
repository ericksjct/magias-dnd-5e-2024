"""
Normaliza os campos de "At Higher Levels" em todos os JSONs de magias.
- Extrai o texto de upgrade de `description` para `upgradeDescription`
- Padroniza o heading: EN → "At Higher Levels." | PT → "Em Níveis Superiores."
- Sempre em <strong><em>...</em></strong>
"""

import json
import re

FILES = {
    'js/spells-5E-2024-EN.json':   'EN',
    'js/spells-5E-2014-EN.json':   'EN',
    'js/spells-5E-2024-PTBR.json': 'PT',
    'js/spells-5E-2014-PTBR.json': 'PT',
}

# Padrões de heading (texto puro, sem tags HTML)
EN_HEADINGS = [
    r'Cantrip\s+Upgrade\.',
    r'At\s+Higher\s+Levels[.:]',
    r'Using\s+a\s+Higher-Level\s+Spell\s+Slot\.(?:\s+Use\s+the\s+spell\s+slot\'s\s+level\s+for\s+the\s+spell\'s\s+level\s+in\s+the\s+stat\s+block)?',
]
PT_HEADINGS = [
    r'Aprimoramento\s+de\s+Truque\.',
    r'Em\s+N[íi]veis\s+Superiores\.',
    r'Usando\s+um\s+Espa[çc]o\s+de\s+Magia\s+de\s+C[íi]rculo\s+Superior\.',
]

EN_STANDARD = 'At Higher Levels.'
PT_STANDARD = 'Em Níveis Superiores.'

def heading_pattern(headings):
    """Regex que detecta o heading de upgrade com qualquer combinação de tags HTML."""
    txt = '(?:' + '|'.join(headings) + ')'
    # Pode estar dentro de: <strong><em>, <em><strong>, <strong>, <em>, ou sem tags
    wrapped = (
        r'(?:'
        r'<strong>\s*<em>\s*' + txt + r'\s*</em>\s*</strong>'
        r'|<em>\s*<strong>\s*' + txt + r'\s*</strong>\s*</em>'
        r'|<strong>\s*' + txt + r'\s*</strong>'
        r'|<em>\s*' + txt + r'\s*</em>'
        r'|' + txt +
        r')'
    )
    return wrapped

def extract_upgrade(desc, headings, standard):
    """
    Encontra o heading de upgrade na description HTML e separa em
    (clean_description, upgrade_description). Retorna (desc, None) se não encontrar.
    """
    hp = heading_pattern(headings)
    std_html = f'<strong><em>{standard}</em></strong>'

    # Tenta os dois layouts possíveis:
    #
    # Layout A: heading abre um <p>
    #   ...main...</p><p>HEADING upgrade text</p>
    #
    # Layout B: heading está fora de <p>
    #   ...main...</p> HEADING <p>upgrade text</p>

    # Layout A: heading dentro de <p> (com ou sem </p> antes)
    pat_a = re.compile(
        r'((?:</p>\s*)+)'       # fechamento(s) do conteúdo principal
        r'<p>\s*'               # abertura do parágrafo de upgrade
        r'(?:' + hp + r')\s*'  # heading
        r'(.*?)'                # texto do upgrade
        r'</p>\s*$',
        re.IGNORECASE | re.DOTALL,
    )

    # Layout B: heading fora de <p>
    pat_b = re.compile(
        r'((?:</p>\s*)+)'       # fechamento do conteúdo principal
        r'(?:' + hp + r')\s*'  # heading solto
        r'(?:<p>)?\s*'          # abertura opcional do parágrafo
        r'(.*?)'                # texto do upgrade
        r'(?:</p>)?\s*$',
        re.IGNORECASE | re.DOTALL,
    )

    for pat in (pat_a, pat_b):
        m = pat.search(desc)
        if m:
            cut = m.start()
            clean = desc[:cut] + '</p>'
            upgrade_text = m.group(2).strip()
            # Remove tags residuais no início/fim
            upgrade_text = re.sub(r'^(?:</p>|<p>)\s*', '', upgrade_text)
            upgrade_text = re.sub(r'\s*(?:</p>|<p>)$', '', upgrade_text)
            upgrade_desc = f'<p>{std_html} {upgrade_text}</p>'
            return clean, upgrade_desc

    return desc, None


def process_file(path, lang):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    headings = EN_HEADINGS if lang == 'EN' else PT_HEADINGS
    standard = EN_STANDARD if lang == 'EN' else PT_STANDARD

    changed = 0
    no_upgrade = 0

    for spell in data['spells']:
        desc = spell.get('description') or ''
        clean, upgrade = extract_upgrade(desc, headings, standard)
        if upgrade:
            spell['description'] = clean
            spell['upgradeDescription'] = upgrade
            changed += 1
        else:
            spell['upgradeDescription'] = None
            no_upgrade += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'{path}')
    print(f'  + {changed} spells com upgradeDescription | {no_upgrade} sem upgrade\n')


if __name__ == '__main__':
    for path, lang in FILES.items():
        process_file(path, lang)
