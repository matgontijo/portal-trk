import { useEffect, useState } from 'react'
import { Sparkles } from 'lucide-react'
import api from '../api'
import { Icon } from '../icons'
import type { Modulo } from '../types'

// Tela elegante para módulos cujo conteúdo completo será portado do app original.
export function ModuloEmBreve({ modulo }: { modulo: string }) {
  const [info, setInfo] = useState<Modulo | null>(null)
  useEffect(() => {
    api.get('/meta/modulos').then((r) => setInfo(r.data.modulos.find((m: Modulo) => m.key === modulo) ?? null)).catch(() => {})
  }, [modulo])

  return (
    <div className="max-w-xl mx-auto py-10 text-center">
      <div className="w-16 h-16 mx-auto rounded-2xl bg-neutral-900 text-white grid place-items-center mb-5">
        <Icon name={info?.icone ?? 'Sparkles'} className="w-8 h-8" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight">{info?.label ?? modulo}</h1>
      <p className="text-neutral-500 mt-2">{info?.descricao}</p>
      <div className="chip-neutral mt-5 inline-flex"><Sparkles className="w-3.5 h-3.5" /> Módulo liberado para o seu setor</div>
      <div className="card p-6 mt-6 text-left">
        <p className="text-sm text-neutral-600">
          Este módulo já está <strong>visível e desbloqueado</strong> para o seu perfil — o controle de acesso por setor está funcionando.
          A experiência completa deste módulo será conectada na próxima fase, reaproveitando as funções já testadas do sistema.
        </p>
      </div>
    </div>
  )
}
