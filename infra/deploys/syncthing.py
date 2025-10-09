from pyinfra.api import deploy
from pyinfra.operations import apt

@deploy("Syncthing")
def install():
    apt.packages(
        name="Install APT tooling & prerequisites",
        packages=[
            "apt-transport-https",
            "ca-certificates",
            "gnupg",
            "curl",
        ],
        _sudo=True,
    )

    apt.key(
        name="Add Syncthing APT repository GPG key",
        src="https://syncthing.net/release-key.gpg",
        _sudo=True,
    )

    repo = apt.repo(
        name="Add Syncthing APT repository",
        src="deb https://apt.syncthing.net/ syncthing stable",
        _sudo=True,
    )

    if repo.changed:
        apt.update(name="Update APT package cache (Syncthing repo)", _sudo=True)

    apt.packages(
        name="Install Syncthing",
        packages=["syncthing"],
        _sudo=True,
    )
