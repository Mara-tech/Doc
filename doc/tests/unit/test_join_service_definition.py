import doc_engine


def test_join_none_services():
    scenarii = {
        'scenarioA': [
            {
                'service': 'servA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'servB',
                            'propA': 'valueA'
                        }
                    ],
                }
            }
        ],
        'scenarioB': [
            {
                'service': 'servA',
            },
            {
                'service': 'servB',
                'propA': 'valueB'
            }
        ]
    }
    services = None
    actual = doc_engine.join_service_definition(scenarii, services)
    expected = scenarii
    assert actual == expected


def test_join_none_senarii():
    scenarii = None
    services = {
        'servA': {
            'type': 'cmd',
            'prop2': 'value2'
        },
        'servB': {
            'type': 'cmd',
            'propA': 'value3'
        }
    }
    actual = doc_engine.join_service_definition(scenarii, services)
    expected = {}
    assert actual == expected


def test_join():
    scenarii = {
        'scenarioA': [
            {
                'service': 'servA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'servB',
                            'propA': 'valueA'
                        }
                    ],
                }
            }
        ],
        'scenarioB': [
            {
                'service': 'servA',
                'prop2': 'value1'
            },
            {
                'service': 'servB',
                'propB': 'valueX'
            }
        ]
    }
    services = {
        'servA': {
            'type': 'cmd',
            'prop2': 'value2'
        },
        'servB': {
            'type': 'cmd',
            'propA': 'value3'
        }
    }
    actual = doc_engine.join_service_definition(scenarii, services)
    expected = {
        'scenarioA': [
            {
                'service': 'servA',
                'type': 'cmd',
                'prop2': 'value2',
                'next-if': {
                    'OK': [
                        {
                            'service': 'servB',
                            'type': 'cmd',
                            'propA': 'valueA'
                        }
                    ],
                }
            }
        ],
        'scenarioB': [
            {
                'service': 'servA',
                'type': 'cmd',
                'prop2': 'value1'
            },
            {
                'service': 'servB',
                'type': 'cmd',
                'propA': 'value3',
                'propB': 'valueX'
            }
        ]
    }
    assert actual == expected
