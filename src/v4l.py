#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2015 Ignacio Juan Martín Benedetti <tranceway@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from fcntl import ioctl
from lib import v4l2
import errno
import glob


def getdict(struct):
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)


class Control(object):
    def __init__(self, *args, **kwargs):
        self.default = kwargs['default']
        self.flags = kwargs['flags']
        self.id = kwargs['id']
        self.maximum = kwargs['maximum']
        self.minimum = kwargs['minimum']
        self.name = kwargs['name']
        self.reserved = kwargs['reserved']
        self.step = kwargs['step']
        self.type = kwargs['type']

    def get_value(self):
        ctrl = v4l2.v4l2_control(self.id)
        with open(self.path, 'rw') as fp:
            ioctl(fp, v4l2.VIDIOC_G_CTRL, ctrl)

        return getdict(ctrl)['value']

    def set_value(self, value):
        if value > self.maximum:
            value = self.maximum

        elif value < self.minimum:
            value = self.minimum

        with open(self.path, 'rw') as fp:
            ioctl(fp, v4l2.VIDIOC_S_CTRL, v4l2.v4l2_control(self.id, value))

    value = property(get_value, set_value)


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

    def set_control(self, control, value):
        with open(self.path, 'rw') as fp:
            ioctl(fp, v4l2.VIDIOC_S_CTRL, v4l2.v4l2_control(control, value))

    def get_control(self, control):
        ctrl = v4l2.v4l2_control(control)
        with open(self.path, 'rw') as fp:
            ioctl(fp, v4l2.VIDIOC_G_CTRL, ctrl)

        print getdict(ctrl)


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
                print data
                id += 1


if __name__ == '__main__':
    a = V4L2()
    #for d in a.devices:
    #    print d.__dict__

    a._populate_controls('/dev/video0')
