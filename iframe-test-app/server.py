from http.server import HTTPServer, SimpleHTTPRequestHandler

ADDRESS = ('', 9000)

server = HTTPServer(ADDRESS, SimpleHTTPRequestHandler)

if __name__ == '__main__':
    server.serve_forever()
