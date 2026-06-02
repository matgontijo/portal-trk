// frontend/src/types/common.ts
// Tipos comuns reutilizáveis

export interface DashboardKPIs {
  total_em_caixa: number
  a_pagar_hoje: number
  a_pagar_semana: number
  em_atraso: number
  empresas_com_divergencia: number
  total_empresas: number
}

export interface Notificacao {
  id: string
  tipo: string
  titulo: string
  mensagem: string | null
  link_acao: string | null
  lida: boolean
  created_at: string
}

export interface EquipeProgresso {
  user_id: string
  user_name: string
  total: number
  concluidos: number
  percentual: number
}
