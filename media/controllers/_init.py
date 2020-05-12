"""_init.py

Initialize each controller

created 14-jan-2020 by richb@instantlinux.net
"""

from . import album, file, picture, storage


def controllers():
    resources = []
    for controller in [
            album.AlbumController,
            file.FileController,
            picture.PictureController,
            storage.StorageController]:
        setup = controller()
        resources.append(setup.resource)
    return resources
