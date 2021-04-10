from flask_lambda import FlaskLambda
import time
from flask_restplus import Api, Resource, fields
import yaml
import json
import doc_log as log

# --------------------
# ---API DEFINITION---
# --------------------
DOC_API_PATH_PREFIX = '/doc'
DOC_OPEN_API_DOC_SUFFIX = DOC_API_PATH_PREFIX + '/swagger-ui'

app = FlaskLambda(__name__)
api = Api(app,
          version='1',
          title='Doc API',
          description='Interactions with Doc',
          license='MIT',
          contact_url='https://github.com/Mara-tech/Doc',
          doc=DOC_OPEN_API_DOC_SUFFIX,
          prefix=DOC_API_PATH_PREFIX
          )
health_ns = api.namespace('health', description='Health checks operations')
compare_ns = api.namespace('compare', description='Compare environments')


def format_response(data=None, status_code=200):
    if data is None or type(data) is str:
        data = {'message': data}
    return (
        # json.dumps(data),
        data,
        status_code,
        {'Content-Type': "application/json"}
    )


# --------------------
# ---API ENDPOINTS----
# --------------------
@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return format_response("Hello World " + str(time.time()))


def start_api():
    app.run(host='0.0.0.0', debug=True, use_reloader=False)


if __name__ == '__main__':
    log.info("Starting API from main")
    start_api()
