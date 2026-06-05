// Mapa de ícones (lucide) por nome — permite ícones dinâmicos vindos do backend.
import {
  LayoutDashboard, CheckSquare, GitBranch, KanbanSquare, Sparkles, Zap,
  Wallet, ArrowRightLeft, Landmark, Building2, Users, TrendingUp,
  FileBarChart, UserCog, Network, Settings, Crown, Workflow, HelpCircle,
} from 'lucide-react'
import type { ComponentType } from 'react'

const MAP: Record<string, ComponentType<{ className?: string }>> = {
  LayoutDashboard, CheckSquare, GitBranch, KanbanSquare, Sparkles, Zap,
  Wallet, ArrowRightLeft, Landmark, Building2, Users, TrendingUp,
  FileBarChart, UserCog, Network, Settings, Crown, Workflow,
}

export function Icon({ name, className }: { name: string; className?: string }) {
  const Cmp = MAP[name] ?? HelpCircle
  return <Cmp className={className} />
}
