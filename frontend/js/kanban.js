// ════════════════════════════════════════════════════════
// KANBAN — Portal Grupo TRK v2.0
// ════════════════════════════════════════════════════════

const Kanban = {
  columns: ['todo', 'doing', 'done'],
  
  openBoard() {
    Modal.open({
      title: 'Quadro Kanban de Tarefas',
      body: `
        <div class="kanban-board" id="kb-board">
          <!-- Columns rendered here -->
        </div>
      `,
      footer: `
        <button class="btn btn-ghost" onclick="Modal.close()">Fechar Kanban</button>
      `
    });
    
    // Give time to render Modal
    setTimeout(() => {
      document.querySelector('.modal').style.maxWidth = '1000px';
      document.querySelector('.modal').style.width = '95%';
      this.renderBoard();
    }, 100);
  },

  renderBoard() {
    const board = document.getElementById('kb-board');
    if (!board) return;

    const list = Store.get('gtrk_tasks', []);

    let html = '';
    const colTitles = {
      todo: 'A Fazer',
      doing: 'Em Andamento',
      done: 'Concluído'
    };

    this.columns.forEach(colId => {
      // Filter tasks by status (if no status, default to 'todo')
      // Map legacy "done: true" to "done"
      const colTasks = list.filter(t => {
        let st = t.status || (t.done ? 'done' : 'todo');
        return st === colId;
      });

      html += `
        <div class="kanban-col">
          <div class="kanban-col-header">
            ${colTitles[colId]}
            <span class="kanban-col-count">${colTasks.length}</span>
          </div>
          <div class="kanban-col-body" data-status="${colId}" ondragover="Kanban.allowDrop(event)" ondrop="Kanban.drop(event)" ondragenter="Kanban.dragEnter(event)" ondragleave="Kanban.dragLeave(event)">
            ${colTasks.map(t => this.renderCard(t)).join('')}
          </div>
        </div>
      `;
    });

    board.innerHTML = html;
  },

  renderCard(t) {
    let dueStr = '';
    let isOverdue = false;
    if (t.due) {
      const today = new Date().toISOString().split('T')[0];
      isOverdue = (t.status !== 'done' && !t.done) && t.due < today;
      const [y,m,d] = t.due.split('-');
      dueStr = `${d}/${m}`;
    }

    return `
      <div class="kanban-card" draggable="true" ondragstart="Kanban.dragStart(event, '${t.id}')" id="kb-card-${t.id}">
        <div class="kb-act">
          <button class="task-act-btn del" onclick="Tasks.remove('${t.id}');setTimeout(()=>Kanban.renderBoard(),300)" title="Excluir">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path></svg>
          </button>
        </div>
        <div class="kb-title" style="${(t.status === 'done' || t.done) ? 'text-decoration:line-through;color:var(--text4)' : ''}">${Utils.escapeHtml(t.text)}</div>
        <div class="kb-meta">
          ${t.prio !== 'normal' ? `<span class="kb-badge prio-${t.prio}">${t.prio.toUpperCase()}</span>` : ''}
          ${t.due ? `<span class="kb-badge task-due ${isOverdue ? 'overdue' : ''}">📅 ${dueStr}</span>` : ''}
        </div>
      </div>
    `;
  },

  dragStart(e, id) {
    e.dataTransfer.setData('text/plain', id);
    setTimeout(() => {
      document.getElementById(`kb-card-${id}`).style.opacity = '0.5';
    }, 0);
  },

  allowDrop(e) {
    e.preventDefault();
  },

  dragEnter(e) {
    e.preventDefault();
    const col = e.target.closest('.kanban-col-body');
    if (col) col.classList.add('drag-over');
  },

  dragLeave(e) {
    const col = e.target.closest('.kanban-col-body');
    if (col) col.classList.remove('drag-over');
  },

  drop(e) {
    e.preventDefault();
    const col = e.target.closest('.kanban-col-body');
    if (col) {
      col.classList.remove('drag-over');
      const id = e.dataTransfer.getData('text/plain');
      const status = col.dataset.status;
      
      this.updateTaskStatus(id, status);
    }
  },

  updateTaskStatus(id, status) {
    let list = Store.get('gtrk_tasks', []);
    const idx = list.findIndex(t => t.id === id);
    if (idx !== -1) {
      list[idx].status = status;
      list[idx].done = (status === 'done'); // update legacy flag
      Store.set('gtrk_tasks', list);
      this.renderBoard();
      Tasks.render(); // update background drawer list too
    }
  }
};
