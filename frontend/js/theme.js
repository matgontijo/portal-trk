// ════════════════════════════════════════════════════════
// THEME — Portal Grupo TRK v2.0
// Dark/Light mode toggle with persistence
// ════════════════════════════════════════════════════════

const Theme = {
  init() {
    const saved = localStorage.getItem('gtrk_theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    this.updateIcon();
  },

  toggle() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('gtrk_theme', newTheme);
    this.updateIcon();
    Toast.show(isDark ? 'Tema claro ativado' : 'Tema escuro ativado', 'info');
  },

  updateIcon() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    if (sunIcon) sunIcon.style.display = isDark ? 'none' : 'block';
    if (moonIcon) moonIcon.style.display = isDark ? 'block' : 'none';
  }
};
