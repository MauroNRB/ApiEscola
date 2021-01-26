import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
import bcrypt


@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        json = request.json
        name = json['username']
        email = json['email']
        password = json['password']
        professor = json['professor']

        alunos = count_alunos()
        # validado se existe espaço na turma
        if len(alunos) > 100:
            resp = jsonify('Quantidade de Alunos Máximo Atingido')
            resp.status_code = 200

            return resp

        usuario_cadastrado = user_email(email)
        # validado se já existe usuario
        if usuario_cadastrado is not None:
            resp = jsonify('Email já cadastrado, tente outro')
            resp.status_code = 200

            return resp

        # validado que esteja cadastrado as informações
        if name and email and password and request.method == 'POST':
            # não salve a senha como um texto simples
            password_user = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
            sql = "INSERT INTO usuarios(username, email, password_user, professor) VALUES(%s, %s, %s, %s)"
            data = (name, email, password_user, professor)
            conexao = mysql.connect()
            cursor = conexao.cursor()
            cursor.execute(sql, data)
            conexao.commit()
            resp = jsonify('Usuário criado com Sucesso')
            resp.status_code = 200

            cursor.close()
            conexao.close()

            return resp
        else:
            return not_found()
    except Exception as e:
        print(e)


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
        print(e)
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
        print(e)
    finally:
        cursor.close()
        conexao.close()

def count_alunos():
    try:
        conexao = mysql.connect()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE professor='0'")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conexao.close()


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
        json = request.json
        id_prova = json['id-prova']
        email = json['email']
        perguntas = json['perguntas']

        usuario_cadastrado = user_email(email)
        # validado se é processor pra cadastrar
        if usuario_cadastrado["professor"] is False:
            resp = jsonify('Você não é professor pra cadastrar prova')
            resp.status_code = 200

            return resp

        # validado que esteja cadastrado as informações
        if perguntas and request.method == 'POST':
            id_professor = usuario_cadastrado["id"]

            conexao = mysql.connect()
            cursor = conexao.cursor()

            sql_prova = "INSERT INTO provas(id, id_professor) VALUES(%s, %s)"
            data_prova = (id_prova, usuario_cadastrado["id"])
            cursor.execute(sql_prova, data_prova)

            for keyPergunta, rowPergunta in perguntas.items():
                pergunta = rowPergunta["pergunta"]
                peso_pergunta = rowPergunta["peso-pergunta"]
                resposta_correta = rowPergunta["resposta-correta"]

                sql_perguntas = "INSERT INTO provas_perguntas(id, id_prova, pergunta, peso_pergunta, resposta_correta) VALUES(%s, %s, %s, %s, %s)"
                data_perguntas = (keyPergunta, id_prova, pergunta, peso_pergunta, resposta_correta)
                cursor.execute(sql_perguntas, data_perguntas)

                for keyResposta, rowResposta in rowPergunta["respostas"].items():
                    sql_respostas = "INSERT INTO provas_respostas(id_gabarito, numero_reposta, resposta) VALUES(%s, %s, %s)"
                    data_respostas = (keyPergunta, keyResposta, rowResposta)
                    cursor.execute(sql_respostas, data_respostas)

            conexao.commit()
            resp = jsonify('Prova Cadastrada com Sucesso')
            resp.status_code = 200

            cursor.close()
            conexao.close()

            return resp
        else:
            return not_found()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run()
