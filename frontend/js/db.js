// ════════════════════════════════════════════════════════
// DATABASE SIMULATOR (Mini-ORM)
// Portal Grupo TRK v2.0
// ════════════════════════════════════════════════════════

const DB = {
  getCollection(name) {
    return Store.get(`db_${name}`, []);
  },
  
  saveCollection(name, data) {
    Store.set(`db_${name}`, data);
  },

  // Inserts a new record
  insert(collection, record) {
    const data = this.getCollection(collection);
    record.id = Utils.uid();
    record.createdAt = new Date().toISOString();
    data.push(record);
    this.saveCollection(collection, data);
    return record;
  },

  // Updates a record
  update(collection, id, updates) {
    const data = this.getCollection(collection);
    const index = data.findIndex(r => r.id === id);
    if (index === -1) return null;
    
    data[index] = { ...data[index], ...updates, updatedAt: new Date().toISOString() };
    this.saveCollection(collection, data);
    return data[index];
  },

  // Auto-conciliation engine
  runAutoConciliation(date) {
    const key = Utils.toKey(date);
    let concData = Store.get('conc_data', {});
    if (!concData[key]) concData[key] = {};

    let conciled = 0;
    let errors = 0;

    // Simulate calling Omie/Bank APIs and matching
    BPO_EMPRESAS.forEach(emp => {
      // 80% chance of auto-match, 20% chance of discrepancy
      const rand = Math.random();
      if (rand > 0.2) {
        // Auto-match OK
        const saldoSimulado = (Math.random() * 50000).toFixed(2);
        concData[key][emp.id] = {
          status: 'ok',
          saldo: saldoSimulado.replace('.', ','),
          obs: '🪄 Auto-conciliado pelo sistema (Match 100%).'
        };
        conciled++;
      } else {
        // Error / Discrepancy
        concData[key][emp.id] = {
          status: 'erro',
          saldo: '',
          obs: '⚠️ Divergência: Lançamento no extrato não encontrado no Omie.'
        };
        errors++;
      }
    });

    Store.set('conc_data', concData);

    // Save audit log
    const hist = Store.get('conc_hist', []);
    hist.unshift({
      date: new Date().toISOString(),
      action: 'Auto-Conciliação Robô',
      detail: `${conciled} OK | ${errors} Erros`
    });
    Store.set('conc_hist', hist);

    return { conciled, errors };
  }
};
