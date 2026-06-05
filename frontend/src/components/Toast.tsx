import { createContext, useCallback, useContext, useState } from 'react'
import type { ReactNode } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'

type Tipo = 'success' | 'error' | 'info'
interface Item { id: number; msg: string; tipo: Tipo }
const Ctx = createContext<{ toast: (m: string, t?: Tipo) => void }>({ toast: () => {} })
export const useToast = () => useContext(Ctx)

const META = {
  success: { Icon: CheckCircle2, cls: 'text-emerald-600' },
  error: { Icon: AlertCircle, cls: 'text-red-600' },
  info: { Icon: Info, cls: 'text-neutral-600' },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Item[]>([])
  const rm = useCallback((id: number) => setItems((p) => p.filter((t) => t.id !== id)), [])
  const toast = useCallback((msg: string, tipo: Tipo = 'info') => {
    const id = Date.now() + Math.random()
    setItems((p) => [...p, { id, msg, tipo }])
    setTimeout(() => rm(id), 3600)
  }, [rm])

  return (
    <Ctx.Provider value={{ toast }}>
      {children}
      <div className="fixed z-[100] bottom-20 lg:bottom-6 right-4 left-4 sm:left-auto flex flex-col gap-2 items-end pointer-events-none">
        {items.map((t) => {
          const { Icon, cls } = META[t.tipo]
          return (
            <div key={t.id} className="pointer-events-auto w-full sm:w-auto sm:max-w-sm bg-white border border-neutral-200 shadow-modal rounded-xl px-4 py-3 flex items-start gap-3 animate-slide-up">
              <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${cls}`} />
              <p className="text-sm text-neutral-800 flex-1">{t.msg}</p>
              <button onClick={() => rm(t.id)} className="text-neutral-400 hover:text-neutral-700"><X className="w-4 h-4" /></button>
            </div>
          )
        })}
      </div>
    </Ctx.Provider>
  )
}
