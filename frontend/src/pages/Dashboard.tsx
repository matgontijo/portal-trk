import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Wallet, Building2, AlertTriangle, Users, Network, ArrowRight } from 'lucide-react'
import api from '../api'
import { useAuth } from '../store/auth'
import { Icon } from '../icons'
import type { Modulo } from '../types'

const brl = (v: number) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export function Dashboard() {
  const { usuario, modulos } = useAuth()
  const [data, setData] = useState<any>(null)
  const [catalogo, setCatalogo] = useState<Modulo[]>([])

  useEffect(() => {
    api.get('/meta/dashboard').then((r) => setData(r.data)).catch(() => {})
    api.get('/meta/modulos').then((r) => setCatalogo(r.data.modulos)).catch(() => {})
  }, [])

  const hora = new Date().getHours()
  const saudacao = hora < 12 ? 'Bom dia' : hora < 18 ? 'Boa tarde' : 'Boa noite'
  const fin = data?.financeiro
  const atalhos = catalogo.filter((m) => modulos.includes(m.key) && m.key !== 'dashboard').slice(0, 6)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{saudacao}, {usuario?.nome.split(' ')[0]} 👋</h1>
        <p className="text-neutral-500 mt-1">
          {usuario?.departamento_nome ? `Setor ${usuario.departamento_nome}` : usuario?.cargo} · você tem acesso a {modulos.length} módulos.
        </p>
      </div>

      {/* KPIs financeiros — só aparecem para quem tem o módulo */}
      {fin && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Kpi label="Total em Caixa" valor={brl(fin.total_em_caixa)} Icon={Wallet} cor="text-emerald-600 bg-emerald-50" />
          <Kpi label="Empresas" valor={String(fin.empresas)} Icon={Building2} cor="text-neutral-700 bg-neutral-100" />
          <Kpi label="Divergências" valor={String(fin.divergencias)} Icon={AlertTriangle}
            cor={fin.divergencias > 0 ? 'text-danger-600 bg-danger-50' : 'text-emerald-600 bg-emerald-50'} />
        </div>
      )}

      {/* KPIs de gestão — diretoria/admin */}
      {(data?.total_usuarios != null && (usuario?.cargo === 'diretor' || modulos.includes('usuarios'))) && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Kpi label="Pessoas" valor={String(data.total_usuarios)} Icon={Users} cor="text-neutral-700 bg-neutral-100" />
          <Kpi label="Setores" valor={String(data.total_departamentos)} Icon={Network} cor="text-neutral-700 bg-neutral-100" />
        </div>
      )}

      {/* Atalhos para os módulos acessíveis */}
      <div>
        <h2 className="text-sm font-bold text-neutral-400 uppercase tracking-wider mb-3">Seus módulos</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {atalhos.map((m) => (
            <Link key={m.key} to={m.key === 'dashboard' ? '/' : `/${m.key}`} className="card card-hover p-4 flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-neutral-100 grid place-items-center text-neutral-700 group-hover:bg-neutral-900 group-hover:text-white transition">
                <Icon name={m.icone} className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-sm truncate">{m.label}</p>
                <p className="text-xs text-neutral-500 truncate">{m.descricao}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-neutral-300 group-hover:text-neutral-900 transition" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

function Kpi({ label, valor, Icon, cor }: { label: string; valor: string; Icon: any; cor: string }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">{label}</span>
        <span className={`w-8 h-8 rounded-full grid place-items-center ${cor}`}><Icon className="w-4 h-4" /></span>
      </div>
      <p className="text-2xl font-bold mt-2">{valor}</p>
    </div>
  )
}
