// ════════════════════════════════════════════════════════
// UI — Portal Grupo TRK v2.0
// Toast, Modal, Confirm Dialog systems
// ════════════════════════════════════════════════════════

// ── TOAST SYSTEM ──
const Toast = {
  icons: {
    success: '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#16a34a" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>',
    error: '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#dc2626" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>',
    info: '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#2563eb" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
  },

  show(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerHTML = `${this.icons[type] || this.icons.info}<span>${msg}</span>`;
    container.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => {
      t.classList.remove('show');
      setTimeout(() => t.remove(), 300);
    }, 2800);
  }
};

// ── MODAL SYSTEM ──
const Modal = {
  _overlay: null,

  init() {
    // Create overlay once
    this._overlay = document.createElement('div');
    this._overlay.className = 'modal-overlay';
    this._overlay.innerHTML = '<div class="modal" id="modal-content"></div>';
    document.body.appendChild(this._overlay);

    // Close on overlay click
    this._overlay.addEventListener('click', (e) => {
      if (e.target === this._overlay) this.close();
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this._overlay.classList.contains('open')) {
        this.close();
      }
    });
  },

  open(options = {}) {
    const { title = '', body = '', footer = '', onClose } = options;
    const modal = document.getElementById('modal-content');
    modal.innerHTML = `
      <div class="modal-header">
        <h2>${title}</h2>
        <button class="modal-close" onclick="Modal.close()">✕</button>
      </div>
      <div class="modal-body">${body}</div>
      ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
    `;
    this._onClose = onClose;
    this._overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  },

  close() {
    this._overlay.classList.remove('open');
    document.body.style.overflow = '';
    if (this._onClose) this._onClose();
  },

  // Show company details
  showCompany(empresa) {
    const bc = Utils.bankClass(empresa.banco);
    this.open({
      title: empresa.nome,
      body: `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
          <div class="avatar ${empresa.grupo}" style="width:52px;height:52px;font-size:16px">${Utils.initials(empresa.nome)}</div>
          <div>
            <span class="group-tag ${empresa.grupo}" style="font-size:13px">${empresa.grupo === 'trk' ? 'Grupo TRK' : 'BPO'}</span>
            <span class="resp-badge ${empresa.resp}" style="margin-left:6px">${empresa.resp === 'rafael' ? 'Rafael' : 'Tárik'}</span>
          </div>
        </div>
        <div class="modal-info-grid">
          <div class="modal-info-item">
            <span class="label">CNPJ</span>
            <span class="value mono" style="cursor:pointer" onclick="Utils.copyToClipboard('${empresa.cnpj}');Toast.show('CNPJ copiado!','info')">${empresa.cnpj} 📋</span>
          </div>
          <div class="modal-info-item">
            <span class="label">Banco</span>
            <span class="value"><span class="bank-tag ${bc}">${empresa.banco}</span></span>
          </div>
          <div class="modal-info-item">
            <span class="label">Agência</span>
            <span class="value mono">${empresa.ag}</span>
          </div>
          <div class="modal-info-item">
            <span class="label">Conta</span>
            <span class="value mono" style="cursor:pointer" onclick="Utils.copyToClipboard('${empresa.conta}');Toast.show('Conta copiada!','info')">${empresa.conta} 📋</span>
          </div>
          <div class="modal-info-item">
            <span class="label">Responsável</span>
            <span class="value">${empresa.resp === 'rafael' ? 'Rafael' : 'Tárik'}</span>
          </div>
          <div class="modal-info-item">
            <span class="label">Grupo</span>
            <span class="value">${empresa.grupo === 'trk' ? 'Grupo TRK' : 'BPO Terceirizado'}</span>
          </div>
          <div class="modal-info-item modal-info-full">
            <span class="label">ID Interno</span>
            <span class="value mono">${empresa.id}</span>
          </div>
        </div>
        
        <div style="margin-top:20px;padding-top:20px;border-top:1px solid var(--border)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <h4 style="font-size:14px;color:var(--text);margin:0">🔌 Integração Omie API</h4>
            <div id="omie-status-${empresa.id}" style="font-size:11px;padding:2px 8px;border-radius:var(--r-full);background:var(--bg2);color:var(--text3)">Carregando...</div>
          </div>
          <div style="display:flex;flex-direction:column;gap:10px">
            <div>
              <label style="font-size:11px;color:var(--text3);display:block;margin-bottom:4px">App Key</label>
              <input type="text" id="omie-key-${empresa.id}" placeholder="Cole a App Key aqui" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:var(--r-sm);background:var(--bg);color:var(--text);font-family:monospace">
            </div>
            <div>
              <label style="font-size:11px;color:var(--text3);display:block;margin-bottom:4px">App Secret</label>
              <input type="password" id="omie-secret-${empresa.id}" placeholder="Cole o App Secret aqui" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:var(--r-sm);background:var(--bg);color:var(--text);font-family:monospace">
            </div>
            <button class="btn btn-primary" onclick="
              const k = document.getElementById('omie-key-${empresa.id}').value;
              const s = document.getElementById('omie-secret-${empresa.id}').value;
              fetch('/api/empresas/omie-keys', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({empresa_id: '${empresa.id}', app_key: k, app_secret: s})
              })
              .then(res => res.json())
              .then(data => {
                Toast.show(data.message, 'success');
                const badge = document.getElementById('omie-status-${empresa.id}');
                if (badge) {
                  badge.textContent = '✅ Chaves Configuradas';
                  badge.style.background = 'var(--tarik-l)';
                  badge.style.color = 'var(--tarik)';
                }
              })
              .catch(err => Toast.show('Erro: ' + err.message, 'error'));
            " style="align-self:flex-start;padding:6px 12px;font-size:12px">Salvar Chaves no Banco de Dados</button>
          </div>
        </div>
      `,
      footer: `
        <button class="btn btn-ghost" onclick="Modal.close()">Fechar</button>
        <button class="btn btn-primary" onclick="Utils.copyToClipboard('${empresa.nome} | CNPJ: ${empresa.cnpj} | ${empresa.banco} Ag:${empresa.ag} C:${empresa.conta}');Toast.show('Dados copiados!','success')">
          📋 Copiar dados
        </button>
      `
    });

    // Fetch existing keys after modal opens
    fetch(`/api/empresas/omie-keys/${empresa.id}`)
      .then(res => res.json())
      .then(data => {
        const badge = document.getElementById(`omie-status-${empresa.id}`);
        const kInp = document.getElementById(`omie-key-${empresa.id}`);
        const sInp = document.getElementById(`omie-secret-${empresa.id}`);
        if (data.has_keys && badge && kInp && sInp) {
          kInp.value = data.app_key;
          sInp.value = data.app_secret;
          badge.textContent = '✅ Chaves Configuradas';
          badge.style.background = 'var(--tarik-l)';
          badge.style.color = 'var(--tarik)';
        } else if (badge) {
          badge.textContent = '❌ Não Configurado';
          badge.style.background = 'var(--trk-l)';
          badge.style.color = 'var(--trk)';
        }
      })
      .catch(err => console.error(err));
  }
};

// ── CONFIRM DIALOG ──
const Confirm = {
  _overlay: null,
  _resolve: null,

  init() {
    this._overlay = document.createElement('div');
    this._overlay.className = 'confirm-overlay';
    this._overlay.innerHTML = '<div class="confirm-box" id="confirm-content"></div>';
    document.body.appendChild(this._overlay);
  },

  show(options = {}) {
    const { title = 'Tem certeza?', message = '', confirmText = 'Confirmar', cancelText = 'Cancelar', type = 'danger' } = options;
    return new Promise((resolve) => {
      this._resolve = resolve;
      const box = document.getElementById('confirm-content');
      box.innerHTML = `
        <h3>${title}</h3>
        <p>${message}</p>
        <div class="confirm-actions">
          <button class="btn btn-ghost" onclick="Confirm._answer(false)">${cancelText}</button>
          <button class="btn btn-${type}" onclick="Confirm._answer(true)">${confirmText}</button>
        </div>
      `;
      this._overlay.classList.add('open');
    });
  },

  _answer(val) {
    this._overlay.classList.remove('open');
    if (this._resolve) this._resolve(val);
    this._resolve = null;
  }
};
