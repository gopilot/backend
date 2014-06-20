import app as backend

import sys

config = 'config.DevelopmentConfig'

if('--production' in sys.argv):
	config = 'config.ProductionConfig'

backend.init_app(config=config)
backend.app.run(debug=True)


