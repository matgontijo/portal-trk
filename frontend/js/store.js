// ════════════════════════════════════════════════════════
// STORE — Portal Grupo TRK v2.0
// LocalStorage wrapper with export/import
// ════════════════════════════════════════════════════════

const Store = {
  PREFIX: 'gtrk_',

  get(key, fallback = null) {
    try {
      const raw = localStorage.getItem(key);
      if (raw === null) return fallback;
      return JSON.parse(raw);
    } catch (e) {
      return localStorage.getItem(key) || fallback;
    }
  },

  set(key, value) {
    if (typeof value === 'object') {
      localStorage.setItem(key, JSON.stringify(value));
    } else {
      localStorage.setItem(key, value);
    }
  },

  remove(key) {
    localStorage.removeItem(key);
  },

  // Export all portal data as JSON
  exportData() {
    const data = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith('gtrk_') || key.startsWith('rot_') || key.startsWith('drive_') || key.startsWith('conc_')) {
        try {
          data[key] = JSON.parse(localStorage.getItem(key));
        } catch (e) {
          data[key] = localStorage.getItem(key);
        }
      }
    }
    return data;
  },

  // Download as JSON file
  downloadBackup() {
    const data = this.exportData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const date = new Date().toISOString().split('T')[0];
    a.href = url;
    a.download = `backup-portal-trk-${date}.json`;
    a.click();
    URL.revokeObjectURL(url);
    Toast.show('Backup baixado com sucesso', 'success');
  },

  // Import from JSON file
  importBackup(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        let count = 0;
        for (const [key, value] of Object.entries(data)) {
          if (typeof value === 'object') {
            localStorage.setItem(key, JSON.stringify(value));
          } else {
            localStorage.setItem(key, value);
          }
          count++;
        }
        Toast.show(`${count} registros restaurados`, 'success');
        // Refresh all tabs
        setTimeout(() => location.reload(), 1000);
      } catch (err) {
        Toast.show('Erro ao importar backup', 'error');
      }
    };
    reader.readAsText(file);
  },

  // Clear all portal data
  clearAll() {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith('gtrk_') || key.startsWith('rot_') || key.startsWith('drive_') || key.startsWith('conc_')) {
        keys.push(key);
      }
    }
    keys.forEach(k => localStorage.removeItem(k));
    return keys.length;
  }
};
