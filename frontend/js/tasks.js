// ════════════════════════════════════════════════════════
// TASKS — Portal Grupo TRK v2.0
// Drawer logic, persistence, filtering
// ════════════════════════════════════════════════════════

const Tasks = {
  list: [],
  filter: 'todas', // todas | pendentes | concluidas

  init() {
    this.list = Store.get('gtrk_tasks', []);
    
    // Setup Drawer UI
    const fab = document.getElementById('fab-tasks');
    const overlay = document.getElementById('drawer-overlay');
    const closeBtn = document.getElementById('drawer-close');
    
    if (fab) fab.addEventListener('click', () => this.toggleDrawer());
    if (closeBtn) closeBtn.addEventListener('click', () => this.toggleDrawer());
    if (overlay) overlay.addEventListener('click', (e) => {
      if (e.target === overlay) this.toggleDrawer();
    });

    // Setup input
    const input = document.getElementById('task-input');
    if (input) input.addEventListener('keypress', e => {
      if (e.key === 'Enter') this.add();
    });

    this.render();
  },

  toggleDrawer() {
    const d = document.getElementById('drawer-tasks');
    const o = document.getElementById('drawer-overlay');
    if (!d || !o) return;
    
    const isOpen = d.classList.contains('open');
    if (isOpen) {
      d.classList.remove('open');
      o.classList.remove('open');
      document.body.style.overflow = '';
    } else {
      d.classList.add('open');
      o.classList.add('open');
      document.body.style.overflow = 'hidden';
      const inp = document.getElementById('task-input');
      if (inp) setTimeout(() => inp.focus(), 300);
    }
  },

  setFilter(f) {
    this.filter = f;
    document.querySelectorAll('.tf').forEach(btn => {
      btn.classList.toggle('on', btn.dataset.f === f);
    });
    this.render();
  },

  add() {
    const input = document.getElementById('task-input');
    const prio = document.getElementById('task-prio').value;
    const due = document.getElementById('task-due').value;
    
    const text = input.value.trim();
    if (!text) {
      Toast.show('Digite uma tarefa', 'error');
      return;
    }

    this.list.unshift({
      id: Utils.uid(),
      text,
      done: false,
      prio,
      due: due || null,
      created: new Date().toISOString()
    });

    Store.set('gtrk_tasks', this.list);
    input.value = '';
    document.getElementById('task-due').value = '';
    this.render();
    Toast.show('Tarefa adicionada', 'success');
  },

  toggle(id) {
    const t = this.list.find(x => x.id === id);
    if (t) {
      t.done = !t.done;
      Store.set('gtrk_tasks', this.list);
      this.render();
    }
  },

  remove(id) {
    Confirm.show({
      title: 'Excluir tarefa?',
      message: 'Esta ação não pode ser desfeita.',
      confirmText: 'Excluir',
      type: 'danger'
    }).then(res => {
      if (res) {
        this.list = this.list.filter(x => x.id !== id);
        Store.set('gtrk_tasks', this.list);
        this.render();
        Toast.show('Tarefa removida', 'success');
      }
    });
  },

  clearDone() {
    const doneCount = this.list.filter(t => t.done).length;
    if (doneCount === 0) return;

    Confirm.show({
      title: 'Limpar concluídas?',
      message: `Você removerá ${doneCount} tarefa(s) concluída(s).`,
      confirmText: 'Limpar',
      type: 'danger'
    }).then(res => {
      if (res) {
        this.list = this.list.filter(t => !t.done);
        Store.set('gtrk_tasks', this.list);
        this.render();
        Toast.show('Tarefas limpas', 'success');
      }
    });
  },

  render() {
    const listEl = document.getElementById('tasks-list');
    if (!listEl) return;

    // Filter
    let filtered = this.list;
    if (this.filter === 'pendentes') filtered = this.list.filter(t => !t.done);
    if (this.filter === 'concluidas') filtered = this.list.filter(t => t.done);

    // Badges update
    const pendCount = this.list.filter(t => !t.done).length;
    const badgeD = document.getElementById('tasks-badge-desk');
    const badgeM = document.getElementById('tasks-badge-mob');
    const fabB = document.getElementById('fab-badge');

    if (badgeD) Utils.animateNum(badgeD, pendCount);
    if (badgeM) badgeM.textContent = pendCount;
    if (fabB) fabB.textContent = pendCount > 0 ? pendCount : '';

    if (filtered.length === 0) {
      listEl.innerHTML = `
        <div class="tasks-empty anim-fade-up">
          <div style="font-size:32px;margin-bottom:8px;opacity:0.5">📋</div>
          ${this.list.length === 0 ? 'Nenhuma tarefa criada' : 'Nenhuma tarefa encontrada no filtro atual'}
        </div>
      `;
      return;
    }

    let html = '';
    const today = new Date().toISOString().split('T')[0];

    filtered.forEach(t => {
      let isOverdue = false;
      let dueStr = '';
      if (t.due) {
        isOverdue = !t.done && t.due < today;
        const [y,m,d] = t.due.split('-');
        dueStr = `${d}/${m}`;
      }

      html += `
        <div class="task-item ${t.done ? 'is-done' : ''}">
          <div class="task-chk ${t.done ? 'done' : ''}" onclick="Tasks.toggle('${t.id}')"></div>
          <div class="task-body">
            <div class="task-text ${t.done ? 'done' : ''}">${Utils.escapeHtml(t.text)}</div>
            <div class="task-badges">
              ${t.prio !== 'normal' ? `<span class="task-badge prio-${t.prio}">${t.prio.toUpperCase()}</span>` : ''}
              ${t.due ? `<span class="task-due ${isOverdue ? 'overdue' : ''}">📅 ${dueStr}</span>` : ''}
            </div>
          </div>
          <div class="task-actions">
            <button class="task-act-btn del" onclick="Tasks.remove('${t.id}')" title="Excluir">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path></svg>
            </button>
          </div>
        </div>
      `;
    });

    listEl.innerHTML = html;
  }
};
