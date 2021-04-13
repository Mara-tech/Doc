from flask_lambda import FlaskLambda
import time
from flask_restplus import Api, Resource, fields, reqparse
import yaml
import json
import doc_log as log
from doc_engine import DocEngine



with open('doc.conf.yml', 'r') as stream:
    doc_conf = yaml.load(stream, Loader=yaml.FullLoader)

doc = DocEngine(doc_conf)


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
@api.doc(description="testing endpoint",
              responses={200: 'test ok'})
class HelloWorld(Resource):
    def get(self):
        return format_response("Hello World " + str(time.time()))

@api.route('/environments')
@api.doc(description="Get all defined environments",
              responses={200: 'list of environments'})
class GetEnvironments(Resource):
    def get(self):
        try:
            return format_response(doc.get_environments())
        except Exception as exc:
            api.abort(500, exc)


@api.route('/services')
@api.doc(description="Get services for selected environment",
              responses={200: 'list of services'})
class GetServices(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('environment', help="A single environment name", required=True)

    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        try:
            return format_response(doc.get_services(args))
        except Exception as exc:
            api.abort(500, exc)


@api.route('/<string:environment>/scenarii')
@api.doc(description="Get scenarii for selected environment",
              responses={200: 'list of scenarii for the selected environment'})
@api.param('environment', 'A single environment name', default='dev')
class GetScenarii(Resource):

    def get(self, environment):
        try:
            return format_response(doc.get_scenarii(environment))
        except KeyError as ke:
            return format_response({'error': str(ke)}, 400)
        except Exception as exc:
            api.abort(500, exc)


def start_api():
    app.run(host='0.0.0.0', debug=True, use_reloader=False)


if __name__ == '__main__':
    log.info("Starting API from main")
    start_api()
