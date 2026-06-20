const ValidationError = require('../errors/validationError');
const moment = require('moment');

// Reservas que ocupam uma cópia do livro (pendentes de aprovação e confirmadas).
const OCUPA_LIVRO = ['pendente', 'confirmada'];

module.exports = (app) => {

  // Acrescenta a cada livro a informação de stock/disponibilidade:
  //   quantidade  -> total de cópias (coluna na BD)
  //   ocupadas    -> cópias com reserva em curso (ativa/aceite)
  //   disponiveis -> cópias livres (quantidade - ocupadas)
  //   disponivel  -> boolean efetivo (estado manual = disponivel E há cópias livres)
  const decorate = (livro, ocupadas) => {
    if (!livro) return livro;
    const quantidade = livro.quantidade || 0;
    const disponiveis = Math.max(0, quantidade - ocupadas);
    return {
      ...livro,
      quantidade,
      ocupadas,
      disponiveis,
      disponivel: livro.estado === 'disponivel' && disponiveis > 0,
    };
  };

  // Conta as cópias ocupadas por livro (mapa livro_id -> ocupadas).
  const contarOcupadas = async (livroIds) => {
    if (!livroIds || livroIds.length === 0) return {};
    const rows = await app.db('reservas')
      .select('livro_id')
      .count('* as ocupadas')
      .whereIn('estado', OCUPA_LIVRO)
      .whereIn('livro_id', livroIds)
      .groupBy('livro_id');
    const map = {};
    rows.forEach((r) => { map[r.livro_id] = Number(r.ocupadas); });
    return map;
  };

  const findAll = async () => {
    const livros = await app.db('livros').select('*');
    const map = await contarOcupadas(livros.map((l) => l.id));
    return livros.map((l) => decorate(l, map[l.id] || 0));
  };

  // Catálogo público: apenas livros efetivamente disponíveis.
  const findAllDisponiveis = async () => {
    const todos = await findAll();
    return todos.filter((l) => l.disponivel);
  };

  const findOne = async (id) => {
    const livro = await app.db('livros').select('*').where('id', id).first();
    if (!livro) return livro;
    const map = await contarOcupadas([livro.id]);
    return decorate(livro, map[livro.id] || 0);
  };

  const findByField = async (filter) => {
    const result = await app.db('livros').select('*').where(filter).first();
    return result;
  };

  const save = async (dataset) => {
    if (!dataset.titulo) throw new ValidationError('O campo [Titulo] é obrigatório!');
    if (!dataset.autor) throw new ValidationError('O campo [Autor] é obrigatório!');
    if (!dataset.isbn) throw new ValidationError('O campo [ISBN] é obrigatório!');

    const newDataset = { ...dataset };
    newDataset.estado = newDataset.estado || 'disponivel';
    newDataset.quantidade = (newDataset.quantidade === undefined || newDataset.quantidade === null)
      ? 1
      : Number(newDataset.quantidade);
    if (Number.isNaN(newDataset.quantidade) || newDataset.quantidade < 0) {
      throw new ValidationError('A [Quantidade] tem de ser um número igual ou superior a 0!');
    }
    newDataset.criado_em = moment().format("YYYY-MM-DD HH:mm:ss");
    const result = await app.db('livros').insert(newDataset, '*');
    return result;
  };

  const update = async (id, dataset) => {
    const newDataset = { ...dataset };
    if (newDataset.quantidade !== undefined) {
      newDataset.quantidade = Number(newDataset.quantidade);
      if (Number.isNaN(newDataset.quantidade) || newDataset.quantidade < 0) {
        throw new ValidationError('A [Quantidade] tem de ser um número igual ou superior a 0!');
      }
    }
    const result = await app.db('livros').where('id', id).update(newDataset, '*');
    return result;
  };

  const remove = async (id) => {
    await app.db('livros').where('id', id).del();
    return [];
  };

  return { findAll, findAllDisponiveis, findOne, save, update, remove, findByField };
};
