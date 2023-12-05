from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import pytest


@pytest.fixture
def test_file_name():
    return "test.txt"


@pytest.fixture
def test_file_content():
    return b"content"


@pytest.fixture
def test_file_in_storage(test_file_name, test_file_content):
    path = default_storage.save(test_file_name, ContentFile(test_file_content))
    yield path
    default_storage.delete(test_file_name)


def test_default_storage(test_file_name, test_file_content, test_file_in_storage):
    assert default_storage.exists(test_file_name)
    assert default_storage.open(test_file_name).read() == test_file_content
