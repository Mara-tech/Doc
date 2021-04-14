import json
import pytest
import app

app.set_conf_filename(str(__file__).replace('.py', '.yml'))


def generate_event(path='/doc/hello', method='GET'):
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
        "queryStringParameters": {},
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
    data = json.loads(ret["body"])

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
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert ret["body"] is not None
    assert json.loads(ret["body"]) == expected
