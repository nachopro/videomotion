import tornado.ioloop
import tornado.web

from uvc import list_devices


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        cameras = list_devices()
        data = {
            'count': len(cameras),
            'devices': [c for c in cameras]
        }
        self.write(data)

class CameraHandler(tornado.web.RequestHandler):
    def get(self, device):
        self.write({'device': device})

application = tornado.web.Application([
    (r"/", HomeHandler),
    (r"/device/(.*)", CameraHandler),
], autoreload=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
