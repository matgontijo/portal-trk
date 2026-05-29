// ════════════════════════════════════════════════════════
// UTILS — Portal Grupo TRK v2.0
// Date formatting, helpers, clipboard, debounce
// ════════════════════════════════════════════════════════

const Utils = {
  DIAS: ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"],
  DIAS_SHORT: ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
  MESES: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
  MESES_SHORT: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],

  // Initials from company name
  initials(name) {
    const words = name.split(" ").filter(x => x.length > 2);
    return ((words[0] || "")[0] + (words[1] || "")[0]).toUpperCase();
  },

  // Bank CSS class
  bankClass(bank) {
    const l = (bank || "").toLowerCase();
    return l.includes("inter") ? "inter" : l.includes("bradesco") ? "bradesco" : "santander";
  },

  // Date to key string (YYYY-MM-DD)
  toKey(d) {
    return d.toISOString().split("T")[0];
  },

  // Full date format
  fmtDate(d) {
    return `${this.DIAS[d.getDay()]}, ${d.getDate()} de ${this.MESES[d.getMonth()]} de ${d.getFullYear()}`;
  },

  // Get date for specific day of the week in current week
  getDateForDay(targetDay) {
    const today = new Date();
    const currentDay = today.getDay();
    const distance = targetDay - currentDay;
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + distance);
    return targetDate;
  },

  // Short date format
  fmtShort(d) {
    return `${this.DIAS_SHORT[d.getDay()]} ${d.getDate()}/${this.MESES_SHORT[d.getMonth()]}/${d.getFullYear()}`;
  },

  // Format as BRL currency
  fmtBRL(n) {
    return "R$ " + parseFloat(n || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 });
  },

  // Copy text to clipboard
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      return true;
    }
  },

  // Debounce function calls
  debounce(fn, ms = 300) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), ms);
    };
  },

  // Highlight search term in text
  highlight(text, query) {
    if (!query) return text;
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  },

  // Animated counter
  animateNum(el, target, duration = 400) {
    if (!el) return;
    const current = parseInt(el.textContent) || 0;
    if (current === target) { el.textContent = target; return; }
    let start = null;
    function step(ts) {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3); // ease-out cubic
      el.textContent = Math.round(current + (target - current) * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  },

  // Stagger animation for list of elements
  staggerAnimate(selector, parentEl) {
    const items = (parentEl || document).querySelectorAll(selector);
    items.forEach((el, i) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(8px)';
      setTimeout(() => {
        el.style.transition = 'opacity .3s ease, transform .3s ease';
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }, i * 40);
    });
  },

  // Escape HTML
  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  // Generate unique ID
  uid() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  }
};
