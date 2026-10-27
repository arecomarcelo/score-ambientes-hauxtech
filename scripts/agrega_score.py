#!/usr/bin/env python3
"""agrega_score.py — junta os payloads públicos de cada ambiente no score-data.json lido pela landing.

Separação dos ambientes (Fase 10, D07/D08, 27/10/2026): cada repositório privado
(hauxtech-documentacao e oficial-documentacao) publica só o próprio payload
(score-data-hauxtech.json, score-data-oficial.json) com o publica_score.sh dele; este script
combina os dois no formato que a index.html já consome. Não lê nada fora deste repositório.

Uso (na raiz do repositório):
    python3 scripts/agrega_score.py            # grava score-data.json
    python3 scripts/agrega_score.py --verificar  # só confere se o score-data.json atual já é o agregado
"""

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AMBIENTES = ("hauxtech", "oficial")
PROIBIDOS = [
    "/home/areco", "/media/areco", "git@github.com", "gho_", "ghp_", "VPS Contabo", "Hostinger",
    "OpenLiteSpeed", "Nginx Proxy Manager", "PostgreSQL único compartilhado", "sga_multiapp", "sga_db_local",
]
MIN_APPS = 20


def carrega(amb):
    caminho = RAIZ / f"score-data-{amb}.json"
    if not caminho.exists():
        sys.exit(f"❌ {caminho.name} não encontrado — publique o ambiente {amb} antes")
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if dados.get("ambiente") != amb or list(dados.get("ambientes", {})) != [amb]:
        sys.exit(f"❌ {caminho.name} não é um payload só do ambiente {amb}")
    if any(app.get("ambiente") != amb for app in dados.get("apps", [])):
        sys.exit(f"❌ {caminho.name} tem apps de outro ambiente")
    return dados


def sem_repetir(*listas):
    vistos, saida = set(), []
    for lista in listas:
        for item in lista:
            chave = json.dumps(item, sort_keys=True, ensure_ascii=False)
            if chave not in vistos:
                vistos.add(chave)
                saida.append(item)
    return saida


def agrega():
    hx, of = carrega("hauxtech"), carrega("oficial")
    nomes = [a["nome"] for a in hx["apps"]] + [a["nome"] for a in of["apps"]]
    repetidos = {n for n in nomes if nomes.count(n) > 1}
    if repetidos:
        sys.exit(f"❌ apps nos dois ambientes: {', '.join(sorted(repetidos))}")
    payload = {
        "schema_version": hx.get("schema_version") or of.get("schema_version"),
        "updated_at": max(hx["updated_at"], of["updated_at"]),
        "source_label": hx.get("source_label") or of.get("source_label"),
        "ambientes": {"hauxtech": hx["ambientes"]["hauxtech"], "oficial": of["ambientes"]["oficial"]},
        "apps": hx["apps"] + of["apps"],
        "insights": sem_repetir(hx.get("insights", []), of.get("insights", [])),
        # as notas gerais do Oficial vêm primeiro, mantendo a ordem que a landing já exibia
        "notas": sem_repetir(of.get("notas", []), hx.get("notas", [])),
    }
    bruto = json.dumps(payload, ensure_ascii=False)
    encontrados = [p for p in PROIBIDOS if p in bruto]
    if encontrados:
        sys.exit("❌ conteúdo sensível no payload agregado: " + ", ".join(encontrados))
    if len(payload["apps"]) < MIN_APPS:
        sys.exit(f"❌ payload agregado com {len(payload['apps'])} apps (mínimo {MIN_APPS})")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verificar", action="store_true", help="não grava; sai com erro se o score-data.json atual for diferente do agregado (ignora updated_at)")
    args = parser.parse_args()
    payload = agrega()
    destino = RAIZ / "score-data.json"
    if args.verificar:
        atual = json.loads(destino.read_text(encoding="utf-8"))
        atual.pop("updated_at", None)
        novo = dict(payload)
        novo.pop("updated_at", None)
        if atual != novo:
            sys.exit("⚠️  score-data.json difere do agregado dos dois ambientes")
        print("✅ score-data.json é o agregado dos dois ambientes")
        return
    destino.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ score-data.json agregado: {len(payload['apps'])} apps, updated_at {payload['updated_at']}")


if __name__ == "__main__":
    main()
