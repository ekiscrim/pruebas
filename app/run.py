from flask import Flask
from main.views import main

app = Flask(__name__)
app.register_blueprint(main)

print app.url_map

app.run()