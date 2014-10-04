import app

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

app.start()
app.app.run()