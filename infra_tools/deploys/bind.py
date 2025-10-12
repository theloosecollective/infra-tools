from pyinfra.api import deploy
from pyinfra.operations import files, server

@deploy("Bind Mount")
def mount(source: str, target: str, owner: str):
    # Ensure directories exist for bind mount
    files.directory(
        name="Ensure {0} directory exists".format(source),
        path=source,
        present=True,
        user=owner,
        group=owner,
        _sudo=True,
    )

    files.directory(
        name="Ensure {0} directory exists".format(target),
        path=target,
        present=True,
        user=owner,
        group=owner,
        _sudo=True,
    )

    # Add bind mount entry to /etc/fstab
    fstab = files.line(
        name="Add bind mount to /etc/fstab",
        path="/etc/fstab",
        line="{0} {1} none bind,uid={2},gid={2},x-systemd.automount 0 0".format(source, target, owner),
        present=True,
        _sudo=True,
    )

    # Reload systemd and mount all fstab entries if fstab changed
    if fstab.changed:
        server.shell(
            name="Reload systemd daemon",
            commands=["systemctl daemon-reload"],
            _sudo=True,
        )

        server.shell(
            name="Mount all fstab entries",
            commands=["mount -a"],
            _sudo=True,
        )

    # Ensure the mounted directory has correct ownership
    files.directory(
        name="Ensure {0} has correct ownership".format(target),
        path=target,
        present=True,
        user=owner,
        group=owner,
        _sudo=True,
    )
