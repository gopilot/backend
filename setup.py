import app as backend
backend.init_app(config='config.DevelopmentConfig')
backend.app.run(debug=True)


