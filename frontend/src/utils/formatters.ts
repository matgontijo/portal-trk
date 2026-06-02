// frontend/src/utils/formatters.ts
// Formatadores de dados do Portal TRK.
// Moeda BRL, datas pt-BR, CNPJ, tempo relativo.

/**
 * Formata valor como moeda brasileira (R$).
 */
export function formatarMoeda(valor: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor)
}

/**
 * Formata data completa em pt-BR.
 */
export function formatarData(data: string | Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(data))
}

/**
 * Formata data e hora em pt-BR.
 */
export function formatarDataHora(data: string | Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(data))
}

/**
 * Formata hora (HH:MM).
 */
export function formatarHora(data: string | Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(data))
}

/**
 * Formata CNPJ: XX.XXX.XXX/XXXX-XX
 */
export function formatarCNPJ(cnpj: string): string {
  const num = cnpj.replace(/\D/g, '')
  return num.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

/**
 * Tempo relativo (há X minutos, há X horas, etc.)
 */
export function tempoRelativo(data: string | Date): string {
  const agora = new Date()
  const d = new Date(data)
  const diffMs = agora.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHoras = Math.floor(diffMin / 60)
  const diffDias = Math.floor(diffHoras / 24)

  if (diffMin < 1) return 'agora mesmo'
  if (diffMin < 60) return `há ${diffMin} min`
  if (diffHoras < 24) return `há ${diffHoras}h`
  if (diffDias < 7) return `há ${diffDias} dia${diffDias > 1 ? 's' : ''}`
  return formatarData(d)
}

/**
 * Dias da semana abreviados.
 */
export const DIAS_SEMANA = ['', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex']
export const DIAS_SEMANA_FULL = ['', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
