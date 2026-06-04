// frontend/src/pages/PipeBoard.tsx
// Board kanban de um pipe: colunas = fases, cards movíveis (◄ ►), SLA e criação.

import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, ChevronLeft, ChevronRight, Plus, Trash2, Clock, Building2, User, X,
} from 'lucide-react'
import api from '../services/api'
import { formatarMoeda } from '../utils/formatters'

interface Fase { id: string; nome: string; cor: string; ordem: number; is_final: boolean; sla_horas: number | null }
interface Card {
  id: string; fase_id: string; titulo: string; sla_status: string
  responsavel_nome: string | null; empresa_nome: string | null; valor_monetario: number | null
}
interface Coluna { fase: Fase; cards: Card[] }
interface Board { pipe: { id: string; nome: string; cor: string }; colunas: Coluna[] }

const SLA_META: Record<string, string> = {
  ok: 'text-success-600', atencao: 'text-warning-600', estourado: 'text-danger-600',
}

export function PipeBoard() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [board, setBoard] = useState<Board | null>(null)
  const [loading, setLoading] = useState(true)
  const [novoCardFase, setNovoCardFase] = useState<string | null>(null)
  const [titulo, setTitulo] = useState('')

  const carregar = useCallback(async () => {
    try { setBoard((await api.get<Board>(`/pipes/${id}/board`)).data) }
    catch (e) { console.error(e) } finally { setLoading(false) }
  }, [id])
  useEffect(() => { carregar() }, [carregar])

  const fasesOrdenadas = board?.colunas.map(c => c.fase) ?? []

  const mover = async (card: Card, dir: -1 | 1) => {
    const idx = fasesOrdenadas.findIndex(f => f.id === card.fase_id)
    const destino = fasesOrdenadas[idx + dir]
    if (!destino) return
    await api.patch(`/pipes/cards/${card.id}/mover`, { fase_id: destino.id })
    carregar()
  }

  const criarCard = async (faseId: string) => {
    if (!titulo.trim()) return
    await api.post(`/pipes/${id}/cards`, { titulo, fase_id: faseId })
    setTitulo(''); setNovoCardFase(null); carregar()
  }

  const removerCard = async (card: Card) => {
    if (!confirm(`Excluir o card "${card.titulo}"?`)) return
    await api.delete(`/pipes/cards/${card.id}`); carregar()
  }

  if (loading) return <div className="h-64 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />
  if (!board) return <div className="card p-8 text-center text-slate-500">Pipe não encontrado.</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/pipes')} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <span className="w-3 h-3 rounded-full" style={{ background: board.pipe.cor }} />
        <h1 className="text-2xl font-bold tracking-tight">{board.pipe.nome}</h1>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-4">
        {board.colunas.map(({ fase, cards }, colIdx) => (
          <div key={fase.id} className="flex-shrink-0 w-72">
            <div className="flex items-center justify-between mb-2 px-1">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: fase.cor }} />
                <h3 className="font-semibold text-sm">{fase.nome}</h3>
                <span className="text-xs text-slate-400">{cards.length}</span>
              </div>
              {fase.sla_horas ? <span className="text-xs text-slate-400 flex items-center gap-1"><Clock className="w-3 h-3" />{fase.sla_horas}h</span> : null}
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-2 space-y-2 min-h-[120px]">
              {cards.map(card => (
                <div key={card.id} className="card p-3 group">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-sm leading-snug">{card.titulo}</p>
                    <button onClick={() => removerCard(card)} className="opacity-0 group-hover:opacity-100 text-danger-400 hover:text-danger-600 transition-opacity">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  {card.valor_monetario != null && (
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 mt-1">{formatarMoeda(card.valor_monetario)}</p>
                  )}
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                    {card.empresa_nome && <span className="flex items-center gap-1 truncate"><Building2 className="w-3 h-3" />{card.empresa_nome}</span>}
                    {card.responsavel_nome && <span className="flex items-center gap-1 truncate"><User className="w-3 h-3" />{card.responsavel_nome}</span>}
                    {fase.sla_horas ? <Clock className={`w-3 h-3 ml-auto ${SLA_META[card.sla_status] ?? ''}`} /> : null}
                  </div>
                  <div className="flex justify-between mt-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <button onClick={() => mover(card, -1)} disabled={colIdx === 0}
                      className="p-1 rounded text-slate-400 hover:text-slate-700 disabled:opacity-30 disabled:cursor-not-allowed">
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button onClick={() => mover(card, 1)} disabled={colIdx === board.colunas.length - 1}
                      className="p-1 rounded text-slate-400 hover:text-slate-700 disabled:opacity-30 disabled:cursor-not-allowed">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}

              {novoCardFase === fase.id ? (
                <div className="card p-2">
                  <input autoFocus className="input text-sm mb-2" value={titulo} onChange={e => setTitulo(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') criarCard(fase.id); if (e.key === 'Escape') setNovoCardFase(null) }}
                    placeholder="Título do card" />
                  <div className="flex gap-1">
                    <button onClick={() => criarCard(fase.id)} className="btn-primary text-xs py-1 px-2 flex-1">Adicionar</button>
                    <button onClick={() => { setNovoCardFase(null); setTitulo('') }} className="p-1 text-slate-400"><X className="w-4 h-4" /></button>
                  </div>
                </div>
              ) : (
                <button onClick={() => { setNovoCardFase(fase.id); setTitulo('') }}
                  className="w-full flex items-center gap-1 text-sm text-slate-400 hover:text-slate-600 px-2 py-1.5 rounded-lg hover:bg-white dark:hover:bg-slate-800 transition-colors">
                  <Plus className="w-4 h-4" /> Adicionar card
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
