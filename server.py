import http.client
import json
import http.server
import socketserver
from Seq import Seq

# Define the Server's port
PORT = 8000
socketserver.TCPServer.allow_reuse_address = True

HOSTNAME = 'rest.ensembl.org'
conn = http.client.HTTPSConnection(HOSTNAME)

def get_info(ENDPOINT):
    METHOD = "GET"
    headers = {'User-Agent': 'http-client'}

    conn.request(METHOD, ENDPOINT, None, headers)

    r1 = conn.getresponse()

    text_json = r1.read().decode("utf-8")
    conn.close()

    return json.loads(text_json)

def open_html():
    f = open("response.html")
    content = f.read()
    f.close()

    return content

def get_id(gene):
    METHOD = "GET"
    headers = {'User-Agent': 'http-client'}

    conn.request(METHOD, '/lookup/symbol/homo_sapiens/' + gene + '?expand=1;content-type=application/json', None, headers)

    r1 = conn.getresponse()

    text_json = r1.read().decode("utf-8")
    conn.close()

    info_id = json.loads(text_json)
    id = info_id['id']

    return id

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received!")

        print('Request line:' + self.requestline)
        print(' Cmd: ' + self.command)
        print(' Path: ' + self.path)

        if self.path == '/':
            f = open("main_form.html")
            code = 200
            content = f.read()
            f.close()
        elif '/listSpecies' in self.path:
            content = open_html()
            species = '>'
            limit = self.path[self.path.find("=") + 1:]
            if limit in self.path:

            #resource = self.path.split("?")
            #print(resource)

            #if not "limit=" in resource[1]:
                #print('hola')
                #limit = str(199)
            #else:
                #limit = resource[1][resource[1].find("=")+1:]
                #print(limit, '!')
                if limit.isdigit() == True:
                    info_species = get_info('/info/species' + '?content-type=application/json')
                    subject = info_species['species']
                    if limit != '0':
                        if 0 < int(limit) <= len(subject):
                            type_h = '<ol>'
                            h1 = 'Names of the first {} species in the database:'.format(limit)
                            for i in range(int(limit)):
                                species += '<li>' + subject[i]['common_name'] + '</li>'
                            code = 200
                            content = content.format(h1, type_h, species)
                        else:
                            error = 'Sorry that limit is out of range'
                            f = open("error.html")
                            code = 404
                            content = f.read().format(error)
                            f.close()
                    else:
                        type_h = '<ol>'
                        h1 = 'Names of all the species available in the database: (no limit)'
                        for i in range(len(subject)):
                            species += '<li>' + subject[i]['common_name'] + '</li>'
                        code = 200
                        content = content.format(h1, type_h, species)
                elif limit == '':
                    info_species = get_info('/info/species' + '?content-type=application/json')
                    subject = info_species['species']
                    type_h = '<ol>'
                    h1 = 'Names of all the species available in the database: (no limit)'
                    for i in range(len(subject)):
                        species += '<li>' + subject[i]['common_name'] + '</li>'
                    code = 200
                    content = content.format(h1, type_h, species)
                else:
                    error = 'Sorry the limit needs to be a positive number'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
            else:
                content = open_html()
                species = '>'
                type_h = '<ol>'
                h1 = 'Names of all the species available in the database: (no limit)'
                info_species = get_info('/info/species' + '?content-type=application/json')
                subject = info_species['species']
                for i in range(len(subject)):
                    species += '<li>' + subject[i]['common_name'] + '</li>'
                code = 200
                content = content.format(h1, type_h, species)

        elif '/karyotype' in self.path:
            try:
                content = open_html()
                kar = '>'
                specie = self.path[self.path.find("=") + 1:]
                specie_in = specie.replace('+','%20')
                info_kar = get_info('/info/assembly/{}'.format(specie_in) + '?content-type=application/json')
                if 'error' in info_kar:
                    error = 'Sorry the karyotype for that specie "{}" was not found in the database'.format(specie)
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                elif info_kar['karyotype'] == []:
                    error = 'Sorry the karyotype for that specie "{}" was not found in the database'.format(specie)
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                else:
                    for i in info_kar['karyotype']:
                        if i == 'MT':
                            continue
                        kar += '<li>' + i + '</li>'
                    type_h = '<ul>'
                    h1 = 'karyotype of {}:'.format(specie)
                    code = 200
                    content = content.format(h1, type_h, kar)
            except KeyError:
                error = 'Sorry the karyotype for that specie was not found in the database'
                f = open('error.html'.format(error))

        elif '/chromosomeLength' in self.path:
            try:
                content = open_html()
                msg_sent = self.path.split("&")
                specie = msg_sent[0][msg_sent[0].find("=") +1:]
                specie_in = specie.replace('+', '%20')
                chromo = msg_sent[1][msg_sent[1].find("=") +1:]
                info_chromo = get_info('/info/assembly/{}/{}'.format(specie_in, chromo) + '?content-type=application/json')
                if 'error' in info_chromo:
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                elif chromo == '':
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                elif specie == '':
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                else:
                    length = '>' + '<li>' + str(info_chromo['length']) + '</li>'
                    type_h = '<ul>'
                    h1 = 'Length of the chromosome: {} of the specie: {}'.format(chromo, specie)
                    code = 200
                    content = content.format(h1, type_h, length)
            except KeyError:
                f = open('error.html')
            except IndexError:
                f = open('error.html')
        elif '/geneSeq' in self.path:
            try:
                gen_seq = ' style="word-break:break-all">'
                content = open_html()
                gene = self.path[self.path.find("=") + 1:]
                id = get_id(gene)
                info_seq = get_info('/sequence/id/' + id + '?content-type=application/json')
                type_h = '<ul>'
                h1 = 'Sequence of the human gene: {}'.format(gene)
                gen_seq += info_seq['seq']
                code = 200
                content = content.format(h1, type_h, gen_seq)
            except KeyError:
                error = 'Sorry that gene is not in the database'
                f = open("error.html")
                code = 404
                content = f.read().format(error)
                f.close()

        elif '/geneInfo' in self.path:
            try:
                info = '>'
                content = open_html()
                gene = self.path[self.path.find("=") + 1:]
                info_info = get_info('/lookup/symbol/homo_sapiens/' + gene + '?expand=1;content-type=application/json')
                start = info_info['start']
                end = info_info['end']
                id = info_info['id']
                length = (end-start) +1
                print(id)
                id_function = get_id(gene)
                print(id_function)
                chromo = info_info['seq_region_name']
                type_h = '<ul>'
                h1 = 'Information about the human gene {}: start, end, Length, id and Chromosome'.format(gene)
                info += '<li>' + 'Start: ' + str(start) + '<li>' + 'End: ' + str(end) + '<li>' 'Total length: ' + str(length) + '<li>' + 'ID: ' + str(id) + '<li>' + 'Chromosome: ' + str(chromo) + '</li>'
                code = 200
                content = content.format(h1, type_h, info)
            except KeyError:
                error = 'Sorry that gene is not in the database'
                f = open("error.html")
                code = 404
                content = f.read().format(error)
                f.close()

        elif '/geneCal' in self.path:
            try:
                info = '>'
                content = open_html()
                gene = self.path[self.path.find("=") + 1:]
                id = get_id(gene)
                info_cal = get_info('/sequence/id/' + id + '?content-type=application/json')
                gen_seq = info_cal['seq']
                s1 = Seq(gen_seq)
                l1 = s1.len()
                perc_A = s1.perc('A')
                perc_T = s1.perc('T')
                perc_C = s1.perc('C')
                perc_G = s1.perc('G')
                type_h = '<ul>'
                h1 = 'Calculations on the human gene {}: Total length and the percentage of all its bases'.format(gene)
                info += '<li>' + 'Total length: ' + str(l1) + '<li>' + 'A percentage: ' + str(perc_A) + '<li>' + 'C percentage: ' + str(perc_C) \
                        + '<li>' + 'T percentage: ' + str(perc_T) + '<li>' + 'G percentage: ' + str(perc_G) + '</li>'
                code = 200
                content = content.format(h1, type_h, info)
            except KeyError:
                error = 'Sorry that gene is not in the database'
                f = open("error.html")
                code = 404
                content = f.read().format(error)
                f.close()
        #elif 'geneList'
            #endpoint = '/overlap/region/human' + chromo + ":"+start+"-"+end + ?feature=gene;feature=transcript;feature=cds;feature=exon;content-type=application/json

        else:
            error = 'Sorry that endpoint is not valid'
            f = open("error.html")
            code = 404
            content = f.read().format(error)
            f.close()

        self.send_response(code)
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