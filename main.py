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


if __name__ == "__main__":
    app.run()
