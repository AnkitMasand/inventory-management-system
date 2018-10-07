import ConfigParser  

config = ConfigParser.ConfigParser()  
config.read('./env.conf')

class Config:
	SQLALCHEMY_DATABASE_URI = 'mysql://' + config.get('DB', 'user') + ':' + config.get('DB', 'password') + '@' + config.get('DB', 'host') + '/' + config.get('DB', 'db')
	SQLALCHEMY_TRACK_MODIFICATIONS = True

