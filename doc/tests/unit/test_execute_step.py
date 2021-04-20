import doc_engine
import toolbox
import time
import json


def test_toolbox_none():
    data = None
    expected = LookupError
    expected_error_msg = "'service' attribute is mandatory for any tool."
    try:
        actual = toolbox.find_tool(data)(data)
        assert False, expected_error_msg
    except expected as err:
        assert str(err) == expected_error_msg


def test_instantiate_empty():
    data = {}
    expected = LookupError
    expected_error_msg = "'service' attribute is mandatory for any tool."
    try:
        actual = toolbox.find_tool(data)(data)
        assert False, expected_error_msg
    except expected as err:
        assert str(err) == expected_error_msg


def test_instantiate_typeless():
    data = {'service': 'typeless tool'}
    actual = toolbox.find_tool(data)(data)
    expected = toolbox.DefaultStep(data)
    assert actual == expected


def test_instantiate_by_type_cmd():
    data = {'service': 'stepA', 'type': 'cmd', 'cmd': 'ls'}
    actual = toolbox.find_tool(data)(data)
    expected = toolbox.cmd.Step(data)
    assert actual == expected


def test_instantiate_by_type_api_rest_no_url():
    data = {'service': 'stepA', 'type': 'api.rest'}
    expected = LookupError
    expected_error_msg = "'url' attribute is mandatory for 'api' tool."
    try:
        actual = toolbox.find_tool(data)(data)
        assert False, expected_error_msg
    except expected as err:
        assert str(err) == expected_error_msg


def test_instantiate_by_type_api_rest():
    data = {'service': 'stepA', 'type': 'api.rest', 'url': 'http://echo.jsontest.com/key/value/one/two'}
    output = {}
    timestamp = int(time.time())
    actual = doc_engine.execute_step(data, output)
    expected_status = 'OK'
    expected = {
        'stepA': {
            'step_type': 'api.rest',
            'status': expected_status,
            'url': 'http://echo.jsontest.com/key/value/one/two',
            'timestamp': timestamp,
            'end_time': int(time.time()),
            'json': '{\n'
                    '   "one": "two",\n'
                    '   "key": "value"\n'
                    '}',
            'json_obj': {
                "one": "two",
                "key": "value"
            }
        }
    }
    assert output == expected
    assert actual == expected_status


# http://www.dummy.restapiexample.com/create
def test_instantiate_by_type_api_rest_post():
    data = {'service': 'stepA', 'type': 'api.rest.post',
            'url': 'http://dummy.restapiexample.com/api/v1/create',
            'payload': '{"name":"test","salary":"123","age":"23"}',
            'headers': {'User-Agent': 'Doc Engine'}
            }
    output = {}
    timestamp = int(time.time())
    actual = doc_engine.execute_step(data, output)
    expected_status = 'OK'
    expected = {
        'stepA': {
            'step_type': 'api.rest.post',
            'status': expected_status,
            'url': 'http://dummy.restapiexample.com/api/v1/create',
            'timestamp': timestamp,
            'end_time': int(time.time()),
            'json': '{"status":"success","data":{"name":"test","salary":"123","age":"23","id":0},'
                    '"message":"Successfully! Record has been added."}',
            'json_obj': {
                "status": "success",
                'message': 'Successfully! Record has been added.',
                "data": {
                    "name": "test",
                    "salary": "123",
                    "age": "23",
                    "id": 0
                }
            }
        }
    }
    # full object equality cannot be tested as a random id is generated
    expected_json = expected['stepA'].pop('json')
    expected_json_obj = expected['stepA'].pop('json_obj')
    actual_json = output['stepA'].pop('json')
    actual_json_obj = output['stepA'].pop('json_obj')
    assert output == expected
    assert json.loads(actual_json) == actual_json_obj
    assert json.loads(expected_json) == expected_json_obj
    generated_id = actual_json_obj['data'].pop('id')
    assert isinstance(generated_id, int)
    assert expected_json_obj['data'].pop('id') == 0
    assert actual_json_obj == expected_json_obj
    assert actual == expected_status


def test_execute_step_cmd_echo():
    data = {'service': 'stepA', 'type': 'cmd', 'cmd': "echo what's up doc ?"}
    output = {}
    timestamp = int(time.time())
    actual = doc_engine.execute_step(data, output)
    expected_status = 'OK'
    expected = {
        'stepA': {
            'step_type': 'cmd',
            'status': expected_status,
            'cmd': "echo what's up doc ?",
            'timestamp': timestamp,
            'end_time': int(time.time()),
            'stdout': "what's up doc ?",
            'stderr': ''
        }
    }
    assert output == expected
    assert actual == expected_status


def test_execute_step_cmd_exit():
    data = {'service': 'stepA', 'type': 'cmd', 'cmd': "exit 1"}
    output = {}
    timestamp = int(time.time())
    actual = doc_engine.execute_step(data, output)
    expected_status = 'KO'
    expected = {
        'stepA': {
            'step_type': 'cmd',
            'status': expected_status,
            'cmd': 'exit 1',
            'timestamp': timestamp,
            'end_time': int(time.time()),
            'stdout': '',
            'stderr': ''
        }
    }
    assert output == expected
    assert actual == expected_status
