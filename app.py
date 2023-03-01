from datetime import timedelta

from flask import Flask, render_template, jsonify, request, session, redirect
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import unset_jwt_cookies, set_access_cookies, set_refresh_cookies
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = 'a77i%rqxfl#1sfta6#g+$li$%!%+0!+%om4je-(!h+rapwnwky'
app.config["JWT_SECRET_KEY"] = "secret"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/'

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

client = MongoClient('localhost', 27017)
db = client.dbsparta


# 메인페이지
@app.route('/')
def home():
    username = None
    query = {'$expr': {'$gt': ['$buyerCount', {'$subtract': ['$count', 3]}]}}
    recommend_product_info = list(db.product.find(query, {'_id': 0}))
    try:
        username = session['username']
    except KeyError:
        return render_template('index.html', recommend_product_info=recommend_product_info)
    if recommend_product_info is None:
        return render_template('index.html')
    return render_template('index.html', recommend_product_info=recommend_product_info, username=username)


# 로그인
@app.route('/login')
def loginView():
    return render_template('login.html')


@app.route('/token/auth', methods=['POST'])
def login():
    email = request.form['email_give']
    password = request.form['password_give']
    checkExist = None if db.user.find_one(
        {'email': email}) == None else db.user.find_one({'email': email})
    # 이메일 체크
    if checkExist is None:
        return '존재하지 않는 이메일입니다. 이메일을 확인하세요.', 400

    # 비밀번호 체크
    checkPassword = checkExist['password']
    if bcrypt.check_password_hash(checkPassword, password) is False:
        return '비밀번호가 다릅니다. 비밀번호를 확인하세요.', 400
    username = checkExist['username']
    session['username'] = username
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp

# 로그아웃


@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route('/detail/<variable>', methods=['GET'])
@jwt_required()
def detailPage(variable):
    username = get_jwt_identity()
    product_info = db.product.find_one({'name': variable}, {'_id': 0})
    return render_template('detail.html', username=username, product_info=product_info), 200


@jwt.unauthorized_loader
def unauthorized_callback(error):
    return redirect('/login')

# 회원가입


@app.route('/signup', methods=['GET'])
def signupView():
    return render_template('signUp.html')


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username_give']
    email = request.form['email_give']
    password = request.form['password_give']
    checkExistEmail = None if db.user.find_one(
        {'email': email}) == None else db.user.find_one({'email': email})['email']
    if checkExistEmail is None:
        hash_password = bcrypt.generate_password_hash(password)
        newUser = {'username': username,
                   'email': email, 'password': hash_password}
        db.user.insert_one(newUser)
        return jsonify({'msg': 'success'})

    if email == checkExistEmail:
        return '존재하는 이메일입니다.', 400

# 참여하기 추가


@app.route('/add-to-buyer', methods=['POST'])
def addToBuyer():
    participateUser = request.form['user_give']
    product_name = request.form['name_give']
    db.product.find_one_and_update(
        {'name': product_name},
        {'$push': {'buyer': participateUser},
         '$inc': {'buyerCount': 1}}, {'_id': 0})
    return jsonify({'msg': 'success'})


# DB 카테고리 user 제외하고 가져오기
@ app.route('/group-list', methods=['GET'])
def show_group_category():
    all_group = db.list_collection_names()
    print(all_group.remove('user'))
    return jsonify({'result': all_group})

# 상품 리스트 가져오기


@ app.route('/list', methods=['GET'])
def show_products():
    keyword = request.args.get('keyword')
    lists = list(db.product.find({'category': keyword}, {
        '_id': False}).sort('likes', -1))

    return jsonify({'lists': lists}), 200


# 입력받은 쿠팡 ulr로 데이터 DB에 넣기
@ app.route('/submit', methods=['POST'])
def submit():
    url = request.form['url']
    category = request.form['category']
    count = request.form['count']
    getData(url, category, count)
    return jsonify({'return': 'success'}), 200


def getData(url, category, count):
    headers = {
        'authority': 'www.coupang.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ko,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://www.coupang.com/np',
        'sec-ch-ua': '"Not A(Brand";v="24", "Chromium";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    name = soup.select_one('.prod-buy-header__title').text
    price = soup.select_one(
        '.total-price').text.replace('원', '').replace(',', '')
    imgUrl = "https:" + soup.select_one('.prod-image__detail')['src']

    doc = {
        'category': category,
        'name': name,
        'price': int(price),
        'imgUrl': imgUrl,
        'count': int(count),
        'likes': 0,
        'buyer': [],
        'buyerCount': 0,
    }


db.product.insert_one(doc)

# 좋아요 count


@ app.route('/like', methods=['POST'])
def likeit():
    name = request.form['name']
    same_product = db.product.find_one({'name': name})
    target_likes = same_product['likes']
    new_likes = target_likes + 1
    db.product.update_one({'name': name}, {'$set': {'likes': new_likes}})
    return jsonify({'return': 'success'})

# 상품등록

# 전체 인기상품 TOP 10개


@ app.route('/popular', methods=['GET'])
def show_popular():
    products = list(db.product.find({}, {'_id': False}).sort('likes', -1))
    high_likes = []
    for i in range(10):
        high_likes.append(products[i])
    return jsonify({'lists': high_likes})


@ app.route('/register')
@jwt_required()
def register():
    username = get_jwt_identity()
    return render_template('register.html', username=username)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
