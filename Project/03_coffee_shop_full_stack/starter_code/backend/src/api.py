import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.route('/auth0/callback', methods=['GET'])
def auth0_callback():
    pass

    return jsonify({}), 200


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    return jsonify(dict(
        success=True,
        drinks=[drink.short() for drink in Drink.query.all()]
    )), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_detail_drinks(user):
    return jsonify(dict(
        success=True,
        drinks=[drink.long() for drink in Drink.query.all()]
    )), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(user):
    data = request.get_json()
    drink = Drink(title=data.get('title'))
    drink.recipe = json.dumps(data.get('recipe'))
    drink.insert()
    return jsonify(dict(
        success=True,
        drinks=drink.long()
    )), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(user, id: int):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    data = request.get_json()
    if 'title' in data:
        drink.title = data.get('title')
    if 'recipe' in data:
        drink.recipe = json.dumps(data.get('recipe'))

    drink.update()
    return jsonify(dict(
        success=True,
        drinks=[drink.long()]
    )), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(user, id: int):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()
    return jsonify(dict(
        success=True,
        delete=id
    )), 200


# Error Handling

@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "invalid request body formatting."
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(error.to_dict()), error.status_code

@app.errorhandler(401)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authentication failed"
    }), 401


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422
