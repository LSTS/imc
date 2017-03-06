#############################################################################
# This Python file uses the following encoding: utf-8                       #
#############################################################################
# Copyright (C) 2017 Laboratório de Sistemas e Tecnologia Subaquática       #
# Departamento de Engenharia Electrotécnica e de Computadores               #
# Rua Dr. Roberto Frias, 4200-465 Porto, Portugal                           #
#############################################################################
# Author: Paulo Dias                                                        #
#############################################################################

def get_fixed_size(msg, root):
    typesElm = root.find('types')
    size = 0
    messageWithKnownTotalSize = True
    if typesElm is not None:
        for f in msg.findall('field'):
            if f.find('[@type]') is None:
                messageWithKnownTotalSize = False
                continue

            type = typesElm.find('type[@name=\'' + f.attrib['type'] + '\']')
            if type is None:
                messageWithKnownTotalSize = False
                continue

            tsz = type.find('[@size]')
            if tsz is None:
                sizeKnown = False
                if f.attrib['type'] == 'rawdata':
                    size += 2
                elif f.attrib['type'] == 'plaintext':
                    size += 2
                elif f.attrib['type'] == 'message':
                    size += 2
                    if 'message-type' in f.attrib:
                        msgType = f.attrib['message-type']
                        msgTypeElem = root.find('message[@abbrev=\'' + msgType + '\']')
                        if msgTypeElem is not None:
                            mtsz = get_fixed_size(msgTypeElem, root)
                            size += mtsz['size']
                            sizeKnown = mtsz['fixed']
                elif f.attrib['type'] == 'message-list':
                    size += 2

                messageWithKnownTotalSize = messageWithKnownTotalSize & sizeKnown
                continue

            size += int(type.attrib['size'])

    return {'size':size, 'fixed':messageWithKnownTotalSize }

def get_range_txt(field):
    frangeTxt = ''

    if 'fixed' in field.attrib:
        frangeTxt += 'fixed'
        if 'value' in field.attrib:
            frangeTxt += ' ['
            frangeTxt += str(field.attrib['value'])
            frangeTxt += ']'

    if 'min' in field.attrib:
        if len(frangeTxt) != 0:
            frangeTxt += ',\n'
        frangeTxt += 'min=' + str(field.attrib['min'])

    if 'max' in field.attrib:
        if len(frangeTxt) != 0:
            frangeTxt += ',\n'
        frangeTxt += 'max=' + str(field.attrib['max'])

    if len(frangeTxt) == 0:
        frangeTxt = 'Same as field type'

    return frangeTxt