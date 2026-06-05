import { useEffect, useState } from 'react'
import { Plus, X, Eye, Pencil, Save, Loader2 } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'
import { useToast } from '../components/Toast'
import { Icon } from '../icons'
import type { Departamento, Modulo, PermMap } from '../types'

const CORES = ['#171717', '#10b981', '#f59e0b', '#3f3f46', '#475569', '#0ea5e9', '#8b5cf6']

export function Departamentos() {
  const { pode } = useAuth()
  const editar = pode('departamentos', 'editar')
  const { toast } = useToast()
  const [deps, setDeps] = useState<Departamento[]>([])
  const [modulos, setModulos] = useState<Modulo[]>([])
  const [edit, setEdit] = useState<Departamento | null>(null)

  const carregar = async () => { setDeps((await api.get('/departamentos')).data) }
  useEffect(() => { carregar(); api.get('/meta/modulos').then((r) => setModulos(r.data.modulos)).catch(() => {}) }, [])

  const novo = (): Departamento => ({ id: '', nome: '', cor: '#171717', icone: 'Building2', descricao: '', permissoes_padrao: {}, total_usuarios: 0 })

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold tracking-tight">Departamentos</h1><p className="text-neutral-500 mt-1">Cada setor tem um template de permissões para novos membros.</p></div>
        {editar && <button onClick={() => setEdit(novo())} className="btn-primary"><Plus className="w-4 h-4" /> Novo setor</button>}
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {deps.map((d) => {
          const libs = Object.values(d.permissoes_padrao || {}).filter((p) => p.ver).length
          return (
            <button key={d.id} onClick={() => editar && setEdit(d)} className="card card-hover p-5 text-left">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl grid place-items-center text-white" style={{ background: d.cor }}><Icon name={d.icone} className="w-5 h-5" /></div>
                <div className="min-w-0"><h3 className="font-semibold truncate">{d.nome}</h3><p className="text-xs text-neutral-500">{d.total_usuarios} pessoa(s)</p></div>
              </div>
              <p className="text-sm text-neutral-600 mt-3 line-clamp-2">{d.descricao}</p>
              <div className="chip-neutral mt-3">{libs} módulos liberados</div>
            </button>
          )
        })}
      </div>

      {edit && <EditorSetor dep={edit} modulos={modulos} onClose={() => setEdit(null)} onSaved={() => { setEdit(null); carregar(); toast('Setor salvo', 'success') }} />}
    </div>
  )
}

function EditorSetor({ dep, modulos, onClose, onSaved }: { dep: Departamento; modulos: Modulo[]; onClose: () => void; onSaved: () => void }) {
  const [nome, setNome] = useState(dep.nome)
  const [descricao, setDescricao] = useState(dep.descricao ?? '')
  const [cor, setCor] = useState(dep.cor)
  const [perm, setPerm] = useState<PermMap>(dep.permissoes_padrao || {})
  const [salvando, setSalvando] = useState(false)

  const toggle = (k: string, a: 'ver' | 'editar') => setPerm((p) => {
    const at = p[k] ?? { ver: false, editar: false }; const nx = { ...at, [a]: !at[a] }
    if (a === 'ver' && !nx.ver) nx.editar = false; if (a === 'editar' && nx.editar) nx.ver = true
    return { ...p, [k]: nx }
  })

  const salvar = async () => {
    setSalvando(true)
    const body = { nome, descricao, cor, icone: dep.icone || 'Building2', permissoes_padrao: perm }
    try { if (dep.id) await api.put(`/departamentos/${dep.id}`, body); else await api.post('/departamentos', body); onSaved() }
    finally { setSalvando(false) }
  }

  const grupos = [...new Set(modulos.map((m) => m.grupo))]
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 grid place-items-center p-4" onClick={onClose}>
      <div className="card w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col animate-scale-in" onClick={(e) => e.stopPropagation()}>
        <div className="p-5 border-b border-neutral-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold">{dep.id ? 'Editar setor' : 'Novo setor'}</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-neutral-400" /></button>
        </div>
        <div className="p-5 overflow-y-auto space-y-4">
          <div className="grid sm:grid-cols-2 gap-3">
            <input className="input" placeholder="Nome do setor" value={nome} onChange={(e) => setNome(e.target.value)} />
            <div className="flex items-center gap-1.5">{CORES.map((c) => <button key={c} onClick={() => setCor(c)} className={`w-7 h-7 rounded-full border-2 ${cor === c ? 'border-neutral-900' : 'border-transparent'}`} style={{ background: c }} />)}</div>
          </div>
          <input className="input" placeholder="Descrição" value={descricao} onChange={(e) => setDescricao(e.target.value)} />
          <div>
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Template de permissões</p>
            {grupos.map((g) => (
              <div key={g} className="mb-2">
                <p className="px-1 text-[11px] font-bold text-neutral-400 uppercase">{g}</p>
                {modulos.filter((m) => m.grupo === g).map((m) => {
                  const p = perm[m.key] ?? { ver: false, editar: false }
                  return (
                    <div key={m.key} className="flex items-center gap-2 px-1 py-1.5 hover:bg-neutral-50 rounded-lg">
                      <span className="text-sm flex-1">{m.label}</span>
                      <button onClick={() => toggle(m.key, 'ver')} className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-semibold ${p.ver ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-400'}`}><Eye className="w-3 h-3" />Ver</button>
                      <button onClick={() => toggle(m.key, 'editar')} className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-semibold ${p.editar ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-400'}`}><Pencil className="w-3 h-3" />Editar</button>
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
        <div className="p-4 border-t border-neutral-100 flex justify-end gap-2">
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={salvar} disabled={!nome || salvando} className="btn-primary">{salvando ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Salvar</button>
        </div>
      </div>
    </div>
  )
}
