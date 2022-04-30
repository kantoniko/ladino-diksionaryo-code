import datetime
import os

from reportlab.pdfgen import canvas

def create_pdf_dictionaries(dictionary, languages):
    for language in languages:
        create_pdf(dictionary, 'ladino', language)

def create_pdf(dictionary, source, target):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # put the files in a subdirectory so if the user unzips the artifact created on GitHub Actions, all the files will be in a subdirectory.
    pdf_dir = os.path.join(root, 'pdf', 'diksionaryo-ladino')
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_file = os.path.join(pdf_dir, f'{source}-{target}.pdf')
    now = datetime.datetime.now()

    can = canvas.Canvas(pdf_file)

    can.drawString(20, 800, f"Dictionaryo {source.capitalize()}-{target.capitalize()}")
    can.drawString(20, 700, f'Version de {now}')

    #can.saveState()
    hostname = "Puedes deskargar la mueva version de aki: https://diksionaryo.szabgab.com/"
    hostlink = "https://diksionaryo.szabgab.com/"
    fontsize = 12
    fontname = 'Times-Roman'
    headerBottom = 500
    bottomLine = headerBottom - fontsize/4
    topLine = headerBottom + fontsize
    lineLength = 300
    can.setFont(fontname,fontsize)
    can.drawRightString(lineLength, headerBottom, hostname)
    hostnamewidth = can.stringWidth(hostname)
    linkRect = (lineLength, bottomLine, lineLength-hostnamewidth, topLine)
    can.linkURL(hostlink, linkRect)

    #for word in sorted(dictionary[source].keys()):
    #    if source == 'ladino':
    #      can.drawString(20, 700, f'Version de {now}')
    #      word
    #            <td>{% for translation in words[word][trg] -%}{{ translation }}{%- if not loop.last %}, {% endif %}{%- endfor %}</td>


    can.showPage()



    #can.drawString(20, 800, "Second Page")
    #can.showPage()

    #can.drawString(20, 700, f'Generated on {now} Puedes deskargar de <a href="https://diksionaryo.szabgab.com/">aki</a>')
    #can.showPage()

    can.save()

