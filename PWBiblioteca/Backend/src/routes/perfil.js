const express = require('express');

// Nunca expor a password nas respostas.
const semPassword = (u) => {
  if (!u) return u;
  const { password, ...rest } = u;
  return rest;
};

// Perfil do próprio utilizador autenticado (qualquer role).
// Opera sempre sobre req.user.id (vindo do token), nunca sobre um id arbitrário.
module.exports = (app) => {
  const router = express.Router();

  // Dados do próprio perfil.
  router.get('/', (req, res, next) => {
    app.services.utilizador.findOne(req.user.id)
      .then((u) => res.status(200).json(semPassword(u)))
      .catch((err) => next(err));
  });

  // Editar o próprio perfil (nome / email).
  router.put('/', async (req, res, next) => {
    try {
      const updated = await app.services.utilizador.updateProfile(req.user.id, {
        nome: req.body.nome,
        email: req.body.email,
      });
      return res.status(200).json(semPassword(updated));
    } catch (err) {
      return next(err);
    }
  });

  // Alterar a própria password (exige a password atual).
  router.put('/password', async (req, res, next) => {
    try {
      await app.services.utilizador.changePassword(
        req.user.id,
        req.body.currentPassword,
        req.body.newPassword,
      );
      return res.status(200).json({ message: 'Password alterada com sucesso.' });
    } catch (err) {
      return next(err);
    }
  });

  return router;
};
