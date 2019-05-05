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
            if "limit" in self.path:
                limit = self.path[self.path.find("=") + 1:]
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
                    error = 'Sorry the karyotype for that specie "{}" was not found in the database'.format(specie_in)
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
                dict_1 = dict()
                content = open_html()
                msg_sent_1 = self.path.split("?")
                msg_sent_2 = msg_sent_1[1].split('&')
                for i in msg_sent_2:
                    try:
                        keys = i.split("=")[0]
                        values = i.split("=")[1]
                        values = values.replace('+', '_')
                        dict_1[keys] = values
                    except IndexError:
                        pass
                info_chromo = get_info('/info/assembly/{}/{}'.format(dict_1['specie'], dict_1['chromo']) + '?content-type=application/json')
                if 'error' in info_chromo:
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                elif dict_1['chromo'] == '':
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                elif dict_1['specie'] == '':
                    error = 'Sorry either the specie or the chomosome was not found in the database'
                    f = open("error.html")
                    code = 404
                    content = f.read().format(error)
                    f.close()
                else:
                    length = '>' + '<li>' + str(info_chromo['length']) + '</li>'
                    type_h = '<ul>'
                    h1 = 'Length of the chromosome: {} of the specie: {}'.format(dict_1['chromo'], dict_1['specie'])
                    code = 200
                    content = content.format(h1, type_h, length)
            except KeyError:
                error = 'Sorry both parameters are needed'
                f = open("error.html")
                code = 404
                content = f.read().format(error)
                f.close()
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

        elif '/geneCalc' in self.path:
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
        elif '/geneList' in self.path:
            try:
                info = '>'
                dict_1 = dict()
                content = open_html()
                msg_sent_1 = self.path.split("?")
                msg_sent_2 = msg_sent_1[1].split('&')
                print(msg_sent_2)
                for i in msg_sent_2:
                    try:
                        keys = i.split("=")[0]
                        values = i.split("=")[1]
                        values = values.replace('+', '_')
                        print(values, '!')
                        dict_1[keys] = values
                        print(dict_1)
                    except IndexError:
                        pass
                info_list = get_info('/overlap/region/human/' + dict_1['chromo'] +":"+dict_1['start']+"-"+dict_1['end'] + '?content-type=application/json;feature=gene;feature=transcript;feature=cds;feature=exon')
                print(info_list, 'p')
                type_h = '<ul>'
                h1 = 'Names of the genes located in the chromosome {} from the start {} to end positions {}'.format(dict_1['chromo'], dict_1['start'], dict_1['end'])
                for i in range(len(info_list)):
                    info += '<li>' + 'Genes: ' + info_list[i]['external_name'] + '</li'  #i convert everything to string when adding to a list because 'int' objects are not subscriptable
                print(info)
                code = 200
                content = content.format(h1, type_h, info)
            except KeyError:
                error = 'Sorry there are no genes located in that chromosome and/or in those positions'
                f = open("error.html")
                code = 404
                content = f.read().format(error)
                f.close()
            except IndexError:   #list index out of range
                error = 'Sorry there are no genes located in that chromosome and/or in those positions'
                f = open("error.html")
                code = 404
                content = f.read().format(error)
                f.close()

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