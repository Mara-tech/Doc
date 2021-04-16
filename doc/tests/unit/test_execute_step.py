import doc_engine
import toolbox
import time


def test_toolbox_none():
    data = None
    actual = toolbox.find_tool(data)(data)
    expected = toolbox.DefaultStep(data)
    assert actual == expected


def test_instantiate_empty():
    data = {}
    actual = toolbox.find_tool(data)(data)
    expected = toolbox.DefaultStep(data)
    assert actual == expected


def test_instantiate_by_type_cmd():
    data = {'name': 'stepA', 'type': 'cmd', 'cmd': 'ls'}
    actual = toolbox.find_tool(data)(data)
    expected = toolbox.cmd.Step(data)
    assert actual == expected


def test_instantiate_by_type_api_rest():
    data = {'name': 'stepA', 'type': 'api.rest'}
    actual = toolbox.find_tool(data)(data)
    expected = toolbox.api.rest.Step(data)
    assert actual == expected


def test_execute_step_cmd():
    data = {'name': 'stepA', 'type': 'cmd', 'cmd': 'ls -a'}
    output = {}
    actual = doc_engine.execute_step(data, output)
    expected_status = 'KO'
    expected = {
        'step_type': 'cmd',
        'status': expected_status,
        'step_name': 'stepA',
        'timestamp': int(time.time())
    }
    assert actual == expected_status
    assert output == expected
