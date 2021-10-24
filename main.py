from flask import Flask, request
from flask_restplus import Api, Resource, fields

from account.account import registerAccount, loginAccount

app = Flask(__name__)
api = Api(app=app)

app.config['SWAGGER_UI_JSONEDITOR'] = True

registeraccountmodel = api.model('account', {'email': fields.Integer, 'email2': fields.Integer, 'username': fields.String, 'passwordhash': fields.String, 'passwordhash2': fields.String})
loginaccountmodel = api.model('account', {'email': fields.Integer, 'passwordhash': fields.String})
changepasswordmodel = api.model('account', {'email': fields.Integer, 'passwordhash': fields.String, 'newpasswordhash': fields.String, 'newpasswordhash2': fields.String})

@api.route("/RegisterAccount", methods=['POST'])
class RegisterAccount(Resource):
    @api.expect(registeraccountmodel)
    def post(self):
        return registerAccount(request)

@api.route("/LoginAccount", methods=['POST'])
class RegisterAccount(Resource):
    @api.expect(loginaccountmodel)
    def post(self):
        return loginAccount(request)

@api.route("/ChangePassword", methods=['POST'])
class ChangePassword(Resource):
    @api.expect(changepasswordaccountmodel)
    def post(self):
        return changePassword(request)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)