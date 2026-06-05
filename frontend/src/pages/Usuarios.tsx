import { useEffect, useState, useCallback } from 'react'
import { UserPlus, Save, Eye, Pencil, ShieldCheck, Lock, Check, X, Loader2 } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'
import { Icon } from '../icons'
import type { Usuario, Modulo, PermMap, Departamento } from '../types'

export function Usuarios() {
  const { pode } = useAuth()
  const editavel = pode('usuarios', 'editar')
  const [users, setUsers] = useState<Usuario[]>([])
  const [sel, setSel] = useState<string | null>(null)
  const [novo, setNovo] = useState(false)

  const carregar = useCallback(async () => {
    const { data } = await api.get('/usuarios')
    setUsers(data)
    if (!sel && data.length) setSel(data[0].id)
  }, [sel])
  useEffect(() => { carregar() }, []) // eslint-disable-line

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Usuários & Acessos</h1>
          <p className="text-neutral-500 mt-1">Defina, por pessoa, o que cada um <strong>vê</strong> e <strong>edita</strong> em cada módulo.</p>
        </div>
        {editavel && <button onClick={() => setNovo(true)} className="btn-primary"><UserPlus className="w-4 h-4" /> Novo usuário</button>}
      </div>

      <div className="grid lg:grid-cols-[300px_1fr] gap-5">
        {/* Lista */}
        <div className="card p-2 h-fit lg:max-h-[calc(100vh-200px)] overflow-y-auto">
          {users.map((u) => (
            <button key={u.id} onClick={() => setSel(u.id)}
              className={`w-full flex items-center gap-3 p-3 rounded-xl text-left transition ${sel === u.id ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-100'}`}>
              <span className="w-9 h-9 rounded-full grid place-items-center text-white font-semibold text-sm shrink-0" style={{ background: u.avatar_cor }}>{u.nome[0]}</span>
              <span className="min-w-0">
                <span className="block text-sm font-medium truncate">{u.nome}</span>
                <span className={`block text-xs truncate ${sel === u.id ? 'text-white/60' : 'text-neutral-500'}`}>{u.departamento_nome ?? u.cargo}</span>
              </span>
            </button>
          ))}
        </div>

        {/* Matriz */}
        {sel ? <Matriz key={sel} userId={sel} editavel={editavel} onChange={carregar} /> : <div className="card p-10 text-center text-neutral-500">Selecione um usuário.</div>}
      </div>

      {novo && <NovoUsuario onClose={() => setNovo(false)} onSaved={() => { setNovo(false); carregar() }} />}
    </div>
  )
}

function Matriz({ userId, editavel, onChange }: { userId: string; editavel: boolean; onChange: () => void }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [modulos, setModulos] = useState<Modulo[]>([])
  const [perm, setPerm] = useState<PermMap>({})
  const [bloqueado, setBloqueado] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [dirty, setDirty] = useState(false)
  const [ok, setOk] = useState(false)

  useEffect(() => {
    api.get(`/usuarios/${userId}/permissoes`).then((r) => {
      setUsuario(r.data.usuario); setModulos(r.data.modulos); setPerm(r.data.permissoes); setBloqueado(r.data.bloqueado_edicao)
      setDirty(false)
    })
  }, [userId])

  const toggle = (key: string, acao: 'ver' | 'editar') => {
    if (!editavel || bloqueado) return
    setPerm((p) => {
      const atual = p[key] ?? { ver: false, editar: false }
      const next = { ...atual, [acao]: !atual[acao] }
      if (acao === 'ver' && !next.ver) next.editar = false // sem ver => sem editar
      if (acao === 'editar' && next.editar) next.ver = true // editar implica ver
      return { ...p, [key]: next }
    })
    setDirty(true); setOk(false)
  }

  const salvar = async () => {
    setSalvando(true)
    try { await api.put(`/usuarios/${userId}`, { permissoes: perm }); setDirty(false); setOk(true); onChange(); setTimeout(() => setOk(false), 2000) }
    finally { setSalvando(false) }
  }

  const grupos = [...new Set(modulos.map((m) => m.grupo))]
  const liberados = Object.values(perm).filter((p) => p.ver).length

  return (
    <div className="card overflow-hidden">
      <div className="p-5 border-b border-neutral-100 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span className="w-11 h-11 rounded-full grid place-items-center text-white font-semibold" style={{ background: usuario?.avatar_cor }}>{usuario?.nome?.[0]}</span>
          <div>
            <p className="font-semibold">{usuario?.nome}</p>
            <p className="text-xs text-neutral-500">{usuario?.email} · {usuario?.cargo} · <span className="text-emerald-600 font-medium">{liberados} módulos liberados</span></p>
          </div>
        </div>
        {editavel && !bloqueado && (
          <button onClick={salvar} disabled={!dirty || salvando} className={`btn ${dirty ? 'btn-primary' : 'btn-secondary'}`}>
            {salvando ? <Loader2 className="w-4 h-4 animate-spin" /> : ok ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {ok ? 'Salvo!' : 'Salvar acessos'}
          </button>
        )}
      </div>

      {bloqueado && (
        <div className="px-5 py-3 bg-neutral-50 text-sm text-neutral-600 flex items-center gap-2 border-b border-neutral-100">
          <ShieldCheck className="w-4 h-4 text-emerald-600" /> Diretor tem acesso total fixo — não editável.
        </div>
      )}

      <div className="p-3">
        {grupos.map((g) => (
          <div key={g} className="mb-3">
            <p className="px-2 py-1 text-[11px] font-bold text-neutral-400 uppercase tracking-wider">{g}</p>
            <div className="space-y-1">
              {modulos.filter((m) => m.grupo === g).map((m) => {
                const p = perm[m.key] ?? { ver: false, editar: false }
                return (
                  <div key={m.key} className="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-neutral-50">
                    <div className="w-8 h-8 rounded-lg bg-neutral-100 grid place-items-center text-neutral-600 shrink-0"><Icon name={m.icone} className="w-4 h-4" /></div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate flex items-center gap-1.5">{m.label} {m.sensivel && <Lock className="w-3 h-3 text-emerald-600" />}</p>
                      <p className="text-xs text-neutral-400 truncate">{m.descricao}</p>
                    </div>
                    <Toggle icon={<Eye className="w-3.5 h-3.5" />} label="Ver" on={p.ver} dis={bloqueado || !editavel} onClick={() => toggle(m.key, 'ver')} />
                    <Toggle icon={<Pencil className="w-3.5 h-3.5" />} label="Editar" on={p.editar} dis={bloqueado || !editavel} onClick={() => toggle(m.key, 'editar')} />
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Toggle({ icon, label, on, dis, onClick }: { icon: React.ReactNode; label: string; on: boolean; dis?: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} disabled={dis}
      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition shrink-0 ${
        on ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-400 hover:bg-neutral-200'} ${dis ? 'opacity-50 cursor-not-allowed' : ''}`}>
      {icon} {label}
    </button>
  )
}

function NovoUsuario({ onClose, onSaved }: { onClose: () => void; onSaved: () => void }) {
  const [deps, setDeps] = useState<Departamento[]>([])
  const [form, setForm] = useState({ nome: '', email: '', senha: 'Trk@123', cargo: 'colaborador', departamento_id: '' })
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')

  useEffect(() => { api.get('/departamentos').then((r) => setDeps(r.data)).catch(() => {}) }, [])

  const salvar = async () => {
    setSalvando(true); setErro('')
    try { await api.post('/usuarios', { ...form, departamento_id: form.departamento_id || null }); onSaved() }
    catch (e: any) { setErro(e?.response?.data?.detail ?? 'Erro ao criar') } finally { setSalvando(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 grid place-items-center p-4" onClick={onClose}>
      <div className="card p-6 w-full max-w-md animate-scale-in" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Novo usuário</h2>
          <button onClick={onClose} className="p-1 text-neutral-400 hover:text-neutral-700"><X className="w-5 h-5" /></button>
        </div>
        <div className="space-y-3">
          <input className="input" placeholder="Nome" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} />
          <input className="input" placeholder="E-mail" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Senha provisória" value={form.senha} onChange={(e) => setForm({ ...form, senha: e.target.value })} />
          <div className="grid grid-cols-2 gap-2">
            <select className="input" value={form.cargo} onChange={(e) => setForm({ ...form, cargo: e.target.value })}>
              <option value="colaborador">Colaborador</option>
              <option value="gestor">Gestor</option>
              <option value="diretor">Diretor</option>
            </select>
            <select className="input" value={form.departamento_id} onChange={(e) => setForm({ ...form, departamento_id: e.target.value })}>
              <option value="">Setor…</option>
              {deps.map((d) => <option key={d.id} value={d.id}>{d.nome}</option>)}
            </select>
          </div>
          <p className="text-xs text-neutral-400">As permissões são herdadas do setor — você ajusta depois na matriz.</p>
          {erro && <div className="chip-danger w-full justify-center py-2">{erro}</div>}
        </div>
        <div className="flex justify-end gap-2 mt-5">
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={salvar} disabled={!form.nome || !form.email || salvando} className="btn-primary">{salvando ? 'Criando…' : 'Criar'}</button>
        </div>
      </div>
    </div>
  )
}
