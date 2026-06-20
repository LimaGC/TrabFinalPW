const moment = require('moment');
const setDate = moment().format('YYYY-MM-DD HH:mm:ss');



exports.seed = async (knex) => {


  const data = [
    {
      titulo: 'Os Lusíadas',
      autor: 'Luís de Camões',
      isbn: '978-972-0-01000-0',
      estado: 'disponivel',
      quantidade: 3,
      criado_em: setDate,
    },
    {
      titulo: 'Mensagem',
      autor: 'Fernando Pessoa',
      isbn: '978-972-0-02000-1',
      estado: 'disponivel',
      quantidade: 5,
      criado_em: setDate,
    },
    {
      titulo: 'Memorial do Convento',
      autor: 'José Saramago',
      isbn: '978-972-0-03000-2',
      estado: 'disponivel',
      quantidade: 2,
      criado_em: setDate,
    },
  ];

  // Idempotente: insere se não existir; caso contrário garante a quantidade de stock.
  return Promise.all(data.map(async (d) => {
    const rows = await knex('livros').select().where('isbn', d.isbn);
    if (rows.length === 0) {
      await knex('livros').insert(d);
    } else {
      await knex('livros').where('isbn', d.isbn).update({ quantidade: d.quantidade });
    }
    return true;
  }));
};
