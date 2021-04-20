import app
import pytest


@pytest.fixture(autouse=True)
def setup_test():
    app.set_conf_filename(str(__file__).replace('.py', '.yml'))
    yield


# This is testing both join_service_definition() (test_join_service_definition.py)
# and explode_next_if_condition() (test_scenarii_engine.py)
# from a DocEngine instance built from yaml conf
def test_get_scenarii():
    actual = app.doc.scenarii
    expected = {
        'github-and-aws': [
            {
                'service': 'github-up',
                'type': 'api.rest.get',
                'url': '${github.${env}.base_url}',
                'next-if': {
                    'OK': [
                        {
                            'service': 'github-user-info',
                            'url': '${github.${env}.base_url}/users/${username}'
                        }
                    ],
                    'KO': [
                        {
                            'service': 'public-ip',
                            'type': 'api.get.info',
                            'url': 'https://api.ipify.org/?format=json',
                        }
                    ]
                }
            },
            {
                'service': 'aws-s3-ls',
                'type': 'cmd',
                'cmd': 'aws s3 ls',
                'next-if': {
                    'KO': [
                        {
                            'service': 'aws-cli-version',
                            'type': 'cmd',
                            'cmd': 'aws --version',
                        }
                    ],
                    'UNDEFINED': [
                        {
                            'service': 'aws-cli-version',
                            'type': 'cmd',
                            'cmd': 'aws --version',
                        }
                    ]
                }
            }
        ],
        'github-only': [
            {
                'service': 'github-up',
                'type': 'api.rest.get',
                'url': '${github.${env}.base_url}',
                'next-if': {
                    'OK': [
                        {
                            'service': 'github-user-info',
                            'url': '${github.${env}.base_url}/users/${username}'
                        }
                    ]
                }
            }
        ],
        'get-public-ip': [
            {
                'service': 'public-ip',
                'type': 'api.get.info',
                'url': 'https://api.ipify.org/?format=json',
            }
        ]
    }
    assert actual == expected
