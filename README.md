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
- **livros**: `id`, `titulo`, `autor`, `isbn` (unique), `estado` (`disponivel`|`indisponivel`), `quantidade` _(novo, total de cópias)_, `criado_em`.
- **reservas**: `id`, `utilizador_id` (FK), `livro_id` (FK), `data_reserva`, `estado` (default `ativa`).

Colunas adicionadas por **migrations novas de _alter table_** (as migrations originais de criação **não** foram alteradas):
- `202606200900_alter_table_utilizadores_add_role.js` — adiciona `role`.
- `202606200910_alter_table_livros_add_quantidade.js` — adiciona `quantidade`.

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
| GET    | `/v1/reservas`                | autenticado | Cliente: as suas reservas. Bibliotecario/admin: todas as reservas em curso (`pendente`/`confirmada`). Inclui `utilizador_nome` e `livro_titulo`. |
| GET    | `/v1/reservas/:id`            | autenticado | Cliente só as suas; staff qualquer uma. |
| POST   | `/v1/reservas`                | autenticado | Criar reserva. Body `{ livro_id }` (o `utilizador_id` vem do token). |
| PUT    | `/v1/reservas/:id`            | autenticado | Mudar estado (`aceite`, `terminada`, `cancelada`). |
| DELETE | `/v1/reservas/:id`            | autenticado | Apagar reserva (devolve o livro se ainda ocupado). |
| GET    | `/v1/utilizadores`            | admin | Listar contas (sem password). |
| GET    | `/v1/utilizadores/:id`        | admin | Detalhe de uma conta. |
| PUT    | `/v1/utilizadores/:id`        | admin | Editar `nome` / `email`. |
| PUT    | `/v1/utilizadores/:id/role`   | admin | Promover/despromover (`cliente` ↔ `bibliotecario`). |
| DELETE | `/v1/utilizadores/:id`        | admin | Eliminar conta. |
| GET    | `/v1/perfil`                  | autenticado | Dados do **próprio** perfil (sem password). |
| PUT    | `/v1/perfil`                  | autenticado | Editar o **próprio** perfil (`nome`/`email`). |
| PUT    | `/v1/perfil/password`         | autenticado | Alterar a própria password. Body `{ currentPassword, newPassword }` (valida a password atual). |

> As rotas legadas (`names`, `skills`, `contactstypes`) mantêm-se intactas.

### Autorização por role

O helper `requireRole(...roles)` (em `src/config/roles.js`) valida `req.user.role` (preenchido pelo Passport a partir do payload do JWT). Em caso de falha lança `ForbiddenError` → **403**. A segurança é garantida **no servidor**; o frontend apenas esconde as ações sem permissão para melhorar a experiência.

---

## Regras de negócio

### Estados do livro e stock

- Cada livro tem uma **quantidade** total de cópias (`quantidade`) e um **estado manual** (`disponivel`/`indisponivel`).
- As cópias **ocupadas** correspondem às reservas em curso (`ativa`/`aceite`) desse livro.
- **Cópias livres** = `quantidade − ocupadas` (calculado, não armazenado).
- Um livro é **efetivamente disponível** quando `estado === 'disponivel'` **e** há cópias livres.
- **Cliente** só vê `disponivel`/`indisponivel`; **bibliotecário/admin** veem o stock (`livres / total`) e o estado manual.

### Estados da reserva

| Estado       | Significado | Efeito nas cópias |
|--------------|-------------|-------------------|
| `pendente`   | Criada pelo cliente, **pendente de aprovação**. | Ocupa uma cópia. |
| `confirmada` | Aprovada por bibliotecario/admin. | Continua a ocupar uma cópia. |
| `terminada`  | Entrega/devolução concluída. | Liberta a cópia. |
| `cancelada`  | Cancelada pelo cliente. | Liberta a cópia. |

Regras aplicadas no `service`:

- **Criar reserva:** o livro tem de existir, estar com `estado = disponivel` e ter pelo menos uma cópia livre. A reserva nasce **`pendente`** (à espera de aprovação).
- **Aprovar:** só bibliotecário/admin podem passar uma reserva de `pendente` para `confirmada`. O cliente **não** pode auto-aprovar (validado no servidor).
- **Terminar:** bibliotecário/admin terminam (`terminada`), libertando a cópia.
- **Cancelar:** o cliente só pode **cancelar** as suas reservas (`cancelada`); libertando a cópia.
- **Disponibilidade calculada:** as cópias livres derivam das reservas em curso (`pendente`/`confirmada`), pelo que o `estado` do livro não é alterado a cada reserva.
- **Filtragem por role:** o cliente só vê/altera as suas reservas; bibliotecario/admin veem e gerem todas. A lista inclui o **nome do cliente** e o **título do livro** (via `join`).

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

Localização: **`PWBiblioteca/Frontend/`**. Tema visual em **castanhos e cinzentos** com **fundo de biblioteca** e tipografia _serif_ nos títulos, mantendo a estrutura do `Exemplo.txt` (sidebar de 264px, topbar, cartões, tabelas). Estilos partilhados em **`css/style.css`** (linkado em todas as páginas) para um look coerente e único. Branding: **"Biblioteca / Gestão de Biblioteca"**.

| Ficheiro | Acesso | Descrição |
|----------|--------|-----------|
| `login.html` | público | Autenticação (corrige o bug do `Exemplo.txt`: envia `password`, não `pass`). Links para registo e recuperação. |
| `register.html` | público | Criar conta. |
| `forgot-password.html` | público | Pede o token de reset; mostra "Email enviado" e o token por baixo. |
| `reset-password.html` | público | Define a nova password (pré-preenche o token do `?token=`). |
| `dashboard.html` | privado | Cartões/menu consoante o role. |
| `livros.html` | privado | Catálogo. Cliente: vê disponível/indisponível e reserva. Bibliotecario/admin: veem stock (`livres/total`) e estado, editam/eliminam + `CREATE`. |
| `livros-create.html` | bibliotecario/admin | Criar livro (`titulo`, `autor`, `isbn`, `quantidade`, `estado`). |
| `livros-edit.html` | bibliotecario/admin | Editar/eliminar livro e gerir o stock. |
| `reservas.html` | privado | Cliente: as suas reservas + cancelar. Bibliotecario/admin: todas em curso, com **nome do cliente**, + aprovar/terminar. |
| `utilizadores.html` | admin | Listar contas, editar/eliminar, promover/despromover. |
| `utilizadores-edit.html` | admin | Editar/eliminar uma conta. |
| `perfil.html` | privado | O próprio utilizador edita os seus dados (`nome`/`email`) e altera a password (atual + nova). |
| `css/style.css` | — | Tema partilhado (paleta castanho/cinzento, fundo de biblioteca, componentes). |
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
- **Migrations novas**: `role` em `utilizadores` e `quantidade` em `livros` (migrations originais intactas).
- **Seeds** atualizadas: utilizadores com 3 roles (password `123456`) e livros com `quantidade` de stock; ambas idempotentes.
- **JWT com role**: payload do `signin` inclui `role` (além de `id`, `email`, `expires`).
- **Novas rotas de auth**: `signup`, `forgot-password`, `reset-password`.
- **Service `utilizador`**: `register`, `updatePassword`, `setRole` (promover/despromover).
- **Service `livro`**: disponibilidade calculada por stock (`quantidade − reservas em curso`); `estado` passa a `disponivel`/`indisponivel`.
- **Helper `requireRole`** (`src/config/roles.js`) + erro `ForbiddenError` (403).
- **Livros**: criar/editar/eliminar restritos a bibliotecario/admin; campo `quantidade`.
- **Reservas**: fluxo de aprovação (`pendente` → `confirmada` por staff; cliente só cancela); verificação de cópias livres ao reservar; listagem com `join` (nome do cliente + título do livro).
- **Rotas de utilizadores** (admin): listar/editar/eliminar/promover/despromover.
- **Perfil self-service** (`src/routes/perfil.js`): `GET/PUT /v1/perfil` (editar nome/email) e `PUT /v1/perfil/password` (alterar password com a password atual). Service: `updateProfile`, `changePassword`.
- Correção de um bug pré-existente no `passport.js` (tokens expirados deixavam de ser aceites — faltava o `return`).

### Frontend

- Conjunto completo de páginas em `PWBiblioteca/Frontend/`, com UI condicionada ao role e base URL única (`http://localhost:3001`).

---

## Decisões tomadas

- **Stock por quantidade**: cada livro tem `quantidade` (total de cópias). A disponibilidade é **calculada** (cópias livres = total − reservas em curso), evitando manter `estado` sincronizado a cada reserva. O `estado` passa a ser um interruptor manual `disponivel`/`indisponivel` (substitui o antigo `reservado`).
- **Visibilidade do stock**: bibliotecário/admin veem `livres / total`; o cliente vê apenas `disponivel`/`indisponivel`.
- **Reservas com nome do cliente**: a listagem faz `join` com `utilizadores` e `livros` para mostrar o nome do cliente e o título do livro (em vez de IDs).
- **Aprovação de reservas**: a reserva nasce `pendente` (pendente de aprovação) e só passa a `confirmada` por ação de bibliotecário/admin. O cliente apenas pode cancelar (validado no servidor, não só no UI).
- **Perfil self-service**: qualquer utilizador edita os seus dados e altera a password (com verificação da password atual) via `/v1/perfil`; o admin continua a gerir todas as contas via `/v1/utilizadores`.
- **`forgot-password`** devolve o token na resposta (não há email real); a página mostra "Email enviado" e o token por baixo.
- **Promoção/despromoção** restrita a `cliente ↔ bibliotecario`.
- **Tema visual** em castanho/cinzento com fundo de biblioteca, centralizado em `css/style.css` partilhado (mais coerente e fácil de manter que CSS repetido por página). A imagem de fundo é carregada de um URL público (Unsplash), pelo que requer internet no browser; sem ela, o fundo escuro de _fallback_ mantém a leitura.
- **`js/config.js` partilhado** mantém a base URL num único local e os helpers de auth/role, sem frameworks nem build.
