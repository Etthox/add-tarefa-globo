import os
from flask import Flask, json, jsonify, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
import datetime
import requests
from sqlalchemy.sql import func
from urllib.parse import quote  
import pandas as pd
import pyodbc
import psycopg2 as pg

import sys
from io import BytesIO



#PARAMETROS DE CONEXÃO AO BANCO
server = '...'
database = '...'
username ='...'
password = '...'

#configurações para insert/update
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "'...'"  % quote(password)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "'...'"
db = SQLAlchemy(app)


def getToken():
    url = f'...'
    header = {
        'Content-Type': "application/json",
    }
    payload = {
        "cpf": '...',
        "password": '...'
    }   
    res = requests.post(url, data = json.dumps(payload), headers = header)
    return json.loads(res.content)["authToken"]

def writeLog(logMessage):
    data_formatada = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00.000Z") 

    logText = f"""{data_formatada} - {logMessage}""" 

    with open(os.getcwd() + '\\log.txt', 'a') as f:
        f.write('\n' + logText)

#PAGINA DE CRIAÇÃO DO gerenciamento de tarefa globo
@app.route('/add_globo/<string:id>', methods=['GET','POST'])
def add_chamado_globo(id):
    try:       
        if request.method =='GET':      
            return render_template("add_chamado_globo.html", id = id)
        if request.method =='POST':
            data = request.json
            data_id = data['data_id']  
            limpeza = data['limpeza']
            obs = data['obs']
            # Formatando para o formato desejado
            data_formatada = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            token = f"Bearer {getToken()}"
            header = {
                'Content-Type': "application/json",
                'Authorization': token,
            }     
            url = '...'       
            payload = {
                "rotinaId": f"""{data_id}""",            
                "data": f"""{data_formatada}""",
                "descricao": f"""Solicitação: {limpeza} \nObservação: {obs}"""
            }
            response = requests.post(url, json=payload, headers=header)
            writeLog(f'rotina: {data_id} - tarefa criada para data {data_formatada}')  
            return jsonify({'message': 'Tarefa adicionada com sucesso!'})
        return response.text.replace('"','')
    except Exception as e:
        writeLog("Erro: " + e.args[0] + " - Rotina: " + id)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        writeLog(f'Add task error {e}: {exc_type, fname, exc_tb.tb_lineno}')       
    return render_template("add_chamado_globo.html", id = id)



@app.route('/')
def inic():
    #db.create_all() 
    return 'hello'

if __name__ == "__main__":
    #descomentar a linha de baixo quando precisar criar uma nova tabela no banco ou recriar as existentes
    #db.create_all()
    app.run(host="0.0.0.0", port=5050)