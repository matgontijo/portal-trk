// ════════════════════════════════════════════════════════
// DATA — Portal Grupo TRK v2.0
// All company data, routines, and constants
// ════════════════════════════════════════════════════════

const TODAS_EMPRESAS = [
  // GRUPO TRK
  { id: "cmf", nome: "CMF Consultoria Imobiliária LTDA", cnpj: "59.954.067/0001-08", resp: "tarik", grupo: "trk", banco: "Santander", ag: "0082", conta: "13007832-8" },
  { id: "rr", nome: "RR Participações LTDA", cnpj: "43.363.892/0001-06", resp: "rafael", grupo: "trk", banco: "Inter", ag: "00019", conta: "18269393-7" },
  { id: "tarifa", nome: "Tarifa Participações LTDA", cnpj: "43.361.973/0001-69", resp: "tarik", grupo: "trk", banco: "Santander", ag: "0082", conta: "13007833-5" },
  { id: "trkalug", nome: "TRK Administradora de Imóveis LTDA (Aluguel)", cnpj: "22.414.542/0001-43", resp: "rafael", grupo: "trk", banco: "Santander", ag: "3067", conta: "13002585-0" },
  { id: "trkempr", nome: "TRK Administradora de Imóveis LTDA (Empresa)", cnpj: "22.414.542/0001-43", resp: "rafael", grupo: "trk", banco: "Santander", ag: "3067", conta: "13002586-7" },
  { id: "trkcons", nome: "TRK Consultoria Imobiliária LTDA", cnpj: "22.414.516/0001-15", resp: "rafael", grupo: "trk", banco: "Santander", ag: "3067", conta: "13002587-4" },
  // BPO
  { id: "acao", nome: "Ação Consultoria e Empreendimentos Imobiliários Ltda", cnpj: "02.716.116/0001-57", resp: "rafael", grupo: "bpo", banco: "Inter", ag: "2001-9", conta: "25035224-9" },
  { id: "ativus", nome: "Ativus Participações S/A", cnpj: "15.017.538/0001-86", resp: "rafael", grupo: "bpo", banco: "Bradesco", ag: "2837", conta: "1290-9" },
  { id: "audax", nome: "Audax Participações LTDA", cnpj: "58.050.747/0001-34", resp: "rafael", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13007634-0" },
  { id: "autor", nome: "Autor Participações S/A", cnpj: "40.358.115/0001-77", resp: "rafael", grupo: "bpo", banco: "Inter", ag: "2001-9", conta: "17814455-0" },
  { id: "bird", nome: "Bird Partners LTDA", cnpj: "58.266.791/0001-86", resp: "rafael", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13007627-8" },
  { id: "eleven", nome: "Eleven & One Partners LTDA", cnpj: "61.037.183/0001-04", resp: "tarik", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13007946-0" },
  { id: "esfera", nome: "Esfera Arena e Negócios Spe LTDA", cnpj: "43.557.445/0001-80", resp: "rafael", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13007438-6" },
  { id: "gibraltar", nome: "Gibraltar Investimentos Imobiliários Part. S/A", cnpj: "15.053.780/0001-05", resp: "tarik", grupo: "bpo", banco: "Bradesco", ag: "7980", conta: "0004869-0" },
  { id: "golf", nome: "Golf Participações e Investimentos Imobiliário LTDA", cnpj: "32.129.155/0001-19", resp: "rafael", grupo: "bpo", banco: "Inter", ag: "0001", conta: "26406840-8" },
  { id: "kfinserv", nome: "K Finserv Serviços Financeiros LTDA", cnpj: "60.503.068/0001-15", resp: "rafael", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13007876-8" },
  { id: "kconsult", nome: "K Consultoria e Marketing Imobiliário LTDA", cnpj: "50.585.739/0001-80", resp: "rafael", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13006838-1" },
  { id: "malaga", nome: "Malaga Participação LTDA", cnpj: "55.370.214/0001-41", resp: "tarik", grupo: "bpo", banco: "Santander", ag: "0082", conta: "13007309-3" },
  { id: "marazul", nome: "Mar Azul Empreendimentos Imobiliários LTDA", cnpj: "42.696.860/0001-51", resp: "tarik", grupo: "bpo", banco: "Santander", ag: "4515", conta: "13006736-3" },
  { id: "quintas", nome: "Quintas Empreendimentos e Participações S/A", cnpj: "14.796.720/0001-10", resp: "tarik", grupo: "bpo", banco: "Inter", ag: "0019", conta: "235561754" },
  { id: "resgard", nome: "Residencial Garden Empreendimentos Imobiliários LTDA", cnpj: "43.301.143/0001-46", resp: "rafael", grupo: "bpo", banco: "Santander", ag: "0082", conta: "130063355" },
  { id: "roi", nome: "ROI Participações e Investimentos S/A", cnpj: "18.942.643/0001-10", resp: "rafael", grupo: "bpo", banco: "Inter", ag: "0001-9", conta: "239352041" },
  { id: "school", nome: "School Participações Investimentos Imobiliário LTDA", cnpj: "31.482.587/0001-46", resp: "rafael", grupo: "bpo", banco: "Inter", ag: "0001", conta: "25299377-2" },
];

const BPO_EMPRESAS = TODAS_EMPRESAS.filter(e => e.grupo === "bpo");

const ROTINAS = {
  0: { label: "Domingo", alertas: [], blocos: [] },
  1: {
    label: "Segunda-feira", alertas: [], blocos: [
      { cat: "banco", label: "Manhã — Extratos", itens: ["Tirar extrato Inter e conciliar no Omie", "Tirar extrato Santander e conciliar no Omie", "Tirar extrato Bradesco e conciliar no Omie"] },
      { cat: "omie", label: "Preparação Rafael (BPO)", itens: ["Coletar NFs das empresas do Rafael", "Coletar boletos das empresas do Rafael", "Lançar pagamentos no Omie empresa por empresa", "Gerar arquivo de remessa"] },
      { cat: "drive", label: "Drive — Pasta do dia", itens: ["Criar pasta: Empresa → 2026 → mês → data", "Subir NFs no Drive", "Subir boletos no Drive", "Subir arquivo de remessa no Drive"] },
      { cat: "banco", label: "Banco", itens: ["Enviar remessa ao banco", "Confirmar recebimento da remessa pelo banco"] },
    ]
  },
  2: {
    label: "Terça-feira", alertas: ["💳 Pagamentos das empresas do Rafael executados hoje"], blocos: [
      { cat: "banco", label: "Manhã — Extratos", itens: ["Tirar extrato Inter e conciliar no Omie", "Tirar extrato Santander e conciliar no Omie", "Tirar extrato Bradesco e conciliar no Omie"] },
      { cat: "omie", label: "Confirmação Rafael", itens: ["Confirmar execução dos pagamentos no banco", "Baixar comprovantes bancários", "Confirmar liquidação no Omie"] },
      { cat: "drive", label: "Drive", itens: ["Subir comprovantes no Drive"] },
    ]
  },
  3: {
    label: "Quarta-feira", alertas: ["⚠️ DEADLINE: Lançar pipes do Vila Raio no Pipefy até fim do dia"], blocos: [
      { cat: "banco", label: "Manhã — Extratos", itens: ["Tirar extrato Inter e conciliar no Omie", "Tirar extrato Santander e conciliar no Omie", "Tirar extrato Bradesco e conciliar no Omie"] },
      { cat: "urgente", label: "⚠️ Deadline Vila Raio", itens: ["Lançar todos os pipes do Vila Raio no Pipefy", "Revisar aprovações pendentes no Pipefy"] },
      { cat: "omie", label: "Preparação Tárik (BPO)", itens: ["Coletar NFs das empresas do Tárik", "Coletar boletos das empresas do Tárik", "Lançar pagamentos no Omie empresa por empresa", "Gerar arquivo de remessa"] },
      { cat: "drive", label: "Drive — Pasta do dia", itens: ["Criar pasta: Empresa → 2026 → mês → data", "Subir NFs no Drive", "Subir boletos no Drive", "Subir arquivo de remessa no Drive"] },
      { cat: "banco", label: "Banco", itens: ["Enviar remessa ao banco", "Confirmar recebimento da remessa"] },
    ]
  },
  4: {
    label: "Quinta-feira", alertas: [], blocos: [
      { cat: "banco", label: "Manhã — Extratos", itens: ["Tirar extrato Inter e conciliar no Omie", "Tirar extrato Santander e conciliar no Omie", "Tirar extrato Bradesco e conciliar no Omie"] },
      { cat: "omie", label: "Confirmação Tárik", itens: ["Confirmar execução dos pagamentos Tárik no banco", "Baixar comprovantes Tárik", "Confirmar liquidação no Omie"] },
      { cat: "drive", label: "Drive", itens: ["Subir comprovantes Tárik no Drive"] },
      { cat: "pipe", label: "Pipefy — Vila Raio", itens: ["Preparar pagamentos Vila Raio no Siegen", "Revisar pipes aprovados no Pipefy"] },
    ]
  },
  5: {
    label: "Sexta-feira", alertas: ["💸 Pagamento Vila Raio executado hoje no Siegen"], blocos: [
      { cat: "banco", label: "Manhã — Extratos", itens: ["Tirar extrato Inter e conciliar no Omie", "Tirar extrato Santander e conciliar no Omie", "Tirar extrato Bradesco e conciliar no Omie"] },
      { cat: "pipe", label: "Vila Raio — Siegen", itens: ["Executar pagamentos no Siegen", "Baixar comprovantes Vila Raio", "Confirmar liquidação no Siegen"] },
      { cat: "drive", label: "Drive", itens: ["Subir comprovantes Vila Raio no Drive"] },
    ]
  },
  6: { label: "Sábado", alertas: [], blocos: [] },
};

const DRIVE_DOCS = ["NF(s)", "Boleto(s)", "Remessa", "Comprovante(s)"];
