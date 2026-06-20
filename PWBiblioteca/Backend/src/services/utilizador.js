const ValidationError = require('../errors/validationError');
const moment = require('moment');
const bcrypt = require('bcrypt');

const ROLES = ['cliente', 'bibliotecario', 'admin'];

module.exports = (app) => {

  const findAll = async () => {
    const result = await app.db('utilizadores').select('*');
    return result;
  };

  const findOne = async (id) => {
    const result = await app.db('utilizadores').select('*').where('id', id).first();
    return result;
  };

  const findByField = async (filter) => {
    const result = await app.db('utilizadores').select('*').where(filter).first();
    return result;
  };

  const save = async (dataset) => {
    if (!dataset.nome) throw new ValidationError('O campo [Nome] é obrigatório!');

    const newDataset = { ...dataset };
    newDataset.criado_em = moment().format("YYYY-MM-DD HH:mm:ss");
    const result = await app.db('utilizadores').insert(newDataset, '*');
    return result;
  };

  // Criação de conta pública: valida campos, email único, hash bcrypt, role cliente.
  const register = async (dataset) => {
    if (!dataset.nome) throw new ValidationError('O campo [Nome] é obrigatório!');
    if (!dataset.email) throw new ValidationError('O campo [Email] é obrigatório!');
    if (!dataset.password) throw new ValidationError('O campo [Password] é obrigatório!');

    const exists = await app.db('utilizadores').where('email', dataset.email).first();
    if (exists) throw new ValidationError('Já existe uma conta com esse email!');

    const newDataset = {
      nome: dataset.nome,
      email: dataset.email,
      password: bcrypt.hashSync(dataset.password, 10),
      role: 'cliente',
      criado_em: moment().format('YYYY-MM-DD HH:mm:ss'),
    };

    // Insert portável (SQLite devolve ids; relemos para devolver o registo completo).
    await app.db('utilizadores').insert(newDataset);
    const created = await app.db('utilizadores').where('email', dataset.email).first();
    return created;
  };

  const update = async (id, dataset) => {
    const newDataset = { ...dataset };
    const result = await app.db('utilizadores').where('id', id).update(newDataset, '*');
    return result;
  };

  // Atualiza apenas a password (com hash). Usado pelo fluxo de reset.
  const updatePassword = async (id, password) => {
    if (!password) throw new ValidationError('O campo [Password] é obrigatório!');
    const result = await app.db('utilizadores')
      .where('id', id)
      .update({ password: bcrypt.hashSync(password, 10) });
    return result;
  };

  // Promover/despromover: apenas entre cliente e bibliotecario.
  const setRole = async (id, role) => {
    if (!['cliente', 'bibliotecario'].includes(role)) {
      throw new ValidationError('Role inválido! Use cliente ou bibliotecario.');
    }
    const result = await app.db('utilizadores').where('id', id).update({ role });
    return result;
  };

  const remove = async (id) => {
    await app.db('utilizadores').where('id', id).del();
    return [];
  };

  return {
    findAll, findOne, save, register, update, updatePassword, setRole, remove, findByField, ROLES,
  };
};
