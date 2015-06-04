#! /usr/bin/env python
# -*- coding: utf-8 -*-

from fcntl import ioctl
from lib import v4l2
import errno
import glob


def getdict(struct):
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)


class Device(object):
    def __init__(self, *args, **kwargs):
        self.bus_info = kwargs['bus_info']
        self.capabilities = kwargs['capabilities']
        self.card = kwargs['card']
        self.driver = kwargs['driver']
        self.id = kwargs['id']
        self.path = kwargs['path']
        self.reserved = kwargs['reserved']
        self.version = kwargs['version']

    def __unicode__(self):
        return unicode(self.__str__())

    def __str__(self):
        return '{0} @ {1}'.format(
            self.card,
            self.path
        )


class V4L2(object):
    def __init__(self, *args, **kwargs):
        self.devices = []

        self._populate_devices()

    def _populate_devices(self):
        for device in glob.glob('/dev/video*'):

            cap = v4l2.v4l2_capability()
            with open(device, 'rw') as fp:
                ioctl(fp, v4l2.VIDIOC_QUERYCAP, cap)

            data = getdict(cap)
            data.update({
                'path': device,
                'id': device.split('/')[-1]
            })

            self.devices.append(Device(**data))

    def _populate_controls(self, device):
        with open(device, 'rw') as fp:

            id = v4l2.V4L2_CID_USER_BASE
            while id < 10099999: #v4l2.V4L2_CID_LASTP1:
                ctrl = v4l2.v4l2_queryctrl(id)

                try:
                    ioctl(fp, v4l2.VIDIOC_QUERYCTRL, ctrl)
                except IOError, e:
                    pass
                    if e.errno in (errno.EINVAL, errno.ENOTTY):#errno.ENOTTY:
                        id += 1
                        continue

                data = getdict(ctrl)
                print data['name']
                id += 1


if __name__ == '__main__':
    a = V4L2()
    #for d in a.devices:
    #    print d.__dict__

    a._populate_controls('/dev/video0')
