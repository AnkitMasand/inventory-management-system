#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# map models
# map models
class Company(db.Model):  
    __tablename__ = 'Company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024), nullable=False)
    active = db.Column(db.Integer, nullable=False)
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Company (%s, %s) >' % (self.rate, self.name)

class Branch(db.Model):  
    __tablename__ = 'Branch'
    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Integer, nullable=True)
    def __init__(self, name, active,companyId):
        self.name = name
        self.active = active
        self.companyId = companyId
    def __repr__(self):
        return '<Branch (%s, %s, %s) >' % (self.companyId, self.name, self.active)

class Item(db.Model):
    __tablename__ = 'Item'
    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer, nullable=False)
    branchId = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    brand = db.Column(db.Integer, db.ForeignKey('Brand.id') ,nullable=False)
    active = db.Column(db.Integer, nullable=False)
    fk_category_item = db.relationship('Category', backref='Item')
    fk_item_variant_id = db.relationship('Variant', backref='Item')
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Item (%s, %s) >' % (self.code, self.name)

class Brand(db.Model):  
    __tablename__ = 'Brand'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Integer, nullable=False)
    fk_brand_id = db.relationship('Item', backref='Brand')
    def __init__(self, name, active):
        self.name = name
        self.active = active
    def __repr__(self):
        return '<Brand (%s, %s) >' % (self.name, self.active)

class Variant(db.Model):
    __tablename__ = 'Variant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=True)
    itemId = db.Column(db.Integer, db.ForeignKey('Item.id'), nullable=False)
    costPrice = db.Column(db.Float, primary_key=True)
    sellingPrice = db.Column(db.Float, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    branchId = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Integer, nullable=False)
    fk_variant_property = db.relationship('Property', backref='Variant')

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

class Property(db.Model):
    __tablename__ = 'Property'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variantId = db.Column(db.Integer, db.ForeignKey('Variant.id'), nullable=False)
    propertyId = db.Column(db.Integer, db.ForeignKey('PropertyType.id'), nullable=False)
    active = db.Column(db.Integer, nullable=False)
    def __init__(self, variantId, propertyId, active):
        self.variantId = variantId
        self.propertyId = propertyId
        self.active = active
    def __repr__(self):
        return '<Property (%s) >' % (self.active)

class PropertyType(db.Model):
    __tablename__ = 'PropertyType'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    active = db.Column(db.Integer, nullable=False)
    fk_property_type = db.relationship('Property', backref='PropertyType')

    def __init__(self, name, active):
        self.active = active
    def __repr__(self):
        return '<PropertyType (%s) >' % (self.active)

class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    itemId = db.Column(db.Integer, db.ForeignKey('Item.id'), nullable=False)
    typeId = db.Column(db.Integer, db.ForeignKey('CategoryType.id'), nullable=False)
    def __init__(self, typeId):
        self.typeId = typeId
    def __repr__(self):
        return '<Category (%s) >' % (self.typeId)

class CategoryType(db.Model):
    __tablename__ = 'CategoryType'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Integer, nullable=False)
    fk_category_type_id = db.relationship('Category', backref='CategoryType')
    def __init__(self, active):
        self.active = active
    def __repr__(self):
        return '<CategoryType (%s) >' % (self.active)

