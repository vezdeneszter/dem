"""Unit tests for the Dev Env."""
# tests/core/test_dev_env.py

# Unit under test:
import dem.core.dev_env as dev_env

# Test framework
from unittest.mock import MagicMock, patch
import pytest

from typing import Any

def test_DevEnv() -> None:
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
        "tools": [MagicMock()]
    }

    # Run unit under test
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Check expectations
    assert test_dev_env.name is test_descriptor["name"]
    assert test_dev_env.tool_image_descriptors is test_descriptor["tools"]

@patch("dem.core.dev_env.json.load")
@patch("dem.core.dev_env.open")
@patch("dem.core.dev_env.os.path.exists")
def test_DevEnv_with_descriptor_path(mock_path_exists: MagicMock, mock_open: MagicMock,
                                     mock_json_load: MagicMock) -> None:
    # Test setup
    test_descriptor_path = "/path/to/descriptor.json"
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
        "tools": [MagicMock()]
    }
    mock_path_exists.return_value = True
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    mock_json_load.return_value = test_descriptor
    
    # Run unit under test
    test_dev_env = dev_env.DevEnv(descriptor_path=test_descriptor_path)

    # Check expectations
    assert test_dev_env.name is test_descriptor["name"]
    assert test_dev_env.tool_image_descriptors is test_descriptor["tools"]
    assert test_dev_env.is_installed is True

    mock_path_exists.assert_called_once_with(test_descriptor_path)
    mock_open.assert_called_once_with(test_descriptor_path, "r")
    mock_json_load.assert_called_once_with(mock_file)

def test_DevEnv_with_descriptor_path_not_existing() -> None:
    # Test setup
    test_descriptor_path = "/path/to/descriptor.json"
    mock_path_exists = MagicMock()
    mock_path_exists.return_value = False

    with pytest.raises(FileNotFoundError) as exc_info:
        # Run unit under test
        test_dev_env = dev_env.DevEnv(descriptor_path=test_descriptor_path)

        # Check expectations
        assert str(exc_info.value) == f"dev_env_descriptor.json doesn't exist."

        mock_path_exists.assert_called_once_with(test_descriptor_path)

def test_DevEnv_with_descriptor_and_descriptor_path() -> None:
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
        "tools": [MagicMock()]
    }
    test_descriptor_path = "/path/to/descriptor.json"

    with pytest.raises(ValueError) as exc_info:
        # Run unit under test
        test_dev_env = dev_env.DevEnv(descriptor=test_descriptor, descriptor_path=test_descriptor_path)

        # Check expectations
        assert str(exc_info.value) == "Only one of the arguments can be not None."

def test_DevEnv_assign_tool_image_instances() -> None:
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
        "tools": [
            {
                "image_name": "test_image_name1",
                "image_version": "test_image_tag1"
            },
            {
                "image_name": "test_image_name2",
                "image_version": "test_image_tag2"
            },
            {
                "image_name": "test_image_name3",
                "image_version": "test_image_tag3"
            }
        ]
    }
    test_dev_env = dev_env.DevEnv(test_descriptor)

    mock_tool_images = MagicMock()
    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "test_image_name1:test_image_tag1"
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "test_image_name2:test_image_tag2"
    mock_tool_image3 = MagicMock()
    mock_tool_image3.name = "test_image_name3:test_image_tag3"
    mock_tool_image4 = MagicMock()
    mock_tool_image4.name = "test_image_name4:test_image_tag4"
    mock_tool_images.all_tool_images = {
        "test_image_name1:test_image_tag1": mock_tool_image1,
        "test_image_name2:test_image_tag2": mock_tool_image2,
        "test_image_name3:test_image_tag3": mock_tool_image3,
        "test_image_name4:test_image_tag4": mock_tool_image4
    }

    # Run unit under test
    test_dev_env.assign_tool_image_instances(mock_tool_images)

    # Check expectations
    assert len(test_dev_env.tool_images) == 3
    for tool_image in test_dev_env.tool_images:
        assert tool_image is mock_tool_images.all_tool_images[tool_image.name]

@patch.object(dev_env.DevEnv, "__init__")
def test_DevEnv_get_tool_image_status(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_dev_env = dev_env.DevEnv(MagicMock())
    mock_tool_image1 = MagicMock()
    mock_tool_image1.availability = dev_env.ToolImage.LOCAL_AND_REGISTRY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.availability = dev_env.ToolImage.LOCAL_ONLY
    test_dev_env.tool_images = [
        mock_tool_image1,
        mock_tool_image2
    ]

    # Run unit under test
    actual_status = test_dev_env.get_tool_image_status()

    # Check expectations
    assert actual_status == dev_env.DevEnv.Status.OK

    mock___init__.assert_called_once()

@patch.object(dev_env.DevEnv, "__init__")
def test_DevEnv_get_tool_image_status_unavailable_image(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_dev_env = dev_env.DevEnv(MagicMock())
    mock_tool_image1 = MagicMock()
    mock_tool_image1.availability = dev_env.ToolImage.NOT_AVAILABLE
    mock_tool_image2 = MagicMock()
    mock_tool_image2.availability = dev_env.ToolImage.LOCAL_ONLY
    test_dev_env.tool_images = [
        mock_tool_image1,
        mock_tool_image2
    ]

    # Run unit under test
    actual_status = test_dev_env.get_tool_image_status()

    # Check expectations
    assert actual_status == dev_env.DevEnv.Status.UNAVAILABLE_IMAGE

    mock___init__.assert_called_once()

@patch.object(dev_env.DevEnv, "__init__")
def test_DevEnv_get_tool_image_status_reinstall_needed(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_dev_env = dev_env.DevEnv(MagicMock())
    mock_tool_image1 = MagicMock()
    mock_tool_image1.availability = dev_env.ToolImage.REGISTRY_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.availability = dev_env.ToolImage.LOCAL_ONLY
    test_dev_env.tool_images = [
        mock_tool_image1,
        mock_tool_image2
    ]

    # Run unit under test
    actual_status = test_dev_env.get_tool_image_status()

    # Check expectations
    assert actual_status == dev_env.DevEnv.Status.REINSTALL_NEEDED

    mock___init__.assert_called_once()

def test_DevEnv_get_deserialized_is_installed_true() -> None:
    # Test setup
    test_descriptor: dict[str, Any] = {
        "name": "test_name",
        "installed": "True",
        "tools": [
            {
                "image_name": "test_image_name1",
                "image_version": "test_image_tag1"
            },
            {
                "image_name": "test_image_name2",
                "image_version": "test_image_tag2"
            },
            {
                "image_name": "test_image_name3",
                "image_version": "test_image_tag3"
            },
            {
                "image_name": "test_image_name4",
                "image_version": "test_image_tag4"
            },
        ]
    }
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Run unit under test
    actual_deserialized_dev_env: dict[str, Any] = test_dev_env.get_deserialized()

    # Check expectations
    assert test_descriptor == actual_deserialized_dev_env

def test_DevEnv_get_deserialized_is_installed_false() -> None:
    # Test setup
    test_descriptor: dict[str, Any] = {
        "name": "test_name",
        "installed": "False",
        "tools": [
            {
                "image_name": "test_image_name1",
                "image_version": "test_image_tag1"
            },
            {
                "image_name": "test_image_name2",
                "image_version": "test_image_tag2"
            },
            {
                "image_name": "test_image_name3",
                "image_version": "test_image_tag3"
            },
            {
                "image_name": "test_image_name4",
                "image_version": "test_image_tag4"
            },
        ]
    }
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Run unit under test
    actual_deserialized_dev_env: dict[str, Any] = test_dev_env.get_deserialized()

    # Check expectations
    assert test_descriptor == actual_deserialized_dev_env

def test_DevEnv_get_deserialized_omit_is_installed() -> None:
    # Test setup
    test_descriptor: dict[str, Any] = {
        "name": "test_name",
        "installed": "True",
        "tools": [
            {
                "image_name": "test_image_name1",
                "image_version": "test_image_tag1"
            },
            {
                "image_name": "test_image_name2",
                "image_version": "test_image_tag2"
            },
            {
                "image_name": "test_image_name3",
                "image_version": "test_image_tag3"
            },
            {
                "image_name": "test_image_name4",
                "image_version": "test_image_tag4"
            },
        ]
    }
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Run unit under test
    actual_deserialized_dev_env: dict[str, Any] = test_dev_env.get_deserialized(True)

    # Check expectations
    del test_descriptor["installed"]
    assert test_descriptor == actual_deserialized_dev_env

@patch("dem.core.dev_env.open")
@patch("dem.core.dev_env.json.dump")
@patch.object(dev_env.DevEnv, "get_deserialized")
@patch.object(dev_env.DevEnv, "__init__")
def test_DevEnv_export(mock___init__: MagicMock, mock_get_deserialized: MagicMock, 
                       mock_json_dump: MagicMock, mock_open: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_deser = MagicMock()
    mock_get_deserialized.return_value = mock_deser

    test_path = "/home/test.json"

    test_dev_env = dev_env.DevEnv(MagicMock())

    # Run unit under test
    test_dev_env.export(test_path)

    # Check expectations
    mock_open.assert_called_once_with(test_path, "w")
    mock_get_deserialized.assert_called_once_with(True)
    mock_json_dump.assert_called_once_with(mock_deser, mock_file, indent=4)