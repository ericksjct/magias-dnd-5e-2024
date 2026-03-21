"""
processor/run.py
Ponto de entrada unificado do processador de magias D&D 5e PTBR.

Uso:
  python processor/run.py \\
    --spells  <pdf_descricoes.pdf> \\
    --classes <pdf_classes.pdf> \\
    --out     <prefixo_saida>     \\
    [--temp   <pasta_temp>]

Exemplos:
  # Livro do Jogador (páginas 214-289) + lista de classes
  python processor/run.py \\
    --spells  "data/temp/dd-5e-livro-do-jogador-fundo-branco-biblioteca-elfica-214-289.pdf" \\
    --classes "data/temp/dd-5e-livro-do-jogador-fundo-branco-biblioteca-elfica-correto.pdf" \\
    --out     output

Saídas geradas:
  <out>.md              — magias em markdown com classes preenchidas
  <out>.json            — magias em JSON estruturado
  <out>_sem_classe.txt  — magias sem dados de classe (se houver)
"""

import sys
import json
import argparse

sys.stdout.reconfigure(encoding="utf-8")

# Adiciona o diretório raiz ao path para importar os módulos do processor
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import parse_classes, parse_spells


def main():
    parser = argparse.ArgumentParser(
        description="Processa PDFs de magias D&D 5e PTBR e gera markdown + JSON enriquecidos."
    )
    parser.add_argument("--spells",  required=True, help="PDF com descrições das magias")
    parser.add_argument("--classes", required=True, help="PDF com listas de magias por classe")
    parser.add_argument("--out",     required=True, help="Prefixo dos arquivos de saída (ex: output)")
    parser.add_argument("--temp",    default="temp_chunks", help="Pasta para chunks temporários de PDF")
    args = parser.parse_args()

    print("\n=== ETAPA 1: Extraindo classes do PDF ===")
    classes_map = parse_classes.extract(args.classes)

    print("\n=== ETAPA 2: Extraindo magias do PDF ===")
    markdown, spells, sem_classe = parse_spells.extract(
        args.spells,
        classes_map,
        temp_dir=args.temp,
    )

    print("\n=== ETAPA 3: Salvando saídas ===")

    md_path = args.out + ".md"
    json_path = args.out + ".json"

    # Remove saídas anteriores
    for path in (md_path, json_path):
        if os.path.exists(path):
            os.remove(path)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"  Markdown : {md_path}  ({len(spells)} magias)")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"spells": spells}, f, ensure_ascii=False, indent=2)
    print(f"  JSON     : {json_path}")

    if sem_classe:
        report_path = args.out + "_sem_classe.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Magias sem dados de classe (preenchimento manual necessário)\n\n")
            f.write("\n".join(f"- {m}" for m in sorted(sem_classe)) + "\n")
        print(f"  Sem classe: {report_path}  ({len(sem_classe)} magias)")
    else:
        print("  Todas as magias tiveram classes preenchidas!")

    print("\nConcluido!")


if __name__ == "__main__":
    main()
