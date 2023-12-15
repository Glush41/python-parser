from web import app as flask_app
import database
import config
import time

database.parser(config.url_name, 524)
time.sleep(15)
if __name__ == '__main__':
    flask_app.run(port=5001, host="0.0.0.0", debug=True)