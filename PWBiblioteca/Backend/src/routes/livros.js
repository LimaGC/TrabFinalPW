const express = require('express');
const requireRole = require('../config/roles');

module.exports = (app) => {
  const router = express.Router();

  // Consulta livre a qualquer utilizador autenticado.
  router.get('/', (req, res, next) => {
    app.services.livro.findAll()
      .then((result) => res.status(200).json(result))
      .catch((err) => next(err));
  });

  router.get('/:id', (req, res, next) => {
    app.services.livro.findOne(req.params.id)
      .then((result) => res.status(200).json(result))
      .catch((err) => next(err));
  });

  // Criar/editar/eliminar apenas bibliotecario/admin.
  router.post('/', requireRole('bibliotecario', 'admin'), async (req, res, next) => {
    try {
      const result = await app.services.livro.save(req.body);
      return res.status(201).json(result);
    } catch (err) {
      return next(err);
    }
  });

  router.put('/:id', requireRole('bibliotecario', 'admin'), (req, res, next) => {
    app.services.livro.update(req.params.id, req.body)
      .then((result) => res.status(200).json(result))
      .catch((err) => next(err));
  });

  router.delete('/:id', requireRole('bibliotecario', 'admin'), (req, res, next) => {
    app.services.livro.remove(req.params.id)
      .then(() => res.status(204).json())
      .catch((err) => next(err));
  });

  return router;
};
