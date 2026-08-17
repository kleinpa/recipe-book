"""Serves the generated website locally so it can be previewed in a browser.

Unpacks the same website.tar that gets deployed, so what's served here is
exactly the published layout (/dal/ -> dal/index.html) rather than an
approximation assembled from loose files.
"""

import functools
import http.server
import os
import socketserver
import tempfile
import tarfile

from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_integer('port', 8000, 'Port to listen on')
flags.DEFINE_string('host', 'localhost', 'Address to bind to')
flags.DEFINE_string('tar', 'website.tar', 'Website tarball to serve')


class Handler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self):
        # The tarball is unpacked once at startup, so a cached page would
        # survive a rebuild-and-restart and hide the change being previewed.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, format, *args):
        print(f'{self.command} {self.path} -> {args[1]}')


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main(argv):
    del argv

    tar = os.path.join(os.path.dirname(__file__), FLAGS.tar)
    with tempfile.TemporaryDirectory() as root:
        with tarfile.open(tar) as f:
            f.extractall(root, filter='data')

        handler = functools.partial(Handler, directory=root)
        with Server((FLAGS.host, FLAGS.port), handler) as httpd:
            print(f'serving {os.path.basename(tar)} at '
                  f'http://{FLAGS.host}:{FLAGS.port}/ (ctrl-c to stop)')
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print()


if __name__ == '__main__':
    app.run(main)
