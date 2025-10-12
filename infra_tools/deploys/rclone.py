from pyinfra import host, logger
from pyinfra.facts.server import Which
from pyinfra.operations import server
from pyinfra.api import deploy

@deploy("Install rclone")
def install():
    rclone_path = host.get_fact(Which, command="rclone")

    logger.info(f"rclone_path: {rclone_path}")

    if not rclone_path:
        server.shell(
            name="Install rclone via official script",
            commands=['curl -fsSL https://rclone.org/install.sh | bash'],
            _sudo=True,
        )
