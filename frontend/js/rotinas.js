// ════════════════════════════════════════════════════════
// ROTINAS — Portal Grupo TRK v2.0
// Daily routines, checklists, and Drive folder generator
// ════════════════════════════════════════════════════════

const Rotinas = {
  currentDay: new Date().getDay(),
  rotData: {}, // { [day]: { [blockIdx_itemIdx]: boolean } }

  init() {
    this.rotData = Store.get('rot_data', {});
    this.render();
    this.updateStats();
  },

  setDay(day) {
    this.currentDay = day;
    document.querySelectorAll('.nav-tab').forEach(t => {
      if (t.dataset.day !== undefined) {
        t.classList.toggle('active', parseInt(t.dataset.day) === day);
      }
    });
    this.render();
  },

  toggleItem(day, id) {
    if (!this.rotData[day]) this.rotData[day] = {};
    this.rotData[day][id] = !this.rotData[day][id];
    Store.set('rot_data', this.rotData);
    
    // Update UI without full re-render
    const chk = document.getElementById(`chk-${day}-${id}`);
    const txt = document.getElementById(`txt-${day}-${id}`);
    if (chk) {
      chk.classList.toggle('checked', this.rotData[day][id]);
      if (this.rotData[day][id]) {
        // Trigger bounce animation
        chk.style.animation = 'none';
        chk.offsetHeight; // trigger reflow
        chk.style.animation = null;
      }
    }
    if (txt) txt.classList.toggle('checked', this.rotData[day][id]);

    this.updateStats();
    
    // Update block header stats
    const blockIdx = id.split('_')[0];
    this.updateBlockStats(day, parseInt(blockIdx));
  },

  toggleBlock(day, blockIdx) {
    const body = document.getElementById(`cl-body-${day}-${blockIdx}`);
    const arrow = document.getElementById(`cl-arrow-${day}-${blockIdx}`);
    if (body && arrow) {
      const isOpen = body.classList.contains('open');
      if (isOpen) {
        body.classList.remove('open');
        arrow.style.transform = 'rotate(0deg)';
      } else {
        body.classList.add('open');
        arrow.style.transform = 'rotate(180deg)';
      }
    }
  },

  updateBlockStats(day, blockIdx) {
    const rot = ROTINAS[day];
    if (!rot || !rot.blocos[blockIdx]) return;
    
    const block = rot.blocos[blockIdx];
    const total = block.itens.length;
    let done = 0;
    
    for (let i = 0; i < total; i++) {
      if (this.rotData[day] && this.rotData[day][`${blockIdx}_${i}`]) done++;
    }

    const progEl = document.getElementById(`cl-prog-${day}-${blockIdx}`);
    if (progEl) {
      if (done === total) {
        progEl.innerHTML = '<span class="cl-done"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg> Concluído</span>';
      } else {
        progEl.innerHTML = `<span class="cl-progress">${done}/${total}</span>`;
      }
    }
  },

  updateStats() {
    let totalItems = 0;
    let doneItems = 0;

    // Calculate only for current day
    const rot = ROTINAS[this.currentDay];
    if (rot) {
      rot.blocos.forEach((b, bIdx) => {
        b.itens.forEach((_, iIdx) => {
          totalItems++;
          if (this.rotData[this.currentDay] && this.rotData[this.currentDay][`${bIdx}_${iIdx}`]) {
            doneItems++;
          }
        });
      });
    }

    const pct = totalItems === 0 ? 0 : Math.round((doneItems / totalItems) * 100);
    
    const fill = document.getElementById('rot-fill');
    const text = document.getElementById('rot-pct');
    if (fill) fill.style.width = `${pct}%`;
    if (text) text.innerHTML = `<span>Progresso diário</span><span><b>${pct}%</b> concluído</span>`;

    // Global stats update
    const statRot = document.getElementById('stat-rotinas');
    if (statRot) Utils.animateNum(statRot, pct);
  },

  render() {
    const container = document.getElementById('rotinas-container');
    if (!container) return;

    const rot = ROTINAS[this.currentDay];
    if (!rot) return;

    const targetDate = Utils.getDateForDay(this.currentDay);

    let html = `
      <div class="day-card anim-fade-down">
        <div class="day-title">${rot.label}</div>
        <div class="day-sub">${Utils.fmtDate(targetDate)}</div>
    `;

    if (rot.alertas.length > 0) {
      rot.alertas.forEach(a => {
        const isUrg = a.includes('⚠️') || a.includes('DEADLINE');
        html += `<div class="day-alert ${isUrg ? 'anim-pulse' : ''}" style="${isUrg ? 'background:var(--err-l);color:var(--err);border-color:var(--err-b)' : ''}">${a}</div>`;
      });
    }

    html += `
        <div class="progress-wrap">
          <div class="progress-bar"><div class="progress-fill" id="rot-fill" style="width:0%"></div></div>
          <div class="progress-text" id="rot-pct"><span>Progresso</span><span><b>0%</b></span></div>
        </div>
      </div>
    `;

    if (rot.blocos.length === 0) {
      html += `
        <div class="empty-state anim-fade-up">
          <span class="empty-icon">🏖️</span>
          <p>Nenhuma rotina programada para este dia.</p>
        </div>
      `;
    } else {
      rot.blocos.forEach((b, bIdx) => {
        const total = b.itens.length;
        let done = 0;
        for (let i = 0; i < total; i++) {
          if (this.rotData[this.currentDay] && this.rotData[this.currentDay][`${bIdx}_${i}`]) done++;
        }
        const isFull = done === total;
        const progHtml = isFull 
          ? '<span class="cl-done"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg> Concluído</span>'
          : `<span class="cl-progress">${done}/${total}</span>`;

        html += `
          <div class="checklist-block anim-fade-up stagger-${bIdx + 1}">
            <div class="cl-header" onclick="Rotinas.toggleBlock(${this.currentDay}, ${bIdx})">
              <div class="cl-left">
                <span class="cat-badge cat-${b.cat}">${b.cat}</span>
                <span>${b.label}</span>
              </div>
              <div style="display:flex;align-items:center;gap:12px">
                <div id="cl-prog-${this.currentDay}-${bIdx}">${progHtml}</div>
                <div class="cl-arrow" id="cl-arrow-${this.currentDay}-${bIdx}" style="transform:rotate(${isFull ? '0' : '180'}deg)">▾</div>
              </div>
            </div>
            <div class="cl-body ${isFull ? '' : 'open'}" id="cl-body-${this.currentDay}-${bIdx}">
        `;

        b.itens.forEach((item, iIdx) => {
          const id = `${bIdx}_${iIdx}`;
          const isChecked = this.rotData[this.currentDay] && this.rotData[this.currentDay][id];
          html += `
            <div class="check-item">
              <div class="chk ${isChecked ? 'checked' : ''}" id="chk-${this.currentDay}-${id}" onclick="Rotinas.toggleItem(${this.currentDay}, '${id}')"></div>
              <div class="chk-text ${isChecked ? 'checked' : ''}" id="txt-${this.currentDay}-${id}" onclick="Rotinas.toggleItem(${this.currentDay}, '${id}')">${item}</div>
            </div>
          `;
        });

        html += `</div></div>`;
      });
    }

    container.innerHTML = html;
    this.updateStats();
  }
};

// ── DRIVE GENERATOR ──
const Drive = {
  data: {}, // { [empId]: boolean }

  init() {
    this.data = Store.get('drive_data', {});
    this.render();
  },

  toggle(empId) {
    this.data[empId] = !this.data[empId];
    Store.set('drive_data', this.data);
    this.render();
    
    // Global stats update
    const doneCount = Object.values(this.data).filter(v => v).length;
    const statDrive = document.getElementById('stat-drive');
    if (statDrive) Utils.animateNum(statDrive, doneCount);
  },

  render() {
    const listEl = document.getElementById('drive-list');
    const pathEl = document.getElementById('drive-path');
    const monthEl = document.getElementById('drive-month');
    
    if (!listEl) return;

    // Set month path
    const d = new Date();
    const mStr = `${(d.getMonth()+1).toString().padStart(2,'0')} - ${Utils.MESES[d.getMonth()]}`;
    const dayStr = `${d.getDate().toString().padStart(2,'0')}.${(d.getMonth()+1).toString().padStart(2,'0')}`;
    
    if (monthEl) monthEl.textContent = mStr;
    if (pathEl) pathEl.value = `[EMPRESA] / 2026 / ${mStr} / ${dayStr}`;

    let html = '';
    BPO_EMPRESAS.forEach(e => {
      const done = this.data[e.id];
      html += `
        <div class="drive-item" style="cursor:pointer" onclick="Drive.toggle('${e.id}')">
          <div class="drive-chk ${done ? 'on' : ''}"></div>
          <div class="drive-label ${done ? 'done' : ''}">${e.nome}</div>
        </div>
      `;
    });

    listEl.innerHTML = html;
  }
};
