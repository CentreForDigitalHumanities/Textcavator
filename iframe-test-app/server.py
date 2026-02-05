from http.server import HTTPServer, SimpleHTTPRequestHandler

ADDRESS = ('', 9000)

server = HTTPServer(ADDRESS, SimpleHTTPRequestHandler)

if __name__ == '__main__':
    print(f'Starting server at http://localhost:{server.server_port}')
    server.serve_forever()
