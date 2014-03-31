#
# Ref: http://linuxtv.org/downloads/v4l-dvb-apis/
#      http://jayrambhia.com/blog/capture-v4l2/
#

import v4l2
import fcntl

vd = open('/dev/video0', 'rw')

cp = v4l2.v4l2_capability()
fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)

print cp.driver
print cp.card
print cp.bus_info
print cp.version
print cp.capabilities
print cp.reserved

fmt = v4l2.v4l2_format()
fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
fmt.fmt.pix.width = 1024
fmt.fmt.pix.height = 768
fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_MJPEG
fmt.fmt.pix.field = v4l2.V4L2_FIELD_NONE

fcntl.ioctl(vd, v4l2.VIDIOC_TRY_FMT, fmt)

print fmt.fmt.pix.width
print fmt.fmt.pix.height

