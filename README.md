Este projeto organiza a escala de organistas para cultos às segundas e quartas
e simula lembretes 5 dias antes (sem envio de mensagens).

FUNCIONALIDADES
- Gera escala em rodízio para N semanas.
- Salva e lê escala.json
- Lista a escala no console
- Simula quais lembretes seriam enviados hoje

Como usar
Gerar escala (12 semanas):
python main.py --gerar-escala 12

Listar escala:
python main.py --listar

Simular lembretes de hoje:
python main.py --simular-hoje

Gerar escala com data base:
python main.py --gerar-escala 12 --inicio 2026-01-12

MELHORIAS
Integrar comm whatsapp para enviar mensagem para organista.



