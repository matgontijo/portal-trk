// ════════════════════════════════════════════════════════
// ROUTER — Portal Grupo TRK v2.0
// Tab navigation with URL hash + mobile nav sync
// ════════════════════════════════════════════════════════

const Router = {
  currentTab: 'rotinas',

  init() {
    // Check URL hash
    const hash = location.hash.replace('#', '');
    if (['rotinas', 'conciliacao', 'empresas'].includes(hash)) {
      this.go(hash, false);
    }
    // Handle back/forward
    window.addEventListener('hashchange', () => {
      const h = location.hash.replace('#', '');
      if (['rotinas', 'conciliacao', 'empresas'].includes(h)) {
        this.go(h, false);
      }
    });
  },

  go(tabId, updateHash = true) {
    this.currentTab = tabId;

    // Update panels
    document.querySelectorAll('.tab-panel').forEach(t => t.classList.remove('active'));
    const panel = document.getElementById('tab-' + tabId);
    if (panel) panel.classList.add('active');

    // Update desktop nav
    document.querySelectorAll('.nav-tab').forEach(t => {
      const onclick = t.getAttribute('onclick') || '';
      t.classList.toggle('active', onclick.includes(`'${tabId}'`));
    });

    // Update mobile nav
    document.querySelectorAll('.bnav-tab').forEach(t => {
      t.classList.toggle('active', t.dataset.tab === tabId);
    });

    // Update URL hash
    if (updateHash) {
      history.pushState(null, '', '#' + tabId);
    }

    // Render tab content
    if (tabId === 'empresas') Empresas.render();
    if (tabId === 'conciliacao') Conciliacao.render();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

function switchTab(id, el) {
  Router.go(id);
}
