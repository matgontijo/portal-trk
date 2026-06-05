import { useEffect, useState } from 'react'
import { Sparkles, Check, Loader2 } from 'lucide-react'
import api from '../api'
import { useToast } from '../components/Toast'
import { Icon } from '../icons'

interface Skill { id: string; nome: string; descricao: string; categoria: string; icone: string; tipo: string }
const TIPO: Record<string, string> = { rotina: 'chip-success', automacao: 'chip-warning', pipe: 'chip-neutral' }

export function Skills() {
  const { toast } = useToast()
  const [skills, setSkills] = useState<Skill[]>([])
  const [inst, setInst] = useState<string | null>(null)
  const [feitas, setFeitas] = useState<Set<string>>(new Set())

  useEffect(() => { api.get('/skills').then((r) => setSkills(r.data)).catch(() => {}) }, [])

  const instalar = async (s: Skill) => {
    setInst(s.id)
    try { await api.post(`/skills/${s.id}/instalar`); setFeitas((p) => new Set(p).add(s.id)); toast(`"${s.nome}" instalada!`, 'success') }
    catch { toast('Erro ao instalar', 'error') } finally { setInst(null) }
  }
  const cats = [...new Set(skills.map((s) => s.categoria))]

  return (
    <div className="space-y-6">
      <div className="card p-6 bg-gradient-to-br from-neutral-900 to-neutral-700 text-white border-0">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-white/10 grid place-items-center"><Sparkles className="w-6 h-6" /></div>
          <div><h1 className="text-2xl font-bold tracking-tight">Biblioteca de Skills</h1>
            <p className="text-sm text-white/70">Capacidades prontas. Instale com 1 clique.</p></div>
        </div>
      </div>
      {cats.map((c) => (
        <div key={c}>
          <h2 className="text-sm font-bold text-neutral-400 uppercase tracking-wider mb-3">{c}</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.filter((s) => s.categoria === c).map((s) => {
              const done = feitas.has(s.id)
              return (
                <div key={s.id} className="card p-5 flex flex-col group">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-neutral-100 grid place-items-center text-neutral-700 group-hover:bg-neutral-900 group-hover:text-white transition"><Icon name={s.icone} className="w-5 h-5" /></div>
                    <span className={`${TIPO[s.tipo] ?? 'chip-neutral'} text-[10px]`}>{s.tipo}</span>
                  </div>
                  <h3 className="font-semibold leading-snug">{s.nome}</h3>
                  <p className="text-sm text-neutral-500 mt-1 flex-1">{s.descricao}</p>
                  <button onClick={() => instalar(s)} disabled={done || inst === s.id} className={`mt-4 ${done ? 'btn-secondary text-emerald-600' : 'btn-primary'}`}>
                    {done ? <><Check className="w-4 h-4" /> Instalada</> : inst === s.id ? <><Loader2 className="w-4 h-4 animate-spin" /> Instalando…</> : 'Instalar'}
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
