from pyinfra.api import deploy
from pyinfra.operations import apt


@deploy("Caddy")
def install():
    apt.packages(
        name="Install",
        packages=["debian-keyring", "debian-archive-keyring", "apt-transport-https"],
    )

    apt.key(
        name="Add Caddy APT repository GPG key",
        src="https://dl.cloudsmith.io/public/caddy/stable/gpg.key",
        _sudo=True,
    )

    repo = apt.repo(
        name="Add Caddy APT repository",
        src="https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main",
        _sudo=True,
    )

    if repo.changed:
        apt.update(name="Update APT package cache (Caddy repo)", _sudo=True)

    apt.packages(
        name="Install Caddy",
        packages=["caddy"],
        _sudo=True,
    )
