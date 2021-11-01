from flask import Flask, request
from flask_restplus import Api, Resource, fields, cors
from flask_cors import CORS, cross_origin

from account.account import registerAccount, loginAccount, logoutAccount
from farm.data_getting import getFarmData
from farm.field_actions import plowField, plantSeed, harvestField

authorizations = {
    "authentication token": {
        "type": "apiKey",
        "in": "header",
        "name": "Authentication"
    }
}

app = Flask(__name__)
api = Api(app=app, authorizations=authorizations)

CORS(app, resources={r'/*': {'origins': '*'}})

# account_ns = api.namespace("Account", description="Actions that are executed on the account itself.")
# farm_ns = api.namespace("Farm", description="Actions that are executed on the farm of a certain account.", authorizations=authorizations)

app.config['SWAGGER_UI_JSONEDITOR'] = True

registeraccountmodel = api.model('register account', {'email': fields.String, 'email2': fields.String, 'username': fields.String, 'password': fields.String, 'password': fields.String})
loginaccountmodel = api.model('login account', {'email': fields.String, 'password': fields.String})
logoutaccountmodel = api.model('logout account', {})
changepasswordmodel = api.model('change password', {'password': fields.String, 'newpassword': fields.String, 'newpassword': fields.String})
plowfieldmodel = api.model('plow field', {'x': fields.Integer, 'y': fields.Integer})
plantseedmodel = api.model('plant seed', {'x': fields.Integer, 'y': fields.Integer, 'seed': fields.String})
harvestfieldmodel = api.model('harvest field', {'x': fields.Integer, 'y': fields.Integer})

## ACCOUNT API'S
@api.route("/RegisterAccount", methods=['POST'])
class RegisterAccount(Resource):
    @api.expect(registeraccountmodel)
    def post(self):
        return registerAccount(request)

@api.route("/LoginAccount", methods=['POST'])
class LoginAccount(Resource):
    @api.expect(loginaccountmodel)
    def post(self):
        return loginAccount(request)

@api.route("/LogoutAccount", methods=['POST']) # requires token
class LogoutAccount(Resource):
    @api.doc(security='authentication token')
    @api.expect(logoutaccountmodel)
    def post(self):
        return logoutAccount(request)

@api.route("/ChangePassword", methods=['POST']) # requires token
class ChangePassword(Resource):
    @api.doc(security='authentication token')
    @api.expect(changepasswordmodel)
    def post(self):
        return changePassword(request)

# ## FARM API'S
@api.route("/GetFarmData", methods=['GET']) # requires token
class GetFarmData(Resource):
    @api.doc(security='authentication token')
    def get(self):
        return getFarmData(request)

@api.route("/PlowField", methods=['POST']) # requires token
class PlowField(Resource):
    @api.doc(security='authentication token')
    @api.expect(plowfieldmodel)
    def post(self):
        return plowField(request)

@api.route("/PlantSeed", methods=['POST']) # requires token
class PlantSeed(Resource):
    @api.doc(security='authentication token')
    @api.expect(plantseedmodel)
    def post(self):
        return plantSeed(request)

@api.route("/HarvestField", methods=['POST']) # requires token
class HarvestField(Resource):
    @api.doc(security='authentication token')
    @api.expect(harvestfieldmodel)
    def post(self):
        return harvestField(request)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)