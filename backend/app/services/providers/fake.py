# backend/app/services/providers/fake.py
# Provedores simulados (mock) — geram dados REALISTAS e DETERMINÍSTICOS.
#
# Por que determinístico?
#   - Mesma empresa + mesma data => sempre o mesmo saldo. Isso torna o
#     ambiente de demonstração estável e os testes confiáveis.
#   - A semente vem do CNPJ + data, então cada dia varia de forma natural,
#     mas reproduzível.
#
# Este é o "mock testável": o fluxo de produção é idêntico ao real; basta
# trocar o provider pela implementação real (factory) quando houver chaves.

from __future__ import annotations

import hashlib
import random
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from .base import LancamentoErp, LancamentoExtrato, SaldoBancario

CENTAVOS = Decimal("0.01")


def _seed(*partes: str) -> random.Random:
    """Random determinístico a partir de uma chave estável."""
    chave = "|".join(partes)
    h = hashlib.sha256(chave.encode("utf-8")).hexdigest()
    return random.Random(int(h[:16], 16))


def _dinheiro(valor: float) -> Decimal:
    return Decimal(str(round(valor, 2))).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


class FakeBankProvider:
    """Simula a API de um banco com saldo e extrato plausíveis."""

    def __init__(self, cnpj: str, nome_banco: str = "fake", *, semente_divergencia: bool = True):
        self.cnpj = cnpj or "00000000000000"
        self.nome_banco = nome_banco
        self._semente_divergencia = semente_divergencia

    def _saldo_base(self) -> Decimal:
        """Saldo "âncora" da empresa — estável no tempo (varia só com movimentos)."""
        rnd = _seed("base", self.cnpj)
        return _dinheiro(rnd.uniform(45_000, 4_800_000))

    async def obter_saldo(self) -> SaldoBancario:
        hoje = date.today()
        base = self._saldo_base()
        # Movimento líquido do dia (determinístico por empresa+dia)
        extrato = await self.obter_extrato(hoje, hoje)
        liquido = sum(
            (l.valor if l.tipo == "credito" else -l.valor for l in extrato),
            Decimal("0"),
        )
        return SaldoBancario(
            saldo=(base + liquido).quantize(CENTAVOS, rounding=ROUND_HALF_UP),
            moeda="BRL",
            atualizado_em=datetime.now(timezone.utc),
            raw={"fonte": "fake", "banco": self.nome_banco, "base": str(base)},
        )

    async def obter_extrato(self, inicio: date, fim: date) -> list[LancamentoExtrato]:
        rnd = _seed("extrato", self.cnpj, inicio.isoformat(), fim.isoformat())
        qtd = rnd.randint(2, 8)
        descricoes = [
            "PIX RECEBIDO", "PIX ENVIADO", "TED RECEBIDA", "PAGAMENTO BOLETO",
            "TARIFA BANCARIA", "TRANSFERENCIA INTERNA", "RECEBIMENTO CLIENTE",
            "PAGAMENTO FORNECEDOR",
        ]
        lancs: list[LancamentoExtrato] = []
        for i in range(qtd):
            tipo = "credito" if rnd.random() > 0.45 else "debito"
            lancs.append(
                LancamentoExtrato(
                    data=inicio,
                    valor=_dinheiro(rnd.uniform(120, 85_000)),
                    tipo=tipo,
                    descricao=rnd.choice(descricoes),
                    identificador=f"FAKE-{self.cnpj[-4:]}-{inicio.isoformat()}-{i}",
                    cnpj_contraparte=None,
                    raw={"fonte": "fake"},
                )
            )
        return lancs


class FakeOmieProvider:
    """Simula a posição esperada no ERP. Na maioria dos dias bate com o banco;
    de forma determinística, ~1 em 6 empresas/dia apresenta divergência —
    para exercitar os alertas de conciliação."""

    def __init__(self, cnpj: str, saldo_banco_ref: Decimal):
        self.cnpj = cnpj or "00000000000000"
        self._saldo_banco_ref = saldo_banco_ref

    async def obter_saldo_esperado(self, referencia: date) -> Decimal:
        rnd = _seed("omie", self.cnpj, referencia.isoformat())
        # ~17% dos casos: introduz divergência plausível
        if rnd.random() < 0.17:
            desvio = _dinheiro(rnd.uniform(150, 12_000))
            sinal = 1 if rnd.random() > 0.5 else -1
            return (self._saldo_banco_ref + sinal * desvio).quantize(
                CENTAVOS, rounding=ROUND_HALF_UP
            )
        return self._saldo_banco_ref

    async def obter_lancamentos(self, referencia: date) -> list[LancamentoErp]:
        """Espelha o extrato bancário do dia (mesma semente) para a conciliação
        encontrar matches. Omite 1 lançamento para simular um não-conciliado."""
        rnd = _seed("extrato", self.cnpj, referencia.isoformat(), referencia.isoformat())
        qtd = rnd.randint(2, 8)  # mesma sequência do FakeBankProvider.obter_extrato
        descricoes = [
            "PIX RECEBIDO", "PIX ENVIADO", "TED RECEBIDA", "PAGAMENTO BOLETO",
            "TARIFA BANCARIA", "TRANSFERENCIA INTERNA", "RECEBIMENTO CLIENTE",
            "PAGAMENTO FORNECEDOR",
        ]
        out: list[LancamentoErp] = []
        # decide deterministicamente qual índice omitir (ou nenhum, se -1)
        omitir_idx = _seed("omie_omit", self.cnpj, referencia.isoformat()).randint(-1, qtd - 1)
        for i in range(qtd):
            tipo = "credito" if rnd.random() > 0.45 else "debito"
            valor = _dinheiro(rnd.uniform(120, 85_000))
            _ = rnd.choice(descricoes)  # mantém a sequência igual à do banco
            if i == omitir_idx:
                continue
            out.append(
                LancamentoErp(
                    data=referencia,
                    valor=valor,
                    descricao=("Conta a receber" if tipo == "credito" else "Conta a pagar"),
                    numero_documento=f"OMIE-{self.cnpj[-4:]}-{referencia.isoformat()}-{i}",
                    id_omie=abs(hash((self.cnpj, referencia.isoformat(), i))) % 10_000_000,
                    data_vencimento=referencia,
                    status="aberto",
                )
            )
        return out
