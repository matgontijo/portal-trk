// frontend/src/components/saldos/SaldosPanel.tsx
// Painel de saldos bancários por empresa com status de sync e ação de atualizar.
// Consome GET /saldos, GET /saldos/status e POST /saldos/sync-todas.

import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, CheckCircle2, AlertTriangle, Clock, HelpCircle } from 'lucide-react'
import api from '../../services/api'
import { formatarMoeda } from '../../utils/formatters'
import { useToast } from '../common/Toast'

interface Saldo {
  empresa_id: string
  empresa_nome: string
  saldo_banco: number
  saldo_omie: number
  delta: number
  tem_divergencia: boolean
  tipo_divergencia: string
  data_referencia: string
  synced_at: string
}

interface SyncStatus {
  empresa_id: string
  empresa_nome: string
  ultimo_sync: string | null
  status: 'ok' | 'divergencia' | 'desatualizado' | 'pendente' | string
  mensagem: string | null
}

const STATUS_META: Record<string, { label: string; cls: string; Icon: typeof CheckCircle2 }> = {
  ok: { label: 'Atualizado', cls: 'text-success-600 bg-success-100 dark:bg-success-900/40', Icon: CheckCircle2 },
  divergencia: { label: 'Divergência', cls: 'text-danger-600 bg-danger-100 dark:bg-danger-900/40', Icon: AlertTriangle },
  desatualizado: { label: 'Desatualizado', cls: 'text-warning-600 bg-warning-100 dark:bg-warning-900/40', Icon: Clock },
  pendente: { label: 'Pendente', cls: 'text-slate-500 bg-slate-100 dark:bg-slate-800', Icon: HelpCircle },
}

function tempoRelativo(iso: string | null): string {
  if (!iso) return 'nunca'
  const diff = Date.now() - new Date(iso).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return 'agora'
  if (min < 60) return `há ${min} min`
  const h = Math.floor(min / 60)
  if (h < 24) return `há ${h}h`
  return `há ${Math.floor(h / 24)}d`
}

export function SaldosPanel() {
  const [saldos, setSaldos] = useState<Saldo[]>([])
  const [status, setStatus] = useState<Record<string, SyncStatus>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const { toast } = useToast()

  const carregar = useCallback(async () => {
    try {
      const [saldosRes, statusRes] = await Promise.all([
        api.get<Saldo[]>('/saldos'),
        api.get<SyncStatus[]>('/saldos/status'),
      ])
      setSaldos(saldosRes.data)
      const map: Record<string, SyncStatus> = {}
      statusRes.data.forEach((s) => { map[s.empresa_id] = s })
      setStatus(map)
    } catch (e) {
      console.error('Erro ao carregar saldos:', e)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { carregar() }, [carregar])

  const sincronizarTudo = async () => {
    setIsSyncing(true)
    try {
      await api.post('/saldos/sync-todas')
      toast('Sincronização iniciada — atualizando saldos…', 'info')
      // O sync roda em background (Celery); recarrega após um intervalo.
      setTimeout(() => { carregar(); setIsSyncing(false); toast('Saldos atualizados', 'success') }, 4000)
    } catch (e) {
      console.error('Erro ao sincronizar:', e)
      toast('Não foi possível iniciar a sincronização', 'error')
      setIsSyncing(false)
    }
  }

  const comDivergencia = saldos.filter((s) => s.tem_divergencia).length

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-lg font-semibold">Saldos do Dia</h2>
          <p className="text-sm text-slate-500">
            {saldos.length} contas · {comDivergencia > 0
              ? <span className="text-danger-600 font-medium">{comDivergencia} com divergência</span>
              : <span className="text-success-600">todas conciliadas</span>}
          </p>
        </div>
        <button
          onClick={sincronizarTudo}
          disabled={isSyncing}
          className="btn-secondary flex items-center gap-2 text-sm disabled:opacity-60"
        >
          <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
          {isSyncing ? 'Sincronizando…' : 'Atualizar saldos'}
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-2 animate-pulse">
          {[1, 2, 3].map((i) => <div key={i} className="h-14 bg-slate-100 dark:bg-slate-800 rounded-lg" />)}
        </div>
      ) : saldos.length === 0 ? (
        <div className="py-8 text-center text-slate-500">
          Nenhum saldo sincronizado ainda. Clique em <strong>Atualizar saldos</strong>.
        </div>
      ) : (
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {saldos.map((s) => {
            const st = status[s.empresa_id]
            const meta = STATUS_META[st?.status ?? 'pendente'] ?? STATUS_META.pendente
            const Icon = meta.Icon
            return (
              <div key={s.empresa_id} className="flex items-center justify-between py-3 gap-4">
                <div className="min-w-0">
                  <p className="font-medium truncate">{s.empresa_nome}</p>
                  <span className={`inline-flex items-center gap-1 mt-0.5 px-2 py-0.5 rounded-full text-xs font-medium ${meta.cls}`}>
                    <Icon className="w-3 h-3" />
                    {meta.label} · {tempoRelativo(st?.ultimo_sync ?? s.synced_at)}
                  </span>
                </div>
                <div className="text-right shrink-0">
                  <p className="font-semibold tabular-nums">{formatarMoeda(s.saldo_banco)}</p>
                  {s.tem_divergencia && (
                    <p className="text-xs text-danger-600 tabular-nums">
                      Δ {formatarMoeda(s.delta)} vs Omie
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
