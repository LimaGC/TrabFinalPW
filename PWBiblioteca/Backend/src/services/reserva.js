const ValidationError = require('../errors/validationError');
const moment = require('moment');

// Estados de reserva:
//   ativa      -> reserva criada pelo cliente (livro fica 'reservado')
//   aceite     -> bibliotecario/admin aceitou (livro continua ocupado)
//   terminada  -> entrega/devolução concluída (livro volta a 'disponivel')
//   cancelada  -> cliente cancelou (livro volta a 'disponivel')
const DEVOLVE_LIVRO = ['cancelada', 'terminada'];
const OCUPA_LIVRO = ['ativa', 'aceite'];

const isStaff = (token) => token.role === 'bibliotecario' || token.role === 'admin';

module.exports = (app) => {

  const findAll = async (token) => {
    // Bibliotecario/Admin veem todas as reservas em curso (ativas e aceites).
    if (isStaff(token)) {
      return app.db('reservas').select('*').whereIn('estado', OCUPA_LIVRO);
    }
    // Cliente vê apenas as suas reservas.
    return app.db('reservas').select('*').where('utilizador_id', token.id);
  };

  const findOne = async (id, token) => {
    const result = await app.db('reservas').select('*').where('id', id).first();
    if (result && !isStaff(token) && result.utilizador_id != token.id) {
      throw new ValidationError('Não tem permissão para consultar');
    }
    return result;
  };

  const findByField = async (filter) => {
    const result = await app.db('reservas').select('*').where(filter).first();
    return result;
  };

  const save = async (dataset, token) => {
    if (!dataset.livro_id) throw new ValidationError('O campo [Livro Id] é obrigatório!');

    const livro = await app.db('livros').where('id', dataset.livro_id).first();
    if (!livro) throw new ValidationError('Livro não encontrado!');
    if (livro.estado !== 'disponivel') throw new ValidationError('Livro não está disponível!');

    const newDataset = {
      utilizador_id: token.id, // utilizador_id vem sempre do token
      livro_id: dataset.livro_id,
      estado: 'ativa',
      data_reserva: moment().format("YYYY-MM-DD HH:mm:ss"),
    };
    const result = await app.db('reservas').insert(newDataset, '*');

    await app.db('livros').where('id', dataset.livro_id).update({ estado: 'reservado' });

    return result;
  };

  const update = async (id, dataset, token) => {
    const reserva = await app.db('reservas').where('id', id).first();
    if (!reserva) throw new ValidationError('Reserva não encontrada!');

    // Cliente só altera as suas; bibliotecario/admin alteram qualquer uma.
    if (!isStaff(token) && reserva.utilizador_id != token.id) {
      throw new ValidationError('Não tem permissão para atualizar');
    }

    const newDataset = { ...dataset };
    const result = await app.db('reservas').where('id', id).update(newDataset, '*');

    // Se a transição leva a um estado que liberta o livro, repor 'disponivel'.
    if (newDataset.estado
        && DEVOLVE_LIVRO.includes(newDataset.estado)
        && !DEVOLVE_LIVRO.includes(reserva.estado)) {
      await app.db('livros').where('id', reserva.livro_id).update({ estado: 'disponivel' });
    }

    return result;
  };

  const remove = async (id, token) => {
    const reserva = await app.db('reservas').where('id', id).first();
    if (!reserva) throw new ValidationError('Reserva não encontrada!');

    if (!isStaff(token) && reserva.utilizador_id != token.id) {
      throw new ValidationError('Não tem permissão para remover');
    }

    // Se a reserva ainda ocupava o livro, devolvê-lo ao catálogo.
    if (OCUPA_LIVRO.includes(reserva.estado)) {
      await app.db('livros').where('id', reserva.livro_id).update({ estado: 'disponivel' });
    }

    await app.db('reservas').where('id', id).del();
    return [];
  };

  return { findAll, findOne, save, update, remove, findByField };
};
