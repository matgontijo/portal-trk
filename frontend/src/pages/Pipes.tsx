import { useEffect, useState, useCallback } from 'react'
import { Plus, ArrowLeft, ChevronLeft, ChevronRight, Trash2, X, GitBranch } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'
import { useToast } from '../components/Toast'

interface Fase { id: string; nome: string; cor: string; ordem: number }
interface Pipe { id: string; nome: string; cor: string; fases: Fase[] }
interface Card { id: string; titulo: string; fase_id: string; valor: number | null }

const TEMPLATES = [
  { id: 'padrao', nome: 'Padrão', desc: 'A Fazer · Andamento · Concluído' },
  { id: 'contas_pagar', nome: 'Contas a Pagar', desc: 'Recebido · Análise · Aprovado · Pago' },
  { id: 'onboarding', nome: 'Onboarding', desc: 'Lead · Doc · Config · Ativo' },
]

export function Pipes() {
  const { pode } = useAuth()
  const editar = pode('pipes', 'editar')
  const { toast } = useToast()
  const [pipes, setPipes] = useState<Pipe[]>([])
  const [sel, setSel] = useState<string | null>(null)
  const [novo, setNovo] = useState(false)
  const [nome, setNome] = useState(''); const [tpl, setTpl] = useState('padrao')

  const carregar = useCallback(async () => { setPipes((await api.get('/pipes')).data) }, [])
  useEffect(() => { carregar() }, [carregar])

  const criar = async () => {
    if (!nome.trim()) return
    const r = await api.post('/pipes', { nome, template: tpl }); setNovo(false); setNome(''); await carregar(); setSel(r.data.id); toast('Pipe criado', 'success')
  }

  if (sel) return <Board pipeId={sel} editar={editar} onBack={() => setSel(null)} />

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold tracking-tight">Pipes</h1><p className="text-neutral-500 mt-1">Processos em fases, estilo Pipefy.</p></div>
        {editar && <button onClick={() => setNovo(true)} className="btn-primary"><Plus className="w-4 h-4" /> Novo pipe</button>}
      </div>
      {pipes.length === 0 ? (
        <div className="card p-10 text-center text-neutral-500"><GitBranch className="w-10 h-10 mx-auto mb-3 text-neutral-300" />Nenhum pipe ainda.</div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {pipes.map((p) => (
            <button key={p.id} onClick={() => setSel(p.id)} className="card card-hover p-5 text-left">
              <span className="w-3 h-3 rounded-full block mb-2" style={{ background: p.cor }} />
              <h3 className="font-semibold">{p.nome}</h3>
              <div className="flex flex-wrap gap-1 mt-3">{p.fases.map((f) => <span key={f.id} className="text-[10px] px-2 py-0.5 rounded-full text-white" style={{ background: f.cor }}>{f.nome}</span>)}</div>
            </button>
          ))}
        </div>
      )}
      {novo && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 grid place-items-center p-4" onClick={() => setNovo(false)}>
          <div className="card p-6 w-full max-w-md animate-scale-in" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4"><h2 className="text-lg font-semibold">Novo pipe</h2><button onClick={() => setNovo(false)}><X className="w-5 h-5 text-neutral-400" /></button></div>
            <input className="input mb-4" placeholder="Nome do pipe" value={nome} onChange={(e) => setNome(e.target.value)} />
            <div className="space-y-2 mb-5">
              {TEMPLATES.map((t) => (
                <button key={t.id} onClick={() => setTpl(t.id)} className={`w-full text-left px-3 py-2 rounded-lg border ${tpl === t.id ? 'border-neutral-900 bg-neutral-50' : 'border-neutral-200'}`}>
                  <p className="font-medium text-sm">{t.nome}</p><p className="text-xs text-neutral-500">{t.desc}</p>
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2"><button onClick={() => setNovo(false)} className="btn-secondary">Cancelar</button><button onClick={criar} disabled={!nome} className="btn-primary">Criar</button></div>
          </div>
        </div>
      )}
    </div>
  )
}

function Board({ pipeId, editar, onBack }: { pipeId: string; editar: boolean; onBack: () => void }) {
  const [board, setBoard] = useState<any>(null)
  const [nova, setNova] = useState<string | null>(null); const [titulo, setTitulo] = useState('')

  const carregar = useCallback(async () => { setBoard((await api.get(`/pipes/${pipeId}/board`)).data) }, [pipeId])
  useEffect(() => { carregar() }, [carregar])
  if (!board) return <div className="skeleton h-64" />

  const fases: Fase[] = board.colunas.map((c: any) => c.fase)
  const mover = async (card: Card, dir: -1 | 1) => {
    const i = fases.findIndex((f) => f.id === card.fase_id); const dest = fases[i + dir]
    if (dest) { await api.patch(`/pipes/cards/${card.id}/mover`, { fase_id: dest.id }); carregar() }
  }
  const criar = async (faseId: string) => { if (!titulo.trim()) return; await api.post(`/pipes/${pipeId}/cards`, { titulo, fase_id: faseId }); setTitulo(''); setNova(null); carregar() }
  const remover = async (card: Card) => { await api.delete(`/pipes/cards/${card.id}`); carregar() }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 rounded-lg hover:bg-neutral-100"><ArrowLeft className="w-5 h-5" /></button>
        <span className="w-3 h-3 rounded-full" style={{ background: board.pipe.cor }} />
        <h1 className="text-2xl font-bold tracking-tight">{board.pipe.nome}</h1>
      </div>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {board.colunas.map((col: any, ci: number) => (
          <div key={col.fase.id} className="flex-shrink-0 w-72">
            <div className="flex items-center gap-2 mb-2 px-1"><span className="w-2.5 h-2.5 rounded-full" style={{ background: col.fase.cor }} /><h3 className="font-semibold text-sm">{col.fase.nome}</h3><span className="text-xs text-neutral-400">{col.cards.length}</span></div>
            <div className="bg-neutral-100/60 rounded-xl p-2 space-y-2 min-h-[100px]">
              {col.cards.map((card: Card) => (
                <div key={card.id} className="card p-3 group">
                  <div className="flex items-start justify-between gap-2"><p className="text-sm font-medium">{card.titulo}</p>{editar && <button onClick={() => remover(card)} className="opacity-0 group-hover:opacity-100 text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>}</div>
                  {editar && <div className="flex justify-between mt-2 pt-2 border-t border-neutral-100"><button onClick={() => mover(card, -1)} disabled={ci === 0} className="p-1 text-neutral-400 disabled:opacity-30"><ChevronLeft className="w-4 h-4" /></button><button onClick={() => mover(card, 1)} disabled={ci === fases.length - 1} className="p-1 text-neutral-400 disabled:opacity-30"><ChevronRight className="w-4 h-4" /></button></div>}
                </div>
              ))}
              {editar && (nova === col.fase.id ? (
                <div className="card p-2"><input autoFocus value={titulo} onChange={(e) => setTitulo(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') criar(col.fase.id); if (e.key === 'Escape') setNova(null) }} className="input text-sm mb-2" placeholder="Card…" /><button onClick={() => criar(col.fase.id)} className="btn-primary text-xs py-1 w-full">Adicionar</button></div>
              ) : (
                <button onClick={() => { setNova(col.fase.id); setTitulo('') }} className="w-full flex items-center gap-1 text-sm text-neutral-400 hover:text-neutral-700 px-2 py-1.5 rounded-lg"><Plus className="w-4 h-4" /> Card</button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
