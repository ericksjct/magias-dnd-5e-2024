/**
 * Converte spells-5E-2014-PTBR.json → spells-5E-2014-PTBR.md
 *
 * Formato de cada magia:
 *
 * ## DisplayName
 * - name: acalmar emoções
 * - classe: Bardo, Clérigo
 * - level: 2
 * - school: encantamento
 * - ritual: false
 * - castTime: Ação
 * - range: 18 metros
 * - components: V, S
 * - concentration: true
 * - duration: até 1 minuto
 *
 * ### Descrição
 *
 * Texto limpo sem HTML, parágrafos separados por linha em branco.
 *
 * ---
 */

const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./js/spells-5E-2014-PTBR.json', 'utf8'));

function stripHtml(html) {
  return html
    // </p> vira separação de parágrafo
    .replace(/<\/p>/gi, '\n\n')
    // <p> removido
    .replace(/<p>/gi, '')
    // <strong> e </strong> removidos
    .replace(/<\/?strong>/gi, '')
    // qualquer outra tag removida
    .replace(/<[^>]+>/g, '')
    // normaliza espaços dentro de cada linha
    .split('\n')
    .map(line => line.replace(/\s+/g, ' ').trim())
    .join('\n')
    // colapsa mais de duas quebras consecutivas em exatamente duas
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

const lines = [];

for (const spell of data.spells) {
  lines.push(`## ${spell.displayName}`);
  lines.push('');
  lines.push(`- name: ${spell.name}`);
  lines.push(`- classe: ${spell.classe.join(', ')}`);
  lines.push(`- level: ${spell.level}`);
  lines.push(`- school: ${spell.school}`);
  lines.push(`- ritual: ${spell.ritual}`);
  lines.push(`- castTime: ${spell.castTime}`);
  lines.push(`- range: ${spell.range}`);
  lines.push(`- components: ${spell.components}`);
  lines.push(`- concentration: ${spell.concentration}`);
  lines.push(`- duration: ${spell.duration}`);
  lines.push('');
  lines.push('### Descrição');
  lines.push('');
  lines.push(stripHtml(spell.description));
  lines.push('');
  lines.push('---');
  lines.push('');
}

fs.writeFileSync('./js/spells-5E-2014-PTBR.md', lines.join('\n'), 'utf8');
console.log(`Exportado: ${data.spells.length} magias → spells-5E-2014-PTBR.md`);
