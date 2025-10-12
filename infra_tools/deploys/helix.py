from pyinfra.api import deploy
from pyinfra.operations import apt


@deploy("Helix")
def install():
    apt.packages(
        name="Install APT prerequisites",
        packages=["software-properties-common"],
        _sudo=True,
    )

    repo = apt.ppa(
        name="Add Helix PPA",
        src="ppa:maveonair/helix-editor",
        _sudo=True,
    )

    if repo.changed:
        apt.update(name="Update APT package cache (Helix PPA)", _sudo=True)

    apt.packages(
        name="Install Helix editor",
        packages=["helix"],
        _sudo=True,
    )
