// frontend/src/pages/Skills.tsx
// Biblioteca de Skills — capacidades prontas instaláveis em 1 clique (estilo Claude).

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Sparkles, Check, Loader2,
  AlertTriangle, WifiOff, CheckCircle2, Wallet, Sunrise, CalendarCheck,
  Receipt, UserPlus, Kanban, Zap,
} from 'lucide-react'
import api from '../services/api'
import { useToast } from '../components/common/Toast'

interface Skill {
  id: string; nome: string; descricao: string
  categoria: string; icone: string; tipo: 'automacao' | 'rotina' | 'pipe'
}

const ICONES: Record<string, typeof Zap> = {
  AlertTriangle, WifiOff, CheckCircle2, Wallet, Sunrise, CalendarCheck, Receipt, UserPlus, Kanban,
}

const TIPO_META: Record<string, { label: string; cls: string; destino: string }> = {
  automacao: { label: 'Automação', cls: 'bg-warning-50 text-warning-700', destino: '/automacoes' },
  rotina: { label: 'Rotina', cls: 'bg-success-50 text-success-700', destino: '/rotinas' },
  pipe: { label: 'Pipe', cls: 'bg-neutral-100 text-neutral-700', destino: '/pipes' },
}

export function Skills() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [instalando, setInstalando] = useState<string | null>(null)
  const [instaladas, setInstaladas] = useState<Set<string>>(new Set())
  const { toast } = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    api.get<Skill[]>('/skills').then(r => setSkills(r.data)).catch(console.error).finally(() => setLoading(false))
  }, [])

  const instalar = async (skill: Skill) => {
    setInstalando(skill.id)
    try {
      await api.post(`/skills/${skill.id}/instalar`)
      setInstaladas(prev => new Set(prev).add(skill.id))
      toast(`"${skill.nome}" instalada!`, 'success')
    } catch (e) {
      console.error(e); toast('Erro ao instalar a skill', 'error')
    } finally { setInstalando(null) }
  }

  const categorias = [...new Set(skills.map(s => s.categoria))]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6 bg-gradient-to-br from-neutral-900 to-neutral-700 text-white border-0">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-white/10 flex items-center justify-center">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Biblioteca de Skills</h1>
            <p className="text-sm text-white/70 mt-0.5">Capacidades prontas. Instale com 1 clique e já comece a usar.</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-40 bg-slate-100 dark:bg-slate-800 rounded-xl" />)}
        </div>
      ) : (
        categorias.map(cat => (
          <div key={cat}>
            <h2 className="text-sm font-semibold text-neutral-500 uppercase tracking-wider mb-3">{cat}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {skills.filter(s => s.categoria === cat).map(skill => {
                const Icon = ICONES[skill.icone] ?? Zap
                const meta = TIPO_META[skill.tipo]
                const done = instaladas.has(skill.id)
                return (
                  <div key={skill.id} className="card p-5 flex flex-col group">
                    <div className="flex items-start justify-between mb-3">
                      <div className="w-10 h-10 rounded-xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center text-neutral-700 group-hover:bg-neutral-900 group-hover:text-white transition-colors">
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${meta.cls}`}>{meta.label}</span>
                    </div>
                    <h3 className="font-semibold leading-snug">{skill.nome}</h3>
                    <p className="text-sm text-slate-500 mt-1 flex-1">{skill.descricao}</p>
                    <div className="flex items-center gap-2 mt-4">
                      {done ? (
                        <>
                          <span className="btn-secondary flex-1 justify-center text-success-600 border-success-200 cursor-default">
                            <Check className="w-4 h-4" /> Instalada
                          </span>
                          <button onClick={() => navigate(meta.destino)} className="btn-secondary text-sm">Abrir</button>
                        </>
                      ) : (
                        <button onClick={() => instalar(skill)} disabled={instalando === skill.id}
                          className="btn-primary flex-1 justify-center disabled:opacity-60">
                          {instalando === skill.id
                            ? <><Loader2 className="w-4 h-4 animate-spin" /> Instalando…</>
                            : <>Instalar</>}
                        </button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
