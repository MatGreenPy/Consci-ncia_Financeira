from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy import func, distinct
import webview

#MÓDULOS
from functionsSecundary import despesasGrafico
from database import usuarios, despesas, db

app = Flask(__name__)
app.debug=True

#window = webview.create_window('Financeiro', app)
app.secret_key = 'financeiro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financeiro.sqlite3'

#INICIALIZAÇÃO DO BANCO DE DADOS REFERENCIANDO A APLICAÇÃO
db.init_app(app)

#CRIAÇÃO DAS TABELAS, ANTES DE QUALQUER REQUEST.
@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

#RECEBE OS DADOS DE LOGIN ATRAVÉS DO FORMULÁRIO, CASO SEJAM VALÍDOS, SERÃO SALVOS NA 'SESSION'
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')      
        usuario = usuarios.query.filter_by(email=email).first()
        if usuario:
            if usuario.senha == senha:
                if len(senha) <= 20:
                    session['email'] = email
                    session['nome'] = usuario.nome
                    session['id_usuario'] = usuario.id
                    return redirect(url_for('home'))
                else:
                    pass
            else:
                flash('Erro: Senha incorreta', 'danger')
        else:
            flash('Erro: Este email não está vinculado a nenhuma conta', 'danger')
    return render_template('login.html')

#CARREGA A PÁGINA INICIAL APÓS O USUÁRIO REALIZAR SEU LOGIN
@app.route('/home')
def home():
    id_usuario = session.get('id_usuario')
    nome_usuario = session.get('nome')

    if not id_usuario:
        flash('Usuário não logado', 'danger')
        return redirect(url_for('login'))
    
    return render_template('home.html', nome_usuario=nome_usuario, id_usuario=id_usuario)

#CADASTRA O USUÁRIO CASO OS DADOS RESPEITEM OS PARAMETROS DECLARADOS, SE SIM, SERÃO SALVOS NA 'SESSION' E O USUÁRIO SERÁ REDIRECIONADO PARA A PÁGINA HOME
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    emailValidado = False
    senhaValidada = False

    if request.method == 'POST':
        session.permanent = True
        email = request.form.get('email')
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if usuarios.query.filter_by(email=email).first():
            flash('Erro: Este email já está vinculado em outra conta', 'danger')
        else:
            emailValidado = True

        if len(senha) > 20:
            flash('Erro: A sua senha não pode conter mais de 20 caracteres', 'info')            
        else:
            senhaValidada = True

        if emailValidado and senhaValidada:
            novo_usuario = usuarios(nome=nome, email=email, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()
            session['email'] = email
            session['nome'] = nome
            session['id_usuario'] = novo_usuario.id
            return redirect(url_for('home'))
    return render_template('cadastro.html')

#LOG-OUT DO USUÁRIO
@app.route('/sair')
def sair():
    session.pop('nome', None)
    session.pop('email', None)
    flash('Você saiu da sua conta', 'info')
    return redirect(url_for('login'))

#LISTAGEM DE DESPESAS DE ACORDO COM OS FILTROS ESCOLHIDOS PELO USUÁRIO
@app.route('/despesas', methods=['GET', 'POST'])
def listaDespesas():
    id_usuario = session.get('id_usuario')
    nome_usuario = session.get('nome')

    if not id_usuario:
        flash('Usuário não logado', 'danger')
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 5
    grafico = None
    dia_filtrar = request.args.get('diaFiltrarSelect', '')
    mes_filtrar = request.args.get('mesFiltrarSelect', '')
    ano_filtrar = request.args.get('anoFiltrarSelect', '')
    aviso_filtro = ''
    total_ano = None
    total_espec = None
    total_mes = None
    anos_usuario = db.session.query(distinct(despesas.ano)).filter_by(usuario_id=id_usuario).all()
    anos_usuario = [ano[0] for ano in anos_usuario]

    filtros = [despesas.usuario_id == id_usuario]

    #RECEBE OS VALORES DAS 3 OPÇÕES DE FILTRO

    if request.method == 'POST':
        dia_filtrar = request.form.get('diaFiltrarSelect', '')
        mes_filtrar = request.form.get('mesFiltrarSelect', '')
        ano_filtrar = request.form.get('anoFiltrarSelect', '')
    
    #CASO O USUÁRIO TENHA SELECIONADO O FILTRO, SELE SERÁ ADICIONADO A LISTA 'FILTROS'

    if dia_filtrar and dia_filtrar != '':
        filtros.append(despesas.dia == int(dia_filtrar))
    if mes_filtrar and mes_filtrar != '':
        filtros.append(despesas.mes == mes_filtrar)
    if ano_filtrar and ano_filtrar != '':
        filtros.append(despesas.ano == int(ano_filtrar))

    #PAGINAÇÃO DAS DESPESAS

    listar_despesas = db.session.query(despesas).filter(*filtros)
    listar_despesas_pag = listar_despesas.paginate(page=page, per_page=per_page)

    if listar_despesas_pag.items:
        #CASO APENAS O FILTRO DE DIA NÃO TENHA SIDO SELECIONADO, O FILTRO SERÁ DE UM MÊS E ANO
        if dia_filtrar == '' and mes_filtrar != '' and ano_filtrar != '':
            total_mes = db.session.query(func.sum(despesas.valor)).filter(despesas.usuario_id == id_usuario, despesas.mes == mes_filtrar, despesas.ano == int(ano_filtrar)).scalar()
            busca = db.session.query(despesas.tipo, func.sum(despesas.valor)).filter_by(usuario_id=id_usuario, mes=mes_filtrar).group_by(despesas.tipo).all()
            grafico = despesasGrafico(busca, dia_filtrar, mes_filtrar, ano_filtrar, id_usuario)

        #CASO TODOS OS FILTROS TENHAM SIDO SEELCIONADOS, O FILTRO SERÁ DE DIA, MÊS E ANO
        elif dia_filtrar != '' and mes_filtrar != '' and ano_filtrar != '':
            total_espec = db.session.query(func.sum(despesas.valor)).filter(despesas.usuario_id == id_usuario, despesas.dia == dia_filtrar, despesas.mes == mes_filtrar, despesas.ano == int(ano_filtrar)).scalar()
            busca = db.session.query(despesas.tipo, func.sum(despesas.valor)).filter_by(usuario_id=id_usuario, dia=dia_filtrar, mes=mes_filtrar, ano=ano_filtrar).group_by(despesas.tipo).all()
            grafico = despesasGrafico(busca, dia_filtrar, mes_filtrar, ano_filtrar, id_usuario)

        #CASO APENAS O FILTRO DE ANO TENHA SIDO SELECIONADO, O FILTRO SERÁ APENAS PELO ANO
        elif ano_filtrar != '' and dia_filtrar == '' and mes_filtrar == '':
            total_ano = db.session.query(func.sum(despesas.valor)).filter(despesas.usuario_id == id_usuario, despesas.ano == int(ano_filtrar)).scalar()
            busca = db.session.query(despesas.tipo, func.sum(despesas.valor)).filter_by(usuario_id=id_usuario, ano=ano_filtrar).group_by(despesas.tipo).all()
            grafico = despesasGrafico(busca, dia_filtrar, mes_filtrar, ano_filtrar, id_usuario)
    else:
        #CASO NENHUMA DESPESAS FOI ENCONTRADA, O SEGUINTE AVISO SERÁ RETORNADO:
        aviso_filtro = f'Nenhuma despesa encontrada com os filtros: Dia = {dia_filtrar}, Mes = {mes_filtrar}, Ano = {ano_filtrar}'

    return render_template('despesas.html', 
                           despesas=listar_despesas_pag, 
                           total_mes=total_mes, 
                           total_espec=total_espec, 
                           total_ano=total_ano, 
                           dia_filtrar=dia_filtrar, 
                           mes_filtrar=mes_filtrar, 
                           ano_filtrar=ano_filtrar, 
                           anos_usuario=anos_usuario, 
                           nome_usuario=nome_usuario, 
                           aviso_filtro=aviso_filtro,
                           grafico=grafico,
                           id_usuario=id_usuario)

#EXCLUÍ O USUÁRIO DA SESSÃO ATUAL, ATRAVÉS DO SEU ID NA ROTA
@app.route('/home/excluirUsuario/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    if 'id_usuario' not in session or session['id_usuario'] != id:
        return jsonify({'message': 'Não autorizado.'}), 403
    else:
        try:
            despesas_usuario = despesas.query.filter_by(usuario_id=id).all()
            for despesa in despesas_usuario:
                db.session.delete(despesa)
            usuario = usuarios.query.get(id)
            if usuario:
                db.session.delete(usuario)
                db.session.commit()
                return jsonify({'message': 'Usuário excluído com sucesso'}), 200
            else:
                return jsonify({'message': 'Usuário não encontrado.'}), 404
        except Exception as e:
            db.session.rollback()
            print(f'Erro: {e}')
            return jsonify({'message': 'Erro ao excluir usuário.'}), 500

#EXCLUÍ A DESPESA, ATRAVÉS DE SEU ID NA ROTA
@app.route('/despesas/excluir/<int:id>', methods=['DELETE'])
def excluir_despesa(id):
    despesa = despesas.query.get(id)
    if despesa is None:
        return jsonify({"message": "Despesa não encontrada"}), 404
    try:
        db.session.delete(despesa)
        db.session.commit()
        return jsonify({"message": "Despesa excluída com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir despesa", "error": str(e)}), 500

#ADICIONA A DESPESA NO BANCO DE DADOS, RECEBENDO OS VALORES DO FORMULÁRIO.
@app.route('/despesas/adicionar', methods=['GET', 'POST'])
def despesasAdicionar():
    id_usuario = session.get('id_usuario')
    if not id_usuario:
        flash('Usuário não logado', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        tipo = request.form.get('tipo')
        valor = request.form.get('valor')
        dia = request.form.get('dia')
        mes = request.form.get('mes')
        ano = request.form.get('ano')

        if nome and tipo and valor and dia and mes and ano:
            try:
                valor = valor.replace(',', '.')
                nova_despesa = despesas(nome_despesa=nome, tipo=tipo, valor=float(valor), usuario_id=id_usuario, dia=int(dia), mes=mes, ano=int(ano))
                db.session.add(nova_despesa)
                db.session.commit()
                return redirect(url_for('listaDespesas'))
            except ValueError:
                flash('Valor inválido para despesa', 'danger')
            except Exception as e:
                flash(f'Erro ao adicionar despesa: {str(e)}', 'danger')
    return render_template('adicionarDespesa.html')

if __name__ == '__main__':
    app.run()
        #webview.start()
    
