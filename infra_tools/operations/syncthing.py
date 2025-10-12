"""
Custom pyinfra operations for managing Syncthing configuration.
"""

from pyinfra import host, logger
from pyinfra.api import operation, StringCommand
from facts.syncthing import SyncthingConfig

@operation()
def folder(
    id: str,
    path: str,
):
    config = host.get_fact(SyncthingConfig)
    folder = next((f for f in config["folders"] if f["id"] == id), None)

    if folder is None:
        logger.info("No folder found with id {0}, creating it".format(id))
        yield StringCommand(
            "syncthing cli config folders add --id={0} --path={1}".format(id, path)
        )
        logger.info("Created folder {0} with path {1}".format(id, path))
    else:
        logger.info("Folder {0} found with path {1}".format(id, folder["path"]))


@operation()
def folder_device(
    id: str,
    device_id: str,
):
    config = host.get_fact(SyncthingConfig)
    folder = next((f for f in config["folders"] if f["id"] == id), None)

    if folder is None:
        logger.warning("No folder found with id {0}, skipping device addition".format(id))
        return

    device = next((d for d in folder["devices"] if d["deviceID"] == device_id), None)

    if device is None:
        yield StringCommand(
            "syncthing cli config folders {0} devices add --device-id={1}".format(id, device_id)
        )
    else:
        logger.info("Device {0} found in folder {1}".format(device_id, id))
