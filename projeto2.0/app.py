
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

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

app.secret_key = os.getenv(
    "SECRET_KEY",
    "truck_parts_chave"
)


# =========================================================
# CONEXÃO COM MYSQL
# =========================================================

def conectar_banco():

    return mysql.connector.connect(
        host=os.getenv(
            "MYSQL_HOST",
            "127.0.0.1"
        ),

        user=os.getenv(
            "MYSQL_USER",
            "root"
        ),

        password=os.getenv(
            "MYSQL_PASSWORD",
            "senai105"
        ),

        database=os.getenv(
            "MYSQL_DATABASE",
            "DB_truck_prts"
        )
    )


def fechar_banco(conexao, cursor):

    if cursor:
        cursor.close()

    if conexao:
        conexao.close()


def usuario_existe(id_usuario):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT 1

            FROM USUARIO

            WHERE id_usuario = %s
            """,
            (id_usuario,)
        )

        return cursor.fetchone() is not None

    except Error:

        return False

    finally:

        fechar_banco(
            conexao,
            cursor
        )


# =========================================================
# USUÁRIO LOGADO
# =========================================================

@app.context_processor
def injetar_usuario():

    return {
        "logado": "usuario_id" in session,
        "usuario_nome": session.get(
            "usuario_nome"
        )
    }


# =========================================================
# PÁGINA INICIAL
# =========================================================

@app.route("/")
def land():

    return render_template(
        "land.html"
    )


# =========================================================
# CADASTRO - PÁGINA
# =========================================================

@app.route("/cadastro")
def cadastro():

    return render_template(
        "cadastro.html"
    )


# =========================================================
# CADASTRO - PROCESSAMENTO
# =========================================================

@app.route(
    "/cadastrar",
    methods=["POST"]
)
def fazer_cadastro():

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    data_nascimento = request.form.get(
        "data_nascimento",
        ""
    ).strip()

    cpf = request.form.get(
        "cpf",
        ""
    ).strip()

    telefone = request.form.get(
        "telefone",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    senha = request.form.get(
        "senha",
        ""
    )

    confirmar_senha = request.form.get(
        "confirmar_senha",
        ""
    )

    cep = request.form.get(
        "cep",
        ""
    ).strip()

    numero = request.form.get(
        "numero",
        ""
    ).strip()

    complemento = request.form.get(
        "complemento",
        ""
    ).strip()

    tipo_cadastro = request.form.get(
        "tipo_cadastro",
        ""
    ).strip()

    interesses = request.form.getlist(
        "interesses"
    )

    interesses_texto = ", ".join(
        interesses
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
        return (
            "A senha deve possuir pelo menos 6 caracteres."
        )


    # =====================================================
    # LIMPAR CPF / TELEFONE / CEP
    # =====================================================

    cpf = "".join(
        filter(str.isdigit, cpf)
    )

    telefone = "".join(
        filter(str.isdigit, telefone)
    )

    cep = "".join(
        filter(str.isdigit, cep)
    )


    if len(cpf) != 11:
        return "CPF inválido."

    if len(telefone) not in (10, 11):
        return "Telefone inválido."

    if len(cep) != 8:
        return "CEP inválido."


    # =====================================================
    # CRIPTOGRAFAR SENHA
    # =====================================================

    senha_hash = generate_password_hash(
        senha
    )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor()


        # =================================================
        # VERIFICAR EMAIL
        # =================================================

        cursor.execute(
            """
            SELECT id_usuario

            FROM USUARIO

            WHERE email = %s
            """,

            (email,)
        )

        if cursor.fetchone():

            return (
                "Este e-mail já está cadastrado."
            )


        # =================================================
        # VERIFICAR CPF
        # =================================================

        cursor.execute(
            """
            SELECT id_usuario

            FROM USUARIO

            WHERE cpf = %s
            """,

            (cpf,)
        )

        if cursor.fetchone():

            return (
                "Este CPF já está cadastrado."
            )


        # =================================================
        # VERIFICAR TELEFONE
        # =================================================

        cursor.execute(
            """
            SELECT id_usuario

            FROM USUARIO

            WHERE telefone = %s
            """,

            (telefone,)
        )

        if cursor.fetchone():

            return (
                "Este telefone já está cadastrado."
            )


        # =================================================
        # CADASTRAR ENDEREÇO
        # =================================================

        cursor.execute(
            """
            INSERT INTO ENDERECO
            (
                cep,
                numero,
                complemento
            )

            VALUES
            (
                %s,
                %s,
                %s
            )
            """,

            (
                cep,
                numero,
                complemento
                if complemento
                else None
            )
        )


        id_endereco = cursor.lastrowid


        # =================================================
        # CADASTRAR USUÁRIO
        # =================================================

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

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
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


        return redirect(
            url_for("login")
        )


    except Error as erro:

        if conexao:
            conexao.rollback()

        return (
            f"Erro ao realizar cadastro: {erro}"
        )


    finally:

        fechar_banco(
            conexao,
            cursor
        )


# =========================================================
# LOGIN - PÁGINA
# =========================================================

@app.route(
    "/login",
    methods=["GET"]
)
def login():

    if "usuario_id" in session:

        return redirect(
            url_for("land")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGIN - PROCESSAMENTO
# =========================================================

@app.route(
    "/login",
    methods=["POST"]
)
def fazer_login():

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    senha = request.form.get(
        "senha",
        ""
    )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                id_usuario,
                nome,
                senha

            FROM USUARIO

            WHERE email = %s
            """,

            (email,)
        )


        usuario = cursor.fetchone()


    except Error as erro:

        return (
            f"Erro ao acessar o banco: {erro}"
        )


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    if usuario is None:

        return (
            "E-mail ou senha incorretos."
        )


    if not check_password_hash(
        usuario["senha"],
        senha
    ):

        return (
            "E-mail ou senha incorretos."
        )


    session.clear()

    session["usuario_id"] = (
        usuario["id_usuario"]
    )

    session["usuario_nome"] = (
        usuario["nome"]
    )


    return redirect(
        url_for("land")
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("land")
    )


# =========================================================
# CATÁLOGO
# =========================================================

@app.route("/catalogo")
def catalogo():

    pesquisa = request.args.get(
        "q",
        ""
    ).strip()

    categoria = request.args.get(
        "categoria",
        ""
    ).strip()


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor(
            dictionary=True
        )


        # =================================================
        # CONSULTA DOS PRODUTOS
        # =================================================

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


        # =================================================
        # PESQUISA
        # =================================================

        if pesquisa:

            sql += """
                AND
                (
                    descricao_prod LIKE %s
                    OR marca_produto LIKE %s
                    OR categoria LIKE %s
                    OR modelo_scania LIKE %s
                )
            """


            termo = f"%{pesquisa}%"


            valores.extend(
                [
                    termo,
                    termo,
                    termo,
                    termo
                ]
            )


        # =================================================
        # CATEGORIA
        # =================================================

        if (
            categoria
            and categoria.lower() != "todos"
        ):

            sql += """
                AND LOWER(categoria)
                    COLLATE utf8mb4_general_ci
                    =
                    LOWER(%s)
                    COLLATE utf8mb4_general_ci
            """


            valores.append(
                categoria
            )


        # =================================================
        # ORDENAR
        # =================================================

        sql += """
            ORDER BY id_produto ASC
        """


        # =================================================
        # EXECUTAR SQL
        # =================================================

        cursor.execute(
            sql,
            valores
        )


        # =================================================
        # PEGAR PRODUTOS
        # =================================================

        products = cursor.fetchall()


    except Error as erro:

        return (
            f"Erro ao carregar catálogo: {erro}"
        )


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    # =====================================================
    # ENVIAR PRODUTOS PARA O HTML
    # =====================================================

    return render_template(
        "catalogo.html",
        products=products,
        pesquisa=pesquisa,
        categoria=categoria
    )


# =========================================================
# ADICIONAR AO CARRINHO
# =========================================================

@app.route(
    "/add_to_cart/<int:product_id>",
    methods=["GET", "POST"]
)
def add_to_cart(product_id):

    # =====================================================
    # VERIFICAR LOGIN
    # =====================================================

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    id_usuario = session["usuario_id"]

    if not usuario_existe(id_usuario):

        session.clear()
        flash(
            "Sua sessão expirou. Faça login novamente.",
            "aviso"
        )

        return redirect(
            url_for("login")
        )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor(
            dictionary=True
        )


        # =================================================
        # BUSCAR PRODUTO
        # =================================================

        cursor.execute(
            """
            SELECT
                id_produto,
                preco_prod,
                estoque

            FROM PRODUTO

            WHERE id_produto = %s
            """,

            (product_id,)
        )


        produto = cursor.fetchone()


        if produto is None:

            return (
                "Produto não encontrado."
            )


        # =================================================
        # VERIFICAR ESTOQUE
        # =================================================

        if produto["estoque"] <= 0:

            return (
                "Produto sem estoque."
            )


        # =================================================
        # VERIFICAR CARRINHO
        # =================================================

        cursor.execute(
            """
            SELECT
                id_carrinho,
                quantidade

            FROM CARRINHO

            WHERE id_produto = %s
            AND id_usuario = %s
            """,

            (
                product_id,
                id_usuario
            )
        )


        item = cursor.fetchone()


        # =================================================
        # PRODUTO JÁ EXISTE
        # =================================================

        if item:

            nova_quantidade = (
                item["quantidade"] + 1
            )


            # =============================================
            # LIMITAR AO ESTOQUE
            # =============================================

            if (
                nova_quantidade
                > produto["estoque"]
            ):

                return (
                    "Você atingiu o limite "
                    "disponível em estoque."
                )


            novo_subtotal = (
                produto["preco_prod"]
                * nova_quantidade
            )


            cursor.execute(
                """
                UPDATE CARRINHO

                SET
                    quantidade = %s,
                    subtotal = %s

                WHERE id_carrinho = %s
                AND id_usuario = %s
                """,

                (
                    nova_quantidade,
                    novo_subtotal,
                    item["id_carrinho"],
                    id_usuario
                )
            )


        # =================================================
        # NOVO PRODUTO
        # =================================================

        else:

            cursor.execute(
                """
                INSERT INTO CARRINHO
                (
                    id_produto,
                    id_usuario,
                    quantidade,
                    subtotal
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,

                (
                    product_id,
                    id_usuario,
                    1,
                    produto["preco_prod"]
                )
            )


        conexao.commit()


    except Error as erro:

        if conexao:

            conexao.rollback()


        return (
            f"Erro ao adicionar produto: {erro}"
        )


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    if request.headers.get("X-Requested-With") == "XMLHttpRequest":

        return jsonify({
            "success": True,
            "message": "Produto adicionado ao carrinho!"
        })

    flash(
        "Produto adicionado ao carrinho!",
        "sucesso"
    )

    return redirect(
        url_for("catalogo")
    )


# =========================================================
# CARRINHO
# =========================================================

@app.route("/carrinho")
def carrinho():

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    id_usuario = session["usuario_id"]

    if not usuario_existe(id_usuario):

        session.clear()
        flash(
            "Sua sessão expirou. Faça login novamente.",
            "aviso"
        )

        return redirect(
            url_for("login")
        )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor(
            dictionary=True
        )


        # =================================================
        # PRODUTOS DO CARRINHO
        # =================================================

        cursor.execute(
            """
            SELECT
                c.id_carrinho,
                c.id_produto,
                c.quantidade,
                c.subtotal,

                p.descricao_prod,
                p.preco_prod,
                p.marca_produto,
                p.categoria,
                p.imagem,
                p.estoque

            FROM CARRINHO c

            INNER JOIN PRODUTO p
                ON c.id_produto = p.id_produto

            WHERE c.id_usuario = %s

            ORDER BY c.id_carrinho DESC
            """,

            (id_usuario,)
        )


        items = cursor.fetchall()


        # =================================================
        # TOTAL
        # =================================================

        total = sum(
            float(item["subtotal"])
            for item in items
        )


    except Error as erro:

        return (
            f"Erro ao carregar carrinho: {erro}"
        )


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    return render_template(
        "carrinho.html",
        items=items,
        total=total
    )


# =========================================================
# AUMENTAR QUANTIDADE
# =========================================================

@app.route(
    "/aumentar_quantidade/<int:cart_id>",
    methods=["POST"]
)
def aumentar_quantidade(cart_id):

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    if not usuario_existe(session["usuario_id"]):

        session.clear()
        flash(
            "Sua sessão expirou. Faça login novamente.",
            "aviso"
        )

        return redirect(
            url_for("login")
        )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor(
            dictionary=True
        )


        # =================================================
        # BUSCAR ITEM + ESTOQUE
        # =================================================

        cursor.execute(
            """
            SELECT
                c.quantidade,
                p.preco_prod,
                p.estoque

            FROM CARRINHO c

            INNER JOIN PRODUTO p
                ON c.id_produto = p.id_produto

            WHERE c.id_carrinho = %s
            AND c.id_usuario = %s
            """,

            (
                cart_id,
                session["usuario_id"]
            )
        )


        item = cursor.fetchone()


        if item is None:

            return (
                "Item não encontrado."
            )


        # =================================================
        # VERIFICAR ESTOQUE
        # =================================================

        if (
            item["quantidade"]
            >= item["estoque"]
        ):

            return (
                "Quantidade máxima "
                "disponível em estoque."
            )


        nova_quantidade = (
            item["quantidade"] + 1
        )


        novo_subtotal = (
            nova_quantidade
            * item["preco_prod"]
        )


        # =================================================
        # ATUALIZAR
        # =================================================

        cursor.execute(
            """
            UPDATE CARRINHO

            SET
                quantidade = %s,
                subtotal = %s

            WHERE id_carrinho = %s
            AND id_usuario = %s
            """,

            (
                nova_quantidade,
                novo_subtotal,
                cart_id,
                session["usuario_id"]
            )
        )


        conexao.commit()


    except Error as erro:

        if conexao:

            conexao.rollback()


        return f"Erro: {erro}"


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    return redirect(
        url_for("carrinho")
    )


# =========================================================
# DIMINUIR QUANTIDADE
# =========================================================

@app.route(
    "/diminuir_quantidade/<int:cart_id>",
    methods=["POST"]
)
def diminuir_quantidade(cart_id):

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    if not usuario_existe(session["usuario_id"]):

        session.clear()
        flash(
            "Sua sessão expirou. Faça login novamente.",
            "aviso"
        )

        return redirect(
            url_for("login")
        )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor(
            dictionary=True
        )


        # =================================================
        # BUSCAR ITEM
        # =================================================

        cursor.execute(
            """
            SELECT quantidade

            FROM CARRINHO

            WHERE id_carrinho = %s
            AND id_usuario = %s
            """,

            (
                cart_id,
                session["usuario_id"]
            )
        )


        item = cursor.fetchone()


        if item:

            # =============================================
            # DIMINUIR
            # =============================================

            if item["quantidade"] > 1:

                cursor.execute(
                    """
                    UPDATE CARRINHO c

                    INNER JOIN PRODUTO p
                        ON c.id_produto = p.id_produto

                    SET
                        c.quantidade =
                            c.quantidade - 1,

                        c.subtotal =
                            (c.quantidade - 1)
                            * p.preco_prod

                    WHERE c.id_carrinho = %s
                    AND c.id_usuario = %s
                    """,

                    (
                        cart_id,
                        session["usuario_id"]
                    )
                )


            # =============================================
            # REMOVER QUANDO CHEGAR A ZERO
            # =============================================

            else:

                cursor.execute(
                    """
                    DELETE FROM CARRINHO

                    WHERE id_carrinho = %s
                    AND id_usuario = %s
                    """,

                    (
                        cart_id,
                        session["usuario_id"]
                    )
                )


        conexao.commit()


    except Error as erro:

        if conexao:

            conexao.rollback()


        return f"Erro: {erro}"


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    return redirect(
        url_for("carrinho")
    )


# =========================================================
# REMOVER DO CARRINHO
# =========================================================

@app.route(
    "/remove_from_cart/<int:cart_id>",
    methods=["POST"]
)
def remove_from_cart(cart_id):

    if "usuario_id" not in session:

        return redirect(
            url_for("login")
        )

    if not usuario_existe(session["usuario_id"]):

        session.clear()
        flash(
            "Sua sessão expirou. Faça login novamente.",
            "aviso"
        )

        return redirect(
            url_for("login")
        )


    conexao = None
    cursor = None


    try:

        conexao = conectar_banco()

        cursor = conexao.cursor()


        cursor.execute(
            """
            DELETE FROM CARRINHO

            WHERE id_carrinho = %s
            AND id_usuario = %s
            """,

            (
                cart_id,
                session["usuario_id"]
            )
        )


        conexao.commit()


    except Error as erro:

        if conexao:

            conexao.rollback()


        return (
            f"Erro ao remover produto: {erro}"
        )


    finally:

        fechar_banco(
            conexao,
            cursor
        )


    return redirect(
        url_for("carrinho")
    )


# =========================================================
# EXECUTAR
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
