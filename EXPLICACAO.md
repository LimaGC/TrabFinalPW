# Explicação do Código — PWBiblioteca

Este ficheiro explica, de forma simples, o que faz **cada ficheiro** do projeto e
**como cada um se encaixa no padrão MVC** (Model–View–Controller).

> **Nota sobre o MVC neste projeto:**
> - **Model** = `src/services/*.js` (lógica de negócio + acesso à base de dados).
> - **Controller = Endpoints** = `src/routes/*.js` (definem as rotas/endpoints da API
>   REST, tratam o pedido/resposta HTTP e chamam os serviços). Sempre que abaixo se
>   fala em "controller", referimo-nos aos **endpoints**.
> - **View** = `PWBiblioteca/Frontend/*` (páginas HTML/CSS/JS que o utilizador vê).

---

## 1. Backend (API REST) — `PWBiblioteca/Backend/`

### 1.1. Ficheiros de configuração e arranque (raiz e `src/`)

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `package.json` | Lista as dependências (Express, Knex, bcrypt, etc.) e os scripts (`knex:test`, etc.). | — (config) |
| `knexfile.js` | Configuração das ligações à base de dados por ambiente (test = SQLite, staging/production = PostgreSQL) e caminhos das migrations/seeds. | — (config) |
| `src/server.js` | Ponto de entrada: arranca o servidor HTTP e põe a aplicação à escuta na porta definida. | — (infra) |
| `src/app.js` | Cria a aplicação Express, ativa o **CORS**, liga à base de dados (Knex), carrega automaticamente (via `consign`) passport, middlewares, **services**, **routes** e o router. Define o **handler global de erros** que converte o tipo de erro no código HTTP (400/403/500). | — (orquestra tudo) |
| `src/config.js` | Define o ambiente atual (`NODE_ENV`) usado para escolher a configuração do Knex. | — (config) |

### 1.2. Configuração de segurança e ligação de rotas — `src/config/`

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `config/passport.js` | Configura a estratégia **passport-jwt**: valida o token JWT recebido, verifica a expiração e disponibiliza os dados do utilizador (incluindo o `role`) em `req.user`. | — (autenticação) |
| `config/middlewares.js` | Regista middlewares globais (ex.: `body-parser` para ler JSON do corpo dos pedidos). | — (infra) |
| `config/router.js` | **Liga cada conjunto de endpoints ao seu prefixo** (ex.: `/auths`, `/livros`, `/v1/livros`, `/v1/reservas`, `/v1/utilizadores`, `/v1/perfil`) e aplica a proteção JWT às rotas `/v1`. | Apoia os **Controllers (endpoints)** |
| `config/roles.js` | Helper **`requireRole(...)`**: middleware de autorização que verifica o `role` do utilizador e bloqueia (erro 403) quem não tem permissão. | Apoia os **Controllers (endpoints)** |

### 1.3. Erros tipados — `src/errors/`

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `errors/validationError.js` | Erro de validação → resposta **HTTP 400**. | — (suporte aos services) |
| `errors/authenticationError.js` | Erro de autenticação → resposta **HTTP 400**. | — (suporte) |
| `errors/forbiddenError.js` | Erro de permissão (role insuficiente) → resposta **HTTP 403**. | — (suporte) |

### 1.4. MODEL — Serviços de negócio — `src/services/`

> Contêm a **lógica de negócio** e o **acesso à base de dados** (via `app.db`, que é o Knex).
> Seguem o padrão `(app) => ({ ... })`.

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `services/utilizador.js` | Gestão de utilizadores: registo (`register`), procura, edição de perfil (`updateProfile`), alteração de password (`changePassword`, valida a atual), reset de password (`updatePassword`), promover/despromover (`setRole`). Cifra passwords com bcrypt. | **Model** |
| `services/livro.js` | Gestão do catálogo: listar/criar/editar/eliminar livros e **calcular a disponibilidade** (cópias livres = `quantidade` − reservas em curso). | **Model** |
| `services/reserva.js` | Gestão de reservas: criar (estado `pendente`), aprovar/terminar/cancelar, e **regras de negócio** (verificar stock, impedir auto-aprovação pelo cliente). Faz `join` para devolver o nome do cliente e o título do livro. | **Model** |
| `services/name.js` | Serviço legado (módulo anterior — "names"). Não usado pela biblioteca. | **Model** (legado) |
| `services/skill.js` | Serviço legado ("skills"). | **Model** (legado) |
| `services/contact_type.js` | Serviço legado ("contact types"). | **Model** (legado) |

### 1.5. CONTROLLER (ENDPOINTS) — Rotas — `src/routes/`

> Definem os **endpoints da API REST** (métodos HTTP GET/POST/PUT/DELETE). Recebem o
> pedido, extraem os dados, chamam o **service** adequado e devolvem a resposta
> (status + JSON). **Esta é a camada Controller do MVC.**

| Ficheiro | Endpoints / o que faz | Camada MVC |
|----------|-----------------------|------------|
| `routes/auths.js` | Endpoints públicos: `POST /auths/signin` (login + token JWT com role), `POST /auths/signup` (criar conta), `POST /auths/forgot-password` (gera token de reset), `POST /auths/reset-password` (define nova password). | **Controller (endpoints)** |
| `routes/livros_publicos.js` | Endpoint público `GET /livros` (catálogo apenas com livros disponíveis, sem login). | **Controller (endpoints)** |
| `routes/livros.js` | Endpoints privados `GET/POST/PUT/DELETE /v1/livros[/:id]`. Criar/editar/eliminar só para bibliotecário/admin (via `requireRole`). | **Controller (endpoints)** |
| `routes/reservas.js` | Endpoints privados `GET/POST/PUT/DELETE /v1/reservas[/:id]` (criar, aprovar, terminar, cancelar). | **Controller (endpoints)** |
| `routes/utilizadores.js` | Endpoints privados de admin `GET/PUT/DELETE /v1/utilizadores[/:id]` e `PUT /v1/utilizadores/:id/role` (promover/despromover). | **Controller (endpoints)** |
| `routes/perfil.js` | Endpoints privados do próprio utilizador: `GET/PUT /v1/perfil` (ver/editar os seus dados) e `PUT /v1/perfil/password` (alterar password). | **Controller (endpoints)** |
| `routes/names.js` | Endpoints legados ("names"). Não usados pela biblioteca. | **Controller** (legado) |
| `routes/skills.js` | Endpoints legados ("skills"). | **Controller** (legado) |
| `routes/contacts_types.js` | Endpoints legados ("contact types"). | **Controller** (legado) |

### 1.6. Migrations (estrutura da BD) — `src/migrations/`

> Criam/alteram as tabelas da base de dados. Não são MVC, são **definição do esquema**.

| Ficheiro | O que faz |
|----------|-----------|
| `202605290900_create_table_utilizadores.js` | Cria a tabela `utilizadores`. |
| `202605290910_create_table_livros.js` | Cria a tabela `livros`. |
| `202605290920_create_table_reservas.js` | Cria a tabela `reservas` (com FKs para utilizadores e livros). |
| `202606200900_alter_table_utilizadores_add_role.js` | **Migration nova:** adiciona a coluna `role` a `utilizadores`. |
| `202606200910_alter_table_livros_add_quantidade.js` | **Migration nova:** adiciona a coluna `quantidade` (stock) a `livros`. |
| `202605080950_create_table_names.js` … `202605151020_create_table_skills.js` | Migrations legadas (names, contacts, contacts_type, skills). Não usadas pela biblioteca. |

### 1.7. Seeds (dados iniciais) — `src/seeds/test/`

> Inserem dados de exemplo (idempotentes). Não são MVC, são **dados de arranque**.

| Ficheiro | O que faz |
|----------|-----------|
| `03.1_utilizadores.js` | Cria 1 admin, 1 bibliotecário e 1 cliente (password `123456`). |
| `04.1_livros.js` | Cria livros de exemplo com `quantidade` de stock. |
| `01.1_names.js`, `02.1_contacts_types.js` | Seeds legados. |

---

## 2. Frontend (VIEW) — `PWBiblioteca/Frontend/`

> Todas as páginas são a camada **View** do MVC. São HTML/CSS/JS puro (vanilla) e
> comunicam com os **endpoints (controllers)** da API via `fetch`.

### 2.1. Recursos partilhados

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `css/style.css` | Folha de estilos partilhada por todas as páginas (tema castanho/cinzento, fundo de biblioteca, componentes: sidebar, topbar, cartões, tabelas, botões, badges). | **View** |
| `js/config.js` | Utilitários partilhados: `API_BASE` (URL único da API), validação do token (`isTokenValid`), sessão (`saveSession`, `getRole`, `isStaff`, `isAdmin`), `checkAuth`, cabeçalhos com token (`authHeaders`) e construção do menu lateral consoante o role (`renderSidebar`). | **View** (apoio) |

### 2.2. Páginas públicas

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `login.html` | Formulário de login → chama `POST /auths/signin`; guarda o token e redireciona. | **View** |
| `register.html` | Criar conta → chama `POST /auths/signup`. | **View** |
| `forgot-password.html` | Pede o token de reset (`POST /auths/forgot-password`) e mostra-o. | **View** |
| `reset-password.html` | Define nova password (`POST /auths/reset-password`). | **View** |

### 2.3. Páginas privadas

| Ficheiro | O que faz | Camada MVC |
|----------|-----------|------------|
| `dashboard.html` | Página inicial após login; mostra cartões/menu consoante o role. | **View** |
| `livros.html` | Catálogo. Cliente vê disponível/indisponível e reserva; bibliotecário/admin veem o stock e editam/eliminam (+ CREATE). Consome `GET /v1/livros`, `POST /v1/reservas`, `DELETE /v1/livros/:id`. | **View** |
| `livros-create.html` | Formulário de criação de livro (`POST /v1/livros`) — só staff. | **View** |
| `livros-edit.html` | Formulário de edição/eliminação de livro (`PUT/DELETE /v1/livros/:id`) — só staff. | **View** |
| `reservas.html` | Cliente vê/cancela as suas reservas; staff vê todas (com nome do cliente) e aprova/termina. Consome `GET/PUT /v1/reservas`. | **View** |
| `utilizadores.html` | Gestão de contas (só admin): listar, eliminar, promover/despromover. Consome `GET/DELETE /v1/utilizadores`, `PUT /v1/utilizadores/:id/role`. | **View** |
| `utilizadores-edit.html` | Edição/eliminação de uma conta (só admin) — `PUT/DELETE /v1/utilizadores/:id`. | **View** |
| `perfil.html` | O próprio utilizador edita os seus dados e altera a password. Consome `GET/PUT /v1/perfil` e `PUT /v1/perfil/password`. | **View** |

---

## 3. Resumo do fluxo MVC (com endpoints)

```
[ VIEW ]                 [ CONTROLLER = ENDPOINTS ]        [ MODEL ]
Frontend (HTML/JS)  -->  src/routes/*.js (rotas REST)  -->  src/services/*.js  -->  Base de Dados (Knex)
   fetch + token            recebe pedido / envia               lógica de negócio        utilizadores
   Authorization            resposta (status + JSON)            e regras                 livros / reservas
```

Exemplo concreto (reservar um livro):
1. **View** — `livros.html` faz `fetch` para `POST /v1/reservas` com o token.
2. **Controller (endpoint)** — `routes/reservas.js` recebe o pedido e chama o serviço.
3. **Model** — `services/reserva.js` verifica o stock e grava a reserva como `pendente`.
4. A resposta volta ao **View**, que atualiza a tabela de reservas.

---

## 4. Tabela rápida: que ficheiros são MVC?

| Camada MVC | Ficheiros |
|------------|-----------|
| **Model** | `src/services/*.js` |
| **Controller (endpoints)** | `src/routes/*.js` (ligados em `src/config/router.js`) |
| **View** | `PWBiblioteca/Frontend/*.html`, `css/style.css`, `js/config.js` |
| Suporte (não MVC) | `app.js`, `server.js`, `config.js`, `config/passport.js`, `config/middlewares.js`, `config/roles.js`, `errors/*`, `migrations/*`, `seeds/*`, `knexfile.js`, `package.json` |
