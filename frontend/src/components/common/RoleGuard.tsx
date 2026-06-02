// frontend/src/components/common/RoleGuard.tsx
import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import type { UserRole } from '../../types/auth'

interface RoleGuardProps {
  children: ReactNode
  allowedRoles: UserRole[]
  redirectTo?: string
  fallback?: ReactNode
}

export function RoleGuard({ children, allowedRoles, redirectTo, fallback = null }: RoleGuardProps) {
  const { user } = useAuthStore()

  if (!user) {
    return redirectTo ? <Navigate to="/login" replace /> : <>{fallback}</>
  }

  if (!allowedRoles.includes(user.role)) {
    return redirectTo ? <Navigate to={redirectTo} replace /> : <>{fallback}</>
  }

  return <>{children}</>
}
