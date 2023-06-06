"""Entry point for dem."""
# dem/__main__.py

from dem import __command__
from dem.cli.console import stderr, stdout
from dem.core.exceptions import RegistryError
<<<<<<< HEAD
<<<<<<< HEAD
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvSetup
=======
from dem.core.dev_env_setup import DevEnvLocalSetup
>>>>>>> 5353bc3 (Started to work on the core callback mechanism.)
=======
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvSetup
>>>>>>> 987018c (Callback mechanism added for the progress bar. Further tweaks in the output design.)
import dem.cli.main, dem.cli.core_cb
import docker.errors

def main():
    """ Entry point for the CLI application"""
<<<<<<< HEAD
<<<<<<< HEAD

    # Set callback for core modules.
    DevEnvLocalSetup.invalid_json_cb = dem.cli.core_cb.user_confirm_cb
    DevEnvLocalSetup.msg_cb = dem.cli.core_cb.msg_cb
<<<<<<< HEAD
    DevEnvLocalSetup.pull_progress_cb = dem.cli.core_cb.pull_progress_cb
=======
=======

    # Set callback for core modules.
>>>>>>> 763e6e6 (Minor fixes. Test cases added.)
    DevEnvLocalSetup.core_cb = dem.cli.core_cb.core_cb
>>>>>>> 5353bc3 (Started to work on the core callback mechanism.)
=======
    DevEnvSetup.pull_progress_cb = dem.cli.core_cb.pull_progress_cb
>>>>>>> 987018c (Callback mechanism added for the progress bar. Further tweaks in the output design.)

    try:
        dem.cli.main.typer_cli(prog_name=__command__)
    except LookupError as e:
        stderr.print("[red]" + str(e) + "[/]")
    except RegistryError as e:
        stderr.print("[red]" + str(e) + "[/]")
    except docker.errors.DockerException as e:
        stderr.print("[red]" + str(e) + "[/]")

        if "Permission denied" in str(e):
            stdout.print("\nHint: Is your user part of the docker group?")
        elif "invalid reference format" in str(e):
            stdout.print("\nHint: The input repository might not exist in the registry.")
        else:
            stdout.print("\nHint: Probably something is wrong with your Docker Engine installation. Try to reinstall it.")

# Call the main() when run as `python -m`
if __name__ == "__main__":
    main()
