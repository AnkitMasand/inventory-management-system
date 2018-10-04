import ConfigParser  
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
import json

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

class Item(mysql.Model):
    __tablename__ = 'Item'
    id = mysql.Column(mysql.Integer, primary_key=True)
    companyId = mysql.Column(mysql.Integer, nullable=False)
    branchId = mysql.Column(mysql.Integer, nullable=False)
    code = mysql.Column(mysql.String(128), nullable=True)
    name = mysql.Column(mysql.String(128), nullable=True)
    brand = mysql.Column(mysql.Integer, mysql.ForeignKey('Brand.id') ,nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    fk_category_item = mysql.relationship('Category', backref='Item')
    fk_item_variant_id = mysql.relationship('Variant', backref='Item')
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Item (%s, %s) >' % (self.code, self.name)

class Brand(mysql.Model):  
    __tablename__ = 'Brand'
    id = mysql.Column(mysql.Integer, primary_key=True)
    name = mysql.Column(mysql.String(128), nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    fk_brand_id = mysql.relationship('Item', backref='Brand')
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Brand (%s, %s) >' % (self.name, self.active)

class Variant(mysql.Model):
    __tablename__ = 'Variant'
    id = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    name = mysql.Column(mysql.String(128), nullable=True)
    itemId = mysql.Column(mysql.Integer, mysql.ForeignKey('Item.id'), nullable=False)
    costPrice = mysql.Column(mysql.Float, primary_key=True)
    sellingPrice = mysql.Column(mysql.Float, primary_key=True)
    quantity = mysql.Column(mysql.Integer, nullable=False)
    branchId = mysql.Column(mysql.Integer, nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    fk_variant_property = mysql.relationship('Property', backref='Variant')

    def __init__(self, name, itemId, costPrice, sellingPrice, quantity, branchId, active):
        self.name = name
        self.itemId = itemId
        self.costPrice = costPrice
        self.sellingPrice = sellingPrice
        self.quantity = quantity
        self.branchId = branchId
        self.active = active
    def __repr__(self):
        return '<Item (%s, %s) >' % (self.itemId, self.name)

class Property(mysql.Model):
    __tablename__ = 'Property'
    id = mysql.Column(mysql.Integer, primary_key=True, autoincrement=True)
    variantId = mysql.Column(mysql.Integer, mysql.ForeignKey('Variant.id'), nullable=False)
    propertyId = mysql.Column(mysql.Integer, mysql.ForeignKey('PropertyType.id'), nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    def __init__(self, variantId, propertyId, active):
        self.variantId = variantId
        self.propertyId = propertyId
        self.active = active
    def __repr__(self):
        return '<Property (%s) >' % (self.active)


class PropertyType(mysql.Model):
    __tablename__ = 'PropertyType'
    id = mysql.Column(mysql.Integer, primary_key=True)
    name = mysql.Column(mysql.String(128), nullable=True)
    active = mysql.Column(mysql.Integer, nullable=False)
    fk_property_type = mysql.relationship('Property', backref='PropertyType')

    def __init__(self, name, active):
        self.active = active
    def __repr__(self):
        return '<PropertyType (%s) >' % (self.active)

class Branch(mysql.Model):  
    __tablename__ = 'Branch'
    id = mysql.Column(mysql.Integer, primary_key=True)
    companyId = mysql.Column(mysql.Integer, nullable=False)
    name = mysql.Column(mysql.String(128), nullable=False)
    active = mysql.Column(mysql.Integer, nullable=True)
    def __repr__(self):
        return '<Branch (%s, %s, %s) >' % (self.companyId, self.name, self.active)

class Category(mysql.Model):
    __tablename__ = 'Category'
    id = mysql.Column(mysql.Integer, primary_key=True)
    itemId = mysql.Column(mysql.Integer, mysql.ForeignKey('Item.id'), nullable=False)
    typeId = mysql.Column(mysql.Integer, mysql.ForeignKey('CategoryType.id'), nullable=False)
    def __init__(self, typeId):
        self.typeId = typeId
    def __repr__(self):
        return '<Category (%s) >' % (self.typeId)

class CategoryType(mysql.Model):
    __tablename__ = 'CategoryType'
    id = mysql.Column(mysql.Integer, primary_key=True)
    name = mysql.Column(mysql.Integer, nullable=False)
    active = mysql.Column(mysql.Integer, nullable=False)
    fk_category_type_id = mysql.relationship('Category', backref='CategoryType')
    def __init__(self, active):
        self.active = active
    def __repr__(self):
        return '<CategoryType (%s) >' % (self.active)




def insertProperty(variantId, typeId):
    print 'called'
    print typeId
    properties = Property(variantId = variantId, propertyId = typeId, active = 1) #prepare query statement
    curr_session = mysql.session #open database session
    resp = {}
    try:
        curr_session.add(properties) #add prepared statment to opened session
        curr_session.commit() #commit changes
        propertyId = properties.id #fetch last inserted id
        data = Property.query.filter_by(id = propertyId).first() #fetch our inserted product
        resp = {"message" : 'Variant added successfully!', 'status_code' : 200}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        resp = {"message" : "Operation unsuccessful!", 'status_code' : 400}
    return jsonify(data = resp)

@app.route("/")
def index():
    return "Index!"

@app.route('/company', methods=['GET'])
def getCompany():
    return jsonify(json_list=[i.name for i in Company.query.all()])

@app.route('/company', methods=['POST'])
def createProduct():
    # fetch name and rate from the request
    name = request.get_json()["name"]
    company = Company(name=name,active=1) #prepare query statement
    curr_session = mysql.session #open database session
    resp = {}
    try:
        curr_session.add(company) #add prepared statment to opened session
        curr_session.commit() #commit changes
        companyId = company.id #fetch last inserted id
        data = Company.query.filter_by(id=companyId).first() #fetch our inserted product
        resp = jsonify({"message" : 'User added successfully!', "name" : data.name})
        resp.status_code = 200
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        resp = jsonify({"message" : "Operation unsuccessful!", "name" : name, "error" : e})
        resp.status_code = 400
    return resp



@app.route('/company/<int:companyId>', methods=['PATCH']) 
def updateProduct(companyId):
    name = request.get_json()["name"] #fetch rate
    curr_session = mysql.session
    resp = {}
    try:
        company = Company.query.filter_by(id=companyId).first() #fetch the product do be updated
        company.name = name #update the column rate with the info fetched from the request
        curr_session.commit() #commit changes
        resp = jsonify({"message":'Operation Successfull!', "name":name})
        resp.status_code = 200
    except Exception as e:
        curr_session.rollback()
        curr_session.flush()
        resp = jsonify({"message":"Operation unsuccessful!", "name":name, "error":e})
        resp.status_code = 400
    return resp

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

@app.route('/branch/<int:cId>', methods=['GET'])
def getBranch(cId):  
    data = Branch.query.filter_by(companyId=cId).all() #fetch all branches on the table
    data_all = []
    for branch in data:
        print branch.id
        data_all.append({"id":branch.id, "name":branch.name, "cid":branch.companyId, "status":branch.active}) #prepare visual data
    print data_all
    return jsonify(results = data_all)

@app.route('/company/<int:cId>/branch/<int:bId>/item', methods=['GET'])
def getAllItem(cId, bId):
    data = mysql.session.query(Brand, Item, Category, CategoryType).join(Item, Item.brand == Brand.id).\
    join(Category, Category.itemId == Item.id).join(CategoryType, Category.typeId == CategoryType.id).\
    filter(Item.companyId == cId, Item.branchId == bId).\
    add_columns(Item.id, Item.name.label('itemName'),Item.companyId, Item.code, Brand.name.label('brandName'), CategoryType.name.label('categoryName')).all()
    print data
    data_all = {}
    for item in data:
        if item.code in data_all:
            data_all[item.code]['categoryType'].append(item.categoryName)
        else:
            data_all[item.code] = {}
            data_all[item.code] = {
            'id':item.id, 'itemName' : item.itemName ,'cid':item.companyId, 'code':item.code, 'brandName' : item.brandName, 
            'categoryType' : [item.categoryName]}
    return jsonify(data = data_all)

@app.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant', methods=['GET'])
def getItemVariant(cId, bId, itemId):
    data = mysql.session.query(Item, Variant, Property, PropertyType).join(Variant, Variant.itemId == Item.id).\
    join(Property, Property.variantId == Variant.id).join(PropertyType, PropertyType.id == Property.propertyId).\
    filter(Item.companyId == cId, Item.branchId == bId, Item.id == itemId, Variant.active == 1).\
    add_columns(Item.id, Item.name.label('itemName'),Item.companyId, Item.code, Variant.name.label('variantName'), Variant.id.label('variantId'),
    Variant.costPrice, Variant.sellingPrice, Variant.quantity, Property.propertyId, PropertyType.name.label('propertyName')).all()
    print data
    data_all = {}
    itemCode = ''
    for item in data:
        itemCode = item.code
        if item.variantId in data_all:
            data_all[item.variantId]['property'].append(item.propertyName)
        else:
            data_all[item.variantId] = {}
            data_all[item.variantId] = {
            'itemId':item.id, 'itemName' : item.itemName ,'cid':item.companyId, 'code':item.code, 'variantId' : item.variantId,'property' : [item.propertyName]}
    return jsonify(data = {itemCode : data_all.values()})

@app.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant', methods=['POST'])
def addItemVariant(cId, bId, itemId) : 
    # fetch name and rate from the request
    name = request.get_json()["name"]
    costPrice = request.get_json()["costPrice"]
    sellingPrice = request.get_json()["sellingPrice"]
    quantity = request.get_json()["quantity"]
    propertyId = request.get_json()["propertyId"]
    print name
    variant = Variant(name=name, itemId=itemId, costPrice = costPrice, sellingPrice = sellingPrice, quantity = quantity, branchId = bId, active = 1) #prepare query statement
    curr_session = mysql.session #open database session
    resp = {}
    try:
        curr_session.add(variant) #add prepared statment to opened session
        curr_session.commit() #commit changes
        variantId = variant.id #fetch last inserted id
        for pId in propertyId:
            insertProperty(variantId, pId)
        data = Variant.query.filter_by(id = variantId).first() #fetch our inserted product
        
        resp = {"message" : 'Variant added successfully!', "name" : data.name, 'status_code' : 200}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        print e
        resp = {"message" : "Operation unsuccessful!", "name" : name, 'status_code' : 400}
    return jsonify(data = resp)

@app.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant', methods=['DELETE'])
def inActiveItemVariant(cId, bId, itemId):
    variantId = request.get_json()["variantId"] 
    curr_session = mysql.session
    resp = {}
    try:
        variant = Variant.query.filter_by(id = variantId, branchId = bId, itemId = itemId).first() #fetch the product do be updated
        variant.active = 0
        curr_session.commit() #commit changes
        resp = jsonify({"message" : 'Operation Successfull!', "name" : variantId})
        resp.status_code = 200
    except Exception as e:
        curr_session.rollback()
        curr_session.flush()
        resp = jsonify({"message" : "Operation unsuccessful!", "name" : variantId, "error" : e})
        resp.status_code = 400
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
