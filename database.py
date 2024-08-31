from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column('id', db.Integer, primary_key = True)
    nome = db.Column('nome', db.String(100), nullable=False)
    email = db.Column('email', db.String(100), unique=True, nullable=False)
    senha = db.Column('senha', db.String(20), nullable=False)
    despesas = db.Relationship('despesas', backref='usuario', lazy=True)

    def __init__(self, email, nome, senha):
        self.email = email
        self.nome = nome
        self.senha = senha

class despesas(db.Model):
    __tablename__ = 'despesas'
    id = db.Column('idDespesa', db.Integer, primary_key = True)
    nome_despesa = db.Column('nomeDespesa', db.String(100), nullable=False)
    tipo = db.Column('tipo', db.String(50), nullable=False)
    valor = db.Column('valor', db.Numeric(10,2), nullable=False)
    dia = db.Column('dia', db.Integer, nullable=False)
    mes = db.Column('mes', db.String(20), nullable=False)
    ano = db.Column('ano', db.Integer, nullable=False)
    usuario_id = db.Column('idUsuario', db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __init__(self, nome_despesa, tipo, valor, usuario_id, dia, mes, ano):
        self.nome_despesa = nome_despesa
        self.tipo = tipo
        self.valor = valor
        self.usuario_id = usuario_id
        self.dia = dia
        self.mes = mes
        self.ano = ano