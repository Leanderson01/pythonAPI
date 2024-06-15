from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

# pegar a URL do banco de dados do arquivo de ambiente
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')  # Corrigido para DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativando o track modifications
db = SQLAlchemy(app)

# criar a tabela de itens
class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())

    def json(self):
        return {'id': self.id, 'name': self.name, 'amount': self.amount, 'image': self.image, 'date': self.date}

# inicializar o banco de dados
db.create_all()

# criar uma rota teste
@app.route('/teste', methods=['GET'])
def teste():
    return make_response(jsonify({'message': 'Hello World'}), 200)

# criar uma rota para adicionar um item
@app.route('/item', methods=['POST'])
def add_item():
    try:
        data = request.get_json()
        if 'name' not in data or 'amount' not in data or 'image' not in data:
            raise ValueError('Campos obrigatórios não fornecidos: name, amount, image')
        
        new_item = Item(
            name=data['name'], 
            amount=data['amount'], 
            image=data['image']
            # Não incluir date aqui se não for fornecido no JSON
        )
        db.session.add(new_item)
        db.session.commit()
        return make_response(jsonify({'message': 'Item cadastrado com sucesso!'}), 200)
    except ValueError as e:
        return make_response(jsonify({'message': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'message': 'Erro ao cadastrar o item: ' + str(e)}), 400)


# criar uma rota para listar todos os itens
@app.route('/item', methods=['GET'])
def get_all_items():
    try:
        items = Item.query.all()
        return make_response(jsonify([item.json() for item in items]), 200)
    except:
        return make_response(jsonify({'message': 'Erro ao buscar os itens!'}), 400)

# criar uma rota para buscar um item pelo id
@app.route('/item/<int:id>', methods=['GET'])
def get_item_by_id(id):
    try:
        item = Item.query.filter_by(id=id).first()
        if item:
            return make_response(jsonify(item.json()), 200)
        else:
            return make_response(jsonify({'message': 'Item não encontrado!'}), 404)
    except:
        return make_response(jsonify({'message': 'Item não encontrado!'}), 400)

# criar uma rota para atualizar um item pelo id
@app.route('/item/<int:id>', methods=['PUT'])
def update_item_by_id(id):
    try:
        item = Item.query.filter_by(id=id).first()
        if item:
            data = request.get_json()
            item.name = data['name']
            item.amount = data['amount']
            item.image = data['image']
            db.session.commit()
            return make_response(jsonify({'message': 'Item atualizado com sucesso!'}), 200)
        else:
            return make_response(jsonify({'message': 'Item não encontrado!'}), 404)
    except:
        return make_response(jsonify({'message': 'Erro ao atualizar o item!'}), 400)

# criar uma rota para deletar um item pelo id
@app.route('/item/<int:id>', methods=['DELETE'])
def delete_item_by_id(id):
    try:
        item = Item.query.filter_by(id=id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return make_response(jsonify({'message': 'Item deletado com sucesso!'}), 200)
        else:
            return make_response(jsonify({'message': 'Item não encontrado!'}), 404)
    except:
        return make_response(jsonify({'message': 'Erro ao deletar o item!'}), 400)
