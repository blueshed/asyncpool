""" Our tornado server """
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

define('debug', type=bool, default=False, help='run in debug mode')


class MainHandler(tornado.web.RequestHandler):  # pylint: disable=W0223
    """ simple welcome """

    def get(self, name):
        """ handle get request """
        self.write(f'Hello, {name}')


def make_app():
    """ make our tornado app """
    return tornado.web.Application(
        [(r'/(.*)', MainHandler),], debug=options.debug
    )


if __name__ == '__main__':
    parse_command_line()
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
