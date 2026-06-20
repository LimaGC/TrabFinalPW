// Migração nova (alter table): adiciona a coluna [role] a utilizadores.
// Não altera a migração original de criação da tabela.
// Valores possíveis: cliente | bibliotecario | admin (default cliente).
exports.up = (knex) => knex.schema.alterTable('utilizadores', (t) => {
  t.string('role', 20).notNullable().defaultTo('cliente');
});

exports.down = (knex) => knex.schema.alterTable('utilizadores', (t) => {
  t.dropColumn('role');
});
