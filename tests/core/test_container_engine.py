"""Unit test for the image_management."""
# tests/core/test_image_management.py

# Unit under test:
import dem.core.container_engine as container_engine

# Test framework
from unittest.mock import patch, MagicMock, call

class mockImage:
    def __init__(self, tags: list[str]) -> None:
        self.tags = tags

def _get_test_image_tags_as_images(test_image_tags):
    test_images = []
    for test_image_tag in test_image_tags:
        test_images.append(mockImage(test_image_tag))
    return test_images

@patch("docker.from_env")
def test_get_local_tool_images(mock_docker_from_env):
    # Test setup
    test_image_tags = [
    ["alpine:latest"],
    [""],
    ["axemsolutions/make_gnu_arm:v1.0.0"],
    ["axemsolutions/stlink_org:latest", "axemsolutions/stlink_org:v1.0.0"],
    ["axemsolutions/cpputest:latest"],
    ["axemsolutions/make_gnu_arm:latest", "axemsolutions/make_gnu_arm:v0.1.0", "axemsolutions/make_gnu_arm:v1.1.0"],
    ["debian:latest"],
    ["ubuntu:latest"],
    ["hello-world:latest"],
    [""],
    ]
    expected_image_tags = [
    "alpine:latest",
    "axemsolutions/make_gnu_arm:v1.0.0",
    "axemsolutions/stlink_org:latest", 
    "axemsolutions/stlink_org:v1.0.0",
    "axemsolutions/cpputest:latest",
    "axemsolutions/make_gnu_arm:latest", 
    "axemsolutions/make_gnu_arm:v0.1.0", 
    "axemsolutions/make_gnu_arm:v1.1.0",
    "debian:latest",
    "ubuntu:latest",
    "hello-world:latest",
    ]
    mock_docker_client = MagicMock()
    mock_docker_client.images.list.return_value = _get_test_image_tags_as_images(test_image_tags)
    mock_docker_from_env.return_value = mock_docker_client

    # Run unit under test
    container_engine_obj = container_engine.ContainerEngine()
    actual_image_tags = container_engine_obj.get_local_tool_images()

    # Check expectations
    assert expected_image_tags == actual_image_tags

    mock_docker_from_env.assert_called_once()
    mock_docker_client.images.list.assert_called_once()

@patch("docker.from_env")
def test_get_local_tool_images_when_none_available(mock_docker_from_env):
    # Test setup
    test_image_tags = []
    expected_image_tags = []
    fake_docker_client = MagicMock()
    mock_docker_from_env.return_value = fake_docker_client
    fake_docker_client.images.list.return_value = _get_test_image_tags_as_images(test_image_tags)

    # Run unit under test
    container_engine_obj = container_engine.ContainerEngine()
    actual_image_tags = container_engine_obj.get_local_tool_images()

    # Check expectations
    assert expected_image_tags == actual_image_tags

    mock_docker_from_env.assert_called_once()
    fake_docker_client.images.list.assert_called_once()

@patch.object(container_engine.Core, "user_output")
@patch("dem.core.container_engine.docker.from_env")
def test_pull(mock_docker_from_env, mock_user_output):
    # Test setup
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client
    test_image_to_pull = "test_image:latest"
    mock_response = MagicMock()
    mock_docker_client.api.pull.return_value = mock_response

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.pull(test_image_to_pull)

    # Check expectations
    mock_docker_from_env.assert_called_once()
    mock_docker_client.api.pull.assert_called_once_with(test_image_to_pull, stream=True, 
                                                        decode=True)
    mock_user_output.progress_generator.assert_called_once_with(mock_response)

@patch.object(container_engine.Core, "user_output")
@patch("docker.from_env")
def test_run(mock_from_env, mock_user_output):
    # Test setup
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client
    test_image = "test_image"
    test_workspace_path = "test_workspace_path"
    test_command = "test_command"
    test_privileged = False
    mock_container = MagicMock()
    mock_docker_client.containers.run.return_value = mock_container
    fake_log_lines = [
        b"log_line_1\n", 
        b"log_line_2\n",
    ]
    mock_container.logs.return_value = fake_log_lines

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.run(test_image, test_workspace_path, test_command, test_privileged)

    # Check expectations
    expected_volumes = [test_workspace_path + ":/work"]
    mock_docker_client.containers.run.assert_called_once_with(test_image, command=test_command, 
                                                              auto_remove=True, 
                                                              privileged=test_privileged,
                                                              stderr=True, volumes=expected_volumes,
                                                              detach=True)
    mock_container.logs.assert_called_once_with(stream=True)
    calls = [
        call("log_line_1"), 
        call("log_line_2"),
    ]
    mock_user_output.msg.assert_has_calls(calls)

@patch("docker.from_env")
def test_remove(mock_from_env):
    # Test setup
    fake_docker_client = MagicMock()
    mock_from_env.return_value = fake_docker_client
    test_image_to_remove = "test_image_to_remove:latest"

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.remove(test_image_to_remove)

    # Check expectations
    fake_docker_client.images.remove.assert_called_once_with(test_image_to_remove)

@patch("docker.from_env")
def test_search(mock_from_env):
    # Test setup
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client
    test_registry = "test_registry"
    test_repositories = [
        {
            "name": "repo1"
        },
        {
            "name": "repo2"
        },
    ]
    mock_docker_client.images.search.return_value = test_repositories

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    actual_registry_image_list = test_container_engine.search(test_registry)

    # Check expectations
    mock_docker_client.images.search.assert_called_once_with(test_registry)

    expected_registry_image_list = ["repo1", "repo2"]
    assert actual_registry_image_list == expected_registry_image_list