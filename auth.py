from flask import Blueprint, render_template, redirect, url_for, request,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from functools import wraps
from app import db,app
import jwt,datetime,uuid
auth = Blueprint('auth', __name__,url_prefix='/API')
@auth.route('/signup', methods=['POST'])
def signup_imdb():
    """
    Method to perform the signup activity.
    will take user details and verify them and then performs the sign up operation.
    """
    data=request.get_json()
    #print(data)
    try:
        username = data['username']
        name = data['name']
        password = data['password']
        try:
            admin_key=data['admin_key']
        except:
            admin_key=""
    except:
        return jsonify({"error":"401","message":"Details missing, please provide username,passowrd,name and admin_key"})
    user = User.query.filter_by(username=username).first()
    if user:
        signUp={"message":"User already exist, the user you are trying for is already present"}
        return jsonify(signUp)
    if(admin_key==app.config['ADMIN_KEY']):
        new_user = User(username=username, name=name, password=generate_password_hash(password, method='sha256'),public_id=str(uuid.uuid4()),isAdmin=True)
    else:
        new_user = User(username=username, name=name, password=generate_password_hash(password, method='sha256'),public_id=str(uuid.uuid4()))
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    signUp={"message":"Sign-Up successful"}
    return jsonify(signUp)

@auth.route('/login', methods=['POST'])
def login_imdb():
    """
    Login method for verifing the user.
    Will authenticate the user on the bases of username and password and will return token
    """
    auth=request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"error":401,"message":"Login Required!"})
    user = User.query.filter_by(username=auth.username).first()
    # check if the user actually exists
    if not user:
        login_Response={"error":401,"message":"User Doesn't exist, Please signup first and try"}
    # if the above check passes, then we know the user has the right credentials
    elif not check_password_hash(user.password, auth.password):
        login_Response={"error":401,"message":"username and password didn't match, please enter valid username and password!!!"}
    else:
        token=jwt.encode({'public_id':user.public_id,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        login_Response={'token':token.decode('UTF-8'),'message':"Login successful!!!"}
    return jsonify(login_Response)


def token_required(func):
    """
    Decorator for checking whether the user request is logged in or not, not used anywhere in application but for future use.
    """
    @wraps(func)
    def decorated(*args,**kwargs):
        token=None
        if 'x-access-token' in request.headers:
            token=request.headers['x-access-token']
        if not token:
            return jsonify({"error":401,"message":"token missing, please provide token!!!"})
        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
            current_user=User.query.filter_by(public_id=data['public_id']).first()
            if not current_user:
                return jsonify({"error":401,"message":"Sorry, Access available to Admin only!!!"})
            return func(current_user,*args,**kwargs)
        except:
            return jsonify({"error":401,"message":"Invalid token!!!"})
    return decorated

#decorator to check whether user requesting is admin or not
def admin_token_required(func):
    """
    Decorator to check whether user requesting is admin or not

    """
    @wraps(func)
    def decorated(*args,**kwargs):
        token=None
        if 'x-access-token' in request.headers:
            token=request.headers['x-access-token']
        if not token:
            return jsonify({"error":401,"message":"token missing, please provide token!!!"})
        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
            try:
                current_user=User.query.filter_by(public_id=data['public_id']).first()
            except:
                return jsonify({"error":401,"message":"Invalid token or user doesn't exist"})
            if not current_user or not current_user.isAdmin:
                return jsonify({"error":401,"message":"Sorry, Access available to Admin only!!!"})
        except:
            return jsonify({"error":401,"message":"Token expired, please login again"})
        return func(current_user,*args,**kwargs)
    return decorated
