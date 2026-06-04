// frontend/src/pages/Pipes.tsx
// Lista de pipes (estilo Pipefy) + criação a partir de template.

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { KanbanSquare, Plus, X, ArrowRight } from 'lucide-react'
import api from '../services/api'
import { useToast } from '../components/common/Toast'

interface Fase { id: string; nome: string; cor: string }
interface Pipe { id: string; nome: string; descricao: string | null; cor: string; fases: Fase[] }

const TEMPLATES = [
  { id: 'padrao', nome: 'Padrão', desc: 'A Fazer · Em Andamento · Concluído' },
  { id: 'contas_pagar', nome: 'Contas a Pagar', desc: 'Recebido · Análise · Aprovado · Pago' },
  { id: 'onboarding', nome: 'Onboarding', desc: 'Lead · Documentação · Configuração · Ativo' },
]

export function Pipes() {
  const [pipes, setPipes] = useState<Pipe[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [nome, setNome] = useState('')
  const [template, setTemplate] = useState('padrao')
  const [salvando, setSalvando] = useState(false)
  const navigate = useNavigate()
  const { toast } = useToast()

  const carregar = async () => {
    try { setPipes((await api.get<Pipe[]>('/pipes')).data) }
    catch (e) { console.error(e) } finally { setLoading(false) }
  }
  useEffect(() => { carregar() }, [])

  const criar = async () => {
    setSalvando(true)
    try {
      const res = await api.post<Pipe>('/pipes', { nome, usar_template: template })
      setShowForm(false); setNome(''); navigate(`/pipes/${res.data.id}`)
    } catch (e) { console.error(e); toast('Erro ao criar pipe', 'error') } finally { setSalvando(false) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <KanbanSquare className="w-6 h-6 text-primary-500" /> Pipes
          </h1>
          <p className="text-sm text-slate-500 mt-1">Processos customizados com fases, campos e SLA.</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Novo pipe
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-pulse">
          {[1, 2, 3].map(i => <div key={i} className="h-32 bg-slate-100 dark:bg-slate-800 rounded-xl" />)}
        </div>
      ) : pipes.length === 0 ? (
        <div className="card p-10 text-center text-slate-500">
          <KanbanSquare className="w-10 h-10 mx-auto mb-3 text-slate-300" />
          Nenhum pipe ainda. Crie o primeiro processo — ex.: <em>Contas a Pagar</em>.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pipes.map(p => (
            <button key={p.id} onClick={() => navigate(`/pipes/${p.id}`)}
              className="card p-5 text-left hover:shadow-md transition-shadow group">
              <div className="flex items-center justify-between mb-2">
                <span className="w-3 h-3 rounded-full" style={{ background: p.cor }} />
                <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-primary-500 transition-colors" />
              </div>
              <h3 className="font-semibold truncate">{p.nome}</h3>
              {p.descricao && <p className="text-sm text-slate-500 truncate">{p.descricao}</p>}
              <div className="flex flex-wrap gap-1 mt-3">
                {p.fases.map(f => (
                  <span key={f.id} className="text-xs px-2 py-0.5 rounded-full text-white" style={{ background: f.cor }}>{f.nome}</span>
                ))}
              </div>
            </button>
          ))}
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <div className="card p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Novo pipe</h2>
              <button onClick={() => setShowForm(false)} className="p-1 text-slate-400 hover:text-slate-700"><X className="w-5 h-5" /></button>
            </div>
            <label className="block mb-4">
              <span className="text-xs font-medium text-slate-500 mb-1 block">Nome</span>
              <input className="input" value={nome} onChange={e => setNome(e.target.value)} placeholder="Ex.: Contas a Pagar — Junho" />
            </label>
            <span className="text-xs font-medium text-slate-500 mb-2 block">Modelo de fases</span>
            <div className="space-y-2 mb-6">
              {TEMPLATES.map(t => (
                <button key={t.id} onClick={() => setTemplate(t.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg border transition-colors ${template === t.id ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'}`}>
                  <p className="font-medium text-sm">{t.nome}</p>
                  <p className="text-xs text-slate-500">{t.desc}</p>
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancelar</button>
              <button onClick={criar} disabled={!nome || salvando} className="btn-primary disabled:opacity-60">
                {salvando ? 'Criando…' : 'Criar pipe'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
