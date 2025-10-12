from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import apt, files
from pyinfra.facts.server import Command

@deploy("Docker")
def install():
    # Discover arch & codename (matches your shell commands)
    arch = host.get_fact(Command, command='dpkg --print-architecture').strip()
    codename = host.get_fact(Command, command='. /etc/os-release && echo "$VERSION_CODENAME"').strip()

    apt.packages(
        name="Install prerequisites for Docker repo",
        packages=["ca-certificates", "curl"],
        _sudo=True,
    )

    # Ensure the keyrings directory exists (0755)
    files.directory(
        name="Create /etc/apt/keyrings",
        path="/etc/apt/keyrings",
        mode="0755",
        _sudo=True,
    )

    # Download Docker’s GPG key to the keyring path with world-readable perms
    files.download(
        name="Fetch Docker APT GPG key",
        src="https://download.docker.com/linux/debian/gpg",
        dest="/etc/apt/keyrings/docker.asc",
        mode="0644",  # equivalent to: chmod a+r
        _sudo=True,
    )

    # Write the Docker APT source list (signed-by + correct arch/codename)
    # Add the Docker APT repository (writes /etc/apt/sources.list.d/docker.list)
    repo = apt.repo(
        name="Add Docker APT repository",
        src=f"deb [arch={arch} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian {codename} stable",
        filename="docker",  # -> /etc/apt/sources.list.d/docker.list
        _sudo=True,
    )

    if repo.changed:
        # Refresh package cache to pick up the new repo (like apt-get update)
        apt.update(
            name="apt-get update (after adding Docker repo)",
            _sudo=True,
        )

    apt.packages(
        name="Install Docker packages",
        packages=["docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin"],
        _sudo=True,
    )
