import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
import bcrypt


@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor()

        json = request.json
        name = json['username']
        email = json['email']
        password = json['password']
        professor = json['professor']

        # Validado se foi informando email
        if email is None:
            return mensagem("Email não informando")

        # validado se existe espaço na turma
        if len(alunos()) > 100:
            return mensagem("Quantidade de alunos máximo atingido")

        usuario_cadastrado = user_email(email)
        # validado se já existe usuario
        if usuario_cadastrado is not None:
            return mensagem("Email já cadastrado, tente outro")

        # validado as informações esteja informadas
        if name is None or password is None:
            return mensagem("Informe todos os campos")

        if request.method == 'POST':
            # não salve a senha como um texto simples
            password_user = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
            sql = "INSERT INTO usuarios(username, email, password_user, professor) VALUES(%s, %s, %s, %s)"
            data = (name, email, password_user, professor)
            cursor.execute(sql, data)
            conexao.commit()

            return mensagem("Usuário criado com sucesso")
        else:
            return mensagem("Informe o método da requisição para POST")
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


@app.route('/users')
def users():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


def user_email(email):
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", email)
        result = cursor.fetchone()
        return result
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()

def alunos():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE professor='0'")
        result = cursor.fetchall()
        return result
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


def mensagem(messagem="Error", status=200):
    resp = jsonify(messagem)
    resp.status_code = status

    return resp

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.route('/add-prova', methods=['POST'])
def add_prova():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor()

        json = request.json
        id_prova = int(json['prova'])
        email = json['email']
        perguntas = json['perguntas']

        # Validado se foi informando email
        if email is None:
            return mensagem("Email não informando")

        usuario_cadastrado = user_email(email)

        # validado se é processor pra cadastrar
        if usuario_cadastrado["professor"] is False:
            return mensagem("Você não é professor pra cadastrar prova")

        # Validado informações
        if perguntas is None:
            return mensagem("Preencha corretamente as perguntas")

        if id_prova is None:
            return mensagem("Informe id da prova")

        if request.method == 'POST':
            id_professor = int(usuario_cadastrado["id"])

            sql_prova = "INSERT INTO provas(id, id_professor) VALUES(%s, %s)"
            data_prova = (id_prova, id_professor)
            cursor.execute(sql_prova, data_prova)

            nota_prova = 0

            for keyPergunta, rowPergunta in perguntas.items():
                peso = rowPergunta["peso-pergunta"]

                if int(peso) == peso:
                    return mensagem("O peso da questão deve ser um numero inteiro")

                if int(peso) < 0:
                    return mensagem("O peso da questão deve  ser positivo")

                nota_prova += int(peso)

            if nota_prova < 0 or nota_prova > 10:
                return mensagem("o valor da prova deve ser maior que 0 e menor e igual a 10")

            for keyPergunta, rowPergunta in perguntas.items():
                pergunta = rowPergunta["pergunta"]
                peso_pergunta = rowPergunta["peso-pergunta"]
                resposta_correta = rowPergunta["resposta-correta"]

                if pergunta is None or peso_pergunta is None or resposta_correta is None:
                    return mensagem("Preencha todos os Campos")

                sql_perguntas = "INSERT INTO provas_perguntas(id, id_prova, pergunta, peso_pergunta, resposta_correta) VALUES(%s, %s, %s, %s, %s)"
                data_perguntas = (keyPergunta, id_prova, pergunta, peso_pergunta, resposta_correta)
                cursor.execute(sql_perguntas, data_perguntas)

                for keyResposta, rowResposta in rowPergunta["respostas"].items():
                    sql_respostas = "INSERT INTO provas_respostas(id_pergunta, numero_reposta, resposta) VALUES(%s, %s, %s)"
                    data_respostas = (keyPergunta, keyResposta, rowResposta)
                    cursor.execute(sql_respostas, data_respostas)

            conexao.commit()

            return mensagem("Prova Cadastrada com Sucesso")
        else:
            return mensagem("Informe o método da requisição para POST")
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


@app.route('/prova-aluno', methods=['POST'])
def prova_aluno():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor()

        json = request.json
        id_prova = json['prova']
        email = json['email']
        respostas = json['respostas']

        if email is None:
            return mensagem("Email não informando")

        usuario_cadastrado = user_email(email)

        # validado se é processor pra cadastrar
        if usuario_cadastrado["professor"]:
            return mensagem("Você não é aluno para fazer a prova")

        if respostas is None:
            return mensagem("Preencha corretamente as respostas")

        provas_antigas = get_provas_alunos(id_prova)

        array_antiga = {}

        if len(provas_antigas) > 0:
            for antiga in provas_antigas:
                array_antiga[antiga["id_aluno"]] = antiga["pergunta_prova"]
        else:
            array_antiga = None

        if request.method == 'POST':
            id_aluno = usuario_cadastrado["id"]

            for keyPergunta, keyResposta in respostas.items():
                if array_antiga is not None and array_antiga.get(id_aluno) == keyPergunta:
                    return mensagem("Você já fez a prova")

                sql_prova = "INSERT INTO provas_respostas_alunos(id_aluno, pergunta_prova, resposta_pergunta, id_prova) VALUES(%s, %s, %s, %s)"
                data_prova = (id_aluno, keyPergunta, keyResposta, id_prova)
                cursor.execute(sql_prova, data_prova)


            conexao.commit()

            cursor.close()
            conexao.close()

            atribuir_nota_aluno(id_aluno, id_prova, respostas)
            return mensagem("Prova salvo com sucesso")
        else:
            return not_found()
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)


def atribuir_nota_aluno(id_aluno, id_prova, respostas):
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor()

        respostas_prova = get_respostas_provas(id_prova)

        peso = {}
        resposta_correta = {}
        nota_prova = 0

        for pergunta in respostas_prova:
            peso[pergunta["id"]] = pergunta["peso_pergunta"]
            resposta_correta[pergunta["id"]] = pergunta["resposta_correta"]

        for key_pergunta, resposta_aluno in respostas.items():
            if resposta_correta.get(int(key_pergunta)) is not None and resposta_correta.get(int(key_pergunta)) == int(resposta_aluno):
                nota_prova += peso.get(int(key_pergunta))

        sql = "INSERT INTO notas_alunos(id_aluno, id_prova, nota) VALUES(%s, %s, %s)"
        data = (id_aluno, id_prova, nota_prova)

        cursor.execute(sql, data)
        conexao.commit()

        return mensagem("Nota cadastrada com Sucesso")
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


@app.route('/alunos-aprovados')
def alunos_aprovados():
    try:
        retorno_alunos = alunos()
        message = {}


        for rowAlunos in retorno_alunos:
            notas = get_notas(rowAlunos["id"])

            nota_final = 0
            nota_somada = 0

            for nota in notas:
                nota_somada += int(nota["nota"])

            nota_final = float(nota_somada / int(count_prova()))

            if nota_final > 7.0:
                message[rowAlunos['id']] = {
                    'Aluno': rowAlunos['username'],
                    'message': 'Foi Aprovado, com a nota final de ' + str(nota_final)
                }
            else:
                message[rowAlunos['id']] = {
                    'Aluno': rowAlunos['username'],
                    'message': 'Foi Reprovados, com a nota final de ' + str(nota_final)
                }

        resp = jsonify({'Lista de Alunos Aprovados/Reprovados': message})
        resp.status_code = 200

        return resp

    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)


def count_prova():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM provas")
        result = cursor.fetchall()

        return len(result)
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


def get_respostas_provas(id_prova):
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM provas_perguntas WHERE id_prova=%s", id_prova)

        result = cursor.fetchall()
        return result
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


def get_provas_alunos(id_prova):
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM provas_respostas_alunos WHERE id_prova=%s", id_prova)

        result = cursor.fetchall()
        return result
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


def get_notas(id):
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM notas_alunos WHERE id_aluno=%s", id)

        result = cursor.fetchall()
        return result
    except Exception as e:
        return mensagem("Error: {0}".format(str(e)), 400)
    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    app.run()
