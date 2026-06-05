import { useEffect, useState } from 'react'
import { Building2, Landmark } from 'lucide-react'
import api from '../api'

interface Empresa { id: string; nome: string; cnpj: string; banco: string; grupo: string; ativo: boolean }

export function Empresas() {
  const [emp, setEmp] = useState<Empresa[]>([])
  const [loading, setLoading] = useState(true)
  useEffect(() => { api.get('/empresas').then((r) => setEmp(r.data)).catch(() => {}).finally(() => setLoading(false)) }, [])

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold tracking-tight">Empresas</h1><p className="text-neutral-500 mt-1">Diretório das empresas do grupo.</p></div>
      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{[1, 2, 3].map((i) => <div key={i} className="skeleton h-28" />)}</div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {emp.map((e) => (
            <div key={e.id} className="card card-hover p-5">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-neutral-100 grid place-items-center text-neutral-700"><Building2 className="w-5 h-5" /></div>
                <div className="min-w-0"><h3 className="font-semibold truncate">{e.nome}</h3><p className="text-xs text-neutral-500">{e.cnpj}</p></div>
              </div>
              <div className="flex items-center gap-2 mt-3">
                <span className="chip-neutral"><Landmark className="w-3 h-3" /> {e.banco}</span>
                <span className="chip-neutral uppercase">{e.grupo}</span>
                {e.ativo && <span className="chip-success">ativa</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
