#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser  
from flask_sqlalchemy import SQLAlchemy

config = ConfigParser.ConfigParser()  
config.read('./env.conf')

def DB(app):
	config = ConfigParser.ConfigParser()  
	config.read('./env.conf')
	# MySQL configurations

	SQLALCHEMY_DATABASE_URI = 'mysql://' + config.get('DB', 'user') + ':' + config.get('DB', 'password') + '@' + config.get('DB', 'host') + '/' + config.get('DB', 'db')

	app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
	db = SQLAlchemy(app)
	return db
