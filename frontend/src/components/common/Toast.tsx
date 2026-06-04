// frontend/src/components/common/Toast.tsx
// Sistema de toasts leve (sem dependências) — substitui alert() por feedback elegante.
// Uso: const { toast } = useToast(); toast('Salvo!', 'success')

import { createContext, useCallback, useContext, useState } from 'react'
import type { ReactNode } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'

type ToastType = 'success' | 'error' | 'info'
interface ToastItem { id: number; message: string; type: ToastType }

interface ToastCtx { toast: (message: string, type?: ToastType) => void }

const Ctx = createContext<ToastCtx>({ toast: () => {} })

export const useToast = () => useContext(Ctx)

const META: Record<ToastType, { Icon: typeof Info; cls: string }> = {
  success: { Icon: CheckCircle2, cls: 'text-success-600' },
  error: { Icon: AlertCircle, cls: 'text-danger-600' },
  info: { Icon: Info, cls: 'text-neutral-600' },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])

  const remover = useCallback((id: number) => {
    setItems((p) => p.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Date.now() + Math.random()
    setItems((p) => [...p, { id, message, type }])
    setTimeout(() => remover(id), 3800)
  }, [remover])

  return (
    <Ctx.Provider value={{ toast }}>
      {children}
      {/* Container — acima da bottom nav no mobile */}
      <div className="fixed z-[100] bottom-20 lg:bottom-6 right-4 left-4 sm:left-auto flex flex-col gap-2 items-end pointer-events-none">
        {items.map((t) => {
          const { Icon, cls } = META[t.type]
          return (
            <div key={t.id}
              className="pointer-events-auto w-full sm:w-auto sm:max-w-sm bg-white border border-neutral-200 shadow-modal rounded-xl px-4 py-3 flex items-start gap-3 animate-slide-up">
              <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${cls}`} />
              <p className="text-sm text-neutral-800 flex-1">{t.message}</p>
              <button onClick={() => remover(t.id)} className="text-neutral-400 hover:text-neutral-700 shrink-0">
                <X className="w-4 h-4" />
              </button>
            </div>
          )
        })}
      </div>
    </Ctx.Provider>
  )
}
