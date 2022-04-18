# Project: SIMPLE DESIGN OF A REST API FOR PAYMENTS
# Author: Leonardo de Almeida Silva Andrade

# DESCRIPTION: 
# This is a project of a simple REST API for payments. The aim was to study the functioning of an API and how to integrate it with a relational database. 
# Despite generating different tokens at each login and storing a hash of passwords, security itself was not the focus of this project.

# Reference: https://www.youtube.com/watch?v=WxGBoY5iNXY

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
import jwt
import datetime
import random
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Used to encode the current user's token...
app.config['SECRET_KEY'] = 'secret'

# The database is stored in the same folder as the 'app.py' file...
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# ---------------- #
#   USER'S TABLE   #
# ================ #

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

# ----------------- #
#  PAYMENT'S TABLE  #
# ================= #

class Payment(db.Model):

    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    cpf = db.Column(db.String(11))
    amount = db.Column(db.Integer)
    payment_method = db.Column(db.Integer) # 0 for bank slip (boleto), 1 for credit card
    
    # It's only filled in if the payment method is a credit card
    # 'payment_method = 1'
    name_card = db.Column(db.String(50))
    num_card = db.Column(db.String(16))
    expiration = db.Column(db.String(5))
    cvv = db.Column(db.Integer)


# -------------------------------- #
# DECORATOR TO VALIDATE THE TOKENS #
# ================================ #

def token_required(f):
    @wraps(f)

    def decorated(*args, **kwargs):

        """
        This is a decorator that works with the token. Assigns the token request to the routes. 
        Indicates that to access the page, it's necessary to have a valid token (logged in).
    
        In each function call with this decorator, we will get the token of the current user who performed 
        the function and decode it to analyze who this user is and what their permissions are.
        
        :return: Returns 'f' function result with the decoded token.
        """

        token = None

        if 'X-Access-Token' in request.headers:
            # Takes the token from a header 'X-Access-Token'
            
            token = request.headers['X-Access-Token']

        if not token:
            # If the X-Access-Token header field is null...

            return jsonify({'message': 'Token is missing!'}), 401 # 401 = Unauthorized

        try:
            # The access token has the public_id, so we need to decode it to have it...

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

            # We search our user by with the 'public_id', which is unique
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        
        except:
            
            # If the token is expired, we show this message
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# ----------------- #
#     HOME PAGE     #
# ================= #

@app.route('/home')
def index():
    
    """
    Just a symbolic home page.
    
    :return: A welcome message.
    """
    
    text = "Bem vindo! Este eh um projeto de uma REST API simples para efetuar pagamentos."

    return text

# --------------------------------------- #
# GET ALL USERS IN DATABASE (ONLY ADMINS) #
# ======================================= #

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    
    """
    Get all the users in the database. Only users with 'admin=True' are allowed to
    performed this function.
    It takes the token from the current user to verify the permission.

    :param current_user: Current user obtained by the decoded token.
    :return: All users in table 'user' (JSON format).
    """

    if not current_user.admin:
        # The current user isn't an admin...

        return jsonify({'message': 'You are not allowed to perform that function!'}), 401

    # Query all users in the table 'user'...
    users = User.query.all()

    output = []

    for user in users:
        # Put the query reponse in JSON format...

        user_data = {}
        user_data['user_id'] = user.id
        user_data['public_id'] = user.public_id
        user_data['name'] = user.username
        user_data['password'] = user.password
        user_data['admin'] = user.admin

        output.append(user_data)

    return jsonify({'users': output}), 200

# --------------------------------------- #
# GET ONE USER IN DATABASE (ONLY ADMINS)  #
# ======================================= #

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    """
    Returns the user who has the public_id passed in. Only users with 'admin=True' are allowed to
    performed this function.
    It takes the token from the current user to verify the permission.

    :param current_user: Current user obtained by the decoded token.
    :param public_id: 'public_id' of the user to be consulted.
    :return: Informations (JSON format) of the user with the 'public_id'passed.
    """

    if not current_user.admin:
        # Current user isn't an admin...

        return jsonify({'message': 'You are not allowed to perform that function!'}), 401
    
    # Query an specific user in table 'user'...
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        # There is no user with the public_id passed in...

        return jsonify({'message': 'No user found!'}), 404

    user_data = {}
    user_data['user_id'] = user.id
    user_data['public_id'] = user.public_id
    user_data['name'] = user.username
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data}), 200


# --------------------------------------------------- #
# CREATE AN USER AND PUT IT IN DATABASE (ONLY ADMINS) #
# =================================================== #

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):

    """
    Creates a new user with username and password. It generates an public_id and encode the password.
    The username and password must be passed through the request in JSON format.

    :param current_user: Current user obtained by the decoded token.
    :return: Message if the action was successful.
    """
    
    if not current_user.admin:
        # Current user isn't an admin...

        return jsonify({'message': 'You are not allowed to perform that function!'}), 401

    # Get the username and password from the data passed through the request...
    data = request.get_json()
    
    # Generate a hash of the password to store in database...
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    # Save the public_id, username, the hash of the password and 'admin=False' by default...
    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password, admin=False)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'}), 200 # 200 = OK

# -------------------------------------- #
# PROMOTE AN USER TO ADMIN (ONLY ADMINS) #
# ====================================== #

@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):

    """
    Promotes an user to admin.

    :param current_user: Current user obtained by the decoded token.
    :param public_id: 'public_id' of the user to be promoted.
    :return: Message if the action was successful.
    """

    if not current_user.admin:
        # Current user isn't an admin...

        return jsonify({'message': 'You are not allowed to perform that function!'}), 401
    
    # Search the user to be promoted by 'public_id'...
    user = User.query.filter_by(public_id=public_id).first()  

    if not user:
        # If the user isn't in the database...

        return jsonify({'message': 'No user found!'}), 404 # 404 = Not Found
    
    user.admin = True
    db.session.commit()

    return jsonify({'message': f"The user '{user.username}' has been promoted!"}), 200


# ---------------------------- #
# DELETE AN USER (ONLY ADMINS) #
# ============================ #

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

    """
    Deletes an user.
    
    :param current_user: Token of the current user.
    :param public_id: 'public_id' of the user to be deleted. 
    :returns: Message if the action was successful.
    """

    if not current_user.admin:
        # Current user isn't an admin...

        return jsonify({'message': 'You are not allowed to perform that function!'}), 401
    

    # Search the user to be deleted by 'public_id'...
    user = User.query.filter_by(public_id=public_id).first()  

    if not user:
        # The user isn't in the database... 

        return jsonify({'message': 'No user found!'}), 404
    
    db.session.delete(user)
    db.session.commit()   
    
    return jsonify({'message': f"The user '{user.username}' has been deleted!"}), 200

# -------------------- #
# LOGIN AUTHENTICATION #
# ==================== #

@app.route('/login')
def login():

    """
    Login page. Requires an username and a password that are in the database.
    
    :param: The parameters must be passed through the request.
    :returns: Token of the user (if login is successful).
    """

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
            
    if check_password_hash(user.password, auth.password):
        # The username and password exists and are in the database.
        # So, it generates an encoded token for that user.
        
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
                            app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'message': f"Welcome {user.username} !",'token': token}), 200
    
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

# ------------------------------------ #
# TAKE ALL PAYMENTS MADE (ONLY ADMINS) #
# ==================================== #

@app.route('/payment', methods=['GET'])
@token_required
def get_all_payments(current_user):

    """
    Returns all payments made. If you are a regular user, you will only be able to see your own payments. 
    If you are an admin user, you will be able to see all payments in the database.
    
    :param current_user: Current user obtained by the decoded token.
    :return: List of all payments made (JSON format).
    """
    
    if not current_user.admin:
        # If the current user is not an admin, returns only payments made by the current user (from whom the token was passed).

        payments = Payment.query.filter_by(user_id=current_user.id).all()
        output = []

        for payment in payments:
        
            if payment.payment_method == 0:
                # The method of payment is bank slip...

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "boleto"
        
            else:
                # The method of payment is credit card...

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "credit card"
                payment_data['credit_card'] = {'name_card': payment.name_card, 'num_card': payment.num_card, 
                                            'expiration': payment.expiration, 'cvv': payment.cvv}

            output.append(payment_data)
    
    else:     
        # If the current user is an admin, returns all payments made by all users.

        payments = Payment.query.all()
        output = []

        for payment in payments:
        
            if payment.payment_method == 0:

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "boleto"
        
            else:

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "credit card"
                payment_data['credit_card'] = {'name_card': payment.name_card, 'num_card': payment.num_card, 
                                            'expiration': payment.expiration, 'cvv': payment.cvv}

            output.append(payment_data)


    return jsonify({'payments': output}), 200


# ------------------------------ #
# TAKE AN ESPECIFIC PAYMENT MADE #
# ============================== #

@app.route('/payment/<payment_id>', methods=['GET'])
@token_required
def get_one_payment(current_user, payment_id):
    
    """
    Returns the payment who has the payment_id passed in. Only users with 'admin=True' are allowed to
    performed this function. If the logged in user is not an admin, he will only be able to access a payment made by himself. 
    If you are an admin, you can access any payment.
    It takes the token from the current user to verify the permission.

    :param current_user: Current user obtained by the decoded token.
    :param payment_id: 'payment_id' of the payment to be consulted.
    :return: Informations (JSON format) of the payment with the 'payment_id'passed.
    """

    if not current_user.admin:
        # Current user isn't an admin, so it's only possible to consult a payment made by the current user of the token.

        # Query an specific payment in table 'payment'...
        payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()

        if not payment:
            # There is no payment with the payment_id passed in...

            return jsonify({'message': 'No payment found!'}), 404
        
        else:
            
            if payment.payment_method == 0:
                # The method of payment is bank slip...

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "boleto"

            else:
                # The method of payment is credit card...

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "credit card"                
                payment_data['credit_card'] = {'name_card': payment.name_card, 'num_card': payment.num_card, 
                                            'expiration': payment.expiration, 'cvv': payment.cvv}

    else:
        # Current user is an admin, so can query any payment of any user...

        # Query an specific payment in table 'payment'...
        payment = Payment.query.filter_by(id=payment_id).first()

        if not payment:
            # There is no payment with the payment_id passed in...

            return jsonify({'message': 'No payment found!'}), 404
        
        else:
            
            if payment.payment_method == 0:
                # The method of payment is bank slip...

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "boleto"

            else:
                # The method of payment is credit card...

                payment_data = {}
                payment_data['payment_id'] = payment.id
                payment_data['user_id'] = payment.user_id
                payment_data['name'] = payment.name
                payment_data['email'] = payment.email
                payment_data['cpf'] = payment.cpf
                payment_data['amount'] = payment.amount
                payment_data['payment_method'] = "credit card"                
                payment_data['credit_card'] = {'name_card': payment.name_card, 'num_card': payment.num_card, 
                                            'expiration': payment.expiration, 'cvv': payment.cvv}

    return jsonify({'payment': payment_data}), 200


# ---------------- #
#  MAKE A PAYMENT  #
# ================ #

@app.route('/payment', methods=['POST'])
@token_required
def make_a_payment(current_user):
        
    """
    Make a payment and sign it with the user_id of the current_user.
    
    :param current_user: Token of the current user.
    :return: Returns the bank slip number if the payment is by bank slip (payment method = 0). 
             If the payment is by credit card (payment method = 1), it returns whether the card 
             processing was successful or not.
    """

    data = request.get_json()

    if data['payment_method'] == 0:
        # Payment in bank slip, it only stores the informations about the user, the amount and payment method...
        
        new_payment = Payment(user_id=current_user.id, name=data['name'], email=data['email'], cpf=data['cpf'],
                              amount=data['amount'], payment_method=data['payment_method'])
        
        a = random.randint(0,9)
        b = random.randint(0,9)
        c = random.randint(0,9)
        d = random.randint(0,9)

        db.session.add(new_payment)
        db.session.commit()
        
        # Generate a random bank slip number... 
        return jsonify({'ticket': (5*str(a)+5*str(b)+5*str(c)+5*str(d))}), 200

    elif data['payment_method'] == 1:
        # Payment with credit card, in addition to storing information about the user, 
        # the amount and the payment method, it also stores credit card information.

        new_payment = Payment(user_id=current_user.id, name=data['name'], email=data['email'], cpf=data['cpf'],
                amount=data['amount'], payment_method=data['payment_method'], name_card=data['name_card'], 
                num_card=data['num_card'], expiration=data['expiration'], cvv=data['cvv'])
        
        # Generate a false response about credit card processing...
        approved_transaction = bool(random.getrandbits(1)) 
        
        if approved_transaction == True:
            # Valid credit card, returns successfull payment...

            db.session.add(new_payment)
            db.session.commit()
            return jsonify({'message': "Successful payment!"}), 200
        
        else:
            # Invalid credit card, returns a bad request...
            
            return jsonify({'message': "Unsuccessful payment... Please, enter a valid card!"}), 400 # Bad Request

    else:
        return jsonify({'message': "Invalid payment method!"}), 400


# ---------------- #
# DELETE A PAYMENT #
# ================ #

@app.route('/payment/<payment_id>', methods=['DELETE'])
@token_required
def delete_payment(current_user, payment_id):

    """
    Deletes a payment from database. If you are a regular user, you will only be able to delete your own payments. 
    If you are an admin user, you will be able to delete any payments in the database.

    :param current_user: Current user obtained by the decoded token.
    :param payment_id: ID of the payment to be deleted.
    :return: A message if the action was succeeded or not.
    """

    if not current_user.admin:
        # Current user isn't an admin, so it is only possible to delete a payment made by the current user of the token...

        payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()  

        if not payment:
            # Payment not in database...

            return jsonify({'message': 'No payment found!'}), 404
        
        else:
            db.session.delete(payment)
            db.session.commit()   
    
            return jsonify({'message': 'The payment has been deleted!'}), 200

    else:
        # Current user is an admin, so it can delete any payment of any user...

        payment = Payment.query.filter_by(id=payment_id).first()

        if not payment:
            return jsonify({'message': 'No payment found!'}), 404

        else:
            db.session.delete(payment)
            db.session.commit()

            return jsonify({'message': 'The payment has been deleted!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
