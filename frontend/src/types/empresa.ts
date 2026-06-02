// frontend/src/types/empresa.ts
// Tipos de empresa do Portal TRK

import type { UserBrief } from './auth'

export type BancoTipo = 'santander' | 'inter' | 'bradesco'
export type EmpresaGrupo = 'trk' | 'bpo'
export type TipoDivergencia = 
  | 'sem_divergencia' 
  | 'lancamento_nao_identificado' 
  | 'pagamento_nao_processado'
  | 'valor_divergente' 
  | 'data_divergente' 
  | 'multiplas'

export interface SaldoResumo {
  saldo_banco: number
  saldo_omie: number
  delta: number
  tem_divergencia: boolean
  tipo_divergencia: TipoDivergencia
  synced_at: string | null
}

export interface Empresa {
  id: string
  nome: string
  cnpj: string
  banco: BancoTipo
  agencia: string | null
  conta: string | null
  grupo: EmpresaGrupo
  responsavel: UserBrief | null
  is_active: boolean
  saldo_atual: SaldoResumo | null
  created_at: string
}

export interface SaldoHistorico {
  data_referencia: string
  saldo_banco: number
  saldo_omie: number
  delta: number
  tem_divergencia: boolean
}
