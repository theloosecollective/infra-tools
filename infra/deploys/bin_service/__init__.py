from pyinfra.api import deploy
from pyinfra.operations import files, systemd, server

@deploy("Binary Service")
def install(
    service_name: str,
    description: str,
    bin_path: str,
    env_file_path: str,
    args: str = "",
    working_dir: str | None = None,
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
    """
    # Ensure env file exists (if it doesn't already)
    files.file(
        name=f"Ensure /etc/{service_name}.env exists",
        path=f"/etc/{service_name}.env",
        present=True,
        mode="0644",
        create_remote_dir=False,
        _sudo=True,
    )

    # Build the systemd unit file content
    unit_content_lines = [
        "[Unit]",
        f"Description={description}",
        "After=network.target",
        "",
        "[Service]",
    ]

    if working_dir:
        unit_content_lines.append(f"WorkingDirectory={working_dir}")

    unit_content_lines.extend([
        f"ExecStart=/opt/{service_name} {args}",
        "ExecStop=/bin/kill -s QUIT $MAINPID",
        f"EnvironmentFile=/etc/{service_name}.env",
        "Restart=always",
        "",
        "[Install]",
        "WantedBy=default.target",
        "",
    ])

    # Deploy the systemd unit file using server.shell with heredoc
    server.shell(
        name=f"Deploy systemd unit file for {service_name}",
        commands=[
            f"cat > /etc/systemd/system/{service_name}.service <<'EOF'\n" +
            "\n".join(unit_content_lines) + "\nEOF"
        ],
        _sudo=True,
    )

    # Deploy the environment file
    files.put(
        name=f"Deploy environment file for {service_name}",
        src=env_file_path,
        dest=f"/etc/{service_name}.env",
        mode="0644",
        create_remote_dir=False,
        _sudo=True,
    )

    # Deploy the binary
    files.put(
        name=f"Deploy binary for {service_name}",
        src=bin_path,
        dest=f"/opt/{service_name}",
        mode="0755",
        create_remote_dir=False,
        _sudo=True,
    )

    # Reload systemd daemon
    server.shell(
        name="Reload systemd daemon",
        commands=["systemctl daemon-reload"],
        _sudo=True,
    )

    # Enable and start the service
    systemd.service(
        name=f"Enable and start {service_name}",
        service=f"{service_name}.service",
        running=True,
        enabled=True,
        restarted=True,
        _sudo=True,
    )
