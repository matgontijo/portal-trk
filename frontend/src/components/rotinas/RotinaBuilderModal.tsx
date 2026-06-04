// frontend/src/components/rotinas/RotinaBuilderModal.tsx
import { useState, useEffect } from 'react'
import { X, Trash2, GripVertical, CheckSquare, Type, UploadCloud } from 'lucide-react'
import api from '../../services/api'
import type { User } from '../../types/auth'

interface BlockConfig {
  id: string
  tipo: 'checkbox' | 'text_short' | 'file_upload'
  label: string
  is_required: boolean
}

interface RotinaBuilderProps {
  onClose: () => void
  onSave: () => void
  rotinaEdit?: any // Se passado, é edição
}

export function RotinaBuilderModal({ onClose, onSave, rotinaEdit }: RotinaBuilderProps) {
  const [usuarios, setUsuarios] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  // Formulário Principal
  const [nome, setNome] = useState(rotinaEdit?.nome || '')
  const [descricao, setDescricao] = useState(rotinaEdit?.descricao || '')
  const [categoria, setCategoria] = useState(rotinaEdit?.categoria || 'geral')
  const [diasSemana, setDiasSemana] = useState<number[]>(rotinaEdit?.dias_semana || [1, 2, 3, 4, 5]) // Seg a Sex padrão

  // Recorrência estilo Todoist
  const [tipoRecorrencia, setTipoRecorrencia] = useState<string>(rotinaEdit?.tipo_recorrencia || 'semanal')
  const recCfgInit = rotinaEdit?.recorrencia_config || {}
  const [cadaDias, setCadaDias] = useState<number>(recCfgInit.cada_dias || 2)
  const [diasMes, setDiasMes] = useState<string>((recCfgInit.dias_mes || []).join(', '))
  const [ultimoDia, setUltimoDia] = useState<boolean>(!!recCfgInit.ultimo_dia)
  const [apenasUteis, setApenasUteis] = useState<boolean>(!!recCfgInit.apenas_dias_uteis)

  // Array de IDs selecionados
  const [userIds, setUserIds] = useState<string[]>(
    rotinaEdit?.atribuicoes ? rotinaEdit.atribuicoes.map((a:any) => a.user_id) : []
  )

  // Blocos dinâmicos
  const [blocos, setBlocos] = useState<BlockConfig[]>(
    rotinaEdit?.blocos ? rotinaEdit.blocos.map((b:any) => ({...b, id: b.id || Math.random().toString()})) : 
    [{ id: 'initial-1', tipo: 'checkbox', label: 'Conferir extrato bancário', is_required: true }]
  )
  
  const [draggedIdx, setDraggedIdx] = useState<number | null>(null)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await api.get('/users')
        // Mostrar apenas funcionários e gestores ativos
        setUsuarios(res.data.filter((u: User) => u.is_active && u.role === 'funcionario'))
      } catch (err) {
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchUsers()
  }, [])

  const toggleDia = (dia: number) => {
    setDiasSemana(prev => prev.includes(dia) ? prev.filter(d => d !== dia) : [...prev, dia].sort())
  }

  const toggleUser = (id: string) => {
    setUserIds(prev => prev.includes(id) ? prev.filter(u => u !== id) : [...prev, id])
  }

  const addBloco = (tipo: 'checkbox' | 'text_short' | 'file_upload') => {
    setBlocos([...blocos, { id: Math.random().toString(), tipo, label: '', is_required: true }])
  }

  const updateBloco = (id: string, field: keyof BlockConfig, value: any) => {
    setBlocos(blocos.map(b => b.id === id ? { ...b, [field]: value } : b))
  }

  const removeBloco = (id: string) => {
    setBlocos(blocos.filter(b => b.id !== id))
  }

  const handleDragStart = (idx: number) => setDraggedIdx(idx)
  
  const handleDragEnter = (idx: number) => {
    if (draggedIdx === null || draggedIdx === idx) return
    const newBlocos = [...blocos]
    const item = newBlocos.splice(draggedIdx, 1)[0]
    newBlocos.splice(idx, 0, item)
    setDraggedIdx(idx)
    setBlocos(newBlocos)
  }

  const handleDragEnd = () => setDraggedIdx(null)

  const handleSave = async () => {
    if (!nome.trim()) return alert('Dê um nome à rotina.')
    if (tipoRecorrencia === 'semanal' && diasSemana.length === 0) return alert('Selecione pelo menos um dia da semana.')
    if (userIds.length === 0) return alert('Atribua a pelo menos um funcionário.')
    if (blocos.length === 0 || blocos.some(b => !b.label.trim())) return alert('Todos os blocos precisam de um título.')

    setIsSaving(true)
    try {
      const recorrencia_config: Record<string, unknown> = {}
      if (tipoRecorrencia === 'diaria' && apenasUteis) recorrencia_config.apenas_dias_uteis = true
      if (tipoRecorrencia === 'intervalo') recorrencia_config.cada_dias = cadaDias
      if (tipoRecorrencia === 'mensal') {
        if (ultimoDia) recorrencia_config.ultimo_dia = true
        else recorrencia_config.dias_mes = diasMes.split(',').map(s => Number(s.trim())).filter(n => n >= 1 && n <= 31)
      }

      const payload = {
        nome,
        descricao,
        dias_semana: diasSemana,
        tipo_recorrencia: tipoRecorrencia,
        recorrencia_config,
        categoria,
        user_ids: userIds,
        alertas: [],
        blocos: blocos.map((b, i) => ({
          tipo: b.tipo,
          label: b.label,
          is_required: b.is_required,
          config: {},
          posicao: i
        }))
      }

      if (rotinaEdit?.id) {
        await api.put(`/rotinas/${rotinaEdit.id}`, payload)
      } else {
        await api.post('/rotinas/', payload)
      }
      onSave()
    } catch (error) {
      alert('Erro ao salvar rotina. Tente novamente.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-neutral-50 rounded-2xl shadow-2xl w-full max-w-4xl max-h-full flex flex-col overflow-hidden animate-scale-in">
        
        {/* Header Modal */}
        <div className="flex-shrink-0 px-6 py-4 bg-white border-b border-neutral-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-neutral-900">{rotinaEdit ? 'Editar Rotina' : 'Nova Rotina Operacional'}</h2>
            <p className="text-sm text-neutral-500">Configure o fluxo e as fases (blocos) dessa operação diária.</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-neutral-100 text-neutral-500 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Coluna Esquerda: Configs Gerais */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white p-5 rounded-xl border border-neutral-200 shadow-sm space-y-4">
                <h3 className="font-semibold text-neutral-900 flex items-center gap-2">Configurações Gerais</h3>
                
                <div>
                  <label className="block text-xs font-semibold text-neutral-600 uppercase mb-1">Nome da Rotina</label>
                  <input type="text" className="input" placeholder="Ex: Conciliação Matinal" value={nome} onChange={e => setNome(e.target.value)} />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-600 uppercase mb-1">Categoria (Cor)</label>
                  <select className="input" value={categoria} onChange={e => setCategoria(e.target.value)}>
                    <option value="geral">Geral (Cinza)</option>
                    <option value="banco">Bancário (Azul Escuro)</option>
                    <option value="omie">Omie ERP (Azul Claro)</option>
                    <option value="drive">Google Drive (Laranja)</option>
                    <option value="pipe">Pipefy (Roxo)</option>
                    <option value="urgente">Urgente (Vermelho)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-600 uppercase mb-1">Descrição</label>
                  <textarea className="input min-h-[80px] resize-none" placeholder="Instruções gerais..." value={descricao} onChange={e => setDescricao(e.target.value)} />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-neutral-600 uppercase mb-2">Recorrência</label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {[
                      { id: 'diaria', label: 'Diária' },
                      { id: 'semanal', label: 'Semanal' },
                      { id: 'intervalo', label: 'A cada X dias' },
                      { id: 'mensal', label: 'Mensal' },
                    ].map(opt => (
                      <button key={opt.id} onClick={() => setTipoRecorrencia(opt.id)}
                        className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${tipoRecorrencia === opt.id ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200'}`}>
                        {opt.label}
                      </button>
                    ))}
                  </div>

                  {tipoRecorrencia === 'semanal' && (
                    <div className="flex flex-wrap gap-2">
                      {['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'].map((d, i) => {
                        const diaInt = i + 1
                        const isSel = diasSemana.includes(diaInt)
                        return (
                          <button key={d} onClick={() => toggleDia(diaInt)} className={`w-9 h-9 rounded-full text-xs font-bold transition-colors ${isSel ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200'}`}>
                            {d}
                          </button>
                        )
                      })}
                    </div>
                  )}

                  {tipoRecorrencia === 'diaria' && (
                    <label className="flex items-center gap-2 text-sm text-neutral-600">
                      <input type="checkbox" checked={apenasUteis} onChange={e => setApenasUteis(e.target.checked)} />
                      Apenas dias úteis (seg–sex)
                    </label>
                  )}

                  {tipoRecorrencia === 'intervalo' && (
                    <div className="flex items-center gap-2 text-sm text-neutral-600">
                      Repetir a cada
                      <input type="number" min={1} value={cadaDias} onChange={e => setCadaDias(Number(e.target.value))} className="input w-20 py-1.5" />
                      dia(s)
                    </div>
                  )}

                  {tipoRecorrencia === 'mensal' && (
                    <div className="space-y-2">
                      <label className="flex items-center gap-2 text-sm text-neutral-600">
                        <input type="checkbox" checked={ultimoDia} onChange={e => setUltimoDia(e.target.checked)} />
                        Todo último dia do mês
                      </label>
                      {!ultimoDia && (
                        <div className="text-sm text-neutral-600">
                          Dias do mês (ex.: 1, 15):
                          <input value={diasMes} onChange={e => setDiasMes(e.target.value)} placeholder="1, 15" className="input mt-1 py-1.5" />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-white p-5 rounded-xl border border-neutral-200 shadow-sm space-y-4">
                <h3 className="font-semibold text-neutral-900">Atribuição de Equipe</h3>
                {isLoading ? (
                  <div className="text-sm text-neutral-400">Carregando equipe...</div>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                    {usuarios.map(u => (
                      <label key={u.id} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${userIds.includes(u.id) ? 'border-neutral-900 bg-neutral-50' : 'border-neutral-200 hover:bg-neutral-50'}`}>
                        <input type="checkbox" className="w-4 h-4 accent-neutral-900" checked={userIds.includes(u.id)} onChange={() => toggleUser(u.id)} />
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-neutral-200 flex items-center justify-center text-xs font-bold text-neutral-600">{u.name.charAt(0)}</div>
                          <span className="text-sm font-medium text-neutral-800">{u.name}</span>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Coluna Direita: Builder de Fases (Blocos) */}
            <div className="lg:col-span-2 flex flex-col h-full min-h-[400px]">
              <div className="bg-white flex-1 p-6 rounded-xl border border-neutral-200 shadow-sm flex flex-col">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-neutral-900">Passo a Passo (Fases)</h3>
                    <p className="text-xs text-neutral-500 mt-1">Arraste os blocos para reordenar. O funcionário deverá preenchê-los na ordem.</p>
                  </div>
                </div>

                <div className="flex-1 space-y-4 overflow-y-auto pr-2 pb-4">
                  {blocos.map((bloco, idx) => (
                    <div 
                      key={bloco.id} 
                      draggable
                      onDragStart={() => handleDragStart(idx)}
                      onDragEnter={() => handleDragEnter(idx)}
                      onDragEnd={handleDragEnd}
                      onDragOver={(e) => e.preventDefault()}
                      className={`flex items-start gap-4 p-5 bg-white border-2 rounded-xl relative group transition-all ${draggedIdx === idx ? 'opacity-40 border-dashed border-neutral-400' : 'border-neutral-200 hover:border-primary-300 shadow-sm'}`}
                    >
                      <div className="mt-2 text-neutral-300 cursor-grab active:cursor-grabbing hover:text-primary-500 transition-colors">
                        <GripVertical className="w-6 h-6" />
                      </div>
                      
                      <div className="flex-1 space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {bloco.tipo === 'checkbox' && <span className="bg-slate-100 p-1.5 rounded-lg text-slate-700 shadow-sm"><CheckSquare className="w-4 h-4"/></span>}
                            {bloco.tipo === 'text_short' && <span className="bg-blue-50 p-1.5 rounded-lg text-blue-600 shadow-sm"><Type className="w-4 h-4"/></span>}
                            {bloco.tipo === 'file_upload' && <span className="bg-orange-50 p-1.5 rounded-lg text-orange-600 shadow-sm"><UploadCloud className="w-4 h-4"/></span>}
                            <span className="text-sm font-bold text-neutral-800">
                              FASE {idx + 1}
                              <span className="text-xs font-medium text-neutral-400 ml-2 font-normal">
                                ({bloco.tipo === 'checkbox' ? 'Check' : bloco.tipo === 'text_short' ? 'Texto' : 'Upload'})
                              </span>
                            </span>
                          </div>
                          <button onClick={() => removeBloco(bloco.id)} className="text-neutral-400 hover:text-red-500 bg-neutral-50 hover:bg-red-50 p-1.5 rounded-md transition-colors opacity-0 group-hover:opacity-100">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        
                        <input 
                          type="text" 
                          placeholder="Ex: Verificar se todos os caixas foram fechados..." 
                          className="w-full bg-slate-50 border border-slate-200 px-3 py-2 text-sm font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
                          value={bloco.label}
                          onChange={(e) => updateBloco(bloco.id, 'label', e.target.value)}
                        />
                        
                        <div className="flex items-center justify-between pt-1">
                          <label className="flex items-center gap-2 cursor-pointer group/req">
                            <input 
                              type="checkbox" 
                              className="w-4 h-4 accent-primary-600 rounded" 
                              checked={bloco.is_required} 
                              onChange={(e) => updateBloco(bloco.id, 'is_required', e.target.checked)} 
                            />
                            <span className="text-xs font-semibold text-neutral-500 group-hover/req:text-neutral-800 transition-colors">Campo Obrigatório</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  ))}
                  {blocos.length === 0 && (
                    <div className="text-center py-12 text-neutral-400 border-2 border-dashed border-neutral-200 rounded-xl bg-neutral-50/50">
                      Nenhuma fase adicionada.<br/>Clique nos botões abaixo para construir a rotina.
                    </div>
                  )}

                  {/* Área de Adicionar Novos Blocos */}
                  <div className="mt-6 pt-6 border-t border-dashed border-neutral-200">
                    <p className="text-xs font-bold text-neutral-400 uppercase text-center mb-4">Adicionar nova fase</p>
                    <div className="grid grid-cols-3 gap-3">
                      <button onClick={() => addBloco('checkbox')} className="flex flex-col items-center justify-center gap-2 p-3 rounded-xl border border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50 transition-all text-slate-700 shadow-sm">
                        <CheckSquare className="w-5 h-5 text-slate-500"/> 
                        <span className="text-xs font-semibold">Check</span>
                      </button>
                      <button onClick={() => addBloco('text_short')} className="flex flex-col items-center justify-center gap-2 p-3 rounded-xl border border-blue-200 bg-white hover:border-blue-400 hover:bg-blue-50 transition-all text-blue-700 shadow-sm">
                        <Type className="w-5 h-5 text-blue-500"/> 
                        <span className="text-xs font-semibold">Texto</span>
                      </button>
                      <button onClick={() => addBloco('file_upload')} className="flex flex-col items-center justify-center gap-2 p-3 rounded-xl border border-orange-200 bg-white hover:border-orange-400 hover:bg-orange-50 transition-all text-orange-700 shadow-sm">
                        <UploadCloud className="w-5 h-5 text-orange-500"/> 
                        <span className="text-xs font-semibold">Upload</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-6 py-4 bg-white border-t border-neutral-200 flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={handleSave} disabled={isSaving} className="btn-primary min-w-[140px]">
            {isSaving ? 'Salvando...' : 'Salvar Rotina'}
          </button>
        </div>
      </div>
    </div>
  )
}
