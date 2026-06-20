const express = require('express');
const jwt = require('jwt-simple');
const bcryptUp = require('bcrypt');
const AuthenticationError = require('../errors/authenticationError');
const ValidationError = require('../errors/validationError');

const secret = 'ERSC202526';

module.exports = (app) => {
  const router = express.Router();

  // POST /auths/signin - autenticação. Devolve { token } com role no payload.
  router.post('/signin', (req, res, next) => {
    app.services.utilizador.findByField({ email: req.body.email })
      .then(async (user) => {
        if (user && bcryptUp.compareSync(req.body.password, user.password)) {
          const payload = {
            id: user.id,
            email: user.email,
            role: user.role,
            expires: Date.now() + (1000 * 60 * 60), // 1 hora
          };
          const token = jwt.encode(payload, secret);
          res.status(200).json({ token });
        } else {
          throw new AuthenticationError('Autentication Error');
        }
      }).catch((err) => next(err));
  });

  // POST /auths/signup - criar conta (pública). Role sempre cliente.
  router.post('/signup', async (req, res, next) => {
    try {
      const user = await app.services.utilizador.register(req.body);
      // Nunca expor a password.
      const { password, ...safeUser } = user;
      return res.status(201).json(safeUser);
    } catch (err) {
      return next(err);
    }
  });

  // POST /auths/forgot-password - gera token de reset (expira em 15 min).
  // Como não existe envio de email real, o token é devolvido na resposta.
  router.post('/forgot-password', (req, res, next) => {
    app.services.utilizador.findByField({ email: req.body.email })
      .then((user) => {
        if (!user) throw new ValidationError('Não existe conta com esse email!');

        const payload = {
          id: user.id,
          email: user.email,
          type: 'reset',
          expires: Date.now() + (1000 * 60 * 15), // 15 minutos
        };
        const resetToken = jwt.encode(payload, secret);
        res.status(200).json({
          resetToken,
          info: 'Não existe email real: use este token na página de reset de password.',
        });
      }).catch((err) => next(err));
  });

  // POST /auths/reset-password - valida o token de reset e atualiza a password.
  router.post('/reset-password', async (req, res, next) => {
    try {
      const { resetToken, password } = req.body;
      if (!resetToken) throw new ValidationError('O campo [resetToken] é obrigatório!');
      if (!password) throw new ValidationError('O campo [Password] é obrigatório!');

      let payload;
      try {
        payload = jwt.decode(resetToken, secret);
      } catch (e) {
        throw new ValidationError('Token de reset inválido!');
      }

      if (payload.type !== 'reset') throw new ValidationError('Token de reset inválido!');
      if (Date.now() >= payload.expires) throw new ValidationError('Token de reset expirado!');

      await app.services.utilizador.updatePassword(payload.id, password);
      return res.status(200).json({ message: 'Password atualizada com sucesso.' });
    } catch (err) {
      return next(err);
    }
  });

  return router;
};
