import ConfigParser  
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
 
config = ConfigParser.ConfigParser()  
config.read('./env.conf')
# MySQL configurations

SQLALCHEMY_DATABASE_URI = 'mysql://' + config.get('DB', 'user') + ':' + config.get('DB', 'password') + '@' + config.get('DB', 'host') + '/' + config.get('DB', 'db')

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

mysql = SQLAlchemy(app)

# map models
# map models

class Company(mysql.Model):  
    __tablename__ = 'Company'
    id = mysql.Column(mysql.Integer, primary_key=True)
    name = mysql.Column(mysql.String(1024), nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Company (%s, %s) >' % (self.rate, self.name)


class Branch(mysql.Model):  
    __tablename__ = 'Branch'
    id = mysql.Column(mysql.Integer, primary_key=True)
    companyId = mysql.Column(mysql.Integer, nullable=False)
    name = mysql.Column(mysql.String(128), nullable=False)
    active = mysql.Column(mysql.Integer, nullable=True)
    def __repr__(self):
        return '<Branch (%s, %s, %s) >' % (self.companyId, self.name, self.active)

class Item(MySQL.Model)
    __tablename__ = 'Company'
    id = mysql.Column(mysql.Integer, primary_key=True)
    companyId = mysql.Column(mysql.Integer, nullable=False)
    code = mysql.Column(mysql.String(128), nullable=True)
    name = mysql.Column(mysql.String(128), nullable=True)
    brand = mysql.Column(mysql.Integer, nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Item (%s, %s) >' % (self.code, self.name)
        
#branch object creation
class BranchObject:
    def __init__(self, id, name, companyId, active):
        self.id = id
        self.companyId = companyId
        self.name = name
        self.active = active


#routes
@app.route("/")
def index():
    return "Index!"
 
@app.route("/hello")
def hello():
    return "Hello World!"
 
#company routes
@app.route('/company', methods=['GET'])
def getCompany():  
    return jsonify(json_list=[i.name for i in Company.query.all()])

@app.route('/company', methods=['POST'])
def createProduct():
    # fetch name and rate from the request
    name = request.get_json()["name"]
    company = Company(name=name,active=1) #prepare query statement
    curr_session = mysql.session #open database session
    try:
        curr_session.add(company) #add prepared statment to opened session
        curr_session.commit() #commit changes
    except:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
    companyId = company.id #fetch last inserted id
    data = Company.query.filter_by(id=companyId).first() #fetch our inserted product
    result = [data.name] #prepare visual data
    return jsonify(session=result)

@app.route('/company/<int:companyId>', methods=['PATCH']) 
def updateProduct(companyId):
    name = request.get_json()["name"] #fetch rate
    curr_session = mysql.session
    try:
        company = Company.query.filter_by(id=companyId).first() #fetch the product do be updated
        company.name = name #update the column rate with the info fetched from the request
        curr_session.commit() #commit changes
    except:
        curr_session.rollback()
        curr_session.flush()
    companyId = company.id
    data = Company.query.filter_by(id=companyId).first() #fetch our updated product
    result = [data.name] #prepare visual data
    return jsonify(session=result)

@app.route('/company/<int:companyId>', methods=['DELETE']) 
def deleteProduct(companyId):
    curr_session = mysql.session
    try:
        company = Company.query.filter_by(id=companyId).first() #fetch the product do be updated
        company.active = 0 #update the column rate with the info fetched from the request
        curr_session.commit() #commit changes
    except:
        curr_session.rollback()
        curr_session.flush()
    companyId = company.id
    data = Company.query.filter_by(id=companyId).first() #fetch our updated product
    result = [data.name] #prepare visual data
    return jsonify(session=result)

#branch route
@app.route('/branch/<int:cId>', methods=['GET'])
def getBranch(cId):  
    data = Branch.query.filter_by(companyId=cId).all() #fetch all branches on the table
    data_all = []
    for branch in data:
        data_all.append([branch.id, branch.name, branch.companyId, branch.active]) #prepare visual data
    return jsonify(branch=data_all)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

    
