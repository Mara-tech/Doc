import doc_engine


def test_explode_condition_empty():
    data = {}
    actual = doc_engine.explode_next_if_condition(data)
    expected = {}
    assert actual == expected


def test_explode_condition_simple():
    data = {
        'scenario1': [
            {
                'name': 'stepA',
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'name': 'stepA',
            }
        ]
    }
    assert actual == expected


def test_explode_condition_next_simple():
    data = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK'
                        }
                    ]
                }
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK'
                        }
                    ]
                }
            }
        ]
    }
    assert actual == expected


def test_explode_condition_next_double():
    data = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO'
                        }
                    ]
                }
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO'
                        }
                    ]
                }
            }
        ]
    }
    assert actual == expected


def test_explode_condition_explode():
    data = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK, VALID': [
                        {
                            'name': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO'
                        }
                    ]
                }
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK'
                        }
                    ],
                    'VALID': [
                        {
                            'name': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO'
                        }
                    ]
                }
            }
        ]
    }
    assert actual == expected


def test_explode_condition_explode_and_third_properties():
    data = {
        'scenario1': [
            {
                'name': 'stepA',
                'property': 'toto',
                'next-if': {
                    'OK, VALID': [
                        {
                            'name': 'stepAOK',
                            'url': 'test.com'
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO',
                            'tree': {
                                'propA': 'aa',
                                'propB': 'bb'
                            }
                        }
                    ]
                }
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'name': 'stepA',
                'property': 'toto',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK',
                            'url': 'test.com'
                        }
                    ],
                    'VALID': [
                        {
                            'name': 'stepAOK',
                            'url': 'test.com'
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO',
                            'tree': {
                                'propA': 'aa',
                                'propB': 'bb'
                            }
                        }
                    ]
                }
            }
        ]
    }
    assert actual == expected


def test_explode_condition_explode_nested():
    data = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK, VALID': [
                        {
                            'name': 'stepAOK',
                            'next-if': {
                                'OK': [
                                    {
                                        'name': 'stepAOKOK'
                                    }
                                ],
                                'KO, ERROR': [
                                    {
                                        'name': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ]
                            }
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO',
                            'next-if': {
                                'OK': [
                                    {
                                        'name': 'stepAKOOK1'
                                    },
                                    {
                                        'name': 'stepAKOOK2'
                                    }
                                ],
                                'KO, UNDEFINED': [
                                    {
                                        'name': 'stepAKOKO'
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'name': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'name': 'stepAOK',
                            'next-if': {
                                'OK': [
                                    {
                                        'name': 'stepAOKOK'
                                    }
                                ],
                                'KO': [
                                    {
                                        'name': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ],
                                'ERROR': [
                                    {
                                        'name': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ]
                            }
                        }
                    ],
                    'VALID': [
                        {
                            'name': 'stepAOK',
                            'next-if': {
                                'OK': [
                                    {
                                        'name': 'stepAOKOK'
                                    }
                                ],
                                'KO': [
                                    {
                                        'name': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ],
                                'ERROR': [
                                    {
                                        'name': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ]
                            }
                        }
                    ],
                    'KO': [
                        {
                            'name': 'stepAKO',
                            'next-if': {
                                'OK': [
                                    {
                                        'name': 'stepAKOOK1'
                                    },
                                    {
                                        'name': 'stepAKOOK2'
                                    }
                                ],
                                'KO': [
                                    {
                                        'name': 'stepAKOKO'
                                    }
                                ],
                                'UNDEFINED': [
                                    {
                                        'name': 'stepAKOKO'
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
    assert actual == expected


def test_next_step_none():
    data = {}
    actual = doc_engine.next_steps(data, None)
    expected = []
    assert actual == expected


def test_next_step_empty():
    data = {}
    actual = doc_engine.next_steps(data, 'OK')
    expected = []
    assert actual == expected


def test_next_step_simple():
    data = {
        'name': 'root',
        'next-if': {
                'OK': [
                    {
                        'name': 'nextOK'
                    }
                ],
                'KO': [
                    {
                        'name': 'nextKO'
                    }
                ]
            }
    }
    actual = doc_engine.next_steps(data, 'OK')
    expected = [{'name': 'nextOK'}]
    assert actual == expected
    actual = doc_engine.next_steps(data, 'KO')
    expected = [{'name': 'nextKO'}]
    assert actual == expected


def test_next_step_nested():
    data = {
        'name': 'root',
        'next-if': {
            'OK': [
                {
                    'name': 'nextOK',
                    'next-if': {
                        'OK': [
                            {
                                'name': 'nextOKnextOK1'
                            },
                            {
                                'name': 'nextOKnextOK2'
                            }
                        ],
                        'KO': [
                            {
                                'name': 'nextOKnextKO',
                                'next-if': {
                                    'OK': [
                                        {
                                            'name': 'nextOKnextKOnextOK'
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            ],
            'KO': [
                {
                    'name': 'nextKO'
                }
            ]
        }
    }
    actual = doc_engine.next_steps(data, 'OK')
    expected = [
        {
            'name': 'nextOK',
            'next-if': {
                'OK': [
                    {
                        'name': 'nextOKnextOK1'
                    },
                    {
                        'name': 'nextOKnextOK2'
                    }
                ],
                'KO': [
                    {
                        'name': 'nextOKnextKO',
                        'next-if': {
                            'OK': [
                                {
                                    'name': 'nextOKnextKOnextOK'
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
    assert actual == expected

    actual = doc_engine.next_steps(actual[0], 'OK')
    expected = [
        {
            'name': 'nextOKnextOK1'
        },
        {
            'name': 'nextOKnextOK2'
        }
    ]
    assert actual == expected

    actual = doc_engine.next_steps(doc_engine.next_steps(data, 'OK')[0], 'KO')
    expected = [
        {
            'name': 'nextOKnextKO',
            'next-if': {
                'OK': [
                    {
                        'name': 'nextOKnextKOnextOK'
                    }
                ]
            }
        }
    ]
    assert actual == expected

    actual = doc_engine.next_steps(doc_engine.next_steps(doc_engine.next_steps(data, 'OK')[0], 'KO')[0], 'OK')
    expected = [{'name': 'nextOKnextKOnextOK'}]
    assert actual == expected
