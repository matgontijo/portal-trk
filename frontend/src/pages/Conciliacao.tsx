// frontend/src/pages/Conciliacao.tsx
import { useState, useEffect } from 'react'
import { AlertCircle, Check, X, Search, Filter, BrainCircuit } from 'lucide-react'
import api from '../services/api'
import { formatarMoeda, formatarData } from '../utils/formatters'
import { Badge } from '../components/common/Badge'

export function Conciliacao() {
  const [pendentes, setPendentes] = useState<any[]>([])
  const [estatisticas, setEstatisticas] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    carregarDados()
  }, [])

  const carregarDados = async () => {
    try {
      const [pendRes, estRes] = await Promise.all([
        api.get('/conciliacao/pendentes'),
        api.get('/conciliacao/estatisticas')
      ])
      setPendentes(pendRes.data)
      setEstatisticas(estRes.data)
    } catch (error) {
      console.error('Erro ao carregar conciliação', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDecisao = async (conciliacaoId: string, aceitar: boolean, omitId?: string) => {
    try {
      // Remover otimisticamente da tela
      setPendentes(prev => prev.filter(c => c.id !== conciliacaoId))
      
      const p = pendentes.find(c => c.id === conciliacaoId)
      if (!p) return

      await api.post('/conciliacao/decidir', {
        lancamento_banco_id: p.lancamento_banco.id,
        lancamento_omie_id: aceitar ? p.lancamento_omie?.id : null,
        aceitar,
        obs: aceitar ? "Confirmado via Portal TRK" : "Rejeitado pelo usuário"
      })

      // Atualizar estatísticas silenciosamente
      const estRes = await api.get('/conciliacao/estatisticas')
      setEstatisticas(estRes.data)

    } catch (error) {
      // Reverter se falhou
      carregarDados()
      console.error('Erro ao decidir match', error)
    }
  }

  if (isLoading) {
    return <div className="animate-pulse h-96 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            Conciliação Bancária
          </h1>
          <p className="text-slate-500 mt-1">Revise os matches sugeridos pela Inteligência Artificial.</p>
        </div>

        {estatisticas && (
          <div className="flex items-center gap-4 bg-white dark:bg-slate-900 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-800">
            <div className="text-center px-2 border-r border-slate-200 dark:border-slate-700">
              <div className="text-2xl font-bold text-primary-600">{estatisticas.taxa_automatica}%</div>
              <div className="text-xs text-slate-500 font-medium">Automação</div>
            </div>
            <div className="text-center px-2">
              <div className="text-2xl font-bold text-slate-700 dark:text-slate-200">{pendentes.length}</div>
              <div className="text-xs text-slate-500 font-medium">Pendentes</div>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Buscar por valor, empresa ou descrição..." 
            className="input pl-9"
          />
        </div>
        <button className="btn-secondary">
          <Filter className="w-4 h-4" />
          Filtros
        </button>
      </div>

      <div className="space-y-4">
        {pendentes.length === 0 ? (
          <div className="card p-12 text-center flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-success-100 text-success-600 dark:bg-success-900/30 rounded-full flex items-center justify-center mb-4">
              <Check className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Tudo conciliado!</h3>
            <p className="text-slate-500">Não há lançamentos pendentes de revisão no momento.</p>
          </div>
        ) : (
          pendentes.map((match) => (
            <div key={match.id} className="card overflow-hidden">
              {/* Card Header */}
              <div className="bg-slate-50 dark:bg-slate-800/50 px-5 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-semibold">{match.empresa_nome}</span>
                  <span className="text-slate-400 text-sm">|</span>
                  <span className="text-slate-500 text-sm">Ref: {formatarData(match.data_referencia)}</span>
                </div>
                
                {match.metodo.startsWith('ml_') && (
                  <Badge variant="primary" icon={<BrainCircuit className="w-3 h-3" />}>
                    Sugestão IA ({(match.confidence_score * 100).toFixed(0)}%)
                  </Badge>
                )}
                {match.metodo === 'rule_exact' && (
                  <Badge variant="warning">Revisão por divergência de datas</Badge>
                )}
              </div>

              {/* Card Body - Comparação */}
              <div className="p-5 flex flex-col md:flex-row gap-6 items-stretch">
                
                {/* Lado Banco */}
                <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 relative">
                  <div className="absolute top-0 left-0 w-1 h-full bg-slate-300 dark:bg-slate-600 rounded-l-lg"></div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Extrato Bancário</div>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium">{formatarData(match.lancamento_banco.data_lancamento)}</span>
                    <span className={`font-bold text-lg ${match.lancamento_banco.valor < 0 ? 'text-danger-600' : 'text-success-600'}`}>
                      {formatarMoeda(match.lancamento_banco.valor)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-300">
                    {match.lancamento_banco.descricao}
                  </p>
                </div>

                {/* Separador Visual VS */}
                <div className="hidden md:flex items-center justify-center -mx-3 z-10">
                  <div className="w-8 h-8 bg-slate-100 dark:bg-slate-800 rounded-full border border-slate-200 dark:border-slate-700 flex items-center justify-center text-xs font-bold text-slate-400">
                    VS
                  </div>
                </div>

                {/* Lado Omie */}
                {match.lancamento_omie ? (
                  <div className="flex-1 bg-white dark:bg-slate-900 border border-primary-200 dark:border-primary-900/50 rounded-lg p-4 relative shadow-[0_0_15px_rgba(99,102,241,0.05)]">
                    <div className="absolute top-0 left-0 w-1 h-full bg-primary-500 rounded-l-lg"></div>
                    <div className="text-xs font-bold text-primary-500 uppercase tracking-wider mb-3 flex items-center justify-between">
                      Lançamento Omie
                      <span className="text-[10px] bg-primary-50 text-primary-600 px-2 py-0.5 rounded">Possível Match</span>
                    </div>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium">{formatarData(match.lancamento_omie.data_lancamento)}</span>
                      <span className={`font-bold text-lg ${match.lancamento_omie.valor < 0 ? 'text-danger-600' : 'text-success-600'}`}>
                        {formatarMoeda(match.lancamento_omie.valor)}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300">
                      {match.lancamento_omie.descricao}
                    </p>
                  </div>
                ) : (
                  <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 border border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-4 flex flex-col items-center justify-center text-center">
                    <AlertCircle className="w-8 h-8 text-slate-400 mb-2" />
                    <p className="text-sm text-slate-500 font-medium">Nenhum lançamento correspondente encontrado no Omie.</p>
                  </div>
                )}
              </div>

              {/* Card Footer - Ações */}
              <div className="bg-slate-50 dark:bg-slate-800/50 px-5 py-3 border-t border-slate-200 dark:border-slate-800 flex justify-end gap-3">
                <button 
                  onClick={() => handleDecisao(match.id, false)}
                  className="btn-secondary !text-danger-600 hover:!bg-danger-50 dark:hover:!bg-danger-900/20"
                >
                  <X className="w-4 h-4" />
                  Rejeitar Match
                </button>
                {match.lancamento_omie && (
                  <button 
                    onClick={() => handleDecisao(match.id, true)}
                    className="btn-primary bg-success-500 hover:bg-success-600 focus:ring-success-500/50"
                  >
                    <Check className="w-4 h-4" />
                    Confirmar Conciliação
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
