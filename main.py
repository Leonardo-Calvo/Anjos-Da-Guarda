from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import sqlite3
from sqlite3 import Error
from datetime import date, datetime

app = Flask(__name__)

# Configuração da pasta de upload
app.config['UPLOAD_FOLDER'] = 'static/imagens/uploads'
                   
@app.route("/")  
def pagina_principal():
    return render_template('home.html')

@app.route('/registrar', methods=['GET', 'POST'])
def pagina_registrar():
    
    if request.method == 'POST':
        nome_crianca = request.form['nome_crianca']
        idade = request.form['idade']
        local_desaparecimento = request.form['local_desaparecimento']
        data_desaparecimento = request.form['data_desaparecimento']
        data_desaparecimento = datetime.strptime(data_desaparecimento, "%Y-%m-%d").strftime("%d/%m/%Y")
        descricao = request.form['descricao']
        nome_responsavel = request.form['nome_responsavel']
        contato = request.form['contato']
        data_registro = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        



        foto = request.files['foto']
        

        if foto.filename != '':
            nome_arquivo = secure_filename(foto.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
            foto.save(caminho)
        else:
            nome_arquivo = None

        # Inserir no banco
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO criancas (nome_crianca, idade, local_desaparecimento,
              data_desaparecimento, descricao, nome_responsavel, contato, data_registro, foto, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome_crianca, idade, local_desaparecimento, data_desaparecimento, descricao, nome_responsavel, contato,data_registro, nome_arquivo, 'analise'))
        conn.commit()
        conn.close()

        return redirect(url_for('pagina_aguardar_analise'))

    return render_template('registrar.html')

@app.route('/analise')
def pagina_aguardar_analise():

    return render_template('aguardar_analise.html')

@app.route('/desaparecidos')
def pagina_desaparecidos():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM criancas WHERE status = 'aprovado'")
    lista = cursor.fetchall()
    conn.close()

    return render_template('desaparecidos.html', criancas=lista)

@app.route("/alertas")
def pagina_alertas():
    return render_template('alertas.html')

@app.route("/orientaçoes")
def pagina_orientaçoes():
    return render_template('orientaçoes.html')

@app.route("/canais_de_apoio")
def pagina_apoio():
    return render_template('apoio.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# ==============Inicio De Administradores========================== #

app.secret_key = 'Chave_Secreta=ha@e34$raFV@??.,s'  # Protege as sessões

@app.route("/login", methods=['GET', 'POST'])
def pagina_login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == 'admin' and senha == 'admin123@@':
            session['admin_logado'] = True 
            return redirect(url_for('pagina_admin'))
        
        else:
            return "Senha Incorreta", 401
    
    return render_template('login.html')
#==========================================================#

@app.route("/admin", methods=['GET', 'POST'])
def pagina_admin():
    if not session.get('admin_logado'):
        return redirect(url_for('pagina_login'))
    else:
        return render_template('painel_admin.html')
    
#==========================================================#

@app.route('/logout')
def logout():
    session.pop('admin_logado', None)
    return redirect(url_for('pagina_principal'))

#==========================================================#

@app.route("/admin/aprovacao", methods=['GET', 'POST'])
def pagina_admin_aprovacao():
    if not session.get('admin_logado'):
        return redirect(url_for('pagina_login'))

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        id_crianca = request.form.get('id_crianca')
        acao = request.form.get('acao')

        if acao == 'aprovar':
            cursor.execute("UPDATE criancas SET status = ? WHERE id = ?", ('aprovado', id_crianca))
        elif acao == 'rejeitar':
            cursor.execute("DELETE FROM criancas WHERE id = ?", (id_crianca,))

        conn.commit()

    # Buscar todos os registros em análise (status = 'analise')
    cursor.execute("""
        SELECT id, nome_crianca, idade, local_desaparecimento, data_desaparecimento, descricao,
               nome_responsavel, contato, data_registro, foto
        FROM criancas WHERE status = ?
    """, ('analise',))
    criancas = cursor.fetchall()
    conn.close()

    return render_template('aprovacao_admin.html', criancas=criancas)


#==========================================================#

@app.route("/admin/registrados", methods=['GET', 'POST'])
def pagina_admin_registrados():
    if not session.get('admin_logado'):
        return redirect(url_for('pagina_login'))

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        id_crianca = request.form.get('id_crianca')
        cursor.execute("DELETE FROM criancas WHERE id = ?", (id_crianca,))
        conn.commit()

    cursor.execute("SELECT * FROM criancas WHERE status = 'aprovado'")
    criancas = cursor.fetchall()
    conn.close()

    return render_template('registrados_admin.html', criancas=criancas)


    
# ==============Fim de Administradores========================== #



app.run(debug= True)