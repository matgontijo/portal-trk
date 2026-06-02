// frontend/src/utils/constants.ts
// Constantes do Portal TRK

export const CATEGORIA_CORES: Record<string, { bg: string; text: string; dot: string }> = {
  banco:   { bg: 'bg-primary-100 dark:bg-primary-900/30', text: 'text-primary-700 dark:text-primary-400', dot: 'bg-primary-500' },
  omie:    { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400', dot: 'bg-blue-500' },
  drive:   { bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
  urgente: { bg: 'bg-danger-100 dark:bg-danger-900/30', text: 'text-danger-700 dark:text-danger-400', dot: 'bg-danger-500' },
  pipe:    { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' },
  geral:   { bg: 'bg-slate-100 dark:bg-slate-800', text: 'text-slate-700 dark:text-slate-400', dot: 'bg-slate-500' },
}

export const PRIORIDADE_CORES: Record<string, { bg: string; text: string }> = {
  baixa:   { bg: 'bg-slate-100 dark:bg-slate-800', text: 'text-slate-600 dark:text-slate-400' },
  normal:  { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400' },
  alta:    { bg: 'bg-warning-100 dark:bg-warning-900/30', text: 'text-warning-700 dark:text-warning-400' },
  urgente: { bg: 'bg-danger-100 dark:bg-danger-900/30', text: 'text-danger-700 dark:text-danger-400' },
}

export const BANCO_LOGOS: Record<string, { nome: string; cor: string }> = {
  santander: { nome: 'Santander', cor: '#EC0000' },
  inter:     { nome: 'Inter', cor: '#FF7A00' },
  bradesco:  { nome: 'Bradesco', cor: '#CC092F' },
}

export const DIVERGENCIA_LABELS: Record<string, string> = {
  sem_divergencia: 'Sem divergência',
  lancamento_nao_identificado: 'Lançamento não identificado',
  pagamento_nao_processado: 'Pagamento não processado',
  valor_divergente: 'Valor divergente',
  data_divergente: 'Data divergente',
  multiplas: 'Múltiplas divergências',
}
