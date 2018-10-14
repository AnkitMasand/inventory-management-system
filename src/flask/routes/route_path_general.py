from flask import Blueprint, jsonify, request
from models.schema import Company, Branch, Item, Brand, Variant, Property, PropertyType, Category, CategoryType, Event, User
from index import init
from database import DB
from math import *
import json

route_path_general = Blueprint("route_path_general", __name__)

app = init()
mysql = DB(app)

@route_path_general.route("/")
def index():
	return "Index!"

@route_path_general.route('/company', methods=['GET'])
def getCompany():
	"""
    Get Company Names endpoint
    ---
    parameters:
        - in: body
          name: body
    responses:
            200:
                schema:
                  properties:
                    name:
                      type: array
    """
	return jsonify(json_list=[i.name for i in Company.query.filter_by(active=1).all()])

@route_path_general.route('/company', methods=['POST'])
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

@route_path_general.route('/company/<int:companyId>', methods=['PATCH'])
def updateProduct(companyId):
    name = request.get_json()["name"]
    print name, companyId
    curr_session = mysql.session
    resp = {}
    # return jsonify({"name" : request.headers.get('user', None)})
    try:
        company = Company.query.filter_by(id=companyId).first()
        company.name = name
        company.active = 1 
        curr_session.commit() #commit changes
        resp = jsonify({"message":'Operation Successfull!', "name":name})
        resp.status_code = 200
    except Exception as e:
        curr_session.rollback()
        curr_session.flush()
        resp = jsonify({"message":"Operation unsuccessful!", "name":name})
        resp.status_code = 400
    return resp

@route_path_general.route('/company/<int:companyId>', methods=['DELETE']) 
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

@route_path_general.route('/branch/<int:cId>', methods=['GET'])
def getBranch(cId):  
    data = Branch.query.filter_by(companyId=cId).all() #fetch all branches on the table
    data_all = []
    for branch in data:
        print branch.id
        data_all.append({"id":branch.id, "name":branch.name, "cid":branch.companyId, "status":branch.active}) #prepare visual data
    print data_all
    return jsonify(results = data_all)

@route_path_general.route('/company/<int:cId>/branch/<int:bId>/item', methods=['GET'])
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


@route_path_general.route('/company/<int:cId>/branch/<int:bId>/item', methods=['POST'])
def addItem(cId, bId) : 
    # fetch name and rate from the request
    code = request.get_json()["code"]
    name = request.get_json()["name"]
    brand = request.get_json()["brand"]
    userId = int(request.get_json()["userId"])
    companyId = cId
    branchId = bId
    # print code, name, brand
    item = Item(companyId=companyId, branchId=branchId, code=code, name=name, brand=brand, active=1) #prepare query statement
    curr_session = mysql.session #open database session
    resp = {}
    try:
        curr_session.add(item) #add prepared statment to opened session
        curr_session.commit() #commit changes
        itemId = item.id #fetch last inserted id
        # for pId in propertyId:
        #     insertProperty(variantId, pId)
        data = Item.query.filter_by(id = itemId).first() #fetch our inserted prod        
        message = 'added item '+ name
        insE = insertEvent('item', message, userId)    
        resp = {"message" : 'Variant added successfully!', "name" : data.name, 'status_code' : 200}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        print e
        resp = {"message" : "Operation unsuccessful!", "name" : name, 'status_code' : 400}
    return jsonify(data = resp)

@route_path_general.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant', methods=['GET'])
def getItemVariant(cId, bId, itemId):
    data = mysql.session.query(Item, Variant, Property, PropertyType).join(Variant, Variant.itemId == Item.id).\
    join(Property, Property.variantId == Variant.id).join(PropertyType, PropertyType.id == Property.propertyId).\
    filter(Item.companyId == cId, Item.branchId == bId, Item.id == itemId, Variant.active == 1).\
    add_columns(Item.id, Item.name.label('itemName'),Item.companyId, Item.code, Variant.name.label('variantName'), Variant.id.label('variantId'),
    Variant.costPrice, Variant.sellingPrice, Variant.quantity, Property.propertyId, PropertyType.name.label('propertyName')).all()
    # print data
    data_all = {}
    itemCode = ''
    for item in data:
        itemCode = item.code
        # print getVariant(item.variantId).name
        if item.variantId in data_all:
            data_all[item.variantId]['property'].append(item.propertyName)
        else:
            data_all[item.variantId] = {}
            data_all[item.variantId] = {
            'itemId':item.id, 'itemName' : item.itemName ,'cid':item.companyId, 'code':item.code, 'variantId' : item.variantId, 'variantName' : item.variantName,'property' : [item.propertyName]}
    return jsonify(data = {itemCode : data_all.values()})

@route_path_general.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant', methods=['POST'])
def addItemVariant(cId, bId, itemId) : 
    # fetch name and rate from the request
    name = request.get_json()["name"]
    costPrice = round(request.get_json()["costPrice"], 2)
    sellingPrice = round(request.get_json()["sellingPrice"], 2)
    quantity = floor(request.get_json()["quantity"])
    propertyId = request.get_json()["propertyId"]
    userId = request.get_json()["userId"]
    print name
    itemDetails = getItem(itemId).name
    print itemDetails

    variant = Variant(name=name, itemId=itemId, costPrice = costPrice, sellingPrice = sellingPrice, quantity = quantity, branchId = bId, active = 1) #prepare query statement
    curr_session = mysql.session #open database session
    resp = {}
    try:
        curr_session.add(variant) #add prepared statment to opened session
        curr_session.commit() #commit changes
        variantId = variant.id #fetch last inserted id
        print variantId
        properties = []
        for pId in propertyId:
            ip = insertProperty(variantId, pId)
            properties.append(ip['propertyName'])
        data = Variant.query.filter_by(id = variantId).first() #fetch our inserted prod   
        message = 'added '+ str(quantity) +' variant ' + name + ' for item ' + itemDetails +  ' with cost price' + str(costPrice) + ' and selling price ' + str(sellingPrice)
        message += ' with properties '+', '.join(properties)
        insE = insertEvent('variant', message, userId)
        resp = {"message" : 'Variant added successfully!', "name" : name, 'status_code' : 200}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        print e
        resp = {"message" : "Operation unsuccessful!", "name" : name, 'status_code' : 400}
    return jsonify(data = resp)

@route_path_general.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant/<int:variantId>', methods=['PATCH'])
def updateItemVariant(cId, bId, itemId, variantId) : 
    # fetch name and rate from the request
    # user = request.headers.get('user', None)
    # variantId = request.get_json()["variantId"]
    updateFormat = request.get_json()
    propertyId = []
    userId = 1
    if updateFormat['propertyId']:
        propertyId = updateFormat['propertyId']
        del updateFormat['propertyId']
    if updateFormat['userId']:
        userId = updateFormat['userId']
        del updateFormat['userId']

    # propertyId = request.get_json()["propertyId"]
    # print name, itemId, variantId
    # return jsonify({'name' : name, 'costPrice' : costPrice, 'sellingPrice' : sellingPrice, 'quantity' : quantity, 'variant' : variantId, 'itemId' : itemId})
    curr_session = mysql.session #open database session
    resp = {}
    try:
        varUpdate = curr_session.query(Variant).filter_by(id = variantId, active = 1)
        varName = varUpdate.first().name
        varUpdate.update(updateFormat)
        itemDetails = getItem(itemId).name
        message = 'updated variant ' + (varName) + ' for item ' + itemDetails 
        insE = insertEvent('variant', message, userId)
        # variant.name = str(name)
        # variant.itemId = int(itemId)
        # variant.costPrice = float(costPrice)
        # variant.sellingPrice = float(sellingPrice)
        # variant.quantity = int(quantity)
        # variant.branchId = int(bId)
        # variant.active = 1
        curr_session.commit()
        print 'committed'
        resp = jsonify({"message":'Operation Successfull!'})
        resp.status_code = 200
    except Exception as e:
        mysql.session.rollback()
        mysql.session.flush()
        print e
        resp = jsonify({"message":'Operation unsuccessful!'})
        resp.status_code = 400
    
    return resp
        
    # try :
  	# 	variant = Variant.query.filter_by(id = variantId, branchId = bId, itemId = itemId).first()
  	# 	variant.name = name
    #     # variant.costPrice = costPrice
    #     # variant.sellingPrice = sellingPrice
    #     # variant.quantity = quantity
  	# 	curr_session.commit() #commit changes
  	# 	resp = jsonify({"message":'Operation Successfull!', "name":name})
  	# 	resp.status_code = 200
  	# except Exception as e:
  	# 	curr_session.rollback()
  	# 	curr_session.flush()
  	# 	resp = jsonify({"message":"Operation unsuccessful!", "name":name, "error":e})
  	# 	resp.status_code = 400
  	# return resp

@route_path_general.route('/company/<int:cId>/branch/<int:bId>/item/<int:itemId>/variant/<int:variantId>', methods=['DELETE'])
def inActiveItemVariant(cId, bId, itemId, variantId):
    # variantId = request.get_json()["variantId"] 
    userId = request.get_json()["userId"]
    curr_session = mysql.session
    resp = {}
    try:
        curr_session.query(Variant).filter_by(id = variantId, branchId = bId, itemId = itemId).update({'active' : 0})
        # variant = Variant.query.filter_by(id = variantId, branchId = bId, itemId = itemId).first() #fetch the product do be updated
        # print variant
        # variant.active = 0
        curr_session.commit() #commit changes
        itemDetails = getItem(itemId).name
        message = 'delated variant ' + str(variantId) + ' for item ' + itemDetails
        insE = insertEvent('variant', message, userId)
        resp = {"message" : 'Operation Successfull!', "name" : variantId, 'status_code' : 200}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush()
        print e
        resp = {"message" : "Operation unsuccessful!", "name" : variantId, 'status_code' : 400}
    return jsonify(data = resp)



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
        # propertyName = json.dumps(list(getPropertyType(typeId)))
        propertyName = getPropertyType(typeId).name
        # propertyName = propertyName['name']
        resp = {"message" : 'Variant added successfully!', 'status_code' : 200, 'propertyName' : propertyName}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        resp = {"message" : "Operation unsuccessful!", 'status_code' : 400}
    return resp

@route_path_general.route('/event/<int:uId>', methods=['GET'])
def getEvent(uId):
	# return jsonify(json_list=[i.message for i in ])
    data_all = {}
    user = {}
    event = Event.query.filter_by(userId=uId).all()
    for data in event:
        if data.userId in data_all:
            index = len(data_all[data.userId])
            print data_all[data.userId][index - 1]['time'], data.createdAt
            if(data_all[data.userId][index - 1]['time'] == data.createdAt) : 
                data_all[data.userId][index - 1]['message'] += ' and '+data.message
            else : 
                data_all[data.userId].append({'message' : user[data.userId] +' '+data.message, 'time' : data.createdAt})
        else : 
            user[data.userId] = getUser(data.userId).name
            data_all[data.userId] = []
            data_all[data.userId].append({'message' : user[data.userId] +' '+data.message, 'time' : data.createdAt})

    return jsonify(data_all=data_all)

@route_path_general.route('/event', methods=['GET'])
def getAllEvent():
	# return jsonify(json_list=[i.message for i in ])
    data_all = {}
    user = {}
    event = Event.query.all()
    for data in event:
        if data.userId in data_all:
            index = len(data_all[data.userId])
            print data_all[data.userId][index - 1]['time'], data.createdAt
            if(data_all[data.userId][index - 1]['time'] == data.createdAt) : 
                data_all[data.userId][index - 1]['message'] += ' and '+data.message
            else : 
                data_all[data.userId].append({'message' : user[data.userId] +' '+data.message, 'time' : data.createdAt})
        else : 
            user[data.userId] = getUser(data.userId).name
            data_all[data.userId] = []
            data_all[data.userId].append({'message' : user[data.userId] +' '+data.message, 'time' : data.createdAt})

    return jsonify(data_all=data_all)

def insertEvent(type, message, userId): 
    eventing = Event(type = type, message = message, userId = userId)
    curr_session = mysql.session
    resp = {}
    try:
        curr_session.add(eventing)
        curr_session.commit()
        eventId = eventing.id
        data = Event.query.filter_by(id = eventId).first() 
        resp = {"message" : 'Variant added successfully!', 'status_code' : 200}
    except Exception as e:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()
        resp = {"message" : "Operation unsuccessful!", 'status_code' : 400}
    return resp

def getUser(userId): 
    user = User.query.filter_by(id = userId, active = 1).first()
    return user

def getItem(itemId): 
    item = Item.query.filter_by(id = itemId, active = 1).first()
    return item

def getVariant(variantId):
    return Variant.query.filter_by(id = variantId).first()

def getPropertyType(pId) : 
    return PropertyType.query.filter_by(id=pId, active = 1).first()