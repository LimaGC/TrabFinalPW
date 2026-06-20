const moment = require('moment');
const bcryptUp = require('bcrypt');
const setDate = moment().format('YYYY-MM-DD HH:mm:ss');



exports.seed = async (knex) => {

  // Todos os utilizadores de demonstração usam a password "123456" (hash bcrypt).
  const demoPass = await bcryptUp.hash('123456', 10);

  const data = [
    {
      nome: 'Carlos Joaquim',
      email: 'cjoaquim@biblioteca.pt',
      password: demoPass,
      role: 'admin',
      criado_em: setDate,
    },
    {
      nome: 'Ana Costa',
      email: 'ana@biblioteca.pt',
      password: demoPass,
      role: 'bibliotecario',
      criado_em: setDate,
    },
    {
      nome: 'Margarida',
      email: 'margarida@biblioteca.pt',
      password: demoPass,
      role: 'cliente',
      criado_em: setDate,
    },
  ];

  // Idempotente: se o utilizador já existir (mesmo email) garante apenas o role correto;
  // caso contrário insere o registo completo.
  return Promise.all(data.map(async (d) => {
    const rows = await knex('utilizadores').select().where('email', d.email);
    if (rows.length === 0) {
      await knex('utilizadores').insert(d);
    } else {
      await knex('utilizadores').where('email', d.email).update({ role: d.role });
    }
    return true;
  }));
};
