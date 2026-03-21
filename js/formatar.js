const fs = require('fs');

const filePath = './js/spells-5E-2014-PTBR.json';
let rawData = fs.readFileSync(filePath, 'utf8');
let db = JSON.parse(rawData);

const ptLower = 'a-záéíóúàèùâêîôûãõç';
const ptUpper = 'A-ZÁÉÍÓÚÀÈÙÂÊÎÔÛÃÕÇ';

// Triggers that follow section headers in D&D spell descriptions
const triggers = [
  'Você', 'O alvo', 'A criatura', 'Se a criatura', 'Cada alvo', 'Um alvo',
  'O deslocamento', 'Qualquer criatura', 'Ele ', 'Essa magia', 'Esta magia',
  'Cada criatura', 'As criaturas', 'Os alvos', 'A arma', 'O alvo deve',
  'Seus ataques', 'A magia', 'Ao fazer'
];
const triggerLookahead = `(?:${triggers.join('|')})`;

// Words to exclude as section headers (ability scores, sizes, etc.)
const excludeWords = new Set([
  'Força', 'Destreza', 'Constituição', 'Inteligência', 'Sabedoria', 'Carisma',
  'Enorme', 'Grande', 'Médio', 'Pequeno', 'Miúdo', 'Colossal'
]);

// Pattern for a section header: 1-4 capitalized words
const wordPattern = `[${ptUpper}][${ptLower}]+(?:\\s[${ptUpper}][${ptLower}]*){0,3}`;
const sectionPattern = ` (${wordPattern})\\.\\s+(?=${triggerLookahead})`;
const sectionRegex = new RegExp(sectionPattern, 'g');

let changed = 0;

db.spells = db.spells.map(spell => {
  let desc = spell.description;
  const original = desc;

  // 1. Isola "Em Níveis Superiores." em um novo parágrafo com negrito
  desc = desc.replace(/ Em Níveis Superiores\./g, '</p>\n<p><strong>Em Níveis Superiores.</strong>');

  // 2. Formata cabeçalhos de seção em negrito usando lookahead para triggers
  desc = desc.replace(sectionRegex, (match, p1) => {
    const words = p1.trim().split(/\s+/);

    // Exclui palavras conhecidas que não são cabeçalhos
    if (excludeWords.has(p1.trim())) return match;

    // Exclui frases com conectivos no meio (indicam frase normal, não cabeçalho)
    if (words.length >= 2 && /\b(e|ou|de|com|para|que)\b/.test(p1)) return match;

    return `</p>\n<p><strong>${p1}.</strong> `;
  });

  // 3. Converte itens de lista marcados com "?" em <ul><li>
  if (desc.includes('? ')) {
    desc = desc.replace(/ \? /g, '\n? ');
    desc = desc.replace(/\? (.*?)(?=\n\? |<\/p>|$)/g, '<li>$1</li>');
    desc = desc.replace(/(<li>.*<\/li>)/s, '\n<ul>\n$1\n</ul>\n');
  }

  if (desc !== original) changed++;
  spell.description = desc;
  return spell;
});

fs.writeFileSync(filePath, JSON.stringify(db, null, 2), 'utf8');
console.log(`Formatação concluída! ${changed} magias modificadas.`);
