// frontend/src/types/tarefa.ts
// Tipos de tarefas (Kanban) do Portal TRK

import type { UserBrief } from './auth'

export type TarefaStatus = 'todo' | 'doing' | 'done'
export type TarefaPrioridade = 'baixa' | 'normal' | 'alta' | 'urgente'

export interface Tarefa {
  id: string
  titulo: string
  descricao: string | null
  status: TarefaStatus
  prioridade: TarefaPrioridade
  prazo: string | null
  criador: UserBrief | null
  responsavel: UserBrief | null
  empresa_nome: string | null
  esta_atrasada: boolean
  created_at: string
  done_at: string | null
}

export interface TarefaCreate {
  titulo: string
  descricao?: string
  prioridade?: TarefaPrioridade
  prazo?: string
  atribuido_a?: string
  empresa_id?: string
}
