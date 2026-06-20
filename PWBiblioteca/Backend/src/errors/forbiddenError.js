module.exports = function forbiddenError(message) {
  this.name = 'forbiddenError';
  this.message = message;
};
