"""info CLI command implementation."""
# dem/cli/command/info_cmd.py

from dem.core.tool_images import ToolImage
from dem.core.dev_env import DevEnv, DevEnv
from dem.cli.console import stdout, stderr
from dem.core.platform import Platform
from rich.table import Table
import typer

image_status_messages = {
    ToolImage.NOT_AVAILABLE: "[red]Error: not available![/]",
    ToolImage.LOCAL_ONLY: "Local",
    ToolImage.REGISTRY_ONLY: "Registry",
    ToolImage.LOCAL_AND_REGISTRY: "Local and Registry",
}

def print_local_dev_env_info(dev_env: DevEnv) -> None:
    """ Print information about the given local Development Environment.
    
        Args:
            dev_env -- the Development Environment to print information about
    """
    tool_info_table = Table()
    tool_info_table.add_column("Image")
    tool_info_table.add_column("Availability")

    for tool_image in sorted(dev_env.tool_images, key=lambda x: x.name):
        tool_info_table.add_row(tool_image.name,
                                image_status_messages[tool_image.availability])
    if dev_env.is_installed:
        installation_status = "[green]Installed[/]"
    else:
        installation_status = "Not installed"
    stdout.print(f"\n[bold]Development Environment: {dev_env.name}[/]\n")
    stdout.print(f"Installation state: {installation_status}\n")
    stdout.print(tool_info_table)

    if dev_env.is_installed and dev_env.get_tool_image_status() == DevEnv.Status.REINSTALL_NEEDED:
        stderr.print("\n[red]Error: Incomplete local install! The Dev Env must be reinstalled![/]")

    if dev_env.get_tool_image_status() == DevEnv.Status.UNAVAILABLE_IMAGE:
        stderr.print("\n[red]Error: Required image could not be found either locally or in the registry![/]")

def local_info(platform: Platform, dev_env_name: str) -> None:
    """ Gather and print information about the given local Development Environment.
    
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment to print information about

        Raises:
            typer.Abort -- if the Development Environment is unknown
    """
    platform.assign_tool_image_instances_to_all_dev_envs()

    dev_env = platform.get_dev_env_by_name(dev_env_name)

    if dev_env is None:
        stderr.print(f"[red]Error: Unknown Development Environment: {dev_env_name}[/]\n")
        raise typer.Abort()

    print_local_dev_env_info(dev_env)

def print_cat_dev_env_info(dev_env: DevEnv, cat_name: str) -> None:
    """ Print information about the given catalog Development Environment.
    
        Args:
            dev_env -- the Development Environment to print information about
            cat_name -- the name of the catalog the Development Environment belongs to
    """
    tool_info_table = Table()
    tool_info_table.add_column("Image")
    tool_info_table.add_column("Availability")

    for tool_image in sorted(dev_env.tool_images, key=lambda x: x.name):
        tool_info_table.add_row(tool_image.name,
                                image_status_messages[tool_image.availability])
    stdout.print(f"\n[bold]Development Environment: {dev_env.name}[/]\n")
    stdout.print(f"Catalog: {cat_name}\n")
    stdout.print(tool_info_table)

    if dev_env.get_tool_image_status() == DevEnv.Status.UNAVAILABLE_IMAGE:
        stderr.print("\n[red]Error: Required image could not be found in the registry![/]")
    
def cat_dev_env_info(platform: Platform, dev_env_name: str, selected_cats: list[str]) -> None:
    """ Gather and print information about the given catalog Development Environment.
    
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment to print information about
            selected_cats -- the selected catalog names, empty list means all catalogs
    """
    for catalog in platform.dev_env_catalogs.catalogs:
        if catalog.name in selected_cats or not selected_cats:
            catalog.request_dev_envs()
            dev_env = catalog.get_dev_env_by_name(dev_env_name)
            if dev_env:
                dev_env.assign_tool_image_instances(platform.tool_images)
                print_cat_dev_env_info(dev_env, catalog.name)
                break
    else:
        stderr.print(f"[red]Error: Unknown Development Environment: {dev_env_name}[/]\n")

def selected_cats_info(platform: Platform, dev_env_name: str, selected_cats: list[str]) -> None:
    """ Print information about the given Development Environment from the selected catalogs.
    
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment to print information about
            selected_cats -- the selected catalog names
            
        Raises:
            typer.Abort -- if the selected catalog is unknown
    """
    available_cats = set([cat.name for cat in platform.dev_env_catalogs.catalogs])
    selected_cats = set(selected_cats)

    if not selected_cats.issubset(available_cats):
        stderr.print(f"[red]Error: Unknown catalog(s): {', '.join(selected_cats - available_cats)}[/]\n")
        raise typer.Abort()

    cat_dev_env_info(platform, dev_env_name, selected_cats)

def all_cats_info(platform: Platform, dev_env_name: str) -> None:
    """ Print information about the given Development Environment from all catalogs.
    
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment to print information about
    """
    cat_dev_env_info(platform, dev_env_name, [])

def execute(platform: Platform, arg_dev_env_name: str, cat: bool, selected_cats: list[str]) -> None:
    """ Print information about the given Development Environment.
    
        Args:
            platform -- the platform
            arg_dev_env_name -- the name of the Development Environment to print information about
            cat -- the flag to print information about the Development Environment from the catalogs
            selected_cats -- the selected catalog names

        Raises:
            typer.Abort -- if the Development Environment is unknown or if the selected catalog is 
                           unknown
    """
    if not cat:
        local_info(platform, arg_dev_env_name)
    elif selected_cats:
        selected_cats_info(platform, arg_dev_env_name, selected_cats)
    else:
        all_cats_info(platform, arg_dev_env_name)