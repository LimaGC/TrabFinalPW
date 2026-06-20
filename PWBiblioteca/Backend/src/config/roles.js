const ForbiddenError = require('../errors/forbiddenError');

// Helper de autorização por role.
// Valida req.user.role (preenchido pelo passport-jwt a partir do payload do token).
// Uso: router.post('/', requireRole('bibliotecario', 'admin'), handler)
// Em caso de falha responde com forbiddenError -> HTTP 403.
const requireRole = (...roles) => (req, res, next) => {
  if (req.user && roles.includes(req.user.role)) return next();
  return next(new ForbiddenError('Não tem permissão para esta operação!'));
};

module.exports = requireRole;
