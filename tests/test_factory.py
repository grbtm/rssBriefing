import os
from donkey_package import create_app


def test_config():

    assert not create_app().testing

    assert create_app(config_class="config.TestingConfig").testing
