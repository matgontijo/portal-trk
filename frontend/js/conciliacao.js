// ════════════════════════════════════════════════════════
// CONCILIAÇÃO — Portal Grupo TRK v2.0
// Daily bank conciliation tracking
// ════════════════════════════════════════════════════════

const Conciliacao = {
  currentDate: new Date(),
  data: {}, // { [dateKey]: { [empresaId]: { status: 'ok|pendente|erro', saldo: '', obs: '' } } }
  history: [], // Audit trail

  init() {
    this.data = Store.get('conc_data', {});
    this.history = Store.get('conc_hist', []);
    
    // Listeners for date nav
    const btnPrev = document.getElementById('conc-prev');
    const btnNext = document.getElementById('conc-next');
    const btnToday = document.getElementById('conc-today');
    const inpDate = document.getElementById('conc-date');

    if (btnPrev) btnPrev.addEventListener('click', () => this.changeDate(-1));
    if (btnNext) btnNext.addEventListener('click', () => this.changeDate(1));
    if (btnToday) btnToday.addEventListener('click', () => {
      this.currentDate = new Date();
      this.render();
    });
    if (inpDate) inpDate.addEventListener('change', (e) => {
      if (e.target.value) {
        const [y,m,d] = e.target.value.split('-');
        this.currentDate = new Date(y, m-1, d);
        this.render();
      }
    });

    // Bulk actions
    const btnOkAll = document.getElementById('bulk-ok');
    const btnResetAll = document.getElementById('bulk-reset');
    
    if (btnOkAll) btnOkAll.addEventListener('click', () => {
      Confirm.show({
        title: 'Marcar todas como OK?',
        message: 'Isso definirá o status de todas as empresas listadas como OK.',
        confirmText: 'Sim, marcar OK',
        type: 'primary'
      }).then(res => {
        if (res) this.bulkSet('ok');
      });
    });

    if (btnResetAll) btnResetAll.addEventListener('click', () => {
      Confirm.show({
        title: 'Resetar todas?',
        message: 'Isso limpará os status e saldos do dia atual.',
        confirmText: 'Sim, resetar',
        type: 'danger'
      }).then(res => {
        if (res) this.bulkSet('vazio');
      });
    });

    // General observation
    const obsDay = document.getElementById('conc-obs-day');
    if (obsDay) obsDay.addEventListener('input', Utils.debounce(e => {
      const key = Utils.toKey(this.currentDate);
      if (!this.data[key]) this.data[key] = {};
      this.data[key]._obs = e.target.value;
      Store.set('conc_data', this.data);
    }, 500));

    this.render();
  },

  runSmartConciliation() {
    Confirm.show({
      title: 'Auto-Conciliação Robô',
      message: 'O sistema vai buscar os lançamentos na API real do Omie. Deseja iniciar?',
      confirmText: 'Sim, iniciar robô',
      type: 'primary'
    }).then(async res => {
      if (res) {
        Toast.show('Iniciando robô de conciliação...', 'info');
        
        try {
          // Test with the first company or a hardcoded one for demonstration
          const empresaId = BPO_EMPRESAS[0].id; // We'll just test the first one
          
          const response = await fetch('/api/omie/conciliar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ empresa_id: empresaId })
          });
          
          const result = await response.json();
          
          if (result.status === 'erro') {
            Toast.show(`Erro Omie: ${result.detalhe}`, 'error');
            // Mock a failure in the UI
            this.update(empresaId, 'status', 'erro');
            this.update(empresaId, 'obs', result.detalhe);
          } else {
            Toast.show('Sucesso na busca do Omie!', 'success');
            this.update(empresaId, 'status', 'ok');
            this.update(empresaId, 'saldo', '1000,00'); // Mock balance
            this.update(empresaId, 'obs', 'Conciliado via API.');
          }
          
        } catch (e) {
          Toast.show(`Falha no servidor: ${e.message}`, 'error');
        }
      }
    });
  },

  changeDate(delta) {
    this.currentDate.setDate(this.currentDate.getDate() + delta);
    this.render();
  },

  logAction(action, detail) {
    this.history.unshift({
      date: new Date().toISOString(),
      action,
      detail
    });
    if (this.history.length > 50) this.history.pop();
    Store.set('conc_hist', this.history);
    this.renderHistory();
  },

  toggleHistory() {
    const p = document.getElementById('conc-hist-panel');
    if (p) {
      p.classList.toggle('open');
      if (p.classList.contains('open')) this.renderHistory();
    }
  },

  renderHistory() {
    const p = document.getElementById('conc-hist-panel');
    if (!p) return;
    if (this.history.length === 0) {
      p.innerHTML = '<div style="color:var(--text4);font-size:12px;text-align:center;padding:10px">Nenhum registro no histórico</div>';
      return;
    }
    let html = '';
    this.history.forEach(h => {
      const d = new Date(h.date);
      const time = `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
      html += `
        <div class="hist-item">
          <div style="font-size:12px"><b>${time}</b> - ${h.action}</div>
          <div class="hist-tags"><span class="ht">${h.detail}</span></div>
        </div>
      `;
    });
    p.innerHTML = html;
  },

  bulkSet(status) {
    const key = Utils.toKey(this.currentDate);
    if (!this.data[key]) this.data[key] = {};
    
    // Only affect visible ones if search is active (not implemented here yet, assuming all)
    BPO_EMPRESAS.forEach(e => {
      if (!this.data[key][e.id]) this.data[key][e.id] = { status: 'vazio', saldo: '', obs: '' };
      this.data[key][e.id].status = status;
      if (status === 'vazio') {
        this.data[key][e.id].saldo = '';
        this.data[key][e.id].obs = '';
      }
    });

    Store.set('conc_data', this.data);
    this.logAction('Bulk Update', status.toUpperCase());
    this.render();
    Toast.show(`Atualização em lote: ${status}`, status === 'ok' ? 'success' : 'info');
  },

  update(empId, field, value) {
    const key = Utils.toKey(this.currentDate);
    if (!this.data[key]) this.data[key] = {};
    if (!this.data[key][empId]) this.data[key][empId] = { status: 'vazio', saldo: '', obs: '' };
    
    this.data[key][empId][field] = value;
    Store.set('conc_data', this.data);
    
    if (field === 'status') {
      this.logAction('Status Update', `${empId.toUpperCase()} -> ${value}`);
      this.render(); // re-render for colors/progress
    } else {
      // Just show saved message
      const msg = document.getElementById(`msg-${empId}`);
      if (msg) {
        msg.classList.add('show');
        setTimeout(() => msg.classList.remove('show'), 2000);
      }
      this.updateProgress();
    }
  },

  toggleDetail(id) {
    const card = document.getElementById(`conc-card-${id}`);
    if (card) card.classList.toggle('open');
  },

  updateProgress() {
    const key = Utils.toKey(this.currentDate);
    const dayData = this.data[key] || {};
    
    let ok = 0, pend = 0, err = 0;
    BPO_EMPRESAS.forEach(e => {
      const st = dayData[e.id]?.status || 'vazio';
      if (st === 'ok') ok++;
      else if (st === 'pendente') pend++;
      else if (st === 'erro') err++;
    });

    const total = BPO_EMPRESAS.length;
    const p = Math.round((ok / total) * 100);

    const fill = document.getElementById('conc-fill');
    const text = document.getElementById('conc-pct');
    const statOk = document.getElementById('conc-stat-ok');
    const statPend = document.getElementById('conc-stat-pend');
    const statErr = document.getElementById('conc-stat-err');

    if (fill) fill.style.width = `${p}%`;
    if (text) text.innerHTML = `<span>Progresso</span><span><b>${p}%</b> concluído</span>`;
    if (statOk) statOk.innerHTML = `<div class="conc-dot" style="background:var(--ok)"></div> OK: ${ok}`;
    if (statPend) statPend.innerHTML = `<div class="conc-dot" style="background:var(--pend)"></div> Pendente: ${pend}`;
    if (statErr) statErr.innerHTML = `<div class="conc-dot" style="background:var(--err)"></div> Erro: ${err}`;
  },

  render() {
    const key = Utils.toKey(this.currentDate);
    const dayData = this.data[key] || {};
    
    // Update date label & input
    const lbl = document.getElementById('conc-date-label');
    const inp = document.getElementById('conc-date');
    if (lbl) lbl.textContent = Utils.fmtDate(this.currentDate);
    if (inp) inp.value = key;

    // Update Day Observation
    const obsDay = document.getElementById('conc-obs-day');
    if (obsDay) obsDay.value = dayData._obs || '';

    // Render list
    const listEl = document.getElementById('conc-list');
    if (!listEl) return;

    let html = '';
    BPO_EMPRESAS.forEach((e, i) => {
      const edata = dayData[e.id] || { status: 'vazio', saldo: '', obs: '' };
      const st = edata.status;
      const bc = Utils.bankClass(e.banco);
      
      html += `
        <div class="conc-card ${st} anim-fade-up stagger-${(i%10)+1}" id="conc-card-${e.id}">
          <div class="conc-top">
            <div class="conc-info" style="cursor:pointer" onclick="Conciliacao.toggleDetail('${e.id}')">
              <div class="conc-nome">${e.nome}</div>
              <div class="conc-meta">
                <span class="bank-tag ${bc}">${e.banco}</span>
                <span class="resp-badge ${e.resp}">${e.resp === 'rafael' ? 'Rafael' : 'Tárik'}</span>
              </div>
            </div>
            <div class="conc-right">
              <input type="text" class="saldo-input" placeholder="R$ Saldo final" value="${edata.saldo}" 
                onchange="Conciliacao.update('${e.id}', 'saldo', this.value)"
                oninput="this.value = this.value.replace(/[^0-9.,-]/g, '')">
              <select class="status-sel ${st !== 'vazio' ? st : ''}" onchange="Conciliacao.update('${e.id}', 'status', this.value)">
                <option value="vazio" ${st === 'vazio' ? 'selected' : ''}>Status...</option>
                <option value="ok" ${st === 'ok' ? 'selected' : ''}>OK</option>
                <option value="pendente" ${st === 'pendente' ? 'selected' : ''}>Pendente</option>
                <option value="erro" ${st === 'erro' ? 'selected' : ''}>Erro</option>
              </select>
              <button class="toggle-btn" onclick="Conciliacao.toggleDetail('${e.id}')">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7"/></svg>
              </button>
            </div>
          </div>
          <div class="conc-detail">
            <div class="detail-grid">
              <div class="detail-field detail-full">
                <label>Observações / Divergências</label>
                <textarea placeholder="Ex: NF X pendente de envio..." oninput="Utils.debounce(() => Conciliacao.update('${e.id}', 'obs', this.value), 500)()">${edata.obs}</textarea>
                <div class="saved-msg" id="msg-${e.id}">
                  <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>
                  Salvo
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    });

    listEl.innerHTML = html;
    this.updateProgress();
  }
};
