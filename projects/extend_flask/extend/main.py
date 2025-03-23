from flask import Flask
import redis

app = Flask('test')
app.redis = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/result_cache/set')
def index():
    return 'ok'


@app.route('/result_cache/get')
def index():
    return 'ok'



if __name__ == '__main__':
    app.run()