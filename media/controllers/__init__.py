"""_init.py

Initialize each controller

created 14-jan-2020 by richb@instantlinux.net
"""

from apicrud.controllers import metric

from . import album, file, picture, storage


def resources():
    results = []
    for controller in [
            album.AlbumController,
            file.FileController,
            metric.MetricController,
            picture.PictureController,
            storage.StorageController]:
        results.append(controller().resource)
    return results
