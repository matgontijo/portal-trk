// frontend/src/pages/Dashboard.tsx
import { useState, useEffect } from 'react'
import { DollarSign, AlertTriangle, Clock, Building2, TrendingUp, CheckCircle2 } from 'lucide-react'
import api from '../services/api'
import { formatarMoeda } from '../utils/formatters'
import { SaldosPanel } from '../components/saldos/SaldosPanel'
import type { DashboardKPIs, EquipeProgresso } from '../types/common'

export function Dashboard() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null)
  const [equipe, setEquipe] = useState<EquipeProgresso[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpisRes, equipeRes] = await Promise.all([
          api.get('/dashboard/kpis'),
          api.get('/dashboard/equipe-progresso')
        ])
        setKpis(kpisRes.data)
        setEquipe(equipeRes.data)
      } catch (error) {
        console.error('Erro ao buscar dados do dashboard:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  if (isLoading || !kpis) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Visão Geral</h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="kpi-card relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary-50 dark:bg-primary-900/20 rounded-full blur-xl"></div>
          <div className="flex items-center justify-between relative z-10">
            <span className="kpi-label">Total em Caixa</span>
            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-primary-600">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <span className="kpi-value mt-2">{formatarMoeda(kpis.total_em_caixa)}</span>
        </div>

        <div className="kpi-card relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-warning-50 dark:bg-warning-900/20 rounded-full blur-xl"></div>
          <div className="flex items-center justify-between relative z-10">
            <span className="kpi-label">A Pagar Hoje</span>
            <div className="w-8 h-8 rounded-full bg-warning-100 dark:bg-warning-900/50 flex items-center justify-center text-warning-600">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <span className="kpi-value mt-2">{formatarMoeda(kpis.a_pagar_hoje)}</span>
          <span className="text-sm text-slate-500 mt-1">
            + {formatarMoeda(kpis.a_pagar_semana)} na semana
          </span>
        </div>

        <div className={`kpi-card relative overflow-hidden ${kpis.em_atraso > 0 ? 'border-danger-200 dark:border-danger-900/50' : ''}`}>
          <div className="flex items-center justify-between relative z-10">
            <span className="kpi-label">Em Atraso</span>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${kpis.em_atraso > 0 ? 'bg-danger-100 text-danger-600 dark:bg-danger-900/50' : 'bg-slate-100 text-slate-500 dark:bg-slate-800'}`}>
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <span className={`kpi-value mt-2 ${kpis.em_atraso > 0 ? 'text-danger-600 dark:text-danger-400' : ''}`}>
            {formatarMoeda(kpis.em_atraso)}
          </span>
        </div>

        <div className={`kpi-card relative overflow-hidden ${kpis.empresas_com_divergencia > 0 ? 'border-danger-200 dark:border-danger-900/50' : ''}`}>
          <div className="flex items-center justify-between relative z-10">
            <span className="kpi-label">Divergências</span>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${kpis.empresas_com_divergencia > 0 ? 'bg-danger-100 text-danger-600 dark:bg-danger-900/50 pulse-danger' : 'bg-success-100 text-success-600 dark:bg-success-900/50'}`}>
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <span className={`kpi-value ${kpis.empresas_com_divergencia > 0 ? 'text-danger-600 dark:text-danger-400' : ''}`}>
              {kpis.empresas_com_divergencia}
            </span>
            <span className="text-sm text-slate-500">de {kpis.total_empresas} empresas</span>
          </div>
        </div>
      </div>

      {/* Saldos bancários do dia (verificação diária) */}
      <SaldosPanel />

      {/* Progresso da Equipe (Rotinas) */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-500" />
          Progresso de Rotinas — Hoje
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {equipe.map(membro => (
            <div key={membro.user_id} className="flex flex-col gap-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-medium">{membro.user_name}</span>
                <span className="text-slate-500">
                  {membro.concluidos} / {membro.total} ({membro.percentual}%)
                </span>
              </div>
              <div className="h-2.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${
                    membro.percentual === 100 ? 'bg-success-500' : 'bg-primary-500'
                  }`}
                  style={{ width: `${membro.percentual}%` }}
                ></div>
              </div>
            </div>
          ))}

          {equipe.length === 0 && (
            <div className="col-span-full py-8 text-center text-slate-500 flex flex-col items-center">
              <CheckCircle2 className="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
              <p>Nenhuma rotina pendente para hoje.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
