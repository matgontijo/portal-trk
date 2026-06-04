// frontend/src/components/common/Badge.tsx
import type { ReactNode } from 'react'

type BadgeVariant = 'success' | 'warning' | 'danger' | 'primary' | 'default'

interface BadgeProps {
  children: ReactNode
  variant?: BadgeVariant
  icon?: ReactNode
  className?: string
}

export function Badge({ children, variant = 'default', icon, className = '' }: BadgeProps) {
  const baseClasses = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold whitespace-nowrap'
  
  const variants = {
    success: 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400',
    warning: 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400',
    danger: 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400',
    primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
    default: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
  }

  return (
    <span className={`${baseClasses} ${variants[variant]} ${className}`}>
      {icon && <span className="w-3.5 h-3.5 flex items-center justify-center">{icon}</span>}
      {children}
    </span>
  )
}
