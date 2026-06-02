// frontend/src/pages/Configuracoes.tsx
import { useState, useEffect } from 'react'
import { Settings, RefreshCw, BrainCircuit, ShieldAlert, Server } from 'lucide-react'
import api from '../services/api'
import { Badge } from '../components/common/Badge'
import { formatarDataHora } from '../utils/formatters'

export function Configuracoes() {
  const [mlConfig, setMlConfig] = useState<any>(null)
  const [syncConfig, setSyncConfig] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    carregarConfigs()
  }, [])

  const carregarConfigs = async () => {
    try {
      const [mlRes, syncRes] = await Promise.all([
        api.get('/configuracoes/ml'),
        api.get('/configuracoes/sync')
      ])
      setMlConfig(mlRes.data)
      setSyncConfig(syncRes.data)
    } catch (error) {
      console.error('Erro ao carregar configurações', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRetreinar = async () => {
    if (!confirm('Iniciar re-treinamento do modelo ML? Isso rodará em background.')) return
    try {
      await api.post('/configuracoes/ml/re-treinar')
      alert('Re-treinamento iniciado!')
    } catch {
      alert('Erro ao iniciar re-treinamento')
    }
  }

  if (isLoading) return <div className="animate-pulse h-96 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          Configurações do Sistema
        </h1>
        <p className="text-slate-500 mt-1">Gerenciamento de infraestrutura, integrações e Inteligência Artificial.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* ML Engine Card */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-primary-100 text-primary-600 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Engine de Conciliação (IA)</h2>
              <p className="text-sm text-slate-500">Modelo RandomForest Classificador</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <span className="text-sm font-medium">Status</span>
              {mlConfig?.is_active ? <Badge variant="success">Ativo</Badge> : <Badge variant="warning">Inativo (Cold Start)</Badge>}
            </div>

            <div className="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <span className="text-sm font-medium">Último Treinamento</span>
              <span className="text-sm text-slate-600 dark:text-slate-300">
                {mlConfig?.treinado_em ? formatarDataHora(mlConfig.treinado_em) : 'Nunca'}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                <span className="block text-xs text-slate-500 mb-1">Precision</span>
                <span className="font-bold">{(mlConfig?.precision_score * 100 || 0).toFixed(1)}%</span>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                <span className="block text-xs text-slate-500 mb-1">Recall</span>
                <span className="font-bold">{(mlConfig?.recall_score * 100 || 0).toFixed(1)}%</span>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-center">
                <span className="block text-xs text-slate-500 mb-1">F1 Score</span>
                <span className="font-bold text-primary-600">{(mlConfig?.f1_score * 100 || 0).toFixed(1)}%</span>
              </div>
            </div>

            <button onClick={handleRetreinar} className="btn-secondary w-full mt-4">
              <RefreshCw className="w-4 h-4" />
              Forçar Re-treinamento Manual
            </button>
          </div>
        </div>

        {/* Sync Automation Card */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-slate-100 text-slate-600 dark:bg-slate-800 rounded-lg flex items-center justify-center">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Automação de Sync</h2>
              <p className="text-sm text-slate-500">Cron jobs do Celery Beat</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Sync Bancário 1 (Manhã)</label>
              <input type="time" className="input" defaultValue={syncConfig?.horario_1} disabled />
            </div>

            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Sync Bancário 2 (Noite)</label>
              <input type="time" className="input" defaultValue={syncConfig?.horario_2} disabled />
            </div>

            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Envio WhatsApp Diário</label>
              <input type="time" className="input" defaultValue={syncConfig?.whatsapp_horario} disabled />
            </div>

            <button className="btn-primary w-full opacity-50 cursor-not-allowed">
              <ShieldAlert className="w-4 h-4" />
              Salvar Alterações
            </button>
            <p className="text-xs text-center text-slate-400">Campos desabilitados na visualização inicial.</p>
          </div>
        </div>

      </div>
    </div>
  )
}
