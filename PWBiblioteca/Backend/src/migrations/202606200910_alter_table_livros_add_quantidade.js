// Migração nova (alter table): adiciona a coluna [quantidade] a livros.
// Representa o número total de cópias do livro em stock (default 1).
exports.up = (knex) => knex.schema.alterTable('livros', (t) => {
  t.integer('quantidade').notNullable().defaultTo(1);
});

exports.down = (knex) => knex.schema.alterTable('livros', (t) => {
  t.dropColumn('quantidade');
});
