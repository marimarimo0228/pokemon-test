from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# typesテーブル: ポケモンのタイプ情報を管理
class Type(db.Model):
    __tablename__ = 'types'
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(30), nullable=False, unique=True)

# pokemon_masterテーブル: 全ポケモンの基本情報を管理
class PokemonMaster(db.Model):
    __tablename__ = 'pokemon_master'
    pokemon_id = db.Column(db.Integer, primary_key=True)
    pokemon_name = db.Column(db.String(50), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'), nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    
    # タイプ名を取得するためのリレーション
    type = db.relationship('Type')

# user_pokemonテーブル: ユーザーが登録した手持ちポケモン
class UserPokemon(db.Model):
    __tablename__ = 'user_pokemon'
    user_pokemon_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 今回は固定値1を使用
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon_master.pokemon_id'), nullable=False)
    
    pokemon = db.relationship('PokemonMaster')

# type_effectivenessテーブル: タイプ間の相性倍率を管理
class TypeEffectiveness(db.Model):
    __tablename__ = 'type_effectiveness'
    attack_type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'), primary_key=True)
    defense_type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'), primary_key=True)
    effectiveness = db.Column(db.Float, nullable=False)