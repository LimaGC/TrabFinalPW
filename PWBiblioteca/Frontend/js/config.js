// ============================================================
// Configuração e helpers de autenticação partilhados.
// Vanilla JS, sem frameworks nem build.
// ============================================================

// Base URL única da API (o backend corre em http://localhost:3001).
const API_BASE = 'http://localhost:3001';

// Descodifica o payload do JWT (parte do meio do token).
function decodeToken(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
}

// Valida o token: existe e ainda não expirou.
function isTokenValid(token) {
  if (!token) return false;

  const payload = decodeToken(token);
  if (!payload) return false;

  const now = Date.now();
  if (payload.expires && payload.expires < now) return false;
  if (payload.exp && payload.exp * 1000 < now) return false;

  return true;
}

// Guarda token + email + role (lido do payload) em localStorage.
function saveSession(token, email) {
  const payload = decodeToken(token) || {};
  localStorage.setItem('token', token);
  localStorage.setItem('email', email || payload.email || '');
  localStorage.setItem('role', payload.role || 'cliente');
}

function getToken() {
  return localStorage.getItem('token');
}

function getRole() {
  return localStorage.getItem('role') || 'cliente';
}

function getEmail() {
  return localStorage.getItem('email') || '';
}

function isStaff() {
  const r = getRole();
  return r === 'bibliotecario' || r === 'admin';
}

function isAdmin() {
  return getRole() === 'admin';
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('email');
  localStorage.removeItem('role');
  window.location.href = 'login.html';
}

// Usar no arranque de cada página privada. Devolve o token válido ou faz logout.
function checkAuth() {
  const token = getToken();
  if (!isTokenValid(token)) {
    logout();
    return null;
  }
  return token;
}

// Header de autorização para chamadas privadas.
function authHeaders(extra) {
  return Object.assign(
    { 'Authorization': `Bearer ${getToken()}` },
    extra || {},
  );
}


// Constrói a sidebar (menu) consoante o role do utilizador autenticado.
// Esconde no UI as opções sem permissão (o backend valida na mesma).
function renderSidebar(activePage) {
  const role = getRole();

  // Itens de menu: cada um indica que roles o podem ver.
  const items = [
    { href: 'dashboard.html', label: 'Dashboard', roles: ['cliente', 'bibliotecario', 'admin'] },
    { href: 'livros.html', label: 'Livros', roles: ['cliente', 'bibliotecario', 'admin'] },
    { href: 'reservas.html', label: 'Reservas', roles: ['cliente', 'bibliotecario', 'admin'] },
    { href: 'utilizadores.html', label: 'Utilizadores', roles: ['admin'] },
    { href: 'perfil.html', label: 'O Meu Perfil', roles: ['cliente', 'bibliotecario', 'admin'] },
  ];

  const links = items
    .filter((i) => i.roles.includes(role))
    .map((i) => {
      const active = i.href === activePage ? ' class="active"' : '';
      return `<a href="${i.href}"${active}>${i.label}</a>`;
    })
    .join('\n');

  const roleLabel = { cliente: 'Cliente', bibliotecario: 'Bibliotecário', admin: 'Administrador' }[role] || role;

  return `
    <h1>Biblioteca</h1>
    <h2>Gestão de Biblioteca</h2>
    <nav class="menu">
      ${links}
    </nav>
    <p class="session-info">${getEmail()}<br><span>${roleLabel}</span></p>
    <button class="logout" onclick="logout()">Logout</button>
  `;
}
