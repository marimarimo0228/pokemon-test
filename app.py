import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, PokemonMaster, UserPokemon, Type, TypeEffectiveness
from dotenv import load_dotenv

# ローカル開発用に.envファイルを読み込む
load_dotenv()

app = Flask(__name__)

# --- データベース接続設定 (PostgreSQL) ---
# Renderなどの環境変数 DATABASE_URL を優先して使用
database_url = os.getenv('DATABASE_URL')

# PostgreSQLの接続URLが古い形式(postgres://)の場合、新しい形式(postgresql://)に修正
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# DB接続URLの設定（環境変数がなければローカルの設定を使用）
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or \
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- 初期データ投入関数 (Seeding) ---
def seed_data():
    """データベースが空の場合、初期データを投入する"""
    if Type.query.first():
        return # データが既に存在すれば何もしない

    print("初期データを投入しています...")
    
    # 1. タイプの登録
    types = [
        (1, 'ノーマル'), (2, 'ほのお'), (3, 'みず'), (4, 'くさ'), (5, 'でんき'),
        (6, 'こおり'), (7, 'かくとう'), (8, 'どく'), (9, 'じめん'), (10, 'ひこう'),
        (11, 'エスパー'), (12, 'むし'), (13, 'いわ'), (14, 'ゴースト'), (15, 'ドラゴン')
    ]
    for t_id, t_name in types:
        db.session.add(Type(type_id=t_id, type_name=t_name))
    
    # 2. ポケモン121体の登録 (ID, 名前, タイプID, 攻撃, 防御, 素早さ)
    pokemons = [
        (1,'フシギダネ',4,49,49,45), (2,'フシギソウ',4,62,63,60), (3,'フシギバナ',4,82,83,80),
        (4,'ヒトカゲ',2,52,43,65), (5,'リザード',2,64,58,80), (6,'リザードン',2,84,78,100),
        (7,'ゼニガメ',3,48,65,43), (8,'カメール',3,63,80,58), (9,'カメックス',3,83,100,78),
        (10,'キャタピー',12,30,35,45), (11,'トランセル',12,20,55,30), (12,'バタフリー',12,45,50,70),
        (13,'ビードル',12,35,30,50), (14,'コクーン',12,25,50,35), (15,'スピアー',12,80,40,75),
        (16,'ポッポ',10,45,40,56), (17,'ピジョン',10,60,55,71), (18,'ピジョット',10,80,75,91),
        (19,'コラッタ',1,56,35,72), (20,'ラッタ',1,81,60,97),
        (21,'オニスズメ',10,60,30,70), (22,'オニドリル',10,90,65,100),
        (23,'アーボ',8,60,44,55), (24,'アーボック',8,85,69,80),
        (25,'ピカチュウ',5,55,30,90), (26,'ライチュウ',5,90,55,100),
        (27,'サンド',9,75,85,40), (28,'サンドパン',9,100,110,65),
        (29,'ニドラン♀',8,47,52,41), (30,'ニドリーナ',8,62,67,56), (31,'ニドクイン',8,82,87,76),
        (32,'ニドラン♂',8,57,40,50), (33,'ニドリーノ',8,72,57,65), (34,'ニドキング',8,92,77,85),
        (35,'ピッピ',1,45,48,35), (36,'ピクシー',1,70,73,60),
        (37,'ロコン',2,41,40,65), (38,'キュウコン',2,76,75,100),
        (39,'プリン',1,45,20,20), (40,'プクリン',1,70,45,45),
        (41,'ズバット',8,45,35,55), (42,'ゴルバット',8,80,70,90),
        (43,'ナゾノクサ',4,50,55,30), (44,'クサイハナ',4,65,70,40), (45,'ラフレシア',4,80,85,50),
        (46,'パラス',12,70,55,25), (47,'パラセクト',12,95,80,30),
        (48,'コンパン',12,55,50,45), (49,'モルフォン',12,60,60,90),
        (50,'ディグダ',9,55,25,95), (51,'ダグトリオ',9,80,50,120),
        (52,'ニャース',1,45,35,90), (53,'ペルシアン',1,70,60,115),
        (54,'コダック',3,52,48,55), (55,'ゴルダック',3,82,78,85),
        (56,'マンキー',7,80,35,70), (57,'オコリザル',7,105,60,95),
        (58,'ガーディ',2,70,45,60), (59,'ウインディ',2,110,80,95),
        (60,'ニョロモ',3,50,40,90), (61,'ニョロゾ',3,65,65,90), (62,'ニョロボン',3,85,95,70),
        (63,'ケーシィ',11,20,15,90), (64,'ユンゲラー',11,35,30,105), (65,'フーディン',11,50,45,120),
        (66,'ワンリキー',7,80,50,35), (67,'ゴーリキー',7,100,70,45), (68,'カイリキー',7,130,80,55),
        (69,'マダツボミ',4,75,35,40), (70,'ウツドン',4,90,50,55), (71,'ウツボット',4,105,65,70),
        (72,'メノクラゲ',3,40,35,70), (73,'ドククラゲ',3,70,65,100),
        (74,'イシツブテ',13,80,100,20), (75,'ゴローン',13,95,115,35), (76,'ゴローニャ',13,110,130,45),
        (77,'ポニータ',2,85,55,90), (78,'ギャロップ',2,100,70,105),
        (79,'ヤドン',3,65,65,15), (80,'ヤドラン',3,75,110,30),
        (81,'コイル',5,35,70,45), (82,'レアコイル',5,60,95,70),
        (83,'カモネギ',10,65,55,60),
        (84,'ドードー',10,85,45,75), (85,'ドードリオ',10,110,70,100),
        (86,'パウワウ',3,45,55,45), (87,'ジュゴン',3,70,80,70),
        (88,'ベトベター',8,80,50,25), (89,'ベトベトン',8,105,75,50),
        (90,'シェルダー',3,65,100,40), (91,'パルシェン',3,95,180,70),
        (92,'ゴース',14,35,30,80), (93,'ゴースト',14,50,45,95), (94,'ゲンガー',14,65,60,110),
        (95,'イワーク',13,45,160,70),
        (96,'スリープ',11,48,45,42), (97,'スリーパー',11,73,70,67),
        (98,'クラブ',3,105,90,50), (99,'キングラー',3,130,115,75),
        (100,'ビリリダマ',5,30,70,100), (101,'マルマイン',5,50,70,140),
        (102,'タマタマ',4,40,80,40), (103,'ナッシー',4,95,85,55),
        (104,'カラカラ',9,50,95,35), (105,'ガラガラ',9,80,110,45),
        (106,'サワムラー',7,120,53,87), (107,'エビワラー',7,105,79,76),
        (108,'ベロリンガ',1,55,75,30),
        (109,'ドガース',8,65,95,35), (110,'マタドガス',8,90,120,60),
        (111,'サイホーン',9,85,95,25), (112,'サイドン',9,130,120,40),
        (113,'ラッキー',1,5,5,50),
        (114,'モンジャラ',4,55,115,60),
        (115,'ガルーラ',1,95,80,90),
        (116,'タッツー',3,40,70,60), (117,'シードラ',3,65,95,85),
        (118,'トサキント',3,67,60,63), (119,'アズマオウ',3,92,65,68),
        (120,'ヒトデマン',3,45,55,85), (121,'スターミー',3,75,85,115)
    ]
    for p_id, name, t_id, atk, df, spd in pokemons:
        db.session.add(PokemonMaster(pokemon_id=p_id, pokemon_name=name, type_id=t_id, attack=atk, defense=df, speed=spd))
    
    # 3. 相性データの登録（効果抜群2.0、いまひとつ0.5 の主要な組み合わせ）
    eff_data = [
        (2,4,2.0),(2,3,0.5),(2,2,0.5),(2,6,2.0),(2,12,2.0),(3,2,2.0),(3,4,0.5),(3,3,0.5),(3,9,2.0),(3,13,2.0),
        (4,3,2.0),(4,2,0.5),(4,4,0.5),(4,9,2.0),(4,13,2.0),(5,3,2.0),(5,5,0.5),(5,4,0.5),(5,10,2.0),
        (6,4,2.0),(6,9,2.0),(6,10,2.0),(6,15,2.0),(7,1,2.0),(7,13,2.0),(7,6,2.0),
        (9,2,2.0),(9,5,2.0),(9,8,2.0),(9,13,2.0),(10,4,2.0),(10,7,2.0),(10,12,2.0),
        (11,7,2.0),(11,8,2.0),(12,4,2.0),(12,11,2.0),(13,2,2.0),(13,6,2.0),(13,10,2.0),(13,12,2.0)
    ]
    for atk, df, eff in eff_data:
        db.session.add(TypeEffectiveness(attack_type_id=atk, defense_type_id=df, effectiveness=eff))
    
    db.session.commit()
    print("データ投入が完了しました。")

# --- アプリケーション起動時の処理 ---
with app.app_context():
    # テーブルを作成
    db.create_all()
    # データ投入関数を実行（既にデータがある場合はスキップされる）
    seed_data()

# --- CRUDルーティング ---

# 1. 参照 (Read) & 対戦シミュレーション
@app.route('/')
def index():
    # 手持ちリストを取得
    my_party = UserPokemon.query.all()
    # 選択肢用に全ポケモンを取得
    all_pokemon = PokemonMaster.query.all()
    
    enemy = None
    results = []
    enemy_id = request.args.get('enemy_id')
    
    # 対戦相手が選ばれた場合のロジック
    if enemy_id:
        enemy = PokemonMaster.query.get(enemy_id)
        # 1. 自分の手持ちの中から
        # 2. 相手のタイプに対して効果抜群の順、
        # 3. さらに素早さが高い順に並び替え
        query = db.session.query(PokemonMaster, TypeEffectiveness)\
            .join(UserPokemon, UserPokemon.pokemon_id == PokemonMaster.pokemon_id)\
            .join(TypeEffectiveness, TypeEffectiveness.attack_type_id == PokemonMaster.type_id)\
            .filter(UserPokemon.user_id == 1)\
            .filter(TypeEffectiveness.defense_type_id == enemy.type_id)\
            .order_by(TypeEffectiveness.effectiveness.desc(), PokemonMaster.speed.desc())
        results = query.all()

    return render_template('index.html', my_party=my_party, all_pokemon=all_pokemon, results=results, enemy=enemy)

# 2. 登録 (Create)
@app.route('/add', methods=['POST'])
def add_pokemon():
    pokemon_id = request.form.get('pokemon_id')
    if pokemon_id:
        # メモは空で新規作成
        db.session.add(UserPokemon(pokemon_id=pokemon_id, memo=""))
        db.session.commit()
    return redirect(url_for('index'))

# 3. 削除 (Delete)
@app.route('/delete/<int:user_pokemon_id>', methods=['POST'])
def delete_pokemon(user_pokemon_id):
    target = UserPokemon.query.get(user_pokemon_id)
    if target:
        db.session.delete(target)
        db.session.commit()
    return redirect(url_for('index'))

# 4. 更新 (Update)
@app.route('/update/<int:user_pokemon_id>', methods=['POST'])
def update_pokemon(user_pokemon_id):
    target = UserPokemon.query.get(user_pokemon_id)
    if target:
        # フォームから送られたメモ内容で更新
        target.memo = request.form.get('memo')
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
