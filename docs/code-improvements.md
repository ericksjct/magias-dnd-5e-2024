# Melhorias identificadas no index.html

> Análise feita em 2026-03-28. O menu duplicado desktop/mobile é decisão de design intencional e não consta aqui.

---

## 1. Wrapper para localStorage

O mesmo padrão `try { localStorage... } catch(e) {}` aparece ~9 vezes espalhadas no código.

```js
// atual (repetido em todo lugar)
try { localStorage.setItem('knownSpells', JSON.stringify(knownSpells)); } catch(e) {}

// proposta
function safeSave(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch(e) {} }
function safeLoad(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch(e) { return fallback; } }
```

---

## 2. Restore de filtros em `applyShareState()`

7 linhas quase idênticas de `.clear()` + `.forEach(add)` para cada filtro (linhas ~1168).

```js
// atual (repetido 7x)
filters.levels.clear();
(f.levels || []).forEach(function(v) { filters.levels.add(v); });
filters.schools.clear();
(f.schools || []).forEach(function(v) { filters.schools.add(v); });
// ...

// proposta
['levels','schools','castTimes','ranges','components','durations','sources'].forEach(function(key) {
    filters[key].clear();
    (f[key] || []).forEach(function(v) { filters[key].add(v); });
});
```

---

## 3. `buildFilterUI()` declarativo

`buildCheckboxGroup()` é chamado 7 vezes com o mesmo padrão. Poderia ser uma config iterada.

```js
// proposta
var filterDefs = [
    { id: 'filter-levels',     set: filters.levels,     values: ..., label: ... },
    { id: 'filter-schools',    set: filters.schools,    values: ..., label: ... },
    // ...
];
filterDefs.forEach(function(def) {
    buildCheckboxGroup(def.id, def.values, def.set, def.label);
});
```

---

## 4. Listeners duplicados para botões espelhados

`#show-known`/`#show-known-m`, `#share-copy`/`#share-copy-m`, `#print-btn`/`#print-btn-m` têm listeners separados com código idêntico.

```js
// proposta: um único listener por ação
['show-known', 'show-known-m'].forEach(function(id) {
    document.getElementById(id).addEventListener('click', toggleKnownFilter);
});
```

---

## 5. `syncKnownIcons()` com seletores hardcoded

Atualiza 4 elementos manualmente. Frágil se um novo botão for adicionado.

```js
// atual
document.querySelector('#show-known img').src = src;
document.querySelector('#show-known-m img').src = src;
document.querySelector('#known-mobile img').src = src;
document.querySelector('#strip-show-known img').src = src;

// proposta: usar um atributo de dados nos elementos
// HTML: <img data-known-icon>
document.querySelectorAll('[data-known-icon]').forEach(function(el) { el.src = src; });
```

---

## 6. `switchLanguage()` extraída

Cada botão de bandeira tem o mesmo bloco de lógica inline: atualiza `currentLang`, history, classes ativas, i18n, filtros e localStorage.

```js
// proposta
function switchLanguage(lang) {
    currentLang = lang;
    history.replaceState(null, '', '?lang=' + lang);
    document.querySelectorAll('.flag-btn').forEach(function(b) {
        b.classList.toggle('active', b.dataset.lang === lang);
    });
    applyI18n();
    buildVersionFilter();
    loadSpells();
    safeSave('lang', lang);
}
```

---

## 7. `unknownIcon()` recalculada em 3 lugares

A lógica de escolher o ícone certo (dark/light) aparece na função dedicada, no toggle de tema e inline no build do card. Deveria sempre passar pela função.

---

## 8. Ícones SVG duplicados no HTML

Os ícones de share, print e abrir-sidebar aparecem 2–3 vezes cada. Poderiam usar `<symbol>` + `<use>`:

```html
<!-- no topo do body, oculto -->
<svg style="display:none">
    <symbol id="icon-share" viewBox="...">...</symbol>
    <symbol id="icon-print" viewBox="...">...</symbol>
</svg>

<!-- nos botões -->
<svg><use href="#icon-share"/></svg>
```

---

## 9. `alignMenu()` é função vazia

Definida na linha ~814 e chamada 5 vezes, mas não faz nada. Resquício de versão anterior — pode ser removida junto com todas as chamadas.
