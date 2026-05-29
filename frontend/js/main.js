// ════════════════════════════════════════════════════════
// MAIN — Portal Grupo TRK v2.0
// Bootstrap, Search System, Keyboard Shortcuts
// ════════════════════════════════════════════════════════

const App = {
  init() {
    // Init Core
    Theme.init();
    Modal.init();
    Confirm.init();

    // Init Modules
    Tasks.init();
    Conciliacao.init();
    Rotinas.init();
    Drive.init();
    Empresas.init();
    Router.init();

    // Setup Global Search
    this.setupSearch();

    // Keyboard shortcuts
    document.addEventListener('keydown', e => {
      // Ctrl+K -> Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const inp = document.getElementById('global-search');
        if (inp) inp.focus();
      }
      // Esc -> Close dropdowns/modals
      if (e.key === 'Escape') {
        const dd = document.getElementById('search-dropdown');
        if (dd) dd.classList.remove('open');
      }
    });

    // Close search dropdown on click outside
    document.addEventListener('click', e => {
      const wrap = document.querySelector('.search-wrap');
      const dd = document.getElementById('search-dropdown');
      if (wrap && dd && !wrap.contains(e.target)) {
        dd.classList.remove('open');
      }
    });
  },

  setupSearch() {
    const inp = document.getElementById('global-search');
    const dd = document.getElementById('search-dropdown');
    if (!inp || !dd) return;

    inp.addEventListener('input', Utils.debounce(e => {
      const q = e.target.value.toLowerCase().trim();
      if (!q) {
        dd.classList.remove('open');
        return;
      }

      // Search companies
      const results = TODAS_EMPRESAS.filter(emp => 
        emp.nome.toLowerCase().includes(q) || 
        emp.cnpj.replace(/\D/g,'').includes(q.replace(/\D/g,'')) ||
        emp.banco.toLowerCase().includes(q)
      );

      if (results.length === 0) {
        dd.innerHTML = `<div class="search-empty">Nenhum resultado para "<b>${Utils.escapeHtml(q)}</b>"</div>`;
      } else {
        let html = '<div class="search-group-title">Empresas</div>';
        results.forEach(emp => {
          const nameHi = Utils.highlight(emp.nome, q);
          const cnpjHi = Utils.highlight(emp.cnpj, q);
          html += `
            <div class="search-result" onclick='App.selectSearchResult(${JSON.stringify(emp).replace(/'/g, "&#39;")})'>
              <div class="sr-icon" style="background:var(--${emp.grupo}-l);color:var(--${emp.grupo})">${Utils.initials(emp.nome)}</div>
              <div class="sr-info">
                <div class="sr-name">${nameHi}</div>
                <div class="sr-detail">${cnpjHi} • ${emp.banco}</div>
              </div>
            </div>
          `;
        });
        dd.innerHTML = html;
      }
      
      dd.classList.add('open');
    }, 200));

    inp.addEventListener('focus', () => {
      if (inp.value.trim()) dd.classList.add('open');
    });
  },

  selectSearchResult(empresa) {
    const dd = document.getElementById('search-dropdown');
    const inp = document.getElementById('global-search');
    if (dd) dd.classList.remove('open');
    if (inp) inp.value = '';
    Modal.showCompany(empresa);
  }
};

// Bootstrap when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
