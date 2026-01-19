from flask import Flask, render_template, request, redirect, url_for
from models import db, PokemonMaster, TypeEffectiveness, UserPokemon

app = Flask(__name__)
# 既存のデータベースファイルを参照
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    # 手持ちポケモン（ユーザーID: 1）のリストを取得
    my_party = UserPokemon.query.filter_by(user_id=1).all()
    # 選択肢用の全ポケモンリストを取得
    all_pokemon = PokemonMaster.query.all()
    
    results = []
    enemy = None
    enemy_id = request.args.get('enemy_id')
    
    if enemy_id:
        enemy = PokemonMaster.query.get(enemy_id)
        # 【設計書ロジック】相性倍率（降順） > 素早さ（降順）でソートして選出
        query = db.session.query(PokemonMaster, TypeEffectiveness.effectiveness)\
            .join(UserPokemon, UserPokemon.pokemon_id == PokemonMaster.pokemon_id)\
            .join(TypeEffectiveness, TypeEffectiveness.attack_type_id == PokemonMaster.type_id)\
            .filter(UserPokemon.user_id == 1)\
            .filter(TypeEffectiveness.defense_type_id == enemy.type_id)\
            .order_by(TypeEffectiveness.effectiveness.desc(), PokemonMaster.speed.desc())
        results = query.all()

    return render_template('index.html', my_party=my_party, all_pokemon=all_pokemon, results=results, enemy=enemy)

@app.route('/add', methods=['POST'])
def add_pokemon():
    # 手持ちポケモンを新規登録（user_pokemonへのINSERT）
    pid = request.form.get('pokemon_id')
    if pid:
        new_entry = UserPokemon(user_id=1, pokemon_id=pid)
        db.session.add(new_entry)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':

    app.run(debug=True)

if __name__ == '__main__':
    # サーバー上ではポート番号などを環境に合わせる必要があるため
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


