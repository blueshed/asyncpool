""" Our test fixtures """

from pytest import fixture


@fixture
def data():
    """ our request objects """
    return ['romeo', 'julliet', 'mercucio']
