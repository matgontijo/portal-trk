// frontend/src/pages/Rotinas.tsx
import { useState, useEffect } from 'react'
import { CheckSquare, Calendar, ChevronDown, ChevronRight, Check, Play, Pause } from 'lucide-react'
import api from '../services/api'
import { Badge } from '../components/common/Badge'
import { useAuthStore } from '../store/authStore'
import { CATEGORIA_CORES } from '../utils/constants'
import { RotinaBuilderModal } from '../components/rotinas/RotinaBuilderModal'

const renderTextWithLinks = (text: string) => {
  if (!text) return ''
  const urlRegex = /(https?:\/\/[^\s]+)/g
  const parts = text.split(urlRegex)
  return parts.map((part, i) => {
    if (part.match(urlRegex)) {
      return (
        <a 
          key={i} 
          href={part.startsWith('http') ? part : `https://${part}`} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="text-primary-600 dark:text-primary-400 hover:underline break-words"
          onClick={(e) => e.stopPropagation()}
        >
          {part}
        </a>
      )
    }
    return <span key={i}>{part}</span>
  })
}

export function Rotinas() {
  const { user } = useAuthStore()
  const [rotinas, setRotinas] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list')
  
  const [isBuilderOpen, setIsBuilderOpen] = useState(false)
  const [rotinaEdit, setRotinaEdit] = useState<any>(null)

  useEffect(() => {
    carregarRotinas()
  }, [])

  const carregarRotinas = async () => {
    try {
      const endpoint = user?.role === 'funcionario' ? '/rotinas/hoje' : '/rotinas'
      const response = await api.get(endpoint)
      setRotinas(response.data)
      
      // Auto expandir a primeira rotina se for funcionário
      if (user?.role === 'funcionario' && response.data.length > 0) {
        setExpandedId(response.data[0].id)
      }
    } catch (error) {
      console.error('Erro ao carregar rotinas', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateProgresso = async (blocoId: string, updates: { is_done?: boolean, valor_texto?: string, arquivo_url?: string, arquivo_nome?: string }) => {
    try {
      // Otimista
      setRotinas(prev => prev.map(r => {
        const bloco = r.blocos.find((b: any) => b.id === blocoId)
        if (!bloco) return r

        const wasDone = bloco.progresso?.is_done || false
        const isNowDone = updates.is_done !== undefined ? updates.is_done : wasDone
        
        const newBlocos = r.blocos.map((b: any) => {
          if (b.id === blocoId) {
            return {
              ...b,
              progresso: {
                ...b.progresso,
                ...updates,
                is_done: isNowDone
              }
            }
          }
          return b
        })

        return {
          ...r,
          blocos: newBlocos,
          blocos_concluidos: r.blocos_concluidos + (isNowDone && !wasDone ? 1 : (!isNowDone && wasDone ? -1 : 0))
        }
      }))

      await api.put('/rotinas/progresso', {
        bloco_id: blocoId,
        ...updates
      })
    } catch (error) {
      carregarRotinas()
    }
  }

  const handleEdit = (rotina: any, e: React.MouseEvent) => {
    e.stopPropagation()
    setRotinaEdit(rotina)
    setIsBuilderOpen(true)
  }

  const handleSeed = async () => {
    try {
      setIsLoading(true)
      await api.post('/rotinas/seed')
      await carregarRotinas()
    } catch (e) {
      alert('Erro ao gerar rotinas padrão')
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Deseja realmente arquivar esta rotina?')) return
    try {
      await api.delete(`/rotinas/${id}`)
      carregarRotinas()
    } catch {
      alert('Erro ao arquivar rotina')
    }
  }

  if (isLoading) {
    return <div className="animate-pulse h-96 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            Rotinas Diárias
          </h1>
          <p className="text-slate-500 mt-1">
            {user?.role === 'funcionario' ? 'Seu checklist de operações para hoje.' : 'Gerenciamento de rotinas operacionais.'}
          </p>
        </div>

        {user?.role !== 'funcionario' && (
          <div className="flex items-center gap-3">
            <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
              <button 
                onClick={() => setViewMode('list')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${viewMode === 'list' ? 'bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 hover:text-slate-700'}`}
              >
                Lista
              </button>
              <button 
                onClick={() => setViewMode('calendar')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${viewMode === 'calendar' ? 'bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 hover:text-slate-700'}`}
              >
                Grade Semanal
              </button>
            </div>
            <button onClick={() => { setRotinaEdit(null); setIsBuilderOpen(true) }} className="btn-primary">
              Nova Rotina
            </button>
          </div>
        )}
      </div>

      {viewMode === 'calendar' && user?.role !== 'funcionario' ? (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          {[
            { num: 1, nome: 'Segunda-feira' },
            { num: 2, nome: 'Terça-feira' },
            { num: 3, nome: 'Quarta-feira' },
            { num: 4, nome: 'Quinta-feira' },
            { num: 5, nome: 'Sexta-feira' },
          ].map(dia => {
            const rotinasDoDia = rotinas.filter(r => r.dias_semana.includes(dia.num))
            return (
              <div key={dia.num} className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-4 border border-slate-200 dark:border-slate-800">
                <h3 className="font-bold text-center text-slate-700 dark:text-slate-300 mb-4 pb-2 border-b border-slate-200 dark:border-slate-800">
                  {dia.nome}
                </h3>
                <div className="space-y-3">
                  {rotinasDoDia.map(r => {
                    const coresCategoria = CATEGORIA_CORES[r.categoria] || CATEGORIA_CORES.geral
                    return (
                      <div 
                        key={r.id} 
                        className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm cursor-pointer hover:border-primary-500 transition-colors" 
                        onClick={(e) => handleEdit(r, e)}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <div className={`flex-shrink-0 w-2 h-2 rounded-full ${coresCategoria.dot}`}></div>
                          <span className="font-semibold text-sm truncate">{r.nome}</span>
                        </div>
                        <div className="text-xs text-slate-500">
                          {r.total_blocos} fases de operação
                        </div>
                      </div>
                    )
                  })}
                  {rotinasDoDia.length === 0 && (
                    <div className="text-center text-xs text-slate-400 py-4">Livre</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
      <div className="space-y-4">
        {rotinas.length === 0 ? (
          <div className="card p-12 text-center flex flex-col items-center">
            <Calendar className="w-12 h-12 text-slate-300 dark:text-slate-700 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhuma rotina configurada</h3>
            <p className="text-slate-500 mb-6 max-w-md text-center">Você não tem rotinas atribuídas. Organize o trabalho da sua equipe criando checklists diários.</p>
            {user?.role !== 'funcionario' && (
              <button onClick={handleSeed} className="btn-secondary">
                Gerar Rotinas Iniciais Padrão
              </button>
            )}
          </div>
        ) : (
          rotinas.map((rotina) => {
            const isExpanded = expandedId === rotina.id
            const percentual = rotina.total_blocos > 0 ? (rotina.blocos_concluidos / rotina.total_blocos) * 100 : 0
            const concluida = percentual === 100
            const coresCategoria = CATEGORIA_CORES[rotina.categoria] || CATEGORIA_CORES.geral

            return (
              <div key={rotina.id} className="card overflow-hidden transition-all duration-200">
                {/* Header Collapsible */}
                <div 
                  className="px-5 py-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50 flex items-center gap-4 select-none"
                  onClick={() => setExpandedId(isExpanded ? null : rotina.id)}
                >
                  <div className="flex-shrink-0 text-slate-400">
                    {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                  </div>

                  <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 min-w-0">
                    <div className="flex items-center gap-2 truncate">
                      <div className={`w-2 h-2 rounded-full ${coresCategoria.dot}`}></div>
                      <span className={`font-semibold truncate ${concluida ? 'text-slate-500 line-through' : ''}`}>
                        {rotina.nome}
                      </span>
                    </div>

                    <div className="hidden md:flex items-center gap-2 ml-auto">
                      {user?.role !== 'funcionario' && (
                        <>
                          {rotina.status === 'ativa' && <Badge variant="success" icon={<Play className="w-3 h-3" />}>Ativa</Badge>}
                          {rotina.status === 'pausada' && <Badge variant="warning" icon={<Pause className="w-3 h-3" />}>Pausada</Badge>}
                          <button onClick={(e) => handleEdit(rotina, e)} className="text-xs text-neutral-500 hover:text-neutral-900 border border-neutral-200 px-2 py-1 rounded-md ml-2 transition-colors">Editar</button>
                          <button onClick={(e) => handleDelete(rotina.id, e)} className="text-xs text-red-500 hover:text-red-700 border border-red-100 hover:bg-red-50 px-2 py-1 rounded-md transition-colors">Arquivar</button>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar Mini */}
                  <div className="w-24 sm:w-32 flex-shrink-0 flex items-center gap-3">
                    <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-500 ${concluida ? 'bg-success-500' : 'bg-primary-500'}`}
                        style={{ width: `${percentual}%` }}
                      />
                    </div>
                    <span className={`text-xs font-medium w-8 text-right ${concluida ? 'text-success-600' : 'text-slate-500'}`}>
                      {rotina.blocos_concluidos}/{rotina.total_blocos}
                    </span>
                  </div>
                </div>

                {/* Body (Expanded) */}
                {isExpanded && (
                  <div className="border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 p-5">
                    {rotina.descricao && (
                      <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 whitespace-pre-wrap">{renderTextWithLinks(rotina.descricao)}</p>
                    )}

                    <div className="space-y-3">
                      {rotina.blocos.map((bloco: any) => {
                        const done = bloco.progresso?.is_done || false
                        const valor = bloco.progresso?.valor_texto || ''
                        const arquivo = bloco.progresso?.arquivo_url || ''
                        
                        return (
                          <div 
                            key={bloco.id}
                            className={`flex flex-col gap-3 p-4 rounded-xl border transition-all duration-300 ${
                              done 
                                ? 'bg-white dark:bg-slate-800 border-success-200 dark:border-success-900/30 opacity-75 shadow-sm' 
                                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              {/* Bloco Checkbox */}
                              {user?.role === 'funcionario' && (
                                <button 
                                  className={`mt-0.5 flex-shrink-0 w-6 h-6 rounded-md flex items-center justify-center transition-all duration-300 border-2 ${
                                    done 
                                      ? 'bg-success-500 border-success-500 text-white shadow-inner scale-105' 
                                      : 'border-slate-300 dark:border-slate-600 hover:border-neutral-900 bg-transparent'
                                  }`}
                                  onClick={() => handleUpdateProgresso(bloco.id, { is_done: !done })}
                                >
                                  {done && <Check className="w-4 h-4 animate-scale-in" />}
                                </button>
                              )}

                              <div className="flex-1 min-w-0">
                                <p className={`text-sm font-semibold transition-colors duration-300 ${done ? 'text-slate-500 line-through' : 'text-slate-900 dark:text-slate-200'}`}>
                                  {renderTextWithLinks(bloco.label)} {bloco.is_required && <span className="text-red-500 ml-1">*</span>}
                                </p>
                                
                                {/* Inputs Específicos para Funcionário (só exibe se não estiver concluído ou se já tiver valor) */}
                                {user?.role === 'funcionario' && bloco.tipo === 'text_short' && (!done || valor) && (
                                  <div className="mt-3">
                                    <input 
                                      type="text" 
                                      className="input text-sm" 
                                      placeholder="Sua resposta..." 
                                      value={valor}
                                      onChange={(e) => handleUpdateProgresso(bloco.id, { valor_texto: e.target.value })}
                                      disabled={done}
                                    />
                                  </div>
                                )}

                                {user?.role === 'funcionario' && bloco.tipo === 'file_upload' && (!done || arquivo) && (
                                  <div className="mt-3 flex items-center gap-2">
                                    <input 
                                      type="url" 
                                      className="input text-sm flex-1" 
                                      placeholder="Cole o link do Drive / Arquivo aqui..." 
                                      value={arquivo}
                                      onChange={(e) => handleUpdateProgresso(bloco.id, { arquivo_url: e.target.value, arquivo_nome: 'Anexo' })}
                                      disabled={done}
                                    />
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
      )}

      {isBuilderOpen && (
        <RotinaBuilderModal 
          rotinaEdit={rotinaEdit} 
          onClose={() => { setIsBuilderOpen(false); setRotinaEdit(null) }} 
          onSave={() => { setIsBuilderOpen(false); setRotinaEdit(null); carregarRotinas() }} 
        />
      )}
    </div>
  )
}
