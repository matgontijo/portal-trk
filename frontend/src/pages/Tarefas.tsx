// frontend/src/pages/Tarefas.tsx
import { useState, useEffect } from 'react'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd'
import { KanbanSquare, Plus, Clock, AlertCircle } from 'lucide-react'
import api from '../services/api'
import { Badge } from '../components/common/Badge'
import { formatarData } from '../utils/formatters'
import { PRIORIDADE_CORES } from '../utils/constants'

// Função utilitária para StrictMode do React com Beautiful DnD
const StrictModeDroppable = ({ children, ...props }: any) => {
  const [enabled, setEnabled] = useState(false)
  useEffect(() => {
    const animation = requestAnimationFrame(() => setEnabled(true))
    return () => { cancelAnimationFrame(animation); setEnabled(false) }
  }, [])
  if (!enabled) return null
  return <Droppable {...props}>{children}</Droppable>
}

export function Tarefas() {
  const [tarefas, setTarefas] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    carregarTarefas()
  }, [])

  const carregarTarefas = async () => {
    try {
      const response = await api.get('/tarefas')
      setTarefas(response.data)
    } catch (error) {
      console.error('Erro ao carregar tarefas', error)
    } finally {
      setIsLoading(false)
    }
  }

  const columns = {
    todo: { id: 'todo', title: 'A Fazer', color: 'bg-slate-100 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800' },
    doing: { id: 'doing', title: 'Em Andamento', color: 'bg-primary-50/50 dark:bg-primary-900/10 border-primary-200 dark:border-primary-900/50' },
    done: { id: 'done', title: 'Concluídas', color: 'bg-success-50/50 dark:bg-success-900/10 border-success-200 dark:border-success-900/50' },
  }

  const onDragEnd = async (result: any) => {
    if (!result.destination) return
    const { source, destination, draggableId } = result

    if (source.droppableId === destination.droppableId) return

    // Atualização Otimista
    setTarefas(prev => prev.map(t => {
      if (t.id === draggableId) {
        return { ...t, status: destination.droppableId }
      }
      return t
    }))

    try {
      await api.patch(`/tarefas/${draggableId}`, {
        status: destination.droppableId
      })
    } catch (error) {
      carregarTarefas() // Reverter em caso de erro
    }
  }

  if (isLoading) {
    return <div className="animate-pulse h-[600px] bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
  }

  return (
    <div className="h-full flex flex-col space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            Quadro Kanban
          </h1>
          <p className="text-slate-500 mt-1">Gestão de tarefas e chamados.</p>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4" />
          Nova Tarefa
        </button>
      </div>

      <div className="flex-1 overflow-x-auto min-h-[500px]">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex gap-6 h-full min-w-[800px] pb-4">
            
            {Object.values(columns).map((col) => {
              const colTasks = tarefas.filter(t => t.status === col.id)
              
              return (
                <div key={col.id} className={`flex-1 flex flex-col rounded-xl border ${col.color}`}>
                  <div className="p-4 border-b border-inherit flex items-center justify-between">
                    <h3 className="font-semibold text-slate-700 dark:text-slate-300">{col.title}</h3>
                    <span className="bg-white dark:bg-slate-800 text-slate-500 text-xs font-bold px-2 py-1 rounded-full border border-slate-200 dark:border-slate-700">
                      {colTasks.length}
                    </span>
                  </div>

                  <StrictModeDroppable droppableId={col.id}>
                    {(provided: any, snapshot: any) => (
                      <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        className={`flex-1 p-4 space-y-3 overflow-y-auto ${snapshot.isDraggingOver ? 'bg-slate-200/50 dark:bg-slate-800/50' : ''}`}
                      >
                        {colTasks.map((tarefa, index) => {
                          const prioColor = PRIORIDADE_CORES[tarefa.prioridade]
                          
                          return (
                            <Draggable key={tarefa.id} draggableId={tarefa.id} index={index}>
                              {(provided: any, snapshot: any) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  className={`card p-4 ${snapshot.isDragging ? 'shadow-lg ring-2 ring-primary-500 rotate-2' : ''} ${tarefa.status === 'done' ? 'opacity-70' : ''}`}
                                >
                                  <div className="flex items-start justify-between gap-2 mb-2">
                                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${prioColor.bg} ${prioColor.text} uppercase tracking-wider`}>
                                      {tarefa.prioridade}
                                    </span>
                                    {tarefa.empresa_nome && (
                                      <span className="text-[10px] text-slate-500 truncate max-w-[100px]" title={tarefa.empresa_nome}>
                                        {tarefa.empresa_nome}
                                      </span>
                                    )}
                                  </div>
                                  
                                  <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2 leading-tight">
                                    {tarefa.titulo}
                                  </h4>

                                  {tarefa.prazo && (
                                    <div className={`flex items-center gap-1.5 text-xs mt-3 ${tarefa.esta_atrasada && tarefa.status !== 'done' ? 'text-danger-600 font-semibold' : 'text-slate-500'}`}>
                                      <Clock className="w-3.5 h-3.5" />
                                      {formatarData(tarefa.prazo)}
                                      {tarefa.esta_atrasada && tarefa.status !== 'done' && <AlertCircle className="w-3.5 h-3.5 ml-auto" />}
                                    </div>
                                  )}

                                  <div className="mt-3 flex justify-between items-center border-t border-slate-100 dark:border-slate-800 pt-3">
                                    <div className="flex -space-x-2">
                                      {tarefa.responsavel ? (
                                        <div className="w-6 h-6 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-[10px] font-bold border-2 border-white dark:border-slate-900" title={tarefa.responsavel.name}>
                                          {tarefa.responsavel.name.charAt(0)}
                                        </div>
                                      ) : (
                                        <div className="w-6 h-6 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center text-xs border-2 border-white dark:border-slate-900 border-dashed">
                                          ?
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </Draggable>
                          )
                        })}
                        {provided.placeholder}
                      </div>
                    )}
                  </StrictModeDroppable>
                </div>
              )
            })}
          </div>
        </DragDropContext>
      </div>
    </div>
  )
}
