import http.client
import json

PORT = 8000

HOSTNAME = 'rest.ensembl.org'
conn = http.client.HTTPSConnection(HOSTNAME)

def get_info(ENDPOINT):
    METHOD = "GET"
    headers = {'User-Agent': 'http-client'}

    conn.request(METHOD, ENDPOINT + '?content-type=application/json' + None, headers)

    r1 = conn.getresponse()

    text_json = r1.read().decode("utf-8")
    conn.close()

    return json.loads(text_json)

#class TestHandler(http.server.BaseHTTPRequestHandler):

def do_GET(self): #it is essential to use this name, with any other it won work

    print(' Cmd: ' + self.command)
    print(' Path: ' + self.path)

    #-- printing the request line
    termcolor.cprint(self.requestline, 'green')

    #info_karyotype = get_info('info/assembly/{}'.)
    #karyotype = info_karyotype['karyotype']

    #info_chrom = get_info('')

    if self.path == '/':
        f = open("main_form.html")
        content = f.read()
        f.close()
    elif self.path == '/listSpecies':
        info_species = get_info('/info/species')
        species = info_species['common_name']

    self.send_response(200)

    self.send_header('Content-Type', 'text/html')
    self.send_header('Content-Length', len(str.encode(content)))
    self.end_headers() # we indicate the haeder is done

    # -- Sending the body of the response message
    self.wfile.write(str.encode(content))


