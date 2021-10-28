from flask import Flask, request
from flask_restplus import Api, Resource, fields
from flask_cors import CORS

from account.account import registerAccount, loginAccount, logoutAccount
from farm.data_getting import getFarmData

app = Flask(__name__)
CORS(app)
api = Api(app=app)

app.config['SWAGGER_UI_JSONEDITOR'] = True

registeraccountmodel = api.model('register account', {'email': fields.String, 'email2': fields.String, 'username': fields.String, 'password': fields.String, 'password': fields.String})
loginaccountmodel = api.model('login account', {'email': fields.String, 'password': fields.String})
logoutaccountmodel = api.model('logout account', {'token': fields.String})
changepasswordmodel = api.model('change password', {'token': fields.String, 'password': fields.String, 'newpassword': fields.String, 'newpassword': fields.String})
tokenmodel = api.model('token', {'token': fields.String})

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

@api.route("/LogoutAccount", methods=['POST'])
class RegisterAccount(Resource):
    @api.expect(logoutaccountmodel)
    def post(self):
        return logoutAccount(request)

@api.route("/ChangePassword", methods=['POST'])
class ChangePassword(Resource):
    @api.expect(changepasswordmodel)
    def post(self):
        return changePassword(request)

@api.route("/GetFarmData", methods=['POST'])
class GetFarmData(Resource):
    @api.expect(tokenmodel)
    def post(self):
        return getFarmData(request)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)