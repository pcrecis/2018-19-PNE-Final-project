import http.client
import json
import http.server
import socketserver

# Define the Server's port
PORT = 8000

HOSTNAME = 'rest.ensembl.org'
conn = http.client.HTTPSConnection(HOSTNAME)

def get_info(ENDPOINT):
    METHOD = "GET"
    headers = {'User-Agent': 'http-client'}

    conn.request(METHOD, ENDPOINT + '?content-type=application/json', None, headers)

    r1 = conn.getresponse()

    text_json = r1.read().decode("utf-8")
    conn.close()

    return json.loads(text_json)

def open_html():
    f = open("response.html")
    content = f.read()
    f.close()

    return content

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received!")

        print('Request line:' + self.requestline)
        print(' Cmd: ' + self.command)
        print(' Path: ' + self.path)

        if self.path == '/':
            f = open("main_form.html")
            content = f.read()
            f.close()
        elif '/listSpecies' in self.path:
            content = open_html()
            limit = self.path[self.path.find("=") +1:]
            species = ''
            if limit.isdigit() == True:
                info_species = get_info('/info/species')
                subject = info_species['species']
                if limit != '0':
                    if 0 < int(limit) <= len(subject):
                        type_h = '<ol>'
                        h1 = 'Names of the first {} species in the database:'.format(limit)
                        for i in range(int(limit)):
                            species += '<li>' + subject[i]['common_name'] + '</li>'
                        content = content.format(h1, type_h, species)
                    else:
                        error = 'Sorry that limit is out of range'
                        f = open("error.html")
                        content = f.read().format(error)
                        f.close()
                else:
                    type_h = '<ol>'
                    h1 = 'Names of all the species available in the database: (no limit)'
                    for i in range(len(subject)):
                        species += '<li>' + subject[i]['common_name'] + '</li>'
                    content = content.format(h1, type_h, species)
            elif limit == '':
                info_species = get_info('/info/species')
                subject = info_species['species']
                type_h = '<ol>'
                h1 = 'Names of all the species available in the database: (no limit)'
                for i in range(len(subject)):
                    species += '<li>' + subject[i]['common_name'] + '</li>'
                content = content.format(h1, type_h, species)
            else:
                error = 'Sorry the limit needs to be a positive number'
                f = open("error.html")
                content = f.read().format(error)
                f.close()

        elif '/karyotype' in self.path:
            try:
                content = open_html()
                kar = ''
                specie = self.path[self.path.find("=") + 1:]
                info_kar = get_info('/info/assembly/{}'.format(specie))
                if 'error' in info_kar:
                    error = 'Sorry the karyotype for that specie "{}" was not found in the database'.format(specie)
                    f = open("error.html")
                    content = f.read().format(error)
                    f.close()
                elif not 'karyotype' in info_kar:
                    error = 'Sorry the karyotype for that specie "{}" was not found in the database'.format(specie)
                    f = open("error.html")
                    content = f.read().format(error)
                    f.close()
                else:
                    for i in info_kar['karyotype']:
                        if i == 'MT':
                            continue
                        elif  i == '':
                            error = 'Sorry the karyotype for that specie "{}" was not found in the database'.format(specie)
                            f = open("error.html")
                            content = f.read().format(error)
                            f.close()
                        kar += '<li>' + i + '</li>'
                    type_h = '<ul>'
                    h1 = 'karyotype of {}:'.format(specie)
                    content = content.format(h1, type_h, kar)
            except KeyError:
                error = 'Sorry the karyotype for that specie was not found in the database'
                f = open('error.html'.format(error))

        elif '/chromosomeLength' in self.path:
            try:
                content = open_html()
                msg_sent = self.path.split("&")
                specie = msg_sent[0][msg_sent[0].find("=") +1:]
                chromo = msg_sent[1][msg_sent[1].find("=") +1:]
                info_chromo = get_info('/info/assembly/{}/{}'.format(specie, chromo))
                if 'error' in info_chromo:
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    content = f.read().format(error)
                    f.close()
                elif chromo == '':
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    content = f.read().format(error)
                    f.close()
                elif specie == '':
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    content = f.read().format(error)
                    f.close()
                else:
                    length = '<li>' + str(info_chromo['length']) + '</li>'
                    type_h = '<ul>'
                    h1 = 'Length of the chromosome: {} of the specie: {}'.format(chromo, specie)
                    content = content.format(h1, type_h, length)
            except KeyError:
                f = open('error.html')
            except IndexError:
                f = open('error.html')
        else:
            f = open("error.html")
            content = f.read()
            f.close()

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')        #Content type, to know the type of message
        self.send_header('Content-Length', len(str.encode(content)))
        self.end_headers()

        self.wfile.write(str.encode(content))

        return


# ------------------------
# - Server MAIN program
Handler = TestHandler

# -- Open the socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stopped by the user")
        httpd.server_close()

print("")
print("Server Stopped")