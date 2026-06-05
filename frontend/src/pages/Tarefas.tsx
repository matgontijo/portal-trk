import { useEffect, useState, useCallback } from 'react'
import { Plus, ChevronLeft, ChevronRight, Trash2, X } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'

interface Tarefa { id: string; titulo: string; status: string; prioridade: string }
const COLS = [
  { id: 'todo', nome: 'A Fazer', cor: '#94a3b8' },
  { id: 'doing', nome: 'Em Andamento', cor: '#f59e0b' },
  { id: 'done', nome: 'Concluído', cor: '#10b981' },
]
const PRIO: Record<string, string> = { baixa: 'chip-neutral', normal: 'chip-neutral', alta: 'chip-warning', urgente: 'chip-danger' }

export function Tarefas() {
  const { pode } = useAuth()
  const editar = pode('tarefas', 'editar')
  const [tarefas, setTarefas] = useState<Tarefa[]>([])
  const [nova, setNova] = useState<string | null>(null)
  const [titulo, setTitulo] = useState('')

  const carregar = useCallback(async () => { setTarefas((await api.get('/tarefas')).data) }, [])
  useEffect(() => { carregar() }, [carregar])

  const criar = async (status: string) => {
    if (!titulo.trim()) return
    await api.post('/tarefas', { titulo, status }); setTitulo(''); setNova(null); carregar()
  }
  const mover = async (t: Tarefa, dir: -1 | 1) => {
    const i = COLS.findIndex((c) => c.id === t.status); const dest = COLS[i + dir]
    if (dest) { await api.put(`/tarefas/${t.id}`, { status: dest.id }); carregar() }
  }
  const remover = async (t: Tarefa) => { await api.delete(`/tarefas/${t.id}`); carregar() }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Tarefas</h1>
        <p className="text-neutral-500 mt-1">Quadro kanban do seu time.</p>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {COLS.map((col, ci) => {
          const cards = tarefas.filter((t) => t.status === col.id)
          return (
            <div key={col.id} className="bg-neutral-100/60 rounded-2xl p-3">
              <div className="flex items-center gap-2 mb-3 px-1">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: col.cor }} />
                <h3 className="font-semibold text-sm">{col.nome}</h3>
                <span className="text-xs text-neutral-400">{cards.length}</span>
              </div>
              <div className="space-y-2">
                {cards.map((t) => (
                  <div key={t.id} className="card p-3 group">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium">{t.titulo}</p>
                      {editar && <button onClick={() => remover(t)} className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600"><Trash2 className="w-3.5 h-3.5" /></button>}
                    </div>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`${PRIO[t.prioridade] ?? 'chip-neutral'} text-[10px]`}>{t.prioridade}</span>
                      {editar && (
                        <div className="flex gap-1">
                          <button onClick={() => mover(t, -1)} disabled={ci === 0} className="p-1 text-neutral-400 hover:text-neutral-800 disabled:opacity-30"><ChevronLeft className="w-4 h-4" /></button>
                          <button onClick={() => mover(t, 1)} disabled={ci === COLS.length - 1} className="p-1 text-neutral-400 hover:text-neutral-800 disabled:opacity-30"><ChevronRight className="w-4 h-4" /></button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {editar && (nova === col.id ? (
                  <div className="card p-2">
                    <input autoFocus value={titulo} onChange={(e) => setTitulo(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') criar(col.id); if (e.key === 'Escape') setNova(null) }}
                      placeholder="Título…" className="input text-sm mb-2" />
                    <div className="flex gap-1">
                      <button onClick={() => criar(col.id)} className="btn-primary text-xs py-1 px-2 flex-1">Adicionar</button>
                      <button onClick={() => setNova(null)} className="p-1 text-neutral-400"><X className="w-4 h-4" /></button>
                    </div>
                  </div>
                ) : (
                  <button onClick={() => { setNova(col.id); setTitulo('') }} className="w-full flex items-center gap-1 text-sm text-neutral-400 hover:text-neutral-700 px-2 py-1.5 rounded-lg hover:bg-white transition">
                    <Plus className="w-4 h-4" /> Adicionar
                  </button>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
