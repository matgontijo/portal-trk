// ════════════════════════════════════════════════════════
// EMPRESAS — Portal Grupo TRK v2.0
// Tab: Empresas (List, Grid, Search, Filter)
// ════════════════════════════════════════════════════════

const Empresas = {
  viewMode: 'list', // list | grid
  sortBy: 'nome',   // nome | banco
  filterGrupo: null, // null | trk | bpo
  searchQuery: '',

  init() {
    // Setup listeners
    const sInp = document.getElementById('emp-search');
    if (sInp) sInp.addEventListener('input', Utils.debounce(e => {
      this.searchQuery = e.target.value;
      this.render();
    }));

    const sortSel = document.getElementById('emp-sort');
    if (sortSel) sortSel.addEventListener('change', e => {
      this.sortBy = e.target.value;
      this.render();
    });

    document.querySelectorAll('.view-btn').forEach(b => {
      b.addEventListener('click', () => {
        this.viewMode = b.dataset.view;
        document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
        b.classList.add('active');
        this.render();
      });
    });

    this.render();
  },

  setFilter(g) {
    if (this.filterGrupo === g) this.filterGrupo = null;
    else this.filterGrupo = g;

    document.querySelectorAll('.emp-pill').forEach(p => p.classList.remove('on'));
    if (this.filterGrupo) {
      document.querySelector(`.emp-pill.p-${this.filterGrupo}`).classList.add('on');
      document.getElementById('emp-clear').classList.add('show');
    } else {
      document.getElementById('emp-clear').classList.remove('show');
    }
    this.render();
  },

  clearFilter() {
    this.filterGrupo = null;
    document.querySelectorAll('.emp-pill').forEach(p => p.classList.remove('on'));
    document.getElementById('emp-clear').classList.remove('show');
    const sInp = document.getElementById('emp-search');
    if (sInp) { sInp.value = ''; this.searchQuery = ''; }
    this.render();
  },

  getFiltered() {
    let list = [...TODAS_EMPRESAS];

    if (this.filterGrupo) {
      list = list.filter(e => e.grupo === this.filterGrupo);
    }

    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase();
      list = list.filter(e => 
        e.nome.toLowerCase().includes(q) || 
        e.cnpj.replace(/\D/g,'').includes(q.replace(/\D/g,'')) ||
        e.banco.toLowerCase().includes(q)
      );
    }

    if (this.sortBy === 'nome') list.sort((a,b) => a.nome.localeCompare(b.nome));
    if (this.sortBy === 'banco') list.sort((a,b) => a.banco.localeCompare(b.banco));

    return list;
  },

  render() {
    const list = this.getFiltered();
    const container = document.getElementById('empresas-list');
    if (!container) return;

    // Update count summary
    const countEl = document.getElementById('emp-count');
    if (countEl) countEl.innerHTML = `Mostrando <b>${list.length}</b> empresas`;

    if (list.length === 0) {
      container.innerHTML = `
        <div class="empty-state anim-fade-up">
          <span class="empty-icon">🏢</span>
          <p>Nenhuma empresa encontrada com os filtros atuais.</p>
        </div>
      `;
      container.className = '';
      return;
    }

    container.className = this.viewMode === 'grid' ? 'cards-grid' : '';
    let html = '';

    list.forEach((e, i) => {
      const bc = Utils.bankClass(e.banco);
      html += `
        <div class="card ${e.grupo} anim-fade-up stagger-${(i%10)+1}" onclick='Modal.showCompany(${JSON.stringify(e).replace(/'/g, "&#39;")})'>
          <div class="avatar ${e.grupo}">${Utils.initials(e.nome)}</div>
          <div class="card-body">
            <div class="card-name">${Utils.highlight(e.nome, this.searchQuery)}</div>
            <div class="card-meta">
              <span class="cnpj" onclick="event.stopPropagation();Utils.copyToClipboard('${e.cnpj}');Toast.show('CNPJ Copiado','success')">${Utils.highlight(e.cnpj, this.searchQuery)}</span>
              <span class="resp-badge ${e.resp}">${e.resp === 'rafael' ? 'Rafael' : 'Tárik'}</span>
            </div>
          </div>
          <div class="card-right">
            <span class="group-tag ${e.grupo}">${e.grupo === 'trk' ? 'TRK' : 'BPO'}</span>
            <span class="bank-tag ${bc}">${Utils.highlight(e.banco, this.searchQuery)}</span>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  }
};
