/**
 * Converte spells-5E-2014-PTBR.md → spells-5E-2014-PTBR.json
 *
 * Espera o formato gerado por json-to-md.js:
 *   ## DisplayName
 *   - key: value  (campos de metadados)
 *   ### Descrição
 *   Texto Markdown puro (sem HTML)
 *   ---
 *
 * O campo "description" é preservado como Markdown exatamente como
 * o usuário o editou — sem conversão para HTML.
 */

const fs = require('fs');

const raw = fs.readFileSync('./js/spells-5E-2014-PTBR.md', 'utf8');

// Divide os blocos pelo separador "---" seguido de linha em branco
const blocks = raw.split(/\n---\n/).map(b => b.trim()).filter(Boolean);

const spells = [];

for (const block of blocks) {
  const lines = block.split('\n');
  const spell = {};

  // Linha 0: ## DisplayName
  const headMatch = lines[0].match(/^##\s+(.+)$/);
  if (!headMatch) {
    console.warn('Bloco sem cabeçalho ## ignorado:', lines[0]);
    continue;
  }
  spell.displayName = headMatch[1].trim();

  // Campos de metadados: linhas "- key: value"
  const metaFields = ['name', 'classe', 'level', 'school', 'ritual', 'castTime', 'range', 'components', 'concentration', 'duration'];
  for (const line of lines) {
    const metaMatch = line.match(/^-\s+(\w+):\s*(.+)$/);
    if (!metaMatch) continue;
    const [, key, value] = metaMatch;
    if (!metaFields.includes(key)) continue;

    if (key === 'classe') {
      spell.classe = value.split(',').map(s => s.trim());
    } else if (key === 'level') {
      spell.level = parseInt(value, 10);
    } else if (key === 'ritual' || key === 'concentration') {
      spell[key] = value.trim() === 'true';
    } else {
      spell[key] = value.trim();
    }
  }

  // Descrição: tudo entre "### Descrição" e o fim do bloco
  const descIdx = lines.findIndex(l => l.startsWith('### Descrição'));
  if (descIdx !== -1) {
    spell.description = lines
      .slice(descIdx + 1)
      .join('\n')
      .trim();
  } else {
    spell.description = '';
  }

  spells.push(spell);
}

// Reordena os campos na mesma ordem do JSON original
const ordered = spells.map(s => ({
  name:          s.name,
  displayName:   s.displayName,
  classe:        s.classe,
  level:         s.level,
  school:        s.school,
  ritual:        s.ritual,
  castTime:      s.castTime,
  range:         s.range,
  components:    s.components,
  concentration: s.concentration,
  duration:      s.duration,
  description:   s.description,
}));

fs.writeFileSync('./js/spells-5E-2014-PTBR.json', JSON.stringify({ spells: ordered }, null, 2), 'utf8');
console.log(`Importado: ${ordered.length} magias → spells-5E-2014-PTBR.json`);
