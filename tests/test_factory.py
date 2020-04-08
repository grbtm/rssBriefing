from rssbriefing import create_app


def test_config():
    """Test create_app with and without test_config. """
    assert not create_app().testing

    assert create_app({"TESTING": True}).testing
