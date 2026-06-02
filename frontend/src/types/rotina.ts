// frontend/src/types/rotina.ts
// Tipos de rotinas do Portal TRK

import type { UserBrief } from './auth'

export type BlocoTipo = 
  | 'checkbox' | 'text_short' | 'text_long' | 'link'
  | 'section_header' | 'file_upload' | 'balance_indicator' | 'date_field'

export type RotinaCategoria = 'banco' | 'omie' | 'drive' | 'urgente' | 'pipe' | 'geral'
export type RotinaStatus = 'ativa' | 'pausada' | 'arquivada'

export interface Progresso {
  id: string
  is_done: boolean
  valor_texto: string | null
  arquivo_url: string | null
  arquivo_nome: string | null
  done_at: string | null
}

export interface Bloco {
  id: string
  tipo: BlocoTipo
  label: string
  config: Record<string, unknown>
  posicao: number
  is_required: boolean
  progresso: Progresso | null
}

export interface Rotina {
  id: string
  nome: string
  descricao: string | null
  dias_semana: number[]
  alertas: string[]
  categoria: RotinaCategoria
  status: RotinaStatus
  blocos: Bloco[]
  atribuidos: UserBrief[]
  total_blocos: number
  blocos_concluidos: number
  created_at: string
}

export interface ProgressoUpdate {
  bloco_id: string
  is_done?: boolean
  valor_texto?: string
  arquivo_url?: string
  arquivo_nome?: string
}
