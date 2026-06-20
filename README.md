# PWBiblioteca — Aplicação de Biblioteca (Programação Web)

Aplicação de gestão de biblioteca composta por:

- **Backend** — API REST em Node.js + Express 5 + Knex (SQLite em `test`, PostgreSQL em `staging`/`production`), autenticação com Passport.js (JWT) e `jwt-simple`, hash de passwords com `bcrypt`.
- **Frontend** — HTML + CSS + JavaScript puro (vanilla), uma página `.html` por ecrã, sem frameworks nem build. Replica o _look & feel_ do `Exemplo.txt`.

> O backend continua a correr em **`http://localhost:3001`** (o valor `4001` do `Exemplo.txt` está incorreto e **não** é usado).

---

## Índice

1. [Arquitetura](#arquitetura)
2. [Como executar](#como-executar)
3. [Roles e utilizadores de seed](#roles-e-utilizadores-de-seed)
4. [Endpoints da API](#endpoints-da-api)
5. [Regras de negócio](#regras-de-negócio)
6. [Fluxo de recuperação de password](#fluxo-de-recuperação-de-password)
7. [Frontend (páginas)](#frontend-páginas)
8. [Resumo das alterações](#resumo-das-alterações)
9. [Decisões tomadas](#decisões-tomadas)

---

## Arquitetura

MVC simplificado, mantido tal como o projeto original:

- `src/services/*.js` — lógica de negócio + acesso à base de dados. Padrão `(app) => ({ ... })`.
- `src/routes/*.js` — _thin wrappers_ HTTP que chamam os serviços.
- Auto-carregados por `consign` (`app.services.<nome>` / `app.routes.<nome>`).
- Erros lançados com `throw new ValidationError(...)` / `ForbiddenError(...)`; o handler global em `app.js` mapeia `err.name` → status:
  - `validationError` → **400**
  - `authenticationError` → **400**
  - `forbiddenError` → **403**
  - restante → **500**
- Secret JWT: `ERSC202526` (mantido). Token enviado no header `Authorization: Bearer <token>`.

### Esquema da base de dados

- **utilizadores**: `id`, `nome`, `email` (unique), `password`, `role` _(novo)_, `criado_em`.
- **livros**: `id`, `titulo`, `autor`, `isbn` (unique), `estado` (default `disponivel`), `criado_em`.
- **reservas**: `id`, `utilizador_id` (FK), `livro_id` (FK), `data_reserva`, `estado` (default `ativa`).

A coluna `role` foi adicionada por uma **migration nova de _alter table_** (`202606200900_alter_table_utilizadores_add_role.js`) — a migration original de criação **não** foi alterada.

---

## Como executar

### Backend

```bash
cd PWBiblioteca/Backend
npm install
npm run knex:test
```

O script `knex:test` corre as migrations, as seeds e arranca o servidor em `http://localhost:3001`.

> **Nota:** `knex:test` usa SQLite (ficheiro `data/database.sqlite`). As seeds são **idempotentes**, pelo que podem ser corridas várias vezes sem duplicar dados.

### Frontend

O frontend é estático. Basta servir a pasta `PWBiblioteca/Frontend/` com qualquer servidor estático e abrir `login.html`. Por exemplo:

```bash
cd PWBiblioteca/Frontend
npx serve .        # ou: python3 -m http.server 5500
```

Depois aceda a `http://localhost:<porta>/login.html`. O CORS no backend (`app.use(cors({ origin: '*' }))`) permite as chamadas a partir do browser.

---

## Roles e utilizadores de seed

Três níveis de acesso:

| Role            | Permissões |
|-----------------|------------|
| `cliente`       | Consultar catálogo; criar/ver/cancelar **as suas** reservas. |
| `bibliotecario` | Tudo o que o cliente faz + criar/editar/eliminar livros; ver **todas** as reservas em curso e aceitá-las/terminá-las. |
| `admin`         | Tudo o que o bibliotecário faz + gestão de contas (listar, editar, eliminar, promover/despromover). |

Utilizadores criados pela seed (password **`123456`** em todos):

| Nome           | Email                      | Role            |
|----------------|----------------------------|-----------------|
| Carlos Joaquim | `cjoaquim@biblioteca.pt`   | `admin`         |
| Ana Costa      | `ana@biblioteca.pt`        | `bibliotecario` |
| Margarida      | `margarida@biblioteca.pt`  | `cliente`       |

---

## Endpoints da API

### Públicos (sem token)

| Método | Rota                      | Descrição |
|--------|---------------------------|-----------|
| POST   | `/auths/signin`           | Login. Body `{ email, password }` → `{ token }` (payload com `id`, `email`, `role`, `expires`). |
| POST   | `/auths/signup`           | Criar conta. Body `{ nome, email, password }` → utilizador criado (role `cliente`, sem expor a password). |
| POST   | `/auths/forgot-password`  | Body `{ email }` → `{ resetToken, info }` (token de reset com expiração curta). |
| POST   | `/auths/reset-password`   | Body `{ resetToken, password }` → atualiza a password. |
| GET    | `/livros`                 | Lista apenas livros com estado `disponivel`. |

### Privados (`Authorization: Bearer <token>`, prefixo `/v1`)

| Método | Rota                          | Acesso | Descrição |
|--------|-------------------------------|--------|-----------|
| GET    | `/v1/livros`                  | autenticado | Lista todos os livros. |
| GET    | `/v1/livros/:id`              | autenticado | Detalhe de um livro. |
| POST   | `/v1/livros`                  | bibliotecario/admin | Criar livro. |
| PUT    | `/v1/livros/:id`              | bibliotecario/admin | Editar livro. |
| DELETE | `/v1/livros/:id`              | bibliotecario/admin | Eliminar livro. |
| GET    | `/v1/reservas`                | autenticado | Cliente: as suas reservas. Bibliotecario/admin: todas as reservas em curso (`ativa`/`aceite`). |
| GET    | `/v1/reservas/:id`            | autenticado | Cliente só as suas; staff qualquer uma. |
| POST   | `/v1/reservas`                | autenticado | Criar reserva. Body `{ livro_id }` (o `utilizador_id` vem do token). |
| PUT    | `/v1/reservas/:id`            | autenticado | Mudar estado (`aceite`, `terminada`, `cancelada`). |
| DELETE | `/v1/reservas/:id`            | autenticado | Apagar reserva (devolve o livro se ainda ocupado). |
| GET    | `/v1/utilizadores`            | admin | Listar contas (sem password). |
| GET    | `/v1/utilizadores/:id`        | admin | Detalhe de uma conta. |
| PUT    | `/v1/utilizadores/:id`        | admin | Editar `nome` / `email`. |
| PUT    | `/v1/utilizadores/:id/role`   | admin | Promover/despromover (`cliente` ↔ `bibliotecario`). |
| DELETE | `/v1/utilizadores/:id`        | admin | Eliminar conta. |

> As rotas legadas (`names`, `skills`, `contactstypes`) mantêm-se intactas.

### Autorização por role

O helper `requireRole(...roles)` (em `src/config/roles.js`) valida `req.user.role` (preenchido pelo Passport a partir do payload do JWT). Em caso de falha lança `ForbiddenError` → **403**. A segurança é garantida **no servidor**; o frontend apenas esconde as ações sem permissão para melhorar a experiência.

---

## Regras de negócio

### Estados do livro

- `disponivel` → pode ser reservado.
- `reservado` → ocupado por uma reserva em curso.

### Estados da reserva

| Estado      | Significado | Efeito no livro |
|-------------|-------------|-----------------|
| `ativa`     | Reserva criada pelo cliente. | Livro passa a `reservado`. |
| `aceite`    | Bibliotecario/admin aceitou. | Livro continua ocupado. |
| `terminada` | Entrega/devolução concluída. | Livro volta a `disponivel`. |
| `cancelada` | Cliente cancelou. | Livro volta a `disponivel`. |

Regras aplicadas no `service` de reservas:

- **Criar:** o livro tem de existir e estar `disponivel`; passa a `reservado`.
- **Cancelar/terminar:** ao transitar para `cancelada` ou `terminada`, o livro volta a `disponivel`.
- **Apagar:** se a reserva ainda ocupava o livro (`ativa`/`aceite`), o livro é devolvido ao catálogo.
- **Filtragem por role:** o cliente só vê/altera as suas reservas; bibliotecario/admin veem e gerem todas.

---

## Fluxo de recuperação de password

Como **não existe envio de email real**, o fluxo é feito com um token devolvido na resposta:

1. O utilizador submete o email em `forgot-password.html` → `POST /auths/forgot-password`.
2. O backend gera um token (`jwt-simple`) com `type: 'reset'` e expiração de **15 minutos** e devolve-o em `{ resetToken, info }`.
3. A página mostra o token e um link para `reset-password.html?token=...`.
4. Em `reset-password.html`, o utilizador cola/confirma o token e define a nova password → `POST /auths/reset-password`.
5. O backend valida o token (assinatura, `type` e expiração) e atualiza a password (com `bcrypt`).

---

## Frontend (páginas)

Localização: **`PWBiblioteca/Frontend/`**. Estilo replicado do `Exemplo.txt` (paleta navy/azul, cartões brancos arredondados, sidebar de 260px, tabelas com cabeçalho `#eef4fa`). Branding: **“Biblioteca / Gestão de Biblioteca”**.

| Ficheiro | Acesso | Descrição |
|----------|--------|-----------|
| `login.html` | público | Autenticação (corrige o bug do `Exemplo.txt`: envia `password`, não `pass`). Links para registo e recuperação. |
| `register.html` | público | Criar conta. |
| `forgot-password.html` | público | Pede o token de reset e mostra-o. |
| `reset-password.html` | público | Define a nova password (pré-preenche o token do `?token=`). |
| `dashboard.html` | privado | Cartões/menu consoante o role. |
| `livros.html` | privado | Catálogo. Cliente reserva; bibliotecario/admin editam/eliminam + `CREATE`. |
| `livros-create.html` | bibliotecario/admin | Criar livro (`titulo`, `autor`, `isbn`, `estado`). |
| `livros-edit.html` | bibliotecario/admin | Editar/eliminar livro. |
| `reservas.html` | privado | Cliente: as suas reservas + cancelar. Bibliotecario/admin: todas as ativas + aceitar/terminar. |
| `utilizadores.html` | admin | Listar contas, editar/eliminar, promover/despromover. |
| `utilizadores-edit.html` | admin | Editar/eliminar uma conta. |
| `js/config.js` | — | Helpers partilhados: `API_BASE` (URL único), `isTokenValid`, `saveSession`, `checkAuth`, `getRole`, `isStaff`, `isAdmin`, `authHeaders`, `renderSidebar`. |

### Autenticação no cliente

- `token`, `email` e `role` são guardados em `localStorage` (o `role` é lido do payload do JWT em `saveSession`).
- `isTokenValid(token)` descodifica `atob(token.split('.')[1])` e valida a expiração.
- `checkAuth()` corre no arranque de cada página privada e faz `logout()` se o token for inválido.
- Todas as chamadas privadas enviam `Authorization: Bearer <token>`.

---

## Resumo das alterações

### Backend

- **CORS** adicionado em `app.js` (`app.use(cors({ origin: '*' }))`).
- **Migration nova** `202606200900_alter_table_utilizadores_add_role.js` (adiciona `role`, default `cliente`).
- **Seed** `03.1_utilizadores.js` atualizada: cria admin + bibliotecário + cliente (password `123456`, idempotente).
- **JWT com role**: payload do `signin` inclui `role` (além de `id`, `email`, `expires`).
- **Novas rotas de auth**: `signup`, `forgot-password`, `reset-password`.
- **Service `utilizador`**: `register`, `updatePassword`, `setRole` (promover/despromover).
- **Helper `requireRole`** (`src/config/roles.js`) + erro `ForbiddenError` (403).
- **Livros**: criar/editar/eliminar restritos a bibliotecario/admin.
- **Reservas**: lógica por role (cliente vê/gere as suas; staff vê/gere todas) e transições de estado que devolvem o livro.
- **Rotas de utilizadores** (admin): listar/editar/eliminar/promover/despromover, registadas em `config/router.js`.
- Correção de um bug pré-existente no `passport.js` (tokens expirados deixavam de ser aceites — faltava o `return`).

### Frontend

- Conjunto completo de páginas em `PWBiblioteca/Frontend/`, com UI condicionada ao role e base URL única (`http://localhost:3001`).

---

## Decisões tomadas

- **Estados extra da reserva** (`aceite`, `terminada`) para suportar o fluxo “aceitar/terminar” do staff, mantendo `ativa`/`cancelada` do original. `cancelada` e `terminada` libertam o livro.
- **Bibliotecário/admin veem reservas `ativa` + `aceite`** (reservas em curso), para um fluxo de gestão utilizável.
- **`forgot-password` devolve o token na resposta** por não existir email real (documentado na própria página e aqui).
- **Promoção/despromoção** restrita a `cliente ↔ bibliotecario` (não cria admins arbitrariamente).
- **`js/config.js` partilhado** mantém a base URL num único local e evita duplicação dos helpers de auth, sem introduzir frameworks nem build.
