import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'

const brl = (v: number) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

interface Saldo {
  id: string; empresa_nome: string; saldo_banco: number; saldo_omie: number; delta: number; tem_divergencia: boolean
}

export function Saldos() {
  const { pode } = useAuth()
  const [saldos, setSaldos] = useState<Saldo[]>([])
  const [loading, setLoading] = useState(true)
  const [sincronizando, setSincronizando] = useState(false)

  const carregar = useCallback(async () => {
    try { setSaldos((await api.get('/saldos')).data) } finally { setLoading(false) }
  }, [])
  useEffect(() => { carregar() }, [carregar])

  const sincronizar = async () => {
    setSincronizando(true)
    try { await api.post('/saldos/sync'); await carregar() } finally { setSincronizando(false) }
  }

  const totalCaixa = saldos.reduce((s, x) => s + x.saldo_banco, 0)
  const comDiverg = saldos.filter((s) => s.tem_divergencia).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Saldos do Dia</h1>
          <p className="text-neutral-500 mt-1">{saldos.length} contas · {brl(totalCaixa)} em caixa · {comDiverg > 0 ? <span className="text-danger-600 font-medium">{comDiverg} divergência(s)</span> : <span className="text-emerald-600">tudo conciliado</span>}</p>
        </div>
        {pode('saldos', 'editar') && (
          <button onClick={sincronizar} disabled={sincronizando} className="btn-secondary">
            <RefreshCw className={`w-4 h-4 ${sincronizando && 'animate-spin'}`} /> {sincronizando ? 'Sincronizando…' : 'Atualizar saldos'}
          </button>
        )}
      </div>

      <div className="card divide-y divide-neutral-100">
        {loading ? (
          <div className="p-4 space-y-2">{[1, 2, 3].map((i) => <div key={i} className="skeleton h-12" />)}</div>
        ) : saldos.length === 0 ? (
          <div className="p-10 text-center text-neutral-500">Sem saldos ainda. Clique em <strong>Atualizar saldos</strong>.</div>
        ) : saldos.map((s) => (
          <div key={s.id} className="flex items-center justify-between p-4 gap-4">
            <div className="min-w-0">
              <p className="font-medium truncate">{s.empresa_nome}</p>
              <span className={s.tem_divergencia ? 'chip-danger mt-1' : 'chip-success mt-1'}>
                {s.tem_divergencia ? <><AlertTriangle className="w-3 h-3" /> Δ {brl(s.delta)} vs Omie</> : <><CheckCircle2 className="w-3 h-3" /> Conciliado</>}
              </span>
            </div>
            <p className="font-semibold tabular-nums shrink-0">{brl(s.saldo_banco)}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
