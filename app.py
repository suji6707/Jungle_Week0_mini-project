from flask import Flask, render_template, jsonify, request, make_response
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt, set_access_cookies, set_refresh_cookies
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

client = MongoClient('localhost', 27017)
db = client.dbsparta


## 메인페이지
@app.route('/')
@jwt_required(optional=True)
def home():
   return render_template('index.html')

#로그인
@app.route('/login')
def loginView():
    return render_template('login.html')

@app.route('/token/auth', methods=['POST'])
def login(): 
    email = request.form['email_give']
    password = request.form['password_give']
    checkExist = None if db.user.find_one({'email': email}) == None else db.user.find_one({'email': email})
    ##이메일 체크
    if checkExist is None:
        return '존재하지 않는 이메일입니다. 이메일을 확인하세요.', 400

    ##비밀번호 체크
    checkPassword = checkExist['password']
    print( bcrypt.check_password_hash(checkPassword, password))
    if bcrypt.check_password_hash(checkPassword, password) is False:
        return '비밀번호가 다릅니다. 비밀번호를 확인하세요.', 400
    username = checkExist['username']
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200
    

@app.route('/detail', methods=['GET'])
@jwt_required
def detailPageView():
    return render_template('detail.html')

@app.route('/protected', methods=['GET'])
@jwt_required
def detailPage():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200



#회원가입
@app.route('/signup', methods=['GET'])
def signupView():
    return render_template('signUp.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username_give']
    email = request.form['email_give']
    password = request.form['password_give']
    checkExistEmail = None if db.user.find_one({'email': email}) == None else db.user.find_one({'email': email})['email']
    if checkExistEmail is None:
        hash_password = bcrypt.generate_password_hash(password)
        newUser = {'username': username, 'email': email, 'password': hash_password}
        db.user.insert_one(newUser)
        return  jsonify({'msg': 'success'})

    if email == checkExistEmail:
        return '존재하는 이메일입니다.', 400
    
@app.route('/show', methods=['GET'])
def show_group():
    result = list(db.product.find({}, {'_id':0}))
    # print(result)
    return jsonify({'lists': result})

# 입력받은 쿠팡 ulr로 데이터 DB에 넣기
@app.route('/submit', methods=['POST'])
def submit():
    url = request.form['url']
    getData(url)
    return jsonify({'return':'success'})

def getData(url):

    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua' : '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'cookie': 'cookie: PCID=16505901704875933154078'
        }

    data = requests.get(url, headers = headers, verify=False)

    soup = BeautifulSoup(data.text, 'html.parser')

    name = soup.select_one('.prod-buy-header__title').text
    price = soup.select_one('.total-price').text.replace('원','').replace(',','')
    imgUrl = "https:" + soup.select_one('.prod-image__detail')['src']

    doc = {
        'name': name, 
        'price' : int(price),
        'imgUrl' : imgUrl
    }

    db.product.insert_one(doc)
    print(name, price, imgUrl)

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)