import os

from flask import Flask

# app factory function
def create_app(test_config=None): # test_config is substitute for instance config file during testing
    # create and configure app
    app = Flask(
        __name__, 
        instance_relative_config=True, # tells the app that the config files are relative to the instance folder that holds local data such as config secrets and database files
    )
    app.config.from_mapping(
        SECRET_KEY='dev', # 'dev' is a convenient value during dev but should be overwritten with random value when deploying
        DATABASE=os.path.join( # path where SQLite db file is saved
            app.instance_path, 
            'flaskr.sqlite'
        ),
    )
    
    if test_config is None:
        # load the instance config, if it existis, when not testing
        app.config.from_pyfile( # overrides default config with values taken from config.py in instance folder if it exists
            'config.py', 
            silent=True,
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        
        
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # a simple page that says hello
    @app.route('/')
    def index():
        return 'Hello, World!'


    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    return app