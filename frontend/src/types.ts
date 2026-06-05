export type Acao = 'ver' | 'editar'
export type PermMap = Record<string, { ver: boolean; editar: boolean }>

export interface Usuario {
  id: string
  nome: string
  email: string
  cargo: 'diretor' | 'gestor' | 'colaborador'
  departamento_id: string | null
  departamento_nome: string | null
  avatar_cor: string
  ativo: boolean
  created_at: string
}

export interface Modulo {
  key: string
  label: string
  icone: string
  grupo: string
  descricao: string
  sensivel: boolean
}

export interface Departamento {
  id: string
  nome: string
  cor: string
  icone: string
  descricao: string | null
  permissoes_padrao: PermMap
  total_usuarios: number
}

export interface Sessao {
  token: string
  usuario: Usuario
  permissoes: PermMap
  modulos_acessiveis: string[]
}
