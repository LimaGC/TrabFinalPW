const passport = require('passport');
const passportJwt = require('passport-jwt');
const config = require('../config');

const secret = 'ERSC202526';

const { Strategy, ExtractJwt } = passportJwt;

module.exports = (app) => {
  const params = {
    secretOrKey: secret,
    jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  };

  const strategy = new Strategy(params, (payload, done) => {
    if (Date.now() >= payload.expires) return done(null, false);

    app.services.utilizador.findByField({ email: payload.email })
      .then((user) => {
        // Mantém o role (e restantes campos) do payload em req.user.
        if (user) done(null, { ...payload });
        else done(null, false);
      }).catch((err) => done(err, false));
  });

  passport.use(strategy);

  return { authenticate: () => passport.authenticate('jwt', { session: false }) };
};
