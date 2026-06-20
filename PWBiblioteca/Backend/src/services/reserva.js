const ValidationError = require('../errors/validationError');
const moment = require('moment');

// Estados de reserva:
//   pendente    -> criada pelo cliente, à espera de aprovação (ocupa uma cópia)
//   confirmada  -> aprovada por bibliotecario/admin (continua a ocupar uma cópia)
//   terminada   -> entrega/devolução concluída (liberta a cópia)
//   cancelada   -> cancelada pelo cliente (liberta a cópia)
//
// A disponibilidade do livro é calculada (quantidade - cópias ocupadas),
// pelo que não é necessário alterar o estado do livro a cada reserva.
const OCUPA_LIVRO = ['pendente', 'confirmada'];

const isStaff = (token) => token.role === 'bibliotecario' || token.role === 'admin';

module.exports = (app) => {

  // Lista com o nome do cliente e o título do livro (via join).
  const baseQuery = () => app.db('reservas')
    .leftJoin('utilizadores', 'reservas.utilizador_id', 'utilizadores.id')
    .leftJoin('livros', 'reservas.livro_id', 'livros.id')
    .select(
      'reservas.*',
      'utilizadores.nome as utilizador_nome',
      'livros.titulo as livro_titulo',
    );

  const findAll = async (token) => {
    // Bibliotecario/Admin veem todas as reservas em curso (ativas e aceites).
    if (isStaff(token)) {
      return baseQuery().whereIn('reservas.estado', OCUPA_LIVRO);
    }
    // Cliente vê apenas as suas reservas.
    return baseQuery().where('reservas.utilizador_id', token.id);
  };

  const findOne = async (id, token) => {
    const result = await baseQuery().where('reservas.id', id).first();
    if (result && !isStaff(token) && result.utilizador_id != token.id) {
      throw new ValidationError('Não tem permissão para consultar');
    }
    return result;
  };

  const findByField = async (filter) => {
    const result = await app.db('reservas').select('*').where(filter).first();
    return result;
  };

  // Nº de cópias ocupadas de um livro (reservas em curso).
  const ocupadasDoLivro = async (livroId) => {
    const row = await app.db('reservas')
      .where('livro_id', livroId)
      .whereIn('estado', OCUPA_LIVRO)
      .count('* as ocupadas')
      .first();
    return Number(row.ocupadas);
  };

  const save = async (dataset, token) => {
    if (!dataset.livro_id) throw new ValidationError('O campo [Livro Id] é obrigatório!');

    const livro = await app.db('livros').where('id', dataset.livro_id).first();
    if (!livro) throw new ValidationError('Livro não encontrado!');

    const ocupadas = await ocupadasDoLivro(dataset.livro_id);
    const disponiveis = (livro.quantidade || 0) - ocupadas;
    if (livro.estado !== 'disponivel' || disponiveis <= 0) {
      throw new ValidationError('Livro não está disponível!');
    }

    const newDataset = {
      utilizador_id: token.id, // utilizador_id vem sempre do token
      livro_id: dataset.livro_id,
      estado: 'pendente', // fica pendente de aprovação até o staff confirmar
      data_reserva: moment().format("YYYY-MM-DD HH:mm:ss"),
    };
    const result = await app.db('reservas').insert(newDataset, '*');
    return result;
  };

  const update = async (id, dataset, token) => {
    const reserva = await app.db('reservas').where('id', id).first();
    if (!reserva) throw new ValidationError('Reserva não encontrada!');

    // Cliente só altera as suas; bibliotecario/admin alteram qualquer uma.
    if (!isStaff(token) && reserva.utilizador_id != token.id) {
      throw new ValidationError('Não tem permissão para atualizar');
    }

    // O cliente só pode cancelar; aprovar (confirmada) ou terminar é só do staff.
    if (!isStaff(token) && dataset.estado && dataset.estado !== 'cancelada') {
      throw new ValidationError('Apenas um bibliotecário ou admin pode aprovar/terminar reservas.');
    }

    const newDataset = { ...dataset };
    const result = await app.db('reservas').where('id', id).update(newDataset, '*');
    return result;
  };

  const remove = async (id, token) => {
    const reserva = await app.db('reservas').where('id', id).first();
    if (!reserva) throw new ValidationError('Reserva não encontrada!');

    if (!isStaff(token) && reserva.utilizador_id != token.id) {
      throw new ValidationError('Não tem permissão para remover');
    }

    await app.db('reservas').where('id', id).del();
    return [];
  };

  return { findAll, findOne, save, update, remove, findByField };
};
