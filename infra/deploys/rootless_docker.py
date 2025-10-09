from pyinfra.api import deploy, OperationError
from pyinfra.operations import server, systemd, files
from pyinfra.facts.files import FindInFile
from pyinfra.facts.systemd import SystemdEnabled
from pyinfra.facts.server import Users
from pyinfra import host
from deploys import docker

def check_ids(entries):
    sufficient = False
    for entry in entries:
        parts = entry.split(':')
        if len(parts) >= 3:
            count = int(parts[2])
            if count >= 65536:
                sufficient = True
                break

    return sufficient

@deploy("Rootless Docker")
def install(user: str, install_docker: bool = True):
    subuid_entries = host.get_fact(FindInFile, path="/etc/subuid", pattern=f"^{user}:")
    if not subuid_entries:
        raise OperationError("No subuid entries found for current user")

    if not check_ids(subuid_entries):
        raise OperationError("Current user does not have sufficient subordinate UIDs (need 65536+)")

    subgid_entries = host.get_fact(FindInFile, path="/etc/subgid", pattern=f"^{user}:")
    if not subgid_entries:
        raise OperationError("No subgid entries found for current user")

    if not check_ids(subgid_entries):
        raise OperationError("Current user does not have sufficient subordinate GIDs (need 65536+)")

    if install_docker:
        docker.install()

    systemd.service(
        name="Stop & disable Docker service",
        service="docker.service",
        enabled=False,
        running=False,
        _sudo=True,
    )

    systemd.service(
        name="Stop & disable Docker socket",
        service="docker.socket",
        enabled=False,
        running=False,
        _sudo=True,
    )

    server.packages(
        name="Install uidmap package for newuidmap/newgidmap",
        packages=["uidmap"],
        _sudo=True,
    )

    server.modprobe(
        name="Load nf_tables kernel module now",
        module="nf_tables",
        present=True,
        _sudo=True,
    )

    files.file(
        name="Create modules-load.d drop-in file for nf_tables",
        path="/etc/modules-load.d/nf_tables.conf",
        present=True,
        _sudo=True,
    )

    files.line(
        name="Ensure nf_tables loads at boot",
        path="/etc/modules-load.d/nf_tables.conf",
        line="nf_tables",
        present=True,
        _sudo=True,
    )

    run_install_script(_sudo=True, _sudo_user=user, _env={
        "XDG_RUNTIME_DIR": "/run/user/{}".format(host.get_fact(Users)[user]["uid"]),
    })


@deploy()
def run_install_script():
    if "docker.service" not in host.get_fact(SystemdEnabled, user_mode=True):
        server.shell(commands="dockerd-rootless-setuptool.sh install")

        systemd.service(
            name="Enable & start Docker service",
            service="docker.service",
            user_mode=True,
            enabled=True,
            running=True,
        )
