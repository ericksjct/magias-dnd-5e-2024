# Estrutura do `.spell-item`

Hierarquia completa dos elementos dentro de um card de magia.

```
.spell-item
└── .spell-body
    ├── .title
    │   ├── .name
    │   │   ├── <p>  (nome da magia)
    │   │   │   └── .statblock-indicator  (opcional)
    │   │   └── <p class="school">  (escola + nível)
    │   └── .known
    │       └── <img>
    ├── .meta-line
    │   ├── .meta-pill  (Cast Time)
    │   ├── .meta-sep
    │   ├── .meta-pill  (Range)
    │   ├── .meta-sep
    │   ├── .meta-pill  (Components)
    │   │   └── .conc-badge  (opcional, dentro do pill de Duration)
    │   ├── .meta-sep
    │   ├── .meta-pill  (Duration)
    │   └── .ritual-pill  (opcional)
    ├── <p class="material-note">  (opcional — componente material)
    ├── <p class="material-note">  (opcional — cast time note)
    ├── .description  (descrição principal)
    ├── .description.upgrade-description  (opcional — "em níveis superiores")
    ├── <p class="material-note">  (opcional — class note)
    ├── <p class="spell-source">  (opcional — fonte)
    └── .tier-badge
```

---

## Elementos e formatação

### `.spell-body`
Container principal do card.
- `padding: 15px 15px 28px`
- `color: var(--subtext1)`
- `box-shadow: 2px 3px 6px rgba(0,0,0,0.08)` (light) / `2px 3px 8px rgba(0,0,0,0.25)` (dark)
- `background: var(--surface0)` / `border-color: var(--surface1)`

---

### `.title`
Linha de cabeçalho com nome + ícone de "conhecido".
- `display: flex; align-items: center`
- `margin-bottom: 10px`

---

### `.name`
Bloco com nome da magia e escola, separado por borda inferior.
- `border-bottom: 1px solid var(--surface2)`
- `display: flex; align-items: baseline; flex-grow: 1`
- `padding-bottom: 10px`

#### `<p>` (nome da magia)
- `font-size: 15pt`
- `font-weight: bold`
- `font-family: 'Texturina', serif`
- `font-variant: small-caps`
- `color: var(--text)`

#### `.statblock-indicator`
Ícone inline no nome, indica que a magia tem stat block.
- `display: inline-block; width: 16px; height: 11px`
- `background: linear-gradient(135deg, var(--mauve), var(--sapphire), var(--teal))`
- Máscara SVG: `img/summon.svg`

#### `.school`
Escola e nível da magia, ao lado direito do nome.
- `font-size: 8pt`
- `font-weight: normal`
- `font-style: italic`
- `color: var(--subtext1)`
- `text-align: right; white-space: nowrap; flex-grow: 1`

---

### `.known`
Ícone clicável de bookmark (magia conhecida/desconhecida).
- `height: 1.5em; cursor: pointer; margin-left: 10px`
- Imagem: `height: 100%; width: auto`
- Oculto na versão de impressão

---

### `.meta-line`
Linha de metadados com Cast Time, Range, Components e Duration.
- `display: flex; flex-wrap: wrap; align-items: baseline`
- `gap: 2px 4px`
- `font-size: 7.5pt`
- `color: var(--subtext0)`
- `line-height: 1.5`
- `margin: 0 0 2px 0`

#### `.meta-pill`
Cada item da meta-line (cast time, range, components, duration).
- `display: inline-flex; align-items: baseline; gap: 2px`
- `color: var(--subtext1)`

#### `.meta-sep`
Separador `·` entre os pills.
- `color: var(--overlay0)`
- `user-select: none`

#### `.ritual-pill`
Pill especial para magias rituais, exibido ao final da meta-line.
- Herda `.meta-pill`
- `color: var(--yellow)`

#### `.conc-badge`
Badge de Concentração, exibido dentro do pill de Duration.
- `font-size: 7.5pt`
- `color: var(--subtext0)`
- `margin-left: 3px`

---

### `.material-note`
Nota de componente material, cast time note ou class note (opcional).
- `font-size: 8pt`
- `color: var(--subtext0)`
- `margin: 6px 0 4px`

---

### `.description`
Bloco de descrição da magia.
- `font-size: 8pt`
- `<p>`: `margin: 0; padding-top: 0.3em; padding-bottom: 0.4em`
- `<ul>`: `padding-left: 1.5em`
- `<table>`: largura total, bordas apenas no topo e base (dotted), linhas pares com `var(--mantle)`

#### `.description.upgrade-description`
Descrição do efeito em níveis superiores ("Em Níveis Superiores").
- Mesma formatação de `.description`
- Sem estilo adicional diferenciado no CSS (distinção apenas semântica)

---

### `.spell-source`
Fonte/livro da magia, posicionada no canto inferior esquerdo do card.
- `position: absolute; bottom: 6px; left: 15px`
- `font-size: 8pt`
- `font-style: italic`
- `color: var(--subtext0)`

---

### `.tier-badge`
Badge de nível da magia, posicionado no canto inferior direito.
- `position: absolute; bottom: 6px; right: 8px`
- `font-size: 8pt`
- `color: var(--accent)`
- `opacity: 0.9`
- `letter-spacing: 1px`
- `user-select: none`
