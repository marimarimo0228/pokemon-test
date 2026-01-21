from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 1. タイプマスタ（例：1=ノーマル, 2=ほのお）
class Type(db.Model):
    __tablename__ = 'types'
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(30), unique=True, nullable=False)

# 2. ポケモン図鑑（マスタデータ）
class PokemonMaster(db.Model):
    __tablename__ = 'pokemon_master'
    pokemon_id = db.Column(db.Integer, primary_key=True)
    pokemon_name = db.Column(db.String(50), nullable=False)
    
    # タイプID（外部キー）
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'), nullable=False)
    
    # タイプ名を取得するためのリレーション設定
    type = db.relationship('Type', backref='pokemons')
    
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    speed = db.Column(db.Integer)

# 3. ユーザーの手持ちポケモン（CRUD操作対象）
class UserPokemon(db.Model):
    __tablename__ = 'user_pokemon'
    user_pokemon_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1) # 簡易的にユーザーIDは1固定
    
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon_master.pokemon_id'))
    memo = db.Column(db.String(200)) # 更新機能（Update）用のメモ欄

    # ポケモンの詳細情報を参照するための設定
    pokemon = db.relationship('PokemonMaster')

# 4. タイプ相性表
class TypeEffectiveness(db.Model):
    __tablename__ = 'type_effectiveness'
    id = db.Column(db.Integer, primary_key=True)
    attack_type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'))
    defense_type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'))
    effectiveness = db.Column(db.Float)

    # 攻撃・防御それぞれのタイプ情報を参照するための設定
    attack_type = db.relationship('Type', foreign_keys=[attack_type_id])
    defense_type = db.relationship('Type', foreign_keys=[defense_type_id])
