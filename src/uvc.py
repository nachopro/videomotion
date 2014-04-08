
import v4l2
import errno
from fcntl import ioctl


def getdict(struct):
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)


class WebCam(object):
    def __init__(self, *args, **kwargs):
        self._camara = '/dev/video0'
        self._fd = None
        self._detalle = None
        self._controles = []

    def _abrir(self):
        self._fd = open(self._camara, 'rw')

    def _cerrar(self):
        if isinstance(self._fd, file):
            self._fd.close()

    def detalle(self):
        if not self._detalle:
            capability = v4l2.v4l2_capability()
            ioctl(self._fd, v4l2.VIDIOC_QUERYCAP, capability)
            detalle = getdict(capability)
            del(detalle['reserved'])
            self._detalle = detalle

        return self._detalle

    def camaras(self):
        pass

    def controles(self):
        queryctrl = v4l2.v4l2_queryctrl(v4l2.V4L2_CID_BASE)

        while queryctrl.id < 10099999: #v4l2.V4L2_CID_LASTP1:
            try:
                ioctl(self._fd, v4l2.VIDIOC_QUERYCTRL, queryctrl)
            except IOError, e:
                assert e.errno == errno.EINVAL
                queryctrl.id += 1
                continue

            control = getdict(queryctrl)
            del(control['reserved'])
            self._controles.append(control)
            queryctrl = v4l2.v4l2_queryctrl(queryctrl.id + 1)

        queryctrl.id = v4l2.V4L2_CID_PRIVATE_BASE
        while True:
            try:
                ioctl(self._fd, v4l2.VIDIOC_QUERYCTRL, queryctrl)
            except IOError, e:
                assert e.errno == errno.EINVAL
                break

            control = getdict(queryctrl)
            del(control['reserved'])
            self._controles.append(control)
            queryctrl = v4l2.v4l2_queryctrl(queryctrl.id + 1)


def list_devices():
    cam = WebCam()
    cam._abrir()
    cam.controles()
    return [
            {
                'name': 'Genius 200c',
                'device': 'video0',
                'url': '/devices/video0',
                'controles': cam._controles
            },
        ]


