from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

import mysql.connector
import os

from mysql.connector import Error

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# CONFIGURAÇÃO
# =========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = os.getenv("SECRET_KEY", "truck_parts_chave")


# =========================================================
# CONEXÃO COM MYSQL
# =========================================================

def conectar_banco():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "senai105"),
        database=os.getenv("MYSQL_DATABASE", "DB_truck_prts")
    )


def fechar_banco(conexao, cursor):

    if cursor:
        cursor.close()

    if conexao:
        conexao.close()


# =========================================================
# USUÁRIO LOGADO
# =========================================================

@app.context_processor
def injetar_usuario():

    return {
        "logado": "usuario_id" in session,
        "usuario_nome": session.get("usuario_nome")
    }


# =========================================================
# PÁGINA INICIAL
# =========================================================

@app.route("/")
def land():

    return render_template("land.html")


# =========================================================
# CADASTRO - PÁGINA
# =========================================================

@app.route("/cadastro")
def cadastro():

    return render_template("cadastro.html")


# =========================================================
# CADASTRO - PROCESSAMENTO
# =========================================================

@app.route("/cadastrar", methods=["POST"])
def fazer_cadastro():

    nome = request.form.get("nome", "").strip()
    data_nascimento = request.form.get("data_nascimento", "").strip()
    cpf = request.form.get("cpf", "").strip()
    telefone = request.form.get("telefone", "").strip()
    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")
    cep = request.form.get("cep", "").strip()
    numero = request.form.get("numero", "").strip()
    complemento = request.form.get("complemento", "").strip()
    tipo_cadastro = request.form.get("tipo_cadastro", "").strip()

    interesses_texto = ", ".join(
        request.form.getlist("interesses")
    )


    # =====================================================
    # VALIDAÇÕES
    # =====================================================

    if not nome:
        return "Informe o nome."

    if not data_nascimento:
        return "Informe a data de nascimento."

    if not cpf:
        return "Informe o CPF."

    if not telefone:
        return "Informe o telefone."

    if not email:
        return "Informe o e-mail."

    if not cep:
        return "Informe o CEP."

    if not numero:
        return "Informe o número do endereço."

    if not tipo_cadastro:
        return "Selecione o tipo de cadastro."

    if not senha:
        return "Informe a senha."

    if senha != confirmar_senha:
        return "As senhas não coincidem."

    if len(senha) < 6:
        return "A senha deve possuir pelo menos 6 caracteres."


    # =====================================================
    # LIMPAR CPF / TELEFONE / CEP
    # =====================================================

    cpf = "".join(filter(str.isdigit, cpf))
    telefone = "".join(filter(str.isdigit, telefone))
    cep = "".join(filter(str.isdigit, cep))

    if len(cpf) != 11:
        return "CPF inválido."

    if len(telefone) not in (10, 11):
        return "Telefone inválido."

    if len(cep) != 8:
        return "CEP inválido."


    senha_hash = generate_password_hash(senha)

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        # VERIFICAR EMAIL
        cursor.execute(
            "SELECT id_usuario FROM USUARIO WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return "Este e-mail já está cadastrado."

        # VERIFICAR CPF
        cursor.execute(
            "SELECT id_usuario FROM USUARIO WHERE cpf = %s",
            (cpf,)
        )

        if cursor.fetchone():
            return "Este CPF já está cadastrado."

        # VERIFICAR TELEFONE
        cursor.execute(
            "SELECT id_usuario FROM USUARIO WHERE telefone = %s",
            (telefone,)
        )

        if cursor.fetchone():
            return "Este telefone já está cadastrado."

        # CADASTRAR ENDEREÇO
        cursor.execute(
            """
            INSERT INTO ENDERECO (cep, numero, complemento)
            VALUES (%s, %s, %s)
            """,
            (cep, numero, complemento if complemento else None)
        )

        id_endereco = cursor.lastrowid

        # CADASTRAR USUÁRIO
        cursor.execute(
            """
            INSERT INTO USUARIO
            (
                id_endereco,
                nome,
                data_nascimento,
                cpf,
                telefone,
                email,
                senha,
                tipo_cadastro,
                interesses
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                id_endereco,
                nome,
                data_nascimento,
                cpf,
                telefone,
                email,
                senha_hash,
                tipo_cadastro,
                interesses_texto
            )
        )

        conexao.commit()

        return redirect(url_for("login"))

    except Error as erro:

        if conexao:
            conexao.rollback()

        return f"Erro ao realizar cadastro: {erro}"

    finally:

        fechar_banco(conexao, cursor)


# =========================================================
# LOGIN - PÁGINA
# =========================================================

@app.route("/login", methods=["GET"])
def login():

    # Se já estiver logado, não precisa ver a tela de login
    if "usuario_id" in session:
        return redirect(url_for("land"))

    return render_template("login.html")


# =========================================================
# LOGIN - PROCESSAMENTO
# =========================================================

@app.route("/login", methods=["POST"])
def fazer_login():

    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_usuario, nome, senha
            FROM USUARIO
            WHERE email = %s
            """,
            (email,)
        )

        usuario = cursor.fetchone()

    except Error as erro:

        return f"Erro ao acessar o banco: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    if usuario is None:
        return "E-mail ou senha incorretos."

    if not check_password_hash(usuario["senha"], senha):
        return "E-mail ou senha incorretos."

    session.clear()
    session["usuario_id"] = usuario["id_usuario"]
    session["usuario_nome"] = usuario["nome"]

    return redirect(url_for("land"))


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("land"))


# =========================================================
# CATÁLOGO
# =========================================================

@app.route("/catalogo")
def catalogo():

    pesquisa = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT
                id_produto,
                descricao_prod,
                preco_prod,
                marca_produto,
                modelo_scania,
                categoria,
                imagem,
                estoque

            FROM PRODUTO

            WHERE 1 = 1
        """

        valores = []

        # PESQUISA
        if pesquisa:

            sql += """
                AND
                (
                    descricao_prod LIKE %s
                    OR marca_produto LIKE %s
                    OR categoria LIKE %s
                )
            """

            termo = f"%{pesquisa}%"

            valores.extend([termo, termo, termo])

        # CATEGORIA (ignora diferenças de maiúsculas e acentos)
        if categoria and categoria.lower() != "todos":

            sql += """
                AND LOWER(categoria) COLLATE utf8mb4_general_ci
                    = LOWER(%s) COLLATE utf8mb4_general_ci
            """

            valores.append(categoria)

        sql += " ORDER BY id_produto ASC"

        cursor.execute(sql, valores)

        products = cursor.fetchall()

    except Error as erro:

        return f"Erro ao carregar catálogo: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    return render_template(
        "catalogo.html",
        products=products,
        pesquisa=pesquisa,
        categoria=categoria
    )


# =========================================================
# CARRINHO - CONFIGURAÇÃO
#
# Tabelas usadas:
#   CARRINHO      (id_carrinho, id_usuario, quantidade, sub, s_carrinho)
#   ITEM_CARRINHO (id_carrinho, id_produto, quantidade, preco_unitario)
#
# CARRINHO.quantidade = total de unidades no carrinho
# CARRINHO.sub        = subtotal do carrinho
# CARRINHO.s_carrinho = situação do carrinho. O carrinho em uso
#                       é o que tem s_carrinho = STATUS_ABERTO.
# =========================================================

STATUS_ABERTO = "aberto"


# =========================================================
# CARRINHO - FUNÇÕES AUXILIARES
# (o cursor precisa ser criado com dictionary=True)
# =========================================================

def obter_carrinho_aberto(cursor, id_usuario, criar=False):

    cursor.execute(
        """
        SELECT id_carrinho
        FROM CARRINHO
        WHERE id_usuario = %s
        AND s_carrinho = %s
        ORDER BY id_carrinho DESC
        LIMIT 1
        """,
        (id_usuario, STATUS_ABERTO)
    )

    linha = cursor.fetchone()

    if linha:
        return linha["id_carrinho"]

    if not criar:
        return None

    cursor.execute(
        """
        INSERT INTO CARRINHO
        (
            id_usuario,
            quantidade,
            sub,
            s_carrinho
        )
        VALUES (%s, 0, 0.00, %s)
        """,
        (id_usuario, STATUS_ABERTO)
    )

    return cursor.lastrowid


def atualizar_totais_carrinho(cursor, id_carrinho):

    # Recalcula quantidade e sub do carrinho a partir dos itens
    cursor.execute(
        """
        UPDATE CARRINHO

        SET
            quantidade = (
                SELECT COALESCE(SUM(i.quantidade), 0)
                FROM ITEM_CARRINHO i
                WHERE i.id_carrinho = %s
            ),
            sub = (
                SELECT COALESCE(SUM(i.quantidade * i.preco_unitario), 0)
                FROM ITEM_CARRINHO i
                WHERE i.id_carrinho = %s
            )

        WHERE id_carrinho = %s
        """,
        (id_carrinho, id_carrinho, id_carrinho)
    )


# =========================================================
# ADICIONAR AO CARRINHO
# =========================================================

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    id_usuario = session["usuario_id"]

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # BUSCAR PRODUTO
        cursor.execute(
            """
            SELECT id_produto, preco_prod, estoque
            FROM PRODUTO
            WHERE id_produto = %s
            """,
            (product_id,)
        )

        produto = cursor.fetchone()

        if produto is None:
            return "Produto não encontrado."

        if produto["estoque"] <= 0:
            return "Produto sem estoque."

        # CARRINHO ABERTO (cria se não existir)
        id_carrinho = obter_carrinho_aberto(
            cursor,
            id_usuario,
            criar=True
        )

        # O PRODUTO JÁ ESTÁ NO CARRINHO?
        cursor.execute(
            """
            SELECT quantidade
            FROM ITEM_CARRINHO
            WHERE id_carrinho = %s
            AND id_produto = %s
            """,
            (id_carrinho, product_id)
        )

        item = cursor.fetchone()

        if item:

            nova_quantidade = item["quantidade"] + 1

            if nova_quantidade > produto["estoque"]:
                return "Você atingiu o limite disponível em estoque."

            cursor.execute(
                """
                UPDATE ITEM_CARRINHO
                SET
                    quantidade = %s,
                    preco_unitario = %s
                WHERE id_carrinho = %s
                AND id_produto = %s
                """,
                (
                    nova_quantidade,
                    produto["preco_prod"],
                    id_carrinho,
                    product_id
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO ITEM_CARRINHO
                (
                    id_carrinho,
                    id_produto,
                    quantidade,
                    preco_unitario
                )
                VALUES (%s, %s, 1, %s)
                """,
                (
                    id_carrinho,
                    product_id,
                    produto["preco_prod"]
                )
            )

        atualizar_totais_carrinho(cursor, id_carrinho)

        conexao.commit()

    except Error as erro:

        if conexao:
            conexao.rollback()

        return f"Erro ao adicionar produto: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    return redirect(url_for("carrinho"))


# =========================================================
# CARRINHO
# =========================================================

@app.route("/carrinho")
def carrinho():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    id_usuario = session["usuario_id"]

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        id_carrinho = obter_carrinho_aberto(cursor, id_usuario)

        items = []
        total = 0.0

        if id_carrinho:

            cursor.execute(
                """
                SELECT
                    i.id_carrinho,
                    i.id_produto,
                    i.quantidade,
                    i.preco_unitario,
                    i.quantidade * i.preco_unitario AS subtotal,

                    p.descricao_prod,
                    p.marca_produto,
                    p.categoria,
                    p.imagem,
                    p.estoque

                FROM ITEM_CARRINHO i

                INNER JOIN PRODUTO p
                    ON p.id_produto = i.id_produto

                WHERE i.id_carrinho = %s

                ORDER BY i.id_produto
                """,
                (id_carrinho,)
            )

            items = cursor.fetchall()

            total = sum(float(item["subtotal"]) for item in items)

    except Error as erro:

        return f"Erro ao carregar carrinho: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    return render_template(
        "carrinho.html",
        items=items,
        total=total
    )


# =========================================================
# FINALIZAR COMPRA
# =========================================================

@app.route("/finalizar_compra", methods=["GET", "POST"])
def finalizar_compra():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    id_usuario = session["usuario_id"]

    if request.method == "POST":
        conexao = None
        cursor = None

        try:
            conexao = conectar_banco()
            cursor = conexao.cursor(dictionary=True)

            id_carrinho = obter_carrinho_aberto(cursor, id_usuario)

            if id_carrinho is not None:
                cursor.execute(
                    """
                    DELETE FROM ITEM_CARRINHO
                    WHERE id_carrinho = %s
                    """,
                    (id_carrinho,)
                )

                cursor.execute(
                    """
                    UPDATE CARRINHO
                    SET quantidade = 0,
                        sub = 0.00
                    WHERE id_carrinho = %s
                    """,
                    (id_carrinho,)
                )

                conexao.commit()

        except Error as erro:
            if conexao:
                conexao.rollback()
            return f"Erro ao finalizar compra: {erro}"

        finally:
            fechar_banco(conexao, cursor)

        return redirect(url_for("catalogo"))

    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        id_carrinho = obter_carrinho_aberto(cursor, id_usuario)

        items = []
        total = 0.0

        if id_carrinho:
            cursor.execute(
                """
                SELECT
                    i.id_carrinho,
                    i.id_produto,
                    i.quantidade,
                    i.preco_unitario,
                    i.quantidade * i.preco_unitario AS subtotal,

                    p.descricao_prod,
                    p.marca_produto,
                    p.categoria,
                    p.imagem

                FROM ITEM_CARRINHO i

                INNER JOIN PRODUTO p
                    ON p.id_produto = i.id_produto

                WHERE i.id_carrinho = %s

                ORDER BY i.id_produto
                """,
                (id_carrinho,)
            )

            items = cursor.fetchall()
            total = sum(float(item["subtotal"]) for item in items)

    except Error as erro:
        return f"Erro ao carregar finalização: {erro}"

    finally:
        fechar_banco(conexao, cursor)

    return render_template(
        "finalizar_compra.html",
        items=items,
        total=total
    )


# =========================================================
# AUMENTAR QUANTIDADE
# (o item é identificado pelo id do produto)
# =========================================================

@app.route("/aumentar_quantidade/<int:product_id>", methods=["POST"])
def aumentar_quantidade(product_id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        id_carrinho = obter_carrinho_aberto(
            cursor,
            session["usuario_id"]
        )

        if id_carrinho is None:
            return "Carrinho não encontrado."

        cursor.execute(
            """
            SELECT
                i.quantidade,
                p.preco_prod,
                p.estoque

            FROM ITEM_CARRINHO i

            INNER JOIN PRODUTO p
                ON p.id_produto = i.id_produto

            WHERE i.id_carrinho = %s
            AND i.id_produto = %s
            """,
            (id_carrinho, product_id)
        )

        item = cursor.fetchone()

        if item is None:
            return "Item não encontrado."

        if item["quantidade"] >= item["estoque"]:
            return "Quantidade máxima disponível em estoque."

        cursor.execute(
            """
            UPDATE ITEM_CARRINHO
            SET
                quantidade = quantidade + 1,
                preco_unitario = %s
            WHERE id_carrinho = %s
            AND id_produto = %s
            """,
            (item["preco_prod"], id_carrinho, product_id)
        )

        atualizar_totais_carrinho(cursor, id_carrinho)

        conexao.commit()

    except Error as erro:

        if conexao:
            conexao.rollback()

        return f"Erro: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    return redirect(url_for("carrinho"))


# =========================================================
# DIMINUIR QUANTIDADE
# =========================================================

@app.route("/diminuir_quantidade/<int:product_id>", methods=["POST"])
def diminuir_quantidade(product_id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        id_carrinho = obter_carrinho_aberto(
            cursor,
            session["usuario_id"]
        )

        if id_carrinho is not None:

            cursor.execute(
                """
                SELECT quantidade
                FROM ITEM_CARRINHO
                WHERE id_carrinho = %s
                AND id_produto = %s
                """,
                (id_carrinho, product_id)
            )

            item = cursor.fetchone()

            if item:

                if item["quantidade"] > 1:

                    cursor.execute(
                        """
                        UPDATE ITEM_CARRINHO
                        SET quantidade = quantidade - 1
                        WHERE id_carrinho = %s
                        AND id_produto = %s
                        """,
                        (id_carrinho, product_id)
                    )

                else:

                    # REMOVE QUANDO CHEGAR A ZERO
                    cursor.execute(
                        """
                        DELETE FROM ITEM_CARRINHO
                        WHERE id_carrinho = %s
                        AND id_produto = %s
                        """,
                        (id_carrinho, product_id)
                    )

                atualizar_totais_carrinho(cursor, id_carrinho)

        conexao.commit()

    except Error as erro:

        if conexao:
            conexao.rollback()

        return f"Erro: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    return redirect(url_for("carrinho"))


# =========================================================
# REMOVER DO CARRINHO
# =========================================================

@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        id_carrinho = obter_carrinho_aberto(
            cursor,
            session["usuario_id"]
        )

        if id_carrinho is not None:

            cursor.execute(
                """
                DELETE FROM ITEM_CARRINHO
                WHERE id_carrinho = %s
                AND id_produto = %s
                """,
                (id_carrinho, product_id)
            )

            atualizar_totais_carrinho(cursor, id_carrinho)

        conexao.commit()

    except Error as erro:

        if conexao:
            conexao.rollback()

        return f"Erro ao remover produto: {erro}"

    finally:

        fechar_banco(conexao, cursor)

    return redirect(url_for("carrinho"))


# =========================================================
# EXECUTAR
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)