// frontend/src/pages/Usuarios.tsx
import { useState, useEffect } from 'react'
import { Plus, Mail, Shield, Trash2, X } from 'lucide-react'
import api from '../services/api'
import { Badge } from '../components/common/Badge'
import { useAuthStore } from '../store/authStore'
import type { User, UserRole } from '../types/auth'
import { formatarDataHora } from '../utils/formatters'

export function Usuarios() {
  const { user } = useAuthStore()
  const [usuarios, setUsuarios] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({ name: '', email: '', password: '', role: 'funcionario' as UserRole, sector: '' })
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    carregarUsuarios()
  }, [])

  const carregarUsuarios = async () => {
    try {
      const response = await api.get('/users')
      setUsuarios(response.data)
    } catch (error) {
      console.error('Erro ao carregar usuários', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      await api.post('/users', formData)
      setIsModalOpen(false)
      setFormData({ name: '', email: '', password: '', role: 'funcionario', sector: '' })
      carregarUsuarios()
    } catch (error: any) {
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) {
        const msgs = detail.map((err: any) => {
          // Remove o prefixo "Value error, " que o Pydantic adiciona
          return err.msg.replace('Value error, ', '')
        })
        alert(msgs.join('\n'))
      } else {
        alert(detail || 'Erro ao criar usuário')
      }
    } finally {
      setIsSaving(false)
    }
  }

  const handleDesativar = async (id: string) => {
    if(!confirm('Deseja realmente desativar este usuário?')) return
    try {
      await api.patch(`/users/${id}/desativar`)
      carregarUsuarios()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao desativar usuário')
    }
  }

  if (isLoading) return <div className="animate-pulse h-96 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            Gestão de Usuários
          </h1>
          <p className="text-slate-500 mt-1">Gerencie os acessos, cargos e permissões da equipe.</p>
        </div>

        <button onClick={() => setIsModalOpen(true)} className="btn-primary">
          <Plus className="w-4 h-4" /> Novo Usuário
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-xs uppercase font-semibold text-slate-500">
              <tr>
                <th className="px-6 py-4">Usuário</th>
                <th className="px-6 py-4">Cargo & Setor</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Criado em</th>
                <th className="px-6 py-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {usuarios.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold">
                        {u.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">{u.name}</div>
                        <div className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                          <Mail className="w-3 h-3" /> {u.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col items-start gap-1">
                      {u.role === 'admin' && <Badge variant="primary" icon={<Shield className="w-3 h-3"/>}>Admin</Badge>}
                      {u.role === 'gestor' && <Badge variant="warning">Gestor</Badge>}
                      {u.role === 'funcionario' && <Badge variant="success">Funcionário</Badge>}
                      {u.sector && <span className="text-xs text-slate-400">{u.sector}</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {u.is_active ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Ativo
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Inativo
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-slate-500 text-xs">
                    {formatarDataHora(u.created_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {u.id !== user?.id && u.is_active && (
                      <button onClick={() => handleDesativar(u.id)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Novo Usuário */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-slide-up">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">Novo Usuário</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nome Completo</label>
                <input required type="text" className="input" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="João da Silva" />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">E-mail Corporativo</label>
                <input required type="email" className="input" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="joao@grupotrk.com" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Senha Provisória</label>
                <input required type="password" className="input" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="••••••••" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Nível de Acesso</label>
                  <select className="input" value={formData.role} onChange={e => setFormData({...formData, role: e.target.value as UserRole})}>
                    <option value="funcionario">Funcionário (Operação)</option>
                    {user?.role === 'admin' && <option value="gestor">Gestor (Líder)</option>}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Setor</label>
                  <input type="text" className="input" value={formData.sector} onChange={e => setFormData({...formData, sector: e.target.value})} placeholder="Ex: BPO" />
                </div>
              </div>

              <div className="pt-4 flex items-center justify-end gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">Cancelar</button>
                <button type="submit" disabled={isSaving} className="btn-primary">
                  {isSaving ? 'Salvando...' : 'Criar Usuário'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
