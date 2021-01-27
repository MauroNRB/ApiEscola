# AlfSchool

# Requisitos:
 - Python 3.9.1
 - MariaDB: 10.4.17

# Configuração do MariaDB:
 - Use o usuário com Root.
 - Não coloque senha.
 - Use o host como "localhost".
 - Faça um banco chamado "alf_school"
 - Execultar esses comandos MariaDB.

Oberservação: Caso desejar usar outras configurações de banco, altere no arquivo db_config.py para as mesma usadas. 

CREATE TABLE usuarios
(
	id INTEGER NOT NULL AUTO_INCREMENT,
	username VARCHAR(75) NOT NULL,
	email VARCHAR(100) NOT NULL, 
	password_user CHAR(32) NOT NULL,
	professor TINYINT(1), 
	
	PRIMARY KEY (id)
);
CREATE TABLE provas
(
	id INTEGER NOT NULL,
	id_professor INTEGER NOT NULL
);
CREATE TABLE provas_perguntas
(
	id INTEGER NOT NULL,
	id_prova INTEGER NOT NULL,
	pergunta VARCHAR(75) NOT NULL,
	peso_pergunta INTEGER NOT NULL,
	resposta_correta INTEGER NOT NULL
);

CREATE TABLE provas_respostas
(
	id INTEGER NOT NULL AUTO_INCREMENT,
	id_pergunta INTEGER NOT NULL,
	numero_reposta INTEGER NOT NULL,
	resposta VARCHAR(75) NOT NULL,
	
	PRIMARY KEY (id)
);

CREATE TABLE provas_respostas_alunos
(
	id INTEGER NOT NULL AUTO_INCREMENT,
	id_aluno INTEGER NOT NULL,
	pergunta_prova INTEGER NOT NULL,
	resposta_pergunta INTEGER NOT NULL, 
   id_prova INTEGER NOT NULL,
	
	PRIMARY KEY (id), 
);
CREATE TABLE notas_alunos
(
	id INTEGER NOT NULL AUTO_INCREMENT,
	id_aluno INTEGER NOT NULL,
	id_prova INTEGER NOT NULL,
	nota INTEGER NOT NULL, 
	
	PRIMARY KEY (id), 
);

# Iniciando o Projeto:
 - Depois de instalado o Python e MariaDB, configurado o banco.
 - Vá com o terminal até onde está o projeto e execulte o seguinte comando "python main.py".

# Criado Usuário Novo:
 - Use o programa Postman.
 - Coloque na URL http://localhost:5000/add-user no modo POST.
 - Use o Body, no modo RAW com o tipo JSON.

Exemplo de JSON para Aluno:
{
	"username": "Pedro da Silva",
	"email": "pedro@aluno.com",
	"password": "123456",
    "professor": false
}

Exemplo de JSON para Professor:
{
	"username": "Carlos José",
	"email": "carlos@professor.com",
	"password": "123456",
    "professor": true
}

# Cadastrado Prova:
 - Use o programa Postman.
 - Coloque na URL http://localhost:5000/add-prova no modo POST.
 - Use o Body, no modo RAW com o tipo JSON.
 - Remova os comentarios

Exemplo de JSON para prova:
{
    "prova": "1", // Id da prova
    "email": "carlos@professor.com", // Email do professor
    "perguntas": {
        "1": { // A chave é o numero da questão da prova
            "pergunta": "Qual é a raiz de quadrada de 4?", // Pergunta
            "respostas": {
                "1": "2", // A chave é o numero da opção, e o valor é a resposta da opção
                "2": "1", // A chave é o numero da opção, e o valor é a resposta da opção
                "3": "0.5", // A chave é o numero da opção, e o valor é a resposta da opção
                "4": "4" // A chave é o numero da opção, e o valor é a resposta da opção
            },
            "resposta-correta": "1", // Qual opção é a resposta certa, então a chave da respostas
            "peso-pergunta": "5" // Peso da questão
        },
        "2": {
            "pergunta": "Quanto é 3x3?",
            "respostas": {
                "1": "6",
                "2": "3",
                "3": "9",
                "4": "12"
            },
            "resposta-correta": "3",
            "peso-pergunta": "5"
        }
    }
}

# Cadastrado as respostas da prova:
 - Use o programa Postman.
 - Coloque na URL http://localhost:5000/prova-aluno no modo POST.
 - Use o Body, no modo RAW com o tipo JSON.
 - Remova os comentarios

Exemplo de JSON de respostas da prova:
{
    "email": "pedro@aluno.com", // Id do aluno
    "prova": "1", // Id da prova
    "respostas": {
        "1": "2", // a chave é o numero da questão, o valor é a resposta da questão
        "2": "3" // a chave é o numero da questão, o valor é a resposta da questão
    }
}

# Pesquisado Alunos Aprovados e Reprovados:
 - Use o programa Postman.
 - Coloque na http://localhost:5000/alunos-aprovados no modo GET

# Caso queira ver Usuario cadastrados
 - Use o programa Postman.
 - Coloque na http://localhost:5000/users no modo GET