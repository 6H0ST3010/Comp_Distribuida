#
# Importar as bibliotecas necessárias
from flask import Flask, redirect, send_file, request, render_template
import socket
import os
import logging
import json
import re

UPLOAD_FOLDER = '.\\static\\images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

vatRegEx = r"^[\w]{3,20}$"
passwordRegEx = r"^[\w]{3,7}$"

#
# Flask application object (app) no contexto do módulo Python currente
#
app = Flask(__name__)
app.url_map.strict_slashes = False

app.config[ 'TEMPLATES_AUTO_RELOAD' ] = True

app.config[ 'UPLOAD_FOLDER' ] = UPLOAD_FOLDER
#
# Ativar o nível de log para debug
#
logging.basicConfig( level=logging.DEBUG )

def allowed_file(filename):
    return '.' in filename and filename.rsplit( '.', 1 )[1].lower() in ALLOWED_EXTENSIONS

def send_socket_request(req_data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('data-service', 5000))
        s.sendall(json.dumps(req_data).encode('utf-8'))
        s.shutdown(socket.SHUT_WR)
        
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        s.close()
        
        resp_str = b''.join(chunks).decode('utf-8')
        if not resp_str:
            return None
        return json.loads(resp_str)
    except Exception as e:
        logging.error(f"Socket error: {e}")
        return None

#
# Função auxiliar para ler dados JSON (em formato utf-8) de um ficheiro
#
def loadData(fName):
    if "utilizadores" in fName:
        return send_socket_request({"action": "get_all_users"}) or []
    elif "dados" in fName:
        return send_socket_request({"action": "get_all_lojas"}) or {}
    return {}


#
# Adicionar o tratamento das rotas / e /static e /static/
#
# Redirecionar para a página de index (/static/index.html)
#
@app.route('/')
@app.route('/static')
def getRoot():
    logging.debug( f"Route / called..." )
    return redirect( "/static/index.html", code=302 )


@app.route('/favicon.ico')
def getFavicon():
    logging.debug( f"Route /favicon.ico called..." )
    return send_file( "./static/favicon.ico", as_attachment=True, max_age=1 )



@app.route('/Registo')
def Registo():
    logging.debug( f"Route /Registo called..." )
    return render_template( 'Registo.html' )

@app.route('/doRegisto', methods = ['POST'])
def doRegisto():
    logging.debug( f"Route /doRegisto called..." )
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('passwordName')
    confirm_password = request.form.get('confirmPassword')
    
    usernameCheck = re.search(vatRegEx, username)
    passwordCheck = re.search(passwordRegEx, password)
    
    if not username or not email or not password or not confirm_password:
         return render_template( 'dadosInvalidos.html', errorMessage = "Todos os dados são obrigatórios", redirectURL ="/Registo" )
    if not usernameCheck or not passwordCheck:
         return render_template( 'dadosInvalidos.html', errorMessage = "Password inválida", redirectURL ="/Registo" )
    if confirm_password != password:
         return render_template( 'dadosInvalidos.html', errorMessage = "A confirmação tem de ser igual à password", redirectURL ="/Registo" )
    
    users = []
    users = loadData('./private/utilizadores.json')
        
    for u in users:
        if u['user'] == username:
            return render_template( 'dadosInvalidos.html', errorMessage = "Username já utilizado", redirectURL ="/Registo" )
        if u['email'] == email:
            return render_template( 'dadosInvalidos.html', errorMessage = "Email já utilizado", redirectURL ="/Registo" )
    
    novo_user = {
        "user": username,
        "password": password,
        "email": email,
        "estado": "inativo"
    }
    send_socket_request({"action": "append_user", "data": novo_user})
    
    return redirect( "/static/index.html", code=302 )



@app.route('/Login')
def Login():
    logging.debug( f"Route /Login called..." )
    return render_template( 'Login.html' )

@app.route('/doLogin', methods = ['POST'])
def doLogin():
    logging.debug( f"Route /doLogin called..." )
    
    username = request.form.get('vatName')
    password = request.form.get('passwordName')
    
    user_data = send_socket_request({"action": "get_user", "username": username})
    if user_data and user_data.get('password') == password:
        if user_data.get('estado') != 'ativo':
            user_data['estado'] = 'ativo'
            send_socket_request({"action": "update_user", "username": username, "data": user_data})
        return redirect( f'/showLojas?username={username}', code=302 )
        
    return render_template( 'dadosInvalidos.html', errorMessage = "Dados inválidos ou incorretos", redirectURL ="/Login" )


@app.route('/Logout')
def Logout():
    logging.debug( f"Route /Logout called..." )
    
    username = request.args.get('username', '')
    if username:
        user_data = send_socket_request({"action": "get_user", "username": username})
        if user_data:
            user_data['estado'] = 'inativo'
            send_socket_request({"action": "update_user", "username": username, "data": user_data})
    
    return redirect('/', code=302 )


@app.route('/showLojas')
def showLojas():
    logging.debug(f"Route /showLojas called...")
    
    username = request.args.get('username', '')
    categoria_selecionada = request.args.get('categoria', '').strip()
    nome_procurado = request.args.get('nome', '').strip()
    
    # Página atual 
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    lojas_por_pagina = 5
    
    # Ler base de dados
    db = loadData('./private/dados.json')
    lojas = db.get('lojas', []) if isinstance(db, dict) else db
    
    # Filtrar por categoria
    if categoria_selecionada:
        lojas = [loja for loja in lojas if loja.get('categoria', '') == categoria_selecionada]
    
    # Filtrar por nome
    if nome_procurado:
        lojas = [loja for loja in lojas if nome_procurado.lower() in loja.get('nome', '').lower()]
    
    # Paginação da tabela
    total_lojas = len(lojas)
    start = (page - 1) * lojas_por_pagina
    end = start + lojas_por_pagina
    lojas_pagina = lojas[start:end]
    
    total_paginas = (total_lojas + lojas_por_pagina - 1) // lojas_por_pagina
    
    # Categorias
    categorias_set = set()
    for loja in db.get('lojas', []):
        cat = loja.get('categoria', '')
        if cat:
            categorias_set.add(cat)
    categorias = sorted(list(categorias_set))
    
    lojas_json = json.dumps(lojas_pagina)
    
    return render_template('Lojas.html', lojas=lojas_pagina, lojas_json=lojas_json, categorias=categorias, categoria_selecionada=categoria_selecionada, nome_procurado=nome_procurado, username=username, page=page, total_paginas=total_paginas)

@app.route('/manageLojas')
def manageLojas():
    logging.debug( f"Route /manageLojas called..." )
    
    username = request.args.get('username', '')
    db = loadData('./private/dados.json')
    lojas = db.get('lojas',[])
    
    return render_template('manageLojas.html', lojas=lojas, username=username)



@app.route('/saveLoja', methods=['POST'])
def saveLoja():
    logging.debug( f"Route /saveLoja called..." )
    
    username = request.form.get('username', '')
    loja_id = request.form.get('loja_id')
    current_foto = request.form.get('current_foto', '')
    
    foto_file = current_foto
    
    file=request.files.get('foto')
    if file and file.filename != '' and allowed_file(file.filename):
        foto_file = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_file))
    
    loja_data = {
            'nome': request.form.get('nome'),
            "categoria": request.form.get('categoria'),
            "link": request.form.get('link'),
            "foto": foto_file,
            "latitude": float(request.form.get('latitude') or 0),
            "longitude": float(request.form.get('longitude') or 0),
            "imagens": [],
            "video": ""
        }
    
    if loja_id and loja_id != '':
        loja_id = int(loja_id)
        loja_atual = send_socket_request({"action": "get_loja", "id": loja_id})
        if loja_atual:
            loja_data['id'] = loja_id
            loja_data['imagens'] = loja_atual.get('imagens', [])
            loja_data['video'] = loja_atual.get('video', "")
            send_socket_request({"action": "update_loja", "id": loja_id, "data": loja_data})

    else:
        send_socket_request({"action": "append_loja", "data": loja_data})
    
    return redirect(f'./manageLojas?username={username}')
    
    
    
@app.route('/editLoja/<int:loja_id>', methods=['GET'])
def editLoja(loja_id):
    logging.debug( f"Route /editLoja called..." )
    
    username = request.args.get('username', '')
    db = loadData( './private/dados.json' )
    lojas = db.get('lojas', [])
    
    loja_data = None
    for loja in lojas:
        if loja.get('id') == loja_id:
            loja_data = loja
            break
    
    return render_template('manageLojas.html', lojas=lojas, loja_data=loja_data, username=username)


@app.route('/deleteLoja/<int:loja_id>', methods=['GET'])
def deleteLoja(loja_id):
    logging.debug( f"Route /deleteLoja called..." )
    
    username = request.args.get('username', '')
    
    send_socket_request({"action": "delete_loja", "id": loja_id})
    
    return redirect(f'/manageLojas?username={username}')

@app.route('/imagensLoja/<int:loja_id>')
def imagensLoja(loja_id):
    logging.debug(f"Route /imagensLoja called for loja_id={loja_id}")

    username = request.args.get('username', '')
    # Encontrar loja
    loja_data = send_socket_request({"action": "get_loja", "id": loja_id})
    
    if not loja_data:
        return render_template( 'dadosInvalidos.html', errorMessage = f"Loja com ID {loja_id} não encontrada.", redirectURL =f"/showLojas?username={username}" )

    return render_template('imagensLoja.html', username=username, loja=loja_data)

@app.route('/uploadImagens/<int:loja_id>', methods=['POST'])
def uploadImagens(loja_id):
    logging.debug(f"Route /uploadImagens called for loja_id={loja_id}")

    username = request.args.get('username', '')
    # Encontrar loja
    loja_data = send_socket_request({"action": "get_loja", "id": loja_id})
    if not loja_data:
        return render_template( 'dadosInvalidos.html', errorMessage = f"Loja com ID {loja_id} não encontrada.", redirectURL =f"/showLojas?username={username}" )

    # Garantir que exista a lista de imagens
    if 'imagens' not in loja_data:
        loja_data['imagens'] = []

    # Receber arquivos
    files = request.files.getlist('imagens')
    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            # Salvar no diretório
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Adicionar à lista de imagens da loja
            if filename not in loja_data['imagens']:
                loja_data['imagens'].append(filename)

    # Salvar no JSON
    send_socket_request({"action": "update_loja", "id": loja_id, "data": loja_data})

    return redirect(f'/imagensLoja/{loja_id}?username={username}')

@app.route('/uploadVideo/<int:loja_id>', methods=['POST'])
def uploadVideo(loja_id):
    logging.debug(f"Route /uploadVideo called for loja_id={loja_id}")

    username = request.args.get('username', '')
    # Encontrar loja
    loja_data = send_socket_request({"action": "get_loja", "id": loja_id})
    if not loja_data:
        return render_template( 'dadosInvalidos.html', errorMessage = f"Loja com ID {loja_id} não encontrada.", redirectURL =f"/showLojas?username={username}" )

    file = request.files.get('video')
    if file and file.filename != '' and file.filename.lower().endswith('.mp4'):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        loja_data['video'] = filename  # atualizar variável video

    send_socket_request({"action": "update_loja", "id": loja_id, "data": loja_data})
    return redirect(f'/imagensLoja/{loja_id}?username={username}')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)