#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um relatorio .docx (Word) sobre o projeto PWBiblioteca usando apenas a
biblioteca padrao do Python (um .docx e um ZIP de XML WordprocessingML).
Inclui capa, indice automatico (TOC), titulos com estilos, tabelas e
marcadores de "print" para o utilizador substituir por capturas de ecra.
"""
import zipfile
from xml.sax.saxutils import escape

OUT = "Relatorio_PWBiblioteca.docx"

# ------------------------------------------------------------------ helpers

body = []  # lista de blocos XML (paragrafos / tabelas)


def esc(t):
    return escape(str(t))


def para(text="", style=None, align=None, bold=False, size=None, color=None,
         spacing_after=None):
    ppr = "<w:pPr>"
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    if spacing_after is not None:
        ppr += f'<w:spacing w:after="{spacing_after}"/>'
    ppr += "</w:pPr>"

    rpr = ""
    if bold or size or color:
        rpr = "<w:rPr>"
        if bold:
            rpr += "<w:b/>"
        if size:
            rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        if color:
            rpr += f'<w:color w:val="{color}"/>'
        rpr += "</w:rPr>"

    run = ""
    if text != "":
        run = f"<w:r>{rpr}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"
    body.append(f"<w:p>{ppr}{run}</w:p>")


def h1(text):
    para(text, style="Heading1")


def h2(text):
    para(text, style="Heading2")


def h3(text):
    para(text, style="Heading3")


def p(text):
    para(text, style="Normal")


def bullet(text):
    para(text, style="ListBullet")


def prnt(text):
    # Marcador de captura de ecra (o utilizador substitui por uma imagem).
    para("[ PRINT ] " + text, style="Print")


def page_break():
    body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')


def spacer(n=1):
    for _ in range(n):
        body.append("<w:p/>")


def toc():
    body.append(
        '<w:p>'
        '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:rPr><w:i/></w:rPr><w:t xml:space="preserve">'
        'Indice automatico: clique aqui com o botao direito e escolha '
        '"Atualizar campo" (ou prima F9) para gerar.'
        '</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        '</w:p>'
    )


def table(headers, rows, widths=None):
    n = len(headers)
    if widths is None:
        widths = [int(9000 / n)] * n
    borders = (
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '</w:tblBorders>'
    )
    xml = ('<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/>'
           + borders + '</w:tblPr><w:tblGrid>')
    for w in widths:
        xml += f'<w:gridCol w:w="{w}"/>'
    xml += "</w:tblGrid>"

    # header
    xml += "<w:tr>"
    for i, htext in enumerate(headers):
        xml += (
            f'<w:tc><w:tcPr><w:tcW w:w="{widths[i]}" w:type="dxa"/>'
            '<w:shd w:val="clear" w:color="auto" w:fill="6B4E32"/></w:tcPr>'
            '<w:p><w:pPr><w:spacing w:after="0"/></w:pPr>'
            '<w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(htext)}</w:t></w:r></w:p></w:tc>'
        )
    xml += "</w:tr>"

    # rows
    for r, row in enumerate(rows):
        fill = "F2ECE1" if r % 2 == 0 else "FFFFFF"
        xml += "<w:tr>"
        for i, cell in enumerate(row):
            xml += (
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[i]}" w:type="dxa"/>'
                f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/></w:tcPr>'
                '<w:p><w:pPr><w:spacing w:after="0"/></w:pPr>'
                f'<w:r><w:t xml:space="preserve">{esc(cell)}</w:t></w:r></w:p></w:tc>'
            )
        xml += "</w:tr>"
    xml += "</w:tbl>"
    body.append(xml)
    # paragrafo vazio a seguir a tabela (boa pratica WordML)
    body.append("<w:p/>")


# =================================================================== CONTEUDO

# ---- CAPA ----
spacer(2)
para("INSTITUTO POLITECNICO / ESCOLA SUPERIOR DE TECNOLOGIA E GESTAO",
     align="center", bold=True, size="24")
para("[substituir pelo nome da sua instituicao]", align="center", size="18",
     color="888888")
spacer(3)
para("Unidade Curricular: Programacao Web", align="center", size="26", bold=True)
spacer(1)
para("Aplicacao Web de Gestao de Biblioteca", align="center", style="Title")
para("PWBiblioteca", align="center", size="28", color="6B4E32", bold=True)
spacer(4)
para("Trabalho realizado por:", align="center", bold=True, size="24")
para("[Nome do Estudante] - Nº [00000]", align="center", size="24")
para("[Nome do Estudante] - Nº [00000]", align="center", size="24")
spacer(2)
para("Docente: [Nome do Docente]", align="center", size="24")
spacer(3)
para("Ano letivo 2025/2026", align="center", size="22")
para("Junho de 2026", align="center", size="22")
page_break()

# ---- INDICE ----
h1("Indice")
toc()
page_break()

# ---- 1. INTRODUCAO ----
h1("1. Introducao")
p("O presente relatorio documenta o desenvolvimento de uma aplicacao web de "
  "gestao de biblioteca, designada PWBiblioteca, realizada no ambito da unidade "
  "curricular de Programacao Web. O projeto parte de um backend ja existente em "
  "Node.js/Express e foi estendido com novas funcionalidades de negocio, controlo "
  "de acessos por perfil (role) e um frontend completo desenvolvido em HTML, CSS e "
  "JavaScript puro (vanilla).")
p("A aplicacao permite a um conjunto de utilizadores com diferentes niveis de "
  "permissao consultar um catalogo de livros, efetuar e gerir reservas, administrar "
  "contas e gerir o seu proprio perfil. O sistema esta dividido em duas camadas "
  "principais: o backend (API REST), responsavel pela logica de negocio e acesso a "
  "base de dados, e o frontend, responsavel pela apresentacao e interacao com o "
  "utilizador.")
p("Ao longo deste documento descreve-se o dominio do problema, o modelo de dados, "
  "a framework adotada e a sua justificacao, a arquitetura MVC, a funcionalidade de "
  "autenticacao e a funcionalidade de negocio central (reserva de livros), terminando "
  "com uma discussao das principais dificuldades e decisoes tecnicas.")

# ---- 2. DOMINIO ----
h1("2. Identificacao do Negocio / Dominio do Problema")
p("O dominio do problema e a gestao de uma biblioteca. Numa biblioteca, existe um "
  "acervo de livros que pode ser consultado pelos utilizadores e reservado quando ha "
  "exemplares disponiveis. A gestao destas operacoes envolve diferentes intervenientes "
  "com responsabilidades distintas.")
p("Foram identificados tres perfis de utilizador (roles):")
bullet("Cliente: consulta o catalogo e efetua reservas de livros; gere e cancela as "
       "suas proprias reservas; edita o seu perfil e altera a sua password.")
bullet("Bibliotecario: alem do que o cliente faz, faz a gestao do catalogo (criar, "
       "editar e eliminar livros e respetivo stock) e aprova/termina as reservas de "
       "todos os clientes.")
bullet("Administrador (admin): faz tudo o que o bibliotecario faz e ainda gere as "
       "contas dos utilizadores (listar, editar, eliminar e promover/despromover "
       "bibliotecarios).")
p("As regras de negocio centrais sao: (1) um livro so pode ser reservado se existir e "
  "tiver, pelo menos, uma copia livre; (2) uma reserva criada por um cliente fica "
  "pendente de aprovacao e so passa a confirmada apos validacao por um bibliotecario "
  "ou administrador; (3) o cancelamento ou a conclusao de uma reserva liberta a copia "
  "do livro para nova reserva.")

# ---- 3. BASE DE DADOS ----
h1("3. Base de Dados e Modelo Conceptual")
p("A persistencia de dados e feita atraves do query builder Knex.js, que abstrai o "
  "acesso ao SGBD. Em ambiente de teste e usado SQLite (ficheiro local) e em "
  "ambientes de staging/producao esta preparado PostgreSQL. O esquema relevante para "
  "o dominio e composto por tres tabelas: utilizadores, livros e reservas.")

h2("3.1. Tabelas e atributos")
p("Tabela utilizadores - representa as contas do sistema:")
table(
    ["Atributo", "Tipo", "Descricao"],
    [
        ["id", "integer (PK)", "Identificador unico"],
        ["nome", "string", "Nome do utilizador"],
        ["email", "string (unico)", "Email / credencial de login"],
        ["password", "string", "Password cifrada com bcrypt"],
        ["role", "string", "Perfil: cliente | bibliotecario | admin"],
        ["criado_em", "datetime", "Data de criacao da conta"],
    ],
    widths=[2200, 2200, 4600],
)
p("Tabela livros - representa o acervo:")
table(
    ["Atributo", "Tipo", "Descricao"],
    [
        ["id", "integer (PK)", "Identificador unico"],
        ["titulo", "string", "Titulo do livro"],
        ["autor", "string", "Autor do livro"],
        ["isbn", "string (unico)", "Codigo ISBN"],
        ["estado", "string", "disponivel | indisponivel (interruptor manual)"],
        ["quantidade", "integer", "Numero total de copias em stock"],
        ["criado_em", "datetime", "Data de registo do livro"],
    ],
    widths=[2200, 2200, 4600],
)
p("Tabela reservas - associa um utilizador a um livro:")
table(
    ["Atributo", "Tipo", "Descricao"],
    [
        ["id", "integer (PK)", "Identificador unico"],
        ["utilizador_id", "integer (FK)", "Cliente que reservou (-> utilizadores.id)"],
        ["livro_id", "integer (FK)", "Livro reservado (-> livros.id)"],
        ["data_reserva", "datetime", "Data/hora da reserva"],
        ["estado", "string", "pendente | confirmada | terminada | cancelada"],
    ],
    widths=[2200, 2200, 4600],
)

h2("3.2. Modelo Entidade-Relacionamento (ER)")
p("As relacoes entre as entidades sao as seguintes: um Utilizador pode ter varias "
  "Reservas (1:N) e um Livro pode estar associado a varias Reservas (1:N). A entidade "
  "Reserva funciona, assim, como tabela de ligacao que materializa a relacao N:M entre "
  "Utilizadores e Livros, acrescentando atributos proprios (data e estado).")
p("Representacao textual simplificada:")
bullet("UTILIZADOR (1) ----< (N) RESERVA (N) >---- (1) LIVRO")
prnt("Diagrama Entidade-Relacionamento (ER) desenhado numa ferramenta (ex.: "
     "draw.io / dbdiagram.io) com as tres entidades, atributos, chaves primarias e "
     "estrangeiras e as cardinalidades 1:N entre Utilizador-Reserva e Livro-Reserva.")

# ---- 4. FRAMEWORK ----
h1("4. Framework Escolhida e Justificacao")
p("O backend foi desenvolvido em Node.js com a framework Express (versao 5). Para o "
  "acesso a base de dados utilizou-se o Knex.js como query builder e, para a "
  "autenticacao, a biblioteca Passport.js com a estrategia passport-jwt, em conjunto "
  "com jwt-simple para a codificacao do token. As passwords sao cifradas com bcrypt.")
p("Principais ferramentas e respetiva funcao:")
table(
    ["Tecnologia", "Funcao no projeto"],
    [
        ["Node.js + Express 5", "Servidor HTTP e definicao de rotas da API REST"],
        ["Knex.js", "Query builder e migracoes/seeds da base de dados"],
        ["SQLite / PostgreSQL", "Sistema de gestao de base de dados"],
        ["Passport.js + passport-jwt", "Autenticacao baseada em token JWT"],
        ["jwt-simple", "Codificacao/descodificacao do token JWT"],
        ["bcrypt", "Cifragem (hash) das passwords"],
        ["consign", "Carregamento automatico de servicos e rotas"],
        ["cors", "Permitir o acesso do frontend (browser) a API"],
    ],
    widths=[3000, 6000],
)
p("Justificacao: o Express e uma framework minimalista, amplamente utilizada e bem "
  "documentada, ideal para construir APIs REST de forma rapida. A combinacao com o "
  "Knex permite trabalhar com SQL de forma programatica e portavel entre SGBD, "
  "facilitando a migracao de SQLite (desenvolvimento) para PostgreSQL (producao). O "
  "uso de JWT torna a API sem estado (stateless), adequada para ser consumida por um "
  "frontend separado. No frontend optou-se por HTML, CSS e JavaScript puro (vanilla), "
  "sem frameworks nem processo de build, para manter o projeto simples, leve e "
  "facilmente executavel em qualquer navegador.")

# ---- 5. MVC ----
h1("5. Arquitetura MVC")
p("O backend segue uma variante simplificada do padrao Model-View-Controller (MVC), "
  "com separacao clara de responsabilidades por pastas dentro de src/:")
table(
    ["Camada", "Pasta / Ficheiros", "Responsabilidade"],
    [
        ["Model + logica", "src/services/*.js",
         "Logica de negocio e acesso a base de dados (via Knex)"],
        ["Controller", "src/routes/*.js",
         "Wrappers HTTP finos que recebem o pedido e chamam os servicos"],
        ["View", "PWBiblioteca/Frontend/*.html",
         "Paginas HTML/CSS/JS que apresentam os dados ao utilizador"],
        ["Configuracao", "src/config/*.js",
         "Passport, middlewares, router e autorizacao por role"],
    ],
    widths=[1800, 3000, 4200],
)
p("Os servicos seguem o padrao (app) => ({ ... }), recebendo a instancia da aplicacao "
  "(e o acesso a base de dados app.db). As rotas e os servicos sao carregados "
  "automaticamente pela biblioteca consign, ficando disponiveis em app.services.<nome> "
  "e app.routes.<nome>. O ficheiro src/config/router.js liga cada conjunto de rotas ao "
  "respetivo prefixo (por exemplo, /v1/livros, /v1/reservas).")
p("O tratamento de erros e centralizado: os servicos lancam erros tipados "
  "(ValidationError, AuthenticationError, ForbiddenError) e um handler global em "
  "app.js converte o nome do erro no codigo HTTP adequado (400, 403 ou 500). A "
  "autorizacao por perfil e feita por um helper requireRole(...) que valida o role "
  "presente no token antes de permitir o acesso a uma rota protegida.")
prnt("Captura da estrutura de pastas do projeto no editor (arvore de ficheiros) a "
     "mostrar as pastas services, routes, migrations, seeds e config, bem como a pasta "
     "Frontend.")

# ---- 6. LOGIN ----
h1("6. Funcionalidade de Login")
p("A autenticacao e feita no endpoint publico POST /auths/signin, que recebe o email e "
  "a password. O servico procura o utilizador pelo email e compara a password recebida "
  "com o hash armazenado, usando bcrypt. Se as credenciais forem validas, e gerado um "
  "token JWT (jwt-simple) cujo payload inclui o id, o email, o role e o instante de "
  "expiracao (expires). O token e devolvido ao cliente.")
p("No frontend (login.html), o token e guardado no localStorage do navegador, "
  "juntamente com o email e o role (este ultimo descodificado do proprio payload do "
  "token). A partir dai, todas as chamadas a endpoints protegidos enviam o cabecalho "
  "Authorization: Bearer <token>. Cada pagina privada executa, no arranque, a funcao "
  "checkAuth(), que valida a existencia e a validade (expiracao) do token; caso seja "
  "invalido, o utilizador e reencaminhado para o login.")
p("No servidor, as rotas sob o prefixo /v1 sao protegidas pela estrategia passport-jwt, "
  "que valida o token e disponibiliza os dados do utilizador em req.user, permitindo a "
  "verificacao do perfil (role) nas operacoes restritas.")
p("Sequencia resumida da autenticacao:")
bullet("1. O utilizador submete email e password no formulario de login.")
bullet("2. O backend valida as credenciais (bcrypt) e devolve um token JWT com o role.")
bullet("3. O frontend guarda o token no localStorage e redireciona para o dashboard.")
bullet("4. Os pedidos seguintes enviam o token no cabecalho Authorization.")
prnt("Captura do ecra de login (pagina login.html) com o formulario de email e "
     "password preenchido.")
prnt("Captura do dashboard apos login bem-sucedido, mostrando o menu lateral adaptado "
     "ao perfil do utilizador autenticado.")
prnt("Captura (opcional) das ferramentas de programador do navegador a mostrar o "
     "token JWT guardado no localStorage e/ou o cabecalho Authorization num pedido.")
prnt("Captura de uma tentativa de login com credenciais invalidas, mostrando a "
     "mensagem de erro devolvida pela API.")

# ---- 7. FUNCIONALIDADE DE NEGOCIO ----
h1("7. Funcionalidade de Negocio: Reserva de Livros")
p("A funcionalidade de negocio central da aplicacao e a reserva de livros com fluxo de "
  "aprovacao. O seu objetivo e permitir que um cliente reserve um exemplar de um livro "
  "do catalogo e que essa reserva seja validada (aprovada) por um bibliotecario ou "
  "administrador, garantindo o controlo do stock de copias disponiveis.")
h2("7.1. Tabelas envolvidas")
p("Esta funcionalidade envolve as tres tabelas do dominio: livros (para verificar a "
  "existencia e a disponibilidade de copias), utilizadores (para identificar o cliente "
  "que reserva) e reservas (onde a reserva e efetivamente registada e o seu estado e "
  "atualizado ao longo do tempo).")
h2("7.2. Fluxo e regras")
bullet("Criar reserva (cliente): o backend verifica se o livro existe, se o seu estado "
       "e 'disponivel' e se ha copias livres (quantidade menos reservas em curso). Se "
       "sim, cria a reserva no estado 'pendente'. O utilizador_id vem sempre do token, "
       "nunca do pedido.")
bullet("Aprovar reserva (bibliotecario/admin): a reserva passa de 'pendente' para "
       "'confirmada'. O cliente nao pode auto-aprovar - esta regra e validada no "
       "servidor.")
bullet("Terminar reserva (bibliotecario/admin): a reserva passa a 'terminada', "
       "libertando a copia para nova reserva.")
bullet("Cancelar reserva (cliente): a reserva passa a 'cancelada', libertando tambem a "
       "copia.")
p("A disponibilidade de cada livro e calculada dinamicamente: copias livres = "
  "quantidade total menos o numero de reservas em curso (pendentes ou confirmadas). "
  "Assim, o estado do livro nao precisa de ser alterado a cada reserva, evitando "
  "inconsistencias. O cliente apenas ve se o livro esta 'disponivel' ou 'indisponivel'; "
  "o bibliotecario e o admin veem o stock detalhado (copias livres / total).")
h2("7.3. Estados da reserva")
table(
    ["Estado", "Significado", "Efeito no stock"],
    [
        ["pendente", "Criada pelo cliente, aguarda aprovacao", "Ocupa uma copia"],
        ["confirmada", "Aprovada pelo staff", "Continua a ocupar uma copia"],
        ["terminada", "Entrega/devolucao concluida", "Liberta a copia"],
        ["cancelada", "Cancelada pelo cliente", "Liberta a copia"],
    ],
    widths=[1800, 4200, 3000],
)
h2("7.4. Evidencias de execucao")
prnt("Captura da pagina de livros (livros.html) na perspetiva de um cliente, com o "
     "botao 'Reservar' num livro disponivel.")
prnt("Captura da pagina de reservas do cliente apos reservar, mostrando a reserva no "
     "estado 'pendente de aprovacao'.")
prnt("Captura da pagina de reservas na perspetiva do bibliotecario/admin, mostrando a "
     "lista de reservas com o nome do cliente e os botoes 'Aprovar' e 'Terminar'.")
prnt("Captura apos a aprovacao, com a reserva no estado 'confirmada'.")
prnt("Captura da pagina de livros na perspetiva do bibliotecario/admin, mostrando a "
     "coluna de stock (copias livres / total) e o botao CREATE.")

# ---- 8. DESENHO WEB ----
h1("8. Capturas de Ecra do Desenho Web")
p("O frontend adota um tema visual coerente em tons de castanho e cinzento, com um "
  "fundo alusivo a uma biblioteca e tipografia com serifa nos titulos. A estrutura das "
  "paginas internas e composta por um menu lateral (sidebar) adaptado ao perfil, uma "
  "barra de topo (topbar) e cartoes/tabelas de conteudo.")
prnt("Captura geral do dashboard a evidenciar a paleta de cores (castanho/cinzento) e "
     "o fundo de biblioteca.")
prnt("Captura da pagina de gestao de utilizadores (apenas admin), com a tabela de "
     "contas e os botoes de editar, eliminar e promover/despromover.")
prnt("Captura da pagina 'O Meu Perfil', com o formulario de dados pessoais e o "
     "formulario de alteracao de password.")
prnt("Captura das paginas de criar/editar livro, mostrando o campo de quantidade "
     "(stock) e o estado.")
prnt("Captura do fluxo de recuperacao de password (paginas de pedido de token e de "
     "definicao de nova password).")

# ---- 9. DIFICULDADES E DECISOES ----
h1("9. Dificuldades e Decisoes Tecnicas")
p("Ao longo do desenvolvimento foram tomadas varias decisoes tecnicas e ultrapassadas "
  "algumas dificuldades, das quais se destacam:")
bullet("Controlo de acessos por perfil: foi adicionada uma coluna 'role' a tabela de "
       "utilizadores (atraves de uma nova migracao, sem alterar a original) e criado um "
       "helper requireRole(...) para proteger as rotas. A seguranca e garantida no "
       "servidor e nao apenas escondendo botoes no interface.")
bullet("Modelacao do stock: optou-se por calcular a disponibilidade (copias livres) a "
       "partir das reservas em curso, em vez de manter um contador no livro, evitando "
       "problemas de sincronizacao entre tabelas.")
bullet("Fluxo de aprovacao de reservas: foi necessario impedir, no servidor, que um "
       "cliente alterasse a sua reserva diretamente para 'confirmada', garantindo que "
       "apenas o staff aprova.")
bullet("Recuperacao de password sem servidor de email: como nao existe envio de email "
       "real, o token de reset e devolvido na resposta da API e apresentado no "
       "frontend, decisao devidamente documentada.")
bullet("Correcao de um bug de seguranca pre-existente na validacao do token (tokens "
       "expirados eram aceites por falta de um 'return'), agora corrigido.")
bullet("CORS: foi necessario ativar o CORS no backend para que o navegador pudesse "
       "consumir a API a partir do frontend.")
bullet("Coerencia visual: para evitar a duplicacao de estilos em cada pagina, os "
       "estilos comuns foram centralizados numa folha de estilos partilhada "
       "(css/style.css) e os utilitarios de autenticacao num ficheiro JavaScript unico "
       "(js/config.js).")

# ---- 10. CONCLUSAO ----
h1("10. Conclusao")
p("O projeto PWBiblioteca cumpre os objetivos propostos, disponibilizando uma "
  "aplicacao web funcional de gestao de biblioteca, com autenticacao segura, controlo "
  "de acessos por perfil e uma funcionalidade de negocio completa de reserva de livros "
  "com fluxo de aprovacao. A arquitetura MVC simplificada, combinada com o "
  "carregamento automatico de servicos e rotas, resultou num codigo organizado e de "
  "facil manutencao.")
p("Como trabalho futuro, poderiam ser acrescentados: o envio real de emails na "
  "recuperacao de password, um historico/relatorio de reservas, paginacao e pesquisa "
  "no catalogo, e testes automatizados para a API. Globalmente, o trabalho permitiu "
  "consolidar conhecimentos de desenvolvimento full-stack, integracao entre frontend e "
  "backend e boas praticas de seguranca em aplicacoes web.")

# ---- 11. REFERENCIAS ----
h1("11. Referencias Bibliograficas")
bullet("Express - documentacao oficial: https://expressjs.com/")
bullet("Knex.js - documentacao oficial: https://knexjs.org/")
bullet("Passport.js - documentacao oficial: https://www.passportjs.org/")
bullet("JSON Web Tokens (JWT): https://jwt.io/")
bullet("bcrypt (npm): https://www.npmjs.com/package/bcrypt")
bullet("MDN Web Docs (HTML, CSS, JavaScript): https://developer.mozilla.org/")
bullet("Node.js - documentacao oficial: https://nodejs.org/")

# =================================================================== EMPACOTAR

sectPr = (
    '<w:sectPr>'
    '<w:pgSz w:w="11906" w:h="16838"/>'
    '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" '
    'w:header="708" w:footer="708" w:gutter="0"/>'
    '</w:sectPr>'
)

document_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:body>'
    + "".join(body)
    + sectPr +
    '</w:body></w:document>'
)


def heading_style(sid, name, outline, size, color, after=120, before=240):
    return (
        f'<w:style w:type="paragraph" w:styleId="{sid}">'
        f'<w:name w:val="{name}"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        f'<w:pPr><w:keepNext/><w:spacing w:before="{before}" w:after="{after}"/>'
        f'<w:outlineLvl w:val="{outline}"/></w:pPr>'
        f'<w:rPr><w:b/><w:color w:val="{color}"/>'
        f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'
        '</w:style>'
    )


styles_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:docDefaults><w:rPrDefault><w:rPr>'
    '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>'
    '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>'
    # Normal
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
    '<w:name w:val="Normal"/>'
    '<w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/>'
    '<w:jc w:val="both"/></w:pPr>'
    '</w:style>'
    # Title
    '<w:style w:type="paragraph" w:styleId="Title">'
    '<w:name w:val="Title"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="240" w:after="120"/><w:jc w:val="center"/></w:pPr>'
    '<w:rPr><w:b/><w:color w:val="33261A"/><w:sz w:val="56"/><w:szCs w:val="56"/></w:rPr>'
    '</w:style>'
    # Headings
    + heading_style("Heading1", "heading 1", "0", "32", "33261A")
    + heading_style("Heading2", "heading 2", "1", "26", "6B4E32")
    + heading_style("Heading3", "heading 3", "2", "24", "6B4E32")
    +
    # ListBullet
    '<w:style w:type="paragraph" w:styleId="ListBullet">'
    '<w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:after="80"/><w:ind w:left="360" w:hanging="360"/>'
    '<w:jc w:val="left"/></w:pPr>'
    '</w:style>'
    # Print placeholder
    '<w:style w:type="paragraph" w:styleId="Print">'
    '<w:name w:val="Print"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="80" w:after="80"/>'
    '<w:pBdr>'
    '<w:top w:val="single" w:sz="6" w:space="4" w:color="B08D57"/>'
    '<w:left w:val="single" w:sz="6" w:space="4" w:color="B08D57"/>'
    '<w:bottom w:val="single" w:sz="6" w:space="4" w:color="B08D57"/>'
    '<w:right w:val="single" w:sz="6" w:space="4" w:color="B08D57"/>'
    '</w:pBdr>'
    '<w:shd w:val="clear" w:color="auto" w:fill="F5EEDD"/>'
    '<w:jc w:val="left"/></w:pPr>'
    '<w:rPr><w:i/><w:color w:val="6B4E32"/></w:rPr>'
    '</w:style>'
    '</w:styles>'
)

settings_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:updateFields w:val="true"/>'
    '</w:settings>'
)

content_types = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/settings.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '</Types>'
)

rels = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="word/document.xml"/>'
    '</Relationships>'
)

document_rels = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
    'Target="styles.xml"/>'
    '<Relationship Id="rId2" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" '
    'Target="settings.xml"/>'
    '</Relationships>'
)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", document_xml)
    z.writestr("word/styles.xml", styles_xml)
    z.writestr("word/settings.xml", settings_xml)
    z.writestr("word/_rels/document.xml.rels", document_rels)

print("Gerado:", OUT)
