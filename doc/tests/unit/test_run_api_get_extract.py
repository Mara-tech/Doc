import json
import pytest
import app


# based on https://swapi.dev/


@pytest.fixture(autouse=True)
def setup_test():
    app.set_conf_filename(str(__file__).replace('.py', '.yml'))
    yield


def generate_event(path='/doc/hello', method='POST', query_params=None):
    if query_params is None:
        query_params = {}
    return {
        "body": '{}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": method,
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": query_params,
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": path},
        "httpMethod": method,
        "stageVariables": {},
        "path": path,
    }


def build_expected_output(*expected_scenario, env):
    expected = {
        'check_obiwan': {
            'scenario': 'check_obiwan',
            'environment': env,
            'check_person': 'Obi-Wan Kenobi'
        },
        'check_flight': {
            'scenario': 'check_flight',
            'environment': env,
            'captain': 'Han Solo',
            'ship': 'Millennium Falcon',
            'crewmate': 'Chewbacca',
            'destination': {'name': 'Alderaan', 'terrain': 'grasslands, mountains'}
        },
        'check_vader': {
            'scenario': 'check_vader',
            'environment': env,
            'check_person': 'Darth Vader'
        },
        'check_anakin': {
            'scenario': 'check_anakin',
            'environment': env,
            'father': 'Anakin Skywalker',
            'son': 'Luke Skywalker',
            'daughter': 'Leia Organa'
        }
    }
    return list(expected[s] for s in expected_scenario)


@pytest.fixture(params=['empire', 'republic'])
def run_scenarii_event_and_expected(request):
    env = request.param
    event = generate_event(f"/doc/{env}/scenarii")
    expected = {
        'empire': build_expected_output('check_flight', 'check_vader', env='empire'),
        'republic': build_expected_output('check_obiwan', 'check_anakin', env='republic')
    }[env]

    return event, expected


def ignore_timestamp(scenarii_output: list):
    for scenario_output in scenarii_output:
        scenario_output.pop('timestamp')
    return scenarii_output


def test_get_scenarii(run_scenarii_event_and_expected, mocker):
    req = run_scenarii_event_and_expected[0]
    expected = run_scenarii_event_and_expected[1]
    ret = app.app(req, "")

    assert ret["body"] is not None
    assert ignore_timestamp(json.loads(ret["body"])) == expected
    assert ret["statusCode"] == 200
