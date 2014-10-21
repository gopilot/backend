import backend

def wsgi_handler():
	backend.start()
	return backend.app

