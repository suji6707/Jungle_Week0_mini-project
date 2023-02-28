from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret"
jwt = JWTManager(app)

client = MongoClient('localhost', 27017)
db = client.dbsparta


## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('index.html')

#로그인
@app.route('/login')
def loginView():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login(): 
    email = request.form['email_give']
    password = request.form['password_give']
    checkExistEmail = db.user.find_one({'email': email})
    checkPassword = db.user.find_one({'email': email}, {'$id': False})['password']
    if checkExistEmail is None:
        return '존재하지 않는 이메일입니다. 이메일을 확인하세요.', 400
    elif password != checkPassword:
        return '비밀번호가 다릅니다. 비밀번호를 확인하세요.', 400
    test_name = db.user.find_one({'email': email})['username']
    test = create_access_token(identity=test_name)
    return jsonify({'msg': 'sucess'})



#회원가입
@app.route('/signup', methods=['GET'])
def signupView():
    test = list(db.user.find({}))
    print(test)
    return render_template('signUp.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username_give']
    email = request.form['email_give']
    password = request.form['password_give']
    checkExistEmail = db.user.find_one({'email': email})
    if checkExistEmail is None:
        newUser = {'username': username, 'email': email, 'password': password}
        db.user.insert_one(newUser)
        return jsonify({'msg': 'success'})

    if email == checkExistEmail:
        return jsonify({'msg': '존재하는 이메일입니다.'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)