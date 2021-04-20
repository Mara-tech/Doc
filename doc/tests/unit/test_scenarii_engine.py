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
                'service': 'stepA',
            }
        ]
    }
    actual = doc_engine.explode_next_if_condition(data)
    expected = {
        'scenario1': [
            {
                'service': 'stepA',
            }
        ]
    }
    assert actual == expected


def test_explode_condition_next_simple():
    data = {
        'scenario1': [
            {
                'service': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK'
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
                'service': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK'
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
                'service': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO'
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
                'service': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO'
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
                'service': 'stepA',
                'next-if': {
                    'OK, VALID': [
                        {
                            'service': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO'
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
                'service': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK'
                        }
                    ],
                    'VALID': [
                        {
                            'service': 'stepAOK'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO'
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
                'service': 'stepA',
                'property': 'toto',
                'next-if': {
                    'OK, VALID': [
                        {
                            'service': 'stepAOK',
                            'url': 'test.com'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO',
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
                'service': 'stepA',
                'property': 'toto',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK',
                            'url': 'test.com'
                        }
                    ],
                    'VALID': [
                        {
                            'service': 'stepAOK',
                            'url': 'test.com'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO',
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
                'service': 'stepA',
                'next-if': {
                    'OK, VALID': [
                        {
                            'service': 'stepAOK',
                            'next-if': {
                                'OK': [
                                    {
                                        'service': 'stepAOKOK'
                                    }
                                ],
                                'KO, ERROR': [
                                    {
                                        'service': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ]
                            }
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO',
                            'next-if': {
                                'OK': [
                                    {
                                        'service': 'stepAKOOK1'
                                    },
                                    {
                                        'service': 'stepAKOOK2'
                                    }
                                ],
                                'KO, UNDEFINED': [
                                    {
                                        'service': 'stepAKOKO'
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
                'service': 'stepA',
                'next-if': {
                    'OK': [
                        {
                            'service': 'stepAOK',
                            'next-if': {
                                'OK': [
                                    {
                                        'service': 'stepAOKOK'
                                    }
                                ],
                                'KO': [
                                    {
                                        'service': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ],
                                'ERROR': [
                                    {
                                        'service': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ]
                            }
                        }
                    ],
                    'VALID': [
                        {
                            'service': 'stepAOK',
                            'next-if': {
                                'OK': [
                                    {
                                        'service': 'stepAOKOK'
                                    }
                                ],
                                'KO': [
                                    {
                                        'service': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ],
                                'ERROR': [
                                    {
                                        'service': 'stepAOKKO',
                                        'someKey': 'theValue'
                                    }
                                ]
                            }
                        }
                    ],
                    'KO': [
                        {
                            'service': 'stepAKO',
                            'next-if': {
                                'OK': [
                                    {
                                        'service': 'stepAKOOK1'
                                    },
                                    {
                                        'service': 'stepAKOOK2'
                                    }
                                ],
                                'KO': [
                                    {
                                        'service': 'stepAKOKO'
                                    }
                                ],
                                'UNDEFINED': [
                                    {
                                        'service': 'stepAKOKO'
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
        'service': 'root',
        'next-if': {
                'OK': [
                    {
                        'service': 'nextOK'
                    }
                ],
                'KO': [
                    {
                        'service': 'nextKO'
                    }
                ]
            }
    }
    actual = doc_engine.next_steps(data, 'OK')
    expected = [{'service': 'nextOK'}]
    assert actual == expected
    actual = doc_engine.next_steps(data, 'KO')
    expected = [{'service': 'nextKO'}]
    assert actual == expected


def test_next_step_nested():
    data = {
        'service': 'root',
        'next-if': {
            'OK': [
                {
                    'service': 'nextOK',
                    'next-if': {
                        'OK': [
                            {
                                'service': 'nextOKnextOK1'
                            },
                            {
                                'service': 'nextOKnextOK2'
                            }
                        ],
                        'KO': [
                            {
                                'service': 'nextOKnextKO',
                                'next-if': {
                                    'OK': [
                                        {
                                            'service': 'nextOKnextKOnextOK'
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
                    'service': 'nextKO'
                }
            ]
        }
    }
    actual = doc_engine.next_steps(data, 'OK')
    expected = [
        {
            'service': 'nextOK',
            'next-if': {
                'OK': [
                    {
                        'service': 'nextOKnextOK1'
                    },
                    {
                        'service': 'nextOKnextOK2'
                    }
                ],
                'KO': [
                    {
                        'service': 'nextOKnextKO',
                        'next-if': {
                            'OK': [
                                {
                                    'service': 'nextOKnextKOnextOK'
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
            'service': 'nextOKnextOK1'
        },
        {
            'service': 'nextOKnextOK2'
        }
    ]
    assert actual == expected

    actual = doc_engine.next_steps(doc_engine.next_steps(data, 'OK')[0], 'KO')
    expected = [
        {
            'service': 'nextOKnextKO',
            'next-if': {
                'OK': [
                    {
                        'service': 'nextOKnextKOnextOK'
                    }
                ]
            }
        }
    ]
    assert actual == expected

    actual = doc_engine.next_steps(doc_engine.next_steps(doc_engine.next_steps(data, 'OK')[0], 'KO')[0], 'OK')
    expected = [{'service': 'nextOKnextKOnextOK'}]
    assert actual == expected
