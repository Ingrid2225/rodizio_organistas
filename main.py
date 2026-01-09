
# -*- coding: utf-8 -*-
"""
Rodízio de organistas (sem envio de mensagens)
Cultos: segunda e quarta
Fuso: America/Sao_Paulo
"""
import os
import json
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from datetime import timezone, timedelta
from typing import List, Dict
import argparse

ESCALA_ARQUIVO = "escala.json"

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        TZ = ZoneInfo("America/Sao_Paulo")
    except (ZoneInfoNotFoundError, Exception):
        # Fallback: UTC-3 (sem ajuste automático de horário de verão)
        TZ = timezone(timedelta(hours=-3))
except ImportError:
    # Python < 3.9: sem zoneinfo nativo; usa UTC-3 fixo
    TZ = timezone(timedelta(hours=-3))



# -------- Organistas --------
ORGANISTAS = [
    {"nome": "Leila"},
    {"nome": "Juliana"},
    {"nome": "Karine"},
    {"nome": "Alessandra"},
    {"nome": "Jhenifer"},
    {"nome": "Vanessa"},
    {"nome": "Luana"},
    {"nome": "Tayna"},
]

# -------- Dados da escala --------
@dataclass
class ItemEscala:
    data: str          # YYYY-MM-DD
    dia_semana: str    # "Segunda" ou "Quarta"
    culto: str         # "Segunda" ou "Quarta"
    organista: str

    @property
    def data_date(self) -> date:
        return datetime.strptime(self.data, "%Y-%m-%d").date()

# -------- Utilidades --------
def proxima_segunda(base: date) -> date:
    """Retorna a próxima segunda (não hoje)."""
    dias = (7 - base.weekday()) % 7
    return base + timedelta(days=dias if dias != 0 else 7)

def gerar_datas_semanais(inicio_segunda: date, semanas: int) -> List[date]:
    """Gera lista de datas (segunda e quarta) por N semanas, começando na 'inicio_segunda'."""
    datas = []
    for w in range(semanas):
        seg = inicio_segunda + timedelta(weeks=w)
        qua = seg + timedelta(days=2)
        datas.extend([seg, qua])
    return datas

def dia_semana_label(dt: date) -> str:
    # 0 = Monday ... 2 = Wednesday
    return "Segunda" if dt.weekday() == 0 else "Quarta"

# -------- Persistência --------
def salvar_escala(escala: List[ItemEscala]) -> None:
    with open(ESCALA_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump([asdict(i) for i in escala], f, ensure_ascii=False, indent=2)

def carregar_escala() -> List[ItemEscala]:
    if not os.path.exists(ESCALA_ARQUIVO):
        return []
    with open(ESCALA_ARQUIVO, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ItemEscala(**item) for item in data]

# -------- Lógica de escala --------
def gerar_escala(inicio: date, semanas: int) -> List[ItemEscala]:
    """
    Gera escala em rodízio: 2 cultos por semana (Seg/Qua), rotacionando os 8 nomes.
    Cada organista toca aproximadamente 1x a cada 4 semanas.
    """
    inicio_seg = proxima_segunda(inicio)
    datas = gerar_datas_semanais(inicio_seg, semanas)
    escala: List[ItemEscala] = []

    idx = 0
    for dt in datas:
        org = ORGANISTAS[idx % len(ORGANISTAS)]
        escala.append(ItemEscala(
            data=dt.strftime("%Y-%m-%d"),
            dia_semana=dia_semana_label(dt),
            culto=dia_semana_label(dt),
            organista=org["nome"],
        ))
        idx += 1

    return escala

def texto_lembrete(item: ItemEscala) -> str:
    dt = item.data_date
    return (
        f"[LEMBRETE SIMULADO] "
        f"{item.organista} está escalada para o culto de {item.culto} "
        f"no dia {dt.strftime('%d/%m/%Y')} (aviso enviado 5 dias antes)."
    )

def simular_lembretes_hoje() -> List[Dict]:
    """
    Verifica a escala e imprime no console quem deveria ser lembrado hoje (cultos em 5 dias).
    """
    registros = []
    hoje = datetime.now(TZ).date()
    escala = carregar_escala()

    if not escala:
        print("Nenhuma escala encontrada. Gere a escala primeiro.")
        return registros

    print(f"Data de hoje: {hoje.strftime('%d/%m/%Y')} (America/Sao_Paulo)")
    for item in escala:
        faltam = (item.data_date - hoje).days
        if faltam == 5:
            mensagem = texto_lembrete(item)
            print(mensagem)
            registros.append({
                "status": "SIMULADO",
                "organista": item.organista,
                "data": item.data,
                "culto": item.culto
            })
    if not registros:
        print("Hoje não há lembretes (nenhum culto em 5 dias).")
    return registros

def listar_escala():
    escala = carregar_escala()
    if not escala:
        print("Nenhuma escala encontrada. Gere a escala primeiro.")
        return
    print("Escala de organistas:")
    for item in escala:
        dt = item.data_date.strftime("%d/%m/%Y")
        print(f"{dt} ({item.culto}) → {item.organista}")

# -------- CLI --------
def main():
    parser = argparse.ArgumentParser(description="Rodízio de organistas (sem envio de mensagens)")
    parser.add_argument("--gerar-escala", type=int, help="Gera escala para N semanas (ex: 12)")
    parser.add_argument("--inicio", type=str, help="Data base (YYYY-MM-DD) para iniciar a escala")
    parser.add_argument("--listar", action="store_true", help="Lista a escala salva")
    parser.add_argument("--simular-hoje", action="store_true", help="Simula lembretes de hoje (cultos em 5 dias)")
    args = parser.parse_args()

    if args.gerar_escala:
        inicio = date.today()
        if args.inicio:
            inicio = datetime.strptime(args.inicio, "%Y-%m-%d").date()
        escala = gerar_escala(inicio, args.gerar_escala)
        salvar_escala(escala)
        print(f"Escala gerada para {args.gerar_escala} semanas a partir de {inicio}.")
        listar_escala()
        return

    if args.listar:
        listar_escala()
        return

    if args.simular_hoje:
        simular_lembretes_hoje()
        return

    parser.print_help()

if __name__ == "__main__":
    main()
