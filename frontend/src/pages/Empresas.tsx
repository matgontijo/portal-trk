// frontend/src/pages/Empresas.tsx
import { useState, useEffect } from 'react'
import { Building2, Search, Filter, AlertTriangle, CheckCircle2, ChevronRight, Lock } from 'lucide-react'
import api from '../services/api'
import { Badge } from '../components/common/Badge'
import { formatarMoeda, formatarCNPJ, formatarDataHora } from '../utils/formatters'
import { BANCO_LOGOS } from '../utils/constants'

export function Empresas() {
  const [empresas, setEmpresas] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [busca, setBusca] = useState('')

  useEffect(() => {
    carregarEmpresas()
  }, [])

  const carregarEmpresas = async () => {
    try {
      const response = await api.get('/empresas')
      setEmpresas(response.data)
    } catch (error) {
      console.error('Erro ao carregar empresas', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSync = async (empresaId: string) => {
    try {
      await api.post(`/saldos/${empresaId}/sync`)
      alert('Sincronização iniciada com sucesso. Os dados serão atualizados em breve.')
    } catch (error) {
      alert('Erro ao iniciar sincronização.')
    }
  }

  const empresasFiltradas = empresas.filter(e => 
    e.nome.toLowerCase().includes(busca.toLowerCase()) || 
    e.cnpj.includes(busca)
  )

  if (isLoading) {
    return <div className="animate-pulse h-96 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            Empresas Gerenciadas
          </h1>
          <p className="text-slate-500 mt-1">Visão geral de saldos, integrações e divergências.</p>
        </div>
        <button className="btn-primary">Nova Empresa</button>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Buscar por nome ou CNPJ..." 
            className="input pl-9"
            value={busca}
            onChange={e => setBusca(e.target.value)}
          />
        </div>
        <button className="btn-secondary hidden sm:flex">
          <Filter className="w-4 h-4" />
          Filtros
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {empresasFiltradas.map((emp) => {
          const banco = BANCO_LOGOS[emp.banco]
          const saldo = emp.saldo_atual
          
          return (
            <div key={emp.id} className="card overflow-hidden flex flex-col group">
              <div className="p-5 border-b border-slate-100 dark:border-slate-800 flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500">
                      {emp.grupo}
                    </span>
                    {saldo?.tem_divergencia && (
                      <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-danger-100 text-danger-600 flex items-center gap-1 pulse-danger">
                        Divergência
                      </span>
                    )}
                  </div>
                  <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 leading-tight">
                    {emp.nome}
                  </h3>
                  <p className="text-sm text-slate-500 mt-1">{formatarCNPJ(emp.cnpj)}</p>
                </div>

                <div 
                  className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white text-xs"
                  style={{ backgroundColor: banco?.cor || '#000' }}
                  title={banco?.nome}
                >
                  {banco?.nome.substring(0, 3).toUpperCase()}
                </div>
              </div>

              <div className="p-5 flex-1 bg-slate-50/50 dark:bg-slate-900/30">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <span className="block text-xs font-medium text-slate-500 mb-1">Saldo Banco</span>
                    <span className="font-bold text-slate-900 dark:text-slate-100">
                      {saldo ? formatarMoeda(saldo.saldo_banco) : 'R$ 0,00'}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs font-medium text-slate-500 mb-1">Saldo Omie</span>
                    <span className="font-bold text-slate-900 dark:text-slate-100">
                      {saldo ? formatarMoeda(saldo.saldo_omie) : 'R$ 0,00'}
                    </span>
                  </div>
                </div>

                {saldo && saldo.delta !== 0 && (
                  <div className={`p-3 rounded-lg text-sm flex items-start gap-2 ${saldo.tem_divergencia ? 'bg-danger-50 text-danger-700 dark:bg-danger-900/20' : 'bg-warning-50 text-warning-700 dark:bg-warning-900/20'}`}>
                    <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold mb-0.5">Delta: {formatarMoeda(saldo.delta)}</p>
                      <p className="text-xs opacity-80">{saldo.tipo_divergencia.replace(/_/g, ' ')}</p>
                    </div>
                  </div>
                )}

                {saldo && saldo.delta === 0 && (
                  <div className="p-3 rounded-lg text-sm flex items-center gap-2 bg-success-50 text-success-700 dark:bg-success-900/20">
                    <CheckCircle2 className="w-4 h-4" />
                    <span className="font-medium">Conciliado (Delta Zero)</span>
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center gap-1.5" title="Último Sync">
                  <Lock className="w-3.5 h-3.5" />
                  {saldo?.synced_at ? formatarDataHora(saldo.synced_at) : 'Nunca sincronizado'}
                </div>
                
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => handleSync(emp.id)}
                    className="text-primary-600 hover:underline font-medium"
                  >
                    Sync
                  </button>
                  <button className="text-slate-900 dark:text-slate-300 flex items-center hover:underline font-medium">
                    Detalhes <ChevronRight className="w-3 h-3 ml-0.5" />
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
