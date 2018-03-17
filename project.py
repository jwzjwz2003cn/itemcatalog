from flask import Flask
# Import a module / component using its blueprint handler variable (mod_auth)
from mod_catalog.controllers import mod_catalog as catalog_module
from mod_auth.controllers import mod_auth as auth_module

app = Flask(__name__)


# Register blueprint(s)
app.register_blueprint(catalog_module)
app.register_blueprint(auth_module)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
