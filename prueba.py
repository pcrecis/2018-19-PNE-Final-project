elif "msg" in self.path:
msg_sent = self.path.split("&")
print(msg_sent)
seq = msg_sent[0][msg_sent[0].find("=") + 1:]
seq = seq.upper()
if valid_characters(seq.upper()):
    content = ("""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>RESPONSE OF THE SEQUENCE RECEIVED:</title>
                    </head>
                    <body style="background-color: lightpink;">
                        <h1>RESPONSE</h1>
                        <p>{}</p>
                        <p>{}</p>
                        <p>{}</p>
                        <a href="/">Main page</a>
                    </body>
                    </html.>""")

    sequence = ""
    sequence += "Sequence: " + str(seq)
    print(sequence)
    length = ""
    operation = ""
    seq = Seq(seq)

    for i in range(len(msg_sent)):
        if "chk=on" in msg_sent[i]:
            else:
            f = open("error.html")
            content = f.read()
            f.close()