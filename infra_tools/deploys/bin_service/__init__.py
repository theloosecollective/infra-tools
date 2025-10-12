from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import files, systemd

# Deploy the systemd unit file from template
TEMPLATE_DIR = Path(__file__).parent / "templates"

@deploy("Binary Service")
def install(
    service_name: str,
    description: str,
    bin_path: str,
    env_file_path: str,
    args: str = "",
    working_dir: str | None = None,
    force_restart: bool = False,
):
    """
    Deploy a binary as a systemd service.

    Args:
        service_name: Name of the service
        description: Description for the systemd unit
        bin_path: Path to the binary file to deploy
        env_file_path: Path to the environment file to deploy
        args: Command-line arguments for the binary
        working_dir: Optional working directory for the service
        force_restart: Force a restart of the service if the binary or environment file has not changed
    """
    unit_file = files.template(
        name=f"Deploy systemd unit file for {service_name}",
        src=str(TEMPLATE_DIR / "service.j2"),
        dest=f"/etc/systemd/system/{service_name}.service",
        mode="0644",
        service_name=service_name,
        description=description,
        args=args,
        working_dir=working_dir,
        _sudo=True,
    )

    env_file = files.put(
        name=f"Deploy environment file for {service_name}",
        src=env_file_path,
        dest=f"/etc/{service_name}.env",
        mode="0644",
        create_remote_dir=False,
        _sudo=True,
    )

    bin_file = files.put(
        name=f"Deploy binary for {service_name}",
        src=bin_path,
        dest=f"/opt/{service_name}",
        mode="0755",
        create_remote_dir=False,
        _sudo=True,
    )

    if unit_file.changed:
        systemd.daemon_reload(_sudo=True)

    systemd.service(
        name=f"Enable and start {service_name}",
        service=f"{service_name}.service",
        running=True,
        enabled=True,
        _sudo=True,
    )

    if env_file.changed or bin_file.changed or force_restart:
        systemd.service(
            name=f"Restart {service_name}",
            service=f"{service_name}.service",
            restarted=True,
            _sudo=True,
        )
