import datetime
import os

from reportlab.pdfgen import canvas

def create_pdf_dictionaries(all_words, languages):
    for language in languages:
        create_pdf(all_words, 'ladino', language)
        create_pdf(all_words, language, 'ladino')

def create_pdf(all_words, source, target):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # put the files in a subdirectory so if the user unzips the artifact created on GitHub Actions, all the files will be in a subdirectory.
    pdf_dir = os.path.join(root, 'pdf', 'diksionaryo-ladino')
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_file = os.path.join(pdf_dir, f'{source}-{target}.pdf')
    now = datetime.datetime.now().replace(microsecond=0)

    can = canvas.Canvas(pdf_file)

    can.drawString(20, 800, f"Diksionaryo {source.capitalize()}-{target.capitalize()}")
    can.drawString(20, 780, f'Version de {now}')

    #can.saveState()
    hostname = "Puedes deskargar la mueva version de aki: https://diksionaryo.szabgab.com/"
    hostlink = "https://diksionaryo.szabgab.com/"
    fontsize = 12
    fontname = 'Times-Roman'
    fontname_bold = 'Times-Bold'
    headerBottom = 760
    bottomLine = headerBottom - fontsize/4
    topLine = headerBottom + fontsize
    lineLength = 400
    can.setFont(fontname,fontsize)
    #can.drawRightString(lineLength, headerBottom, hostname)
    can.drawString(20, headerBottom, hostname)
    hostnamewidth = can.stringWidth(hostname)
    #linkRect = (lineLength, bottomLine, lineLength-hostnamewidth, topLine)
    linkRect = (20+hostnamewidth, bottomLine, 20, topLine)
    #print(linkRect)
    can.linkURL(hostlink, linkRect)

    can.drawString(20, 740, '©2003-2009 Güler Orgun, Ricardo Portal i Antonio Ruiz Tinoco')
    can.drawString(20, 720, '©2022 Ladinokomunita')

    row = 700
    if source == 'ladino':
        for word in sorted(all_words, key=lambda word: word['versions'][0]['ladino'].lower()):
            ladino = word['versions'][0].get('accented', word['versions'][0]['ladino'])
            translations = word['versions'][0]['translations'].get(target)
            if not translations:
                continue
            can.setFont(fontname_bold, fontsize)
            word['versions'][0]['ladino']
            ladino_text = ladino
            if word['grammar'] == 'verb':
                ladino_text += " (v)"
            if word['versions'][0].get('gender', '') == 'masculine' and word['versions'][0].get('number', '') == 'singular':
                ladino_text += ' (el)'
            if word['versions'][0].get('gender', '') == 'masculine' and word['versions'][0].get('number', '') == 'plural':
                ladino_text += ' (los)'
            if word['versions'][0].get('gender', '') == 'feminine' and word['versions'][0].get('number', '') == 'singular':
                ladino_text += ' (la)'
            if word['versions'][0].get('gender', '') == 'feminine' and word['versions'][0].get('number', '') == 'plural':
                ladino_text += ' (las)'
            ladino_text += ':'
            can.drawString(20, row, ladino_text)
            width = can.stringWidth(ladino_text)
            can.setFont(fontname, fontsize)
            can.drawString(20+2+width, row, f'{translations[0]}')
            row -= 12
            if row < 30:
                row = 760
                can.showPage()


    can.save()

