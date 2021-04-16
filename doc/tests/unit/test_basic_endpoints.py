import json
import pytest
import app

app.set_conf_filename(str(__file__).replace('.py', '.yml'))


def generate_event(path='/doc/hello', method='GET', query_params=None):
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


@pytest.fixture()
def get_envs_event():
    return generate_event("/doc/environments")


def test_get_environments(get_envs_event, mocker):
    ret = app.app(get_envs_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] is not None
    assert json.loads(ret["body"]) == ["prod", "dev"]


@pytest.fixture(params=['prod', 'dev'])
def get_scenarii_event_and_expected(request):
    env = request.param
    event = generate_event(f"/doc/{env}/scenarii")
    expected = {
        'prod': ['github-and-aws', 'github-only', 'get-public-ip'],
        'dev': ['github-only', 'get-public-ip']
    }[env]

    return event, expected


def test_get_scenarii(get_scenarii_event_and_expected, mocker):
    req = get_scenarii_event_and_expected[0]
    expected = get_scenarii_event_and_expected[1]
    ret = app.app(req, "")

    assert ret["statusCode"] == 200
    assert ret["body"] is not None
    assert json.loads(ret["body"]) == expected


@pytest.fixture(params=[None, False, True])
def get_properties_event_and_expected(request):
    flatten_query_param = request.param
    event = generate_event(f"/doc/properties",
                           query_params={'flat': flatten_query_param} if flatten_query_param is not None else {})
    DEFAULT_BEHAVIOR = False
    expected = {
        False: {
            'ipify':
                {'url': 'https://api.ipify.org/?format=json'},
            'github': {
                'prod': {
                    'base_url': 'https://api.github.com/'
                },
                'dev': {
                    'base_url': 'https://dev.api.github.com/'
                }
            }
        },
        True: {
            'ipify.url': 'https://api.ipify.org/?format=json',
            'github.prod.base_url': 'https://api.github.com/',
            'github.dev.base_url': 'https://dev.api.github.com/'
        }
    }[flatten_query_param if flatten_query_param is not None else DEFAULT_BEHAVIOR]

    return event, expected


def test_get_properties(get_properties_event_and_expected, mocker):
    req = get_properties_event_and_expected[0]
    expected = get_properties_event_and_expected[1]
    ret = app.app(req, "")

    assert ret["statusCode"] == 200
    assert ret["body"] is not None
    assert json.loads(ret["body"]) == expected


@pytest.fixture(params=list((scenario, env, resolve)
                            for scenario in ['github-and-aws']
                            for env in [None, 'prod','dev']
                            for resolve in [True, False]))
def get_scenario_event_and_expected(request):
    scenario_name = request.param[0]
    env_query_param = request.param[1]
    resolve_placeholder_query_param = request.param[2]
    qp = {'resolve_placeholders': resolve_placeholder_query_param}
    if env_query_param is not None:
        qp['environment'] = env_query_param

    event = generate_event(f"/doc/scenario/{scenario_name}",
                           query_params=qp)
    if env_query_param == 'dev':
        expected = {'error': 'Scenario github-and-aws is not defined for environment dev.'}
        expected_status_code = 400
    else:
        expected = {
            'github-and-aws': [
                {
                    'name': 'github-up',
                    'next-if': {
                        'OK': [
                            {'name': 'github-user-info'}
                        ],
                        'KO': '${scenarii.get-public-ip}' if resolve_placeholder_query_param is False
                        else [{'name': 'public-ip'}]
                    }
                },
                {
                    'name': 'aws-s3-ls',
                    'next-if': {
                        'KO': [
                            {'name': 'aws-cli-version'}
                        ],
                        'UNDEFINED': [
                            {'name': 'aws-cli-version'}
                        ]
                    }
                }
            ]
        }[scenario_name]
        expected_status_code = 200

    return event, expected, expected_status_code


def test_get_scenario(get_scenario_event_and_expected, mocker):
    req = get_scenario_event_and_expected[0]
    expected = get_scenario_event_and_expected[1]
    expected_status_code = get_scenario_event_and_expected[2]
    ret = app.app(req, "")

    assert ret["statusCode"] == expected_status_code
    assert ret["body"] is not None
    assert json.loads(ret["body"]) == expected
