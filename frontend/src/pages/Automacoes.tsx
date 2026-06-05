import { useEffect, useState } from 'react'
import { Zap, Plus, Trash2, Power, X } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'
import { useToast } from '../components/Toast'

interface Auto { id: string; nome: string; gatilho: string; acao: string; ativa: boolean; execucoes: number }

export function Automacoes() {
  const { pode } = useAuth()
  const editar = pode('automacoes', 'editar')
  const { toast } = useToast()
  const [items, setItems] = useState<Auto[]>([])
  const [meta, setMeta] = useState<{ gatilhos: string[]; acoes: string[] }>({ gatilhos: [], acoes: [] })
  const [form, setForm] = useState<{ nome: string; gatilho: string; acao: string } | null>(null)

  const carregar = async () => { setItems((await api.get('/automacoes')).data) }
  useEffect(() => { carregar(); api.get('/automacoes/meta').then((r) => setMeta(r.data)).catch(() => {}) }, [])

  const criar = async () => {
    if (!form?.nome) return
    await api.post('/automacoes', form); setForm(null); carregar(); toast('Automação criada', 'success')
  }
  const toggle = async (a: Auto) => { await api.put(`/automacoes/${a.id}`, { ativa: !a.ativa }); carregar() }
  const remover = async (a: Auto) => { await api.delete(`/automacoes/${a.id}`); carregar() }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold tracking-tight flex items-center gap-2"><Zap className="w-6 h-6 text-neutral-700" /> Automações</h1><p className="text-neutral-500 mt-1">Regras que reagem sozinhas aos eventos.</p></div>
        {editar && <button onClick={() => setForm({ nome: '', gatilho: meta.gatilhos[0] ?? 'saldo_divergencia', acao: meta.acoes[0] ?? 'notificar' })} className="btn-primary"><Plus className="w-4 h-4" /> Nova</button>}
      </div>
      {items.length === 0 ? (
        <div className="card p-10 text-center text-neutral-500"><Zap className="w-10 h-10 mx-auto mb-3 text-neutral-300" />Nenhuma automação ainda.</div>
      ) : (
        <div className="grid gap-3">
          {items.map((a) => (
            <div key={a.id} className={`card p-4 flex items-center justify-between ${!a.ativa && 'opacity-60'}`}>
              <div><p className="font-semibold">{a.nome}</p><p className="text-sm text-neutral-500"><b>QUANDO</b> {a.gatilho} <b>ENTÃO</b> {a.acao} · disparada {a.execucoes}×</p></div>
              {editar && <div className="flex gap-1"><button onClick={() => toggle(a)} className={`p-2 rounded-lg ${a.ativa ? 'text-emerald-600 hover:bg-emerald-50' : 'text-neutral-400 hover:bg-neutral-100'}`}><Power className="w-4 h-4" /></button><button onClick={() => remover(a)} className="p-2 rounded-lg text-red-500 hover:bg-red-50"><Trash2 className="w-4 h-4" /></button></div>}
            </div>
          ))}
        </div>
      )}
      {form && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 grid place-items-center p-4" onClick={() => setForm(null)}>
          <div className="card p-6 w-full max-w-md animate-scale-in" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4"><h2 className="text-lg font-semibold">Nova automação</h2><button onClick={() => setForm(null)}><X className="w-5 h-5 text-neutral-400" /></button></div>
            <div className="space-y-3">
              <input className="input" placeholder="Nome" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} />
              <div><label className="text-xs font-semibold text-neutral-500">QUANDO (gatilho)</label><select className="input mt-1" value={form.gatilho} onChange={(e) => setForm({ ...form, gatilho: e.target.value })}>{meta.gatilhos.map((g) => <option key={g} value={g}>{g}</option>)}</select></div>
              <div><label className="text-xs font-semibold text-neutral-500">ENTÃO (ação)</label><select className="input mt-1" value={form.acao} onChange={(e) => setForm({ ...form, acao: e.target.value })}>{meta.acoes.map((a) => <option key={a} value={a}>{a}</option>)}</select></div>
            </div>
            <div className="flex justify-end gap-2 mt-5"><button onClick={() => setForm(null)} className="btn-secondary">Cancelar</button><button onClick={criar} disabled={!form.nome} className="btn-primary">Criar</button></div>
          </div>
        </div>
      )}
    </div>
  )
}
