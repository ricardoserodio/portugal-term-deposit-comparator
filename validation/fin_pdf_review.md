# FIN/PDF Validation Review

Generated at: 2026-05-05 23:07:52

This document summarizes the fields extracted from official FIN/PDF documents. The extraction is semi-automatic and should be reviewed before updating the dataset.

---

## 1. Banco de Investimento Global — Super Depósito 3 Meses

**Source file:** `incoming_fin/FIN_PTDP2025074.pdf`

**Parser used:** Banco BiG specific parser

**Document version:** Not detected

**Extraction confidence:** Medium

**Manual review required:** Yes - TANB requires visual confirmation

### Extracted Fields

- **Bank:** Banco de Investimento Global
- **Product:** Super Depósito 3 Meses
- **Maturity / Prazo:** MOVIMENTAÇÃO ANTECIPADA MOEDA RENOVAÇÃO MONTANTE REFORÇOS REGIME DE CAPITALIZAÇÃO
- **TANB:** Requires visual confirmation
- **Minimum Amount / Montante mínimo:** Not detected
- **Maximum Amount / Montante máximo:** 100.000 EUR
- **Early Withdrawal / Mobilização antecipada:** Requires manual confirmation
- **Renewal / Renovação:** Não renovável
- **Tax Regime / Regime fiscal:** OUTRAS CONDIÇÕES GARANTIA DE CAPITAL Não renovável. FICHA DE INFORMAÇÃO NORMALIZADA FUNDO DE GARANTIA DE DEPÓSITOS ; S.A. ASSINATURAS DE TODOS OS TITULARES (CONFORME DOC. DE IDENTIFICAÇÃO NA FICHA PARTICULAR)

### Human Validation

***Human Decision:** Validated

Use one of: `Validated`, `Update dataset`, `Keep under review`, `Source unavailable`

**Validator Notes:** FIN/PDF oficial do Banco BiG consultada. Produto identificado como “SUPER DEPÓSITO 3%” / Super Depósito 3 Meses, código PTDP2025074. Prazo confirmado: 3 meses. TANB confirmada: 3,0000%. TANL para pessoas singulares: 2,1600%. TANL para pessoas coletivas: 2,2500%. Montante mínimo confirmado: EUR 5.000. Montante máximo confirmado: EUR 50.000. Movimentação antecipada permitida apenas total, com perda de 85% dos juros. Renovação: não renovável. Moeda: EUR. Condições de acesso: válido apenas para novos clientes com novos recursos e durante os primeiros 3 meses como cliente, limitado a uma constituição por morada registada no BiG. Validade das condições: 06-05-2026. Dados confirmados manualmente na FIN oficial; o parser identificou parcialmente os campos, mas a validação final foi humana.

Example:

> FIN oficial consultada. Produto, prazo, TANB, montante mínimo/máximo, mobilização antecipada e renovação confirmados. Valores coincidem com o dataset.

### Extracted Text Preview

```text
DESIGNAÇÃO CONDIÇÕES DE A CESSO MO DALIDADE PRAZO MOVIMENTAÇÃO ANTECIPADA MOEDA RENOVAÇÃO MONTANTE REFORÇOS REGIME DE CAPITALIZAÇÃO TAXA DE REMUNERAÇÃO CÁLCULO DE JUROS PAGAMENTO DE JUROS REGIME FISCAL OUTRAS CONDIÇÕES GARANTIA DE CAPITAL Não renovável. FICHA DE INFORMAÇÃO NORMALIZADA FUNDO DE GARANTIA DE DEPÓSITOS ; S.A. ASSINATURAS DE TODOS OS TITULARES (CONFORME DOC. DE IDENTIFICAÇÃO NA FICHA PARTICULAR) INSTITUIÇÃO DEPOSITÁRIA VALIDADE DAS CONDIÇÕES Banco de Investimento Global, S.A. www.big.pt tel: 21 330 53 00 email: apoio@big.pt Condições válidas desde, até à emissão de novas condições. relacionadas com a sua situação financeira. O Fundo de Garantia de Depósitos garante o reembolso até ao valor máximo de 100.000 EUR por cada depositante. No cálculo do valor do depósito de cada depositante considera-se o valor do conjunto das contas de depósito na data em que se verificou a indisponibilidade de pagamento, incluindo os juros e, para o saldo dos depósitos em moeda estrangeira, convertendo em EUR, ao câmbio da referida data. Para informações complementares consulte o endereço http://www.fgd.pt. FICHA DE INFORMAÇÃO NORMALIZADA NÚMERO DE CONTA DATA
```

---

