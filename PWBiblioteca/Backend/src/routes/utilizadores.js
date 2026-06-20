const express = require('express');
const requireRole = require('../config/roles');

// Nunca expor a password nas respostas.
const semPassword = (u) => {
  if (!u) return u;
  const { password, ...rest } = u;
  return rest;
};

module.exports = (app) => {
  const router = express.Router();

  // Toda a gestão de contas é restrita a admin.
  router.use(requireRole('admin'));

  // Listar todas as contas.
  router.get('/', (req, res, next) => {
    app.services.utilizador.findAll()
      .then((result) => res.status(200).json(result.map(semPassword)))
      .catch((err) => next(err));
  });

  // Consultar uma conta.
  router.get('/:id', (req, res, next) => {
    app.services.utilizador.findOne(req.params.id)
      .then((result) => res.status(200).json(semPassword(result)))
      .catch((err) => next(err));
  });

  // Editar conta (nome / email). Ignora password e role neste endpoint.
  router.put('/:id', async (req, res, next) => {
    try {
      const dataset = {};
      if (req.body.nome !== undefined) dataset.nome = req.body.nome;
      if (req.body.email !== undefined) dataset.email = req.body.email;
      await app.services.utilizador.update(req.params.id, dataset);
      const updated = await app.services.utilizador.findOne(req.params.id);
      return res.status(200).json(semPassword(updated));
    } catch (err) {
      return next(err);
    }
  });

  // Promover / despromover (cliente <-> bibliotecario).
  router.put('/:id/role', async (req, res, next) => {
    try {
      await app.services.utilizador.setRole(req.params.id, req.body.role);
      const updated = await app.services.utilizador.findOne(req.params.id);
      return res.status(200).json(semPassword(updated));
    } catch (err) {
      return next(err);
    }
  });

  // Eliminar conta.
  router.delete('/:id', (req, res, next) => {
    app.services.utilizador.remove(req.params.id)
      .then(() => res.status(204).json())
      .catch((err) => next(err));
  });

  return router;
};
