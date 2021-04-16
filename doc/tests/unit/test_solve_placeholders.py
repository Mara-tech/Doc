import doc_engine


def test_parameter():
    actual = doc_engine.parameter('env')
    expected = '${env}'
    assert actual == expected


def test_merge_dicos():
    dico_1 = {'who': 'world'}
    dico_2 = {'name': 'person', 'job': 'cow-boy'}
    actual = doc_engine.merge_dicos(**dico_1, **dico_2, env='prod')
    expected = {'who': 'world',
                'name': 'person',
                'job': 'cow-boy',
                'env': 'prod'}
    assert actual == expected


def test_merge_and_flatten():
    dico_1 = {'who': 'world'}
    dico_2 = {
        'state': {
            'zip': 123,
            'city': ['San Andreas', 'Las Vegas']
        }
    }
    actual = doc_engine.merge_and_flatten(**dico_1, **dico_2, env='prod')
    expected = {'who': 'world',
                'state.zip': 123,
                'state.city': ['San Andreas', 'Las Vegas'],
                'env': 'prod'}
    assert actual == expected


def test_replace():
    data = 'hello ${who}'
    dico = {'who': 'world'}
    actual = doc_engine.replace(data, **dico)
    expected = 'hello world'
    assert actual == expected


def test_single_replace():
    data = 'hello ${who}'
    dico = {'who': 'world'}
    actual = doc_engine.solve_placeholders(data, **dico)
    expected = 'hello world'
    assert actual == expected


def test_multiple_replace():
    data = '${what} ${who}'
    dico = {'who': 'world', 'what': 'goodbye'}
    actual = doc_engine.solve_placeholders(data, **dico)
    expected = 'goodbye world'
    assert actual == expected


def test_nested_replace():
    data = '${my.${stage}.url}'
    dico = {'my.prod.url': 'toto', 'my.dev.url': 'tata'}
    actual = doc_engine.solve_placeholders(data, **dico, stage='dev')
    expected = 'tata'
    assert actual == expected
    actual = doc_engine.solve_placeholders(data, **dico, stage='prod')
    expected = 'toto'
    assert actual == expected


def test_list_single_replace():
    data = ['hello ${who}', 'goodbye ${who}', 'alright']
    dico = {'who': 'world'}
    actual = doc_engine.solve_placeholders(data, **dico)
    expected = ['hello world', 'goodbye world', 'alright']
    assert actual == expected


def test_list_multiple_replace():
    data = ['${what} ${who}', '${where} ${who}', 'alright']
    dico = {'who': 'world', 'what': 'goodbye', 'where': 'earth'}
    actual = doc_engine.solve_placeholders(data, **dico)
    expected = ['goodbye world', 'earth world', 'alright']
    assert actual == expected


def test_list_nested_replace():
    data = ['${my.${stage}.url}', '${my.${stage}.login}']
    dico = {'my.prod.url': 'toto', 'my.dev.url': 'tata',
            'my.prod.login': 'admin@admin', 'my.dev.login': 'admin'}

    actual = doc_engine.solve_placeholders(data, **dico, stage='dev')
    expected = ['tata', 'admin']
    assert actual == expected
    actual = doc_engine.solve_placeholders(data, **dico, stage='prod')
    expected = ['toto', 'admin@admin']
    assert actual == expected


def test_list_deep_nested_replace():
    data = [{'aDictKey': '${my.${stage}.url}'}, '${my.${stage}.login}']
    dico = {'my.prod.url': 'toto', 'my.dev.url': 'tata',
            'my.prod.login': 'admin@admin', 'my.dev.login': 'admin'}

    actual = doc_engine.solve_placeholders(data, **dico, stage='dev')
    expected = [{'aDictKey': 'tata'}, 'admin']
    assert actual == expected
    actual = doc_engine.solve_placeholders(data, **dico, stage='prod')
    expected = [{'aDictKey': 'toto'}, 'admin@admin']
    assert actual == expected


def test_dict_single_replace():
    data = {'url': 'hello ${who}',
            'login': 'goodbye ${who}',
            'message': 'alright'}
    dico = {'who': 'world'}
    actual = doc_engine.solve_placeholders(data, **dico)
    expected = {'url': 'hello world',
                'login': 'goodbye world',
                'message': 'alright'}
    assert actual == expected


def test_dict_multiple_replace():
    data = {'url': '${protocol}://${host}:${port}',
            'login': '${who}',
            'message': 'alright'}
    dico = {'who': 'admin'}
    dico_tech = {'protocol': 'http',
                 'host': 'example.com',
                 'port': '8080'}
    actual = doc_engine.solve_placeholders(data, **dico, **dico_tech)
    expected = {'url': 'http://example.com:8080',
                'login': 'admin',
                'message': 'alright'}
    assert actual == expected


def test_dict_nested_replace():
    data = {'url': '${my.${stage}.url}',
            'login': '${my.${stage}.login}'}

    dico = {'my.prod.url': '${prod.protocol}://${prod.host}:${prod.port}',
            'my.dev.url': '${dev.protocol}://${dev.host}:${dev.port}',
            'my.prod.login': 'admin@${prod.host}', 'my.dev.login': 'admin'}

    dico_properties = {
        'prod':
            {
                'protocol': 'https',
                'host': 'example.com',
                'port': 443
            },
        'dev':
            {
                'protocol': 'http',
                'host': 'test.com',
                'port': 8080},
    }
    actual = doc_engine.solve_placeholders(data, **dico, **dico_properties, stage='dev')
    expected = {'url': 'http://test.com:8080',
                'login': 'admin'}
    assert actual == expected

    actual = doc_engine.solve_placeholders(data, **dico, **dico_properties, stage='prod')
    expected = {'url': 'https://example.com:443',
                'login': 'admin@example.com'}
    assert actual == expected


def test_dict_deep_nested_replace():
    data = {
        'someData': {
            'someChild': {
                'url': '${my.${stage}.url}',
                'login': '${my.${stage}.login}'
            },
            'anotherChild': {
                'url-bis': '${my.${stage}.url}',
                'login-bis': '${my.${stage}.login}'
            }
        }
    }

    dico = {'my.prod.url': '${prod.protocol}://${prod.host}:${prod.port}',
            'my.dev.url': '${dev.protocol}://${dev.host}:${dev.port}',
            'my.prod.login': 'admin@${prod.host}', 'my.dev.login': 'admin'}

    dico_properties = {
        'prod':
            {
                'protocol': 'https',
                'host': 'example.com',
                'port': 443
            },
        'dev':
            {
                'protocol': 'http',
                'host': 'test.com',
                'port': 8080},
    }
    actual = doc_engine.solve_placeholders(data, **dico, **dico_properties, stage='dev')
    expected = {
        'someData': {
            'someChild': {
                'url': 'http://test.com:8080',
                'login': 'admin'
            },
            'anotherChild': {
                'url-bis': 'http://test.com:8080',
                'login-bis': 'admin'
            }
        }
    }
    assert actual == expected

    actual = doc_engine.solve_placeholders(data, **dico, **dico_properties, stage='prod')
    expected = {
        'someData': {
            'someChild': {
                'url': 'https://example.com:443',
                'login': 'admin@example.com'
            },
            'anotherChild': {
                'url-bis': 'https://example.com:443',
                'login-bis': 'admin@example.com'
            }
        }
    }
    assert actual == expected
