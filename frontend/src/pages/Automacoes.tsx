// frontend/src/pages/Automacoes.tsx
// Gestão de automações (o "customize cowork"): QUANDO gatilho [E condição] ENTÃO ação.

import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Zap, Plus, Trash2, Power, FlaskConical, X } from 'lucide-react'
import api from '../services/api'

interface Automacao {
  id: string
  nome: string
  descricao: string | null
  gatilho: string
  condicao: { logica?: string; regras?: Array<{ campo: string; op: string; valor: unknown }> }
  acao: string
  acao_config: Record<string, unknown>
  ativa: boolean
  prioridade: number
  execucoes: number
}

interface Meta {
  gatilhos: string[]
  acoes: string[]
  operadores: string[]
  campos_por_gatilho: Record<string, string[]>
}

const ROTULO_GATILHO: Record<string, string> = {
  saldo_divergencia: 'Saldo divergente',
  saldo_atualizado: 'Saldo atualizado',
  saldo_falha: 'Falha no sync',
  rotina_concluida: 'Rotina concluída',
  rotina_atrasada: 'Rotina atrasada',
  tarefa_criada: 'Tarefa criada',
  agendado: 'Agendado',
}
const ROTULO_ACAO: Record<string, string> = {
  notificar: 'Notificar', criar_tarefa: 'Criar tarefa', whatsapp: 'WhatsApp', webhook: 'Webhook',
}

const FORM_INICIAL = {
  nome: '', gatilho: 'saldo_divergencia', acao: 'criar_tarefa',
  campo: '', op: '>', valor: '',
  titulo: '', mensagem: '', prioridade: 'alta', prazo_dias: '1', url: '', para: '',
}

export function Automacoes() {
  const [items, setItems] = useState<Automacao[]>([])
  const [meta, setMeta] = useState<Meta | null>(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ ...FORM_INICIAL })
  const [salvando, setSalvando] = useState(false)

  const carregar = async () => {
    try {
      const [a, m] = await Promise.all([api.get<Automacao[]>('/automacoes'), api.get<Meta>('/automacoes/meta')])
      setItems(a.data); setMeta(m.data)
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }
  useEffect(() => { carregar() }, [])

  const montarAcaoConfig = (): Record<string, unknown> => {
    if (form.acao === 'criar_tarefa') return { titulo: form.titulo, prioridade: form.prioridade, prazo_dias: Number(form.prazo_dias) }
    if (form.acao === 'notificar') return { titulo: form.titulo, mensagem: form.mensagem, tipo: 'sistema' }
    if (form.acao === 'whatsapp') return { para: form.para, mensagem: form.mensagem }
    if (form.acao === 'webhook') return { url: form.url }
    return {}
  }

  const salvar = async () => {
    setSalvando(true)
    try {
      const condicao = form.campo
        ? { logica: 'and', regras: [{ campo: form.campo, op: form.op, valor: isNaN(Number(form.valor)) ? form.valor : Number(form.valor) }] }
        : {}
      await api.post('/automacoes', {
        nome: form.nome, gatilho: form.gatilho, acao: form.acao,
        condicao, acao_config: montarAcaoConfig(), ativa: true,
      })
      setShowForm(false); setForm({ ...FORM_INICIAL }); carregar()
    } catch (e) { console.error(e); alert('Erro ao salvar automação') } finally { setSalvando(false) }
  }

  const toggle = async (a: Automacao) => {
    await api.put(`/automacoes/${a.id}`, { ativa: !a.ativa }); carregar()
  }
  const remover = async (a: Automacao) => {
    if (!confirm(`Excluir a automação "${a.nome}"?`)) return
    await api.delete(`/automacoes/${a.id}`); carregar()
  }

  const campos = meta?.campos_por_gatilho[form.gatilho] ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Zap className="w-6 h-6 text-primary-500" /> Automações
          </h1>
          <p className="text-sm text-slate-500 mt-1">Regras que reagem sozinhas aos eventos do portal.</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Nova automação
        </button>
      </div>

      {loading ? (
        <div className="space-y-2 animate-pulse">{[1, 2, 3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-xl" />)}</div>
      ) : items.length === 0 ? (
        <div className="card p-10 text-center text-slate-500">
          <Zap className="w-10 h-10 mx-auto mb-3 text-slate-300" />
          Nenhuma automação ainda. Crie a primeira — ex.: <em>“quando saldo divergir mais de R$1.000, criar tarefa urgente”.</em>
        </div>
      ) : (
        <div className="grid gap-3">
          {items.map(a => (
            <div key={a.id} className={`card p-4 flex items-center justify-between gap-4 ${!a.ativa && 'opacity-60'}`}>
              <div className="min-w-0">
                <p className="font-semibold truncate">{a.nome}</p>
                <p className="text-sm text-slate-500">
                  <span className="font-medium text-slate-700 dark:text-slate-300">QUANDO</span> {ROTULO_GATILHO[a.gatilho] ?? a.gatilho}
                  {a.condicao?.regras?.length ? <> <span className="font-medium text-slate-700 dark:text-slate-300">SE</span> {a.condicao.regras.map(r => `${r.campo} ${r.op} ${r.valor}`).join(' e ')}</> : null}
                  {' '}<span className="font-medium text-slate-700 dark:text-slate-300">ENTÃO</span> {ROTULO_ACAO[a.acao] ?? a.acao}
                </p>
                <p className="text-xs text-slate-400 mt-1">Disparada {a.execucoes}×</p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <button onClick={() => toggle(a)} title={a.ativa ? 'Desativar' : 'Ativar'}
                  className={`p-2 rounded-lg ${a.ativa ? 'text-success-600 hover:bg-success-50' : 'text-slate-400 hover:bg-slate-100'}`}>
                  <Power className="w-4 h-4" />
                </button>
                <button onClick={() => remover(a)} title="Excluir" className="p-2 rounded-lg text-danger-500 hover:bg-danger-50">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && meta && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <div className="card p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Nova automação</h2>
              <button onClick={() => setShowForm(false)} className="p-1 text-slate-400 hover:text-slate-700"><X className="w-5 h-5" /></button>
            </div>

            <div className="space-y-4">
              <Field label="Nome">
                <input className="input" value={form.nome} onChange={e => setForm({ ...form, nome: e.target.value })} placeholder="Ex.: Alerta de divergência alta" />
              </Field>

              <Field label="QUANDO (gatilho)">
                <select className="input" value={form.gatilho} onChange={e => setForm({ ...form, gatilho: e.target.value, campo: '' })}>
                  {meta.gatilhos.map(g => <option key={g} value={g}>{ROTULO_GATILHO[g] ?? g}</option>)}
                </select>
              </Field>

              <div className="grid grid-cols-3 gap-2">
                <Field label="SE (campo, opcional)">
                  <select className="input" value={form.campo} onChange={e => setForm({ ...form, campo: e.target.value })}>
                    <option value="">— sempre —</option>
                    {campos.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </Field>
                <Field label="Operador">
                  <select className="input" value={form.op} onChange={e => setForm({ ...form, op: e.target.value })} disabled={!form.campo}>
                    {meta.operadores.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </Field>
                <Field label="Valor">
                  <input className="input" value={form.valor} onChange={e => setForm({ ...form, valor: e.target.value })} disabled={!form.campo} placeholder="1000" />
                </Field>
              </div>

              <Field label="ENTÃO (ação)">
                <select className="input" value={form.acao} onChange={e => setForm({ ...form, acao: e.target.value })}>
                  {meta.acoes.map(a => <option key={a} value={a}>{ROTULO_ACAO[a] ?? a}</option>)}
                </select>
              </Field>

              {(form.acao === 'criar_tarefa' || form.acao === 'notificar') && (
                <Field label="Título"><input className="input" value={form.titulo} onChange={e => setForm({ ...form, titulo: e.target.value })} placeholder="Use {empresa_nome}, {delta_abs}…" /></Field>
              )}
              {form.acao === 'criar_tarefa' && (
                <div className="grid grid-cols-2 gap-2">
                  <Field label="Prioridade">
                    <select className="input" value={form.prioridade} onChange={e => setForm({ ...form, prioridade: e.target.value })}>
                      {['baixa', 'normal', 'alta', 'urgente'].map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </Field>
                  <Field label="Prazo (dias)"><input className="input" type="number" value={form.prazo_dias} onChange={e => setForm({ ...form, prazo_dias: e.target.value })} /></Field>
                </div>
              )}
              {(form.acao === 'notificar' || form.acao === 'whatsapp') && (
                <Field label="Mensagem"><input className="input" value={form.mensagem} onChange={e => setForm({ ...form, mensagem: e.target.value })} placeholder="Use {empresa_nome}, {delta_abs}…" /></Field>
              )}
              {form.acao === 'whatsapp' && (
                <Field label="Para (telefone)"><input className="input" value={form.para} onChange={e => setForm({ ...form, para: e.target.value })} placeholder="+55..." /></Field>
              )}
              {form.acao === 'webhook' && (
                <Field label="URL"><input className="input" value={form.url} onChange={e => setForm({ ...form, url: e.target.value })} placeholder="https://..." /></Field>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 mt-6">
              <button onClick={() => setShowForm(false)} className="btn-secondary flex items-center gap-1">
                <FlaskConical className="w-4 h-4 opacity-0" /> Cancelar
              </button>
              <button onClick={salvar} disabled={!form.nome || salvando} className="btn-primary disabled:opacity-60">
                {salvando ? 'Salvando…' : 'Criar automação'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs font-medium text-slate-500 mb-1 block">{label}</span>
      {children}
    </label>
  )
}
