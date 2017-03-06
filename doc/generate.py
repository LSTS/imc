#############################################################################
# This Python file uses the following encoding: utf-8                       #
#############################################################################
# Copyright (C) 2016 Laboratório de Sistemas e Tecnologia Subaquática       #
# Departamento de Engenharia Electrotécnica e de Computadores               #
# Rua Dr. Roberto Frias, 4200-465 Porto, Portugal                           #
#############################################################################
# Author: Ricardo Martins                                                   #
# Author: Paulo Dias                                                        #
#############################################################################

import sys
import os
import os.path
import shutil
import rst
import message
import argparse
from subprocess import check_call

def findDescriptionTagAndOutputTextBlock(elem, noDescriptionText = False):
    text = ''
    noDescTxt = 'No description'
    if noDescriptionText:
        noDescTxt = '*-*'
    if elem.find('description') is None:
        text += rst.block(noDescTxt)
    elif elem.find('description').text is None:
        text += rst.block(noDescTxt)
    elif elem.find('description').text.strip() == '':
        text += rst.block(noDescTxt)
    elif elem.find('description').text.strip() != '':
        text += rst.block(elem.find('description').text)

    return text;

def getEnumerationDescripion(elem, headerPrefix = '', refPrefix = ''):
    text = '.. _%s%s:\n\n' % (refPrefix, elem.attrib['abbrev'])
    text += '.. _%s%s%s:\n\n' % (refPrefix, 'prefix-', elem.attrib['prefix'])
    text += rst.h3(headerPrefix + elem.attrib['name'])
    text += findDescriptionTagAndOutputTextBlock(elem)
    text += '- Abbreviation: ' + elem.attrib['abbrev'] + '\n'
    text += '- Prefix: ' + elem.attrib['prefix'] + '\n'
    text += '\n'
    tenums = rst.Table()
    tenums.add_row('Value', 'Name', 'Abbreviation', 'Description')
    for v in elem.findall('value'):
        tenums.add_row(v.attrib['id'], v.attrib['name'], v.attrib['abbrev'], 
            findDescriptionTagAndOutputTextBlock(v, True))
    text += str(tenums)

    return text

# Folder where this script is located.
cod_dir = os.path.dirname(os.path.abspath(__file__))

# Parse command line arguments.
parser = argparse.ArgumentParser(
    description="This script generates IMC's reference documentation.")
parser.add_argument('--prefix', dest='prefix', default=os.path.join(cod_dir, 'reference'),
    help='destination folder')
parser.add_argument('--commit', dest='commit', default='unknown',
    help='commit id')
args = parser.parse_args()

# Destination/build folder.
bld_dir = args.prefix
src_dir = os.path.join(bld_dir, '_sources')
thm_dir = os.path.join(cod_dir, 'themes')
img_dir = os.path.join(cod_dir, 'images')
xml = os.path.join(cod_dir, '..', 'IMC.xml')

from xml.etree.ElementTree import ElementTree
tree = ElementTree()
root = tree.parse(xml)
release = root.get('version')
version = '.'.join(release.split('.')[:2])
revision = args.commit

files = []

# Prepare directory tree.
shutil.rmtree(src_dir, True)
shutil.rmtree(bld_dir, True)
os.makedirs(src_dir)
shutil.copytree(img_dir, os.path.join(bld_dir, 'images'))

# Message format.
text = rst.h1('Message Format')
files.append('Message Format.rst')

headerFooterSize = 0

# Field types.
text += rst.h2('Field types')
text += rst.block(root.find('types/description').text)
ttypes = rst.Table()
ttypes.add_row('Name', 'Size', 'Description')
for t in root.findall('types/type'):
    if 'size' in t.attrib:
        size = t.attrib['size'].strip()
    else:
        size = 'n/a'
    ttypes.add_row(t.attrib['name'], size, t.find('description').text)
text += str(ttypes)
open(os.path.join(src_dir, 'Message Format.rst'), 'w', encoding='utf-8').write(text)

# Serialization.
if root.find('serialization') is not None:
    text = rst.h2('Serialization')
    descElm = root.find('serialization/description')
    if descElm is not None:
        text += rst.block(descElm.text)
    ttypes = rst.Table()
    ttypes.add_row('Name', 'Serialization')
    for t in root.findall('serialization/type'):
        ttypes.add_row(t.attrib['name'], t.find('description').text)
    text += str(ttypes)
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# Header.
text = rst.h2('Header')
if root.find('header/description') is not None:
    text += rst.block(root.find('header/description').text)
sz = message.get_fixed_size(root.find('header'), root)
headerFooterSize += sz['size']
text += '- Size: '+ str(sz['size']) 
if not sz['fixed']:
    text += '+ '
text += ' bytes\n'
text += '\n'
table = rst.Table()
table.add_row('Name', 'Type', 'Fixed Value', 'Description')
for t in root.findall('header/field'):
    if 'value' in t.attrib:
        value = t.attrib['value']
    else:
        value = '*-*'
    table.add_row(t.attrib['name'] + '\n(*' + t.attrib['abbrev'] + '*)', t.attrib['type'], value,
                  t.find('description').text)
text += str(table)
open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# Footer.
if root.find('footer') is not None:
    text = rst.h2('Footer')
    if root.find('footer/description') is not None:
        text += rst.block(root.find('footer/description').text)
    sz = message.get_fixed_size(root.find('footer'), root)
    headerFooterSize += sz['size']
    text += '- Size: '+ str(sz['size']) 
    if not sz['fixed']:
        text += '+ '
    text += ' bytes\n'
    text += '\n'
    table = rst.Table()
    table.add_row('Name', 'Type', 'Fixed Value', 'Description')
    for t in root.findall('footer/field'):
        if 'value' in t.attrib:
            value = t.attrib['value']
        else:
            value = '*-*'
        table.add_row(t.attrib['name'] + '\n(*' + t.attrib['abbrev'] + '*)', t.attrib['type'], value,
                      t.find('description').text)
    text += str(table)
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# flags.
if root.find('flags') is not None:
    text = rst.h2('Flags')
    tfls = rst.Table()
    tfls.add_row('Name', 'Abbreviation', 'Description')
    for f in root.findall('flags/flag'):
        noteAtt = f.find('[@note]')
        noteTxt = '*-*'
        if noteAtt is not None:
            noteTxt = noteAtt.text
        tfls.add_row(f.attrib['name'], f.attrib['abbrev'], noteTxt)
    text += str(tfls)
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# Units.
if root.find('units') is not None:
    text = rst.h2('Reference of Units')
    if root.find('units/description') is not None:
        text += rst.block(root.find('units/description').text)
    tunits = rst.Table()
    descFlg = False
    if root.find('units/unit/description') is not None:
        tunits.add_row('Abbreviation', 'Name', 'Description')
        descFlg = True
    else:
        tunits.add_row('Abbreviation', 'Name')
    for u in root.findall('units/unit'):
        if descFlg:
            tunits.add_row(u.attrib['abbrev'], u.attrib['name'],
                findDescriptionTagAndOutputTextBlock(u, True))
        else:
            tunits.add_row(u.attrib['abbrev'], u.attrib['name'])
    text += str(tunits)
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# enumerations.
if root.find('enumerations/def') is not None:
    text = rst.h2('Reference of Global Enumerations')
    for e in root.findall('enumerations/def'):
        text += getEnumerationDescripion(e, 'Enum ', 'enum-')
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# bitfields.
if root.find('bitfields/def') is not None:
    text = rst.h2('Reference of Global Bitfields')
    for b in root.findall('bitfields/def'):
        text += getEnumerationDescripion(b, 'Bitfield ', 'bitfield-')
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# message-groups.
if root.find('message-groups/message-group') is not None:
    text = rst.h2('Reference of Message-Groups')
    for mg in root.findall('message-groups/message-group'):
        text += '.. _%s:\n\n' % mg.attrib['abbrev']
        text += rst.h3('Message-Group ' + mg.attrib['name'])
        text += findDescriptionTagAndOutputTextBlock(mg)
        text += '- Abbreviation: ' + mg.attrib['abbrev'] + '\n'
        text += '\n'
        tmgs = rst.Table()
        descFlg = False
        if root.find('message-groups/message-group/description') is not None:
            tmgs.add_row('Message', 'Description')
            descFlg = True
        else:
            tmgs.add_row('Message')
        for t in mg.findall('message-type'):
            if descFlg:
                tmgs.add_row(rst.ref(t.attrib['abbrev']), findDescriptionTagAndOutputTextBlock(t, True))
            else:
                tmgs.add_row(rst.ref(t.attrib['abbrev']))
        text += str(tmgs)
    open(os.path.join(src_dir, 'Message Format.rst'), 'a', encoding='utf-8').write(text)

# Messages by Group.
groups = []
for group in root.findall('groups/group'):
    name = group.attrib['name']
    min_id = int(group.attrib['min'])
    max_id = int(group.attrib['max'])
    files.append(name + '.rst')
    groups.append({'name': name, 'min': min_id, 'max': max_id})
    text = rst.h1(name + ' Messages')
    open(os.path.join(src_dir, name + '.rst'), 'w', encoding='utf-8').write(text)

# Messages.
for msg in root.findall('message'):
    abbrev = msg.attrib['abbrev']
    id = int(msg.attrib['id'])

    text = '.. _%s:\n\n' % msg.get('abbrev')
    text += rst.h2(msg.attrib['name'])

    text += findDescriptionTagAndOutputTextBlock(msg)

    text += '- Abbreviation: ' + abbrev + '\n'
    text += '- Identification Number: ' + msg.attrib['id'] + '\n'
    sz = message.get_fixed_size(msg, root)
    text += '- Payload Size: ' + str(sz['size'])
    if not sz['fixed']:
        text += '+ '
    text += ' bytes\n'
    text += '- Message Size: ' + str(sz['size'] + headerFooterSize)
    if not sz['fixed']:
        text += '+ '
    text += ' bytes\n'
    flgsAtt = msg.find('[@flags]')
    if flgsAtt is not None:
        text += '- Flags: ' + msg.attrib['flags'] + '\n'
    text += '\n'

    if msg.findall('field') == []:
        text += 'This message has no fields.\n\n'
    else:
        t = rst.Table()
        t.add_row('Name', 'Abbreviation', 'Unit', 'Type', 'Description', 'Range')
        txtLocalEnumBitField = ''
        for f in msg.findall('field'):
            if f.find('description') is None:
                desc = ''
            else:
                desc = f.find('description').text

            unit = '-'
            if 'unit' in f.attrib:
                unit = f.attrib['unit'].strip()

            frange = message.get_range_txt(f)

            name = f.attrib['name'].strip()
            txtType = ''
            txtUnit = ''
            if (f.attrib['type'].strip() == 'message' or f.attrib['type'].strip() == 'message-list') and f.find('[@message-type]') is not None:
                txtType = '\n(' + rst.ref(f.attrib['message-type']) + ')'

            if f.find('[@unit]') is not None and (f.attrib['unit'].strip() == 'Enumerated'):
                if f.findall('value') == []:
                    if ('enum-def' in f.attrib):
                        prefixLk = f.attrib['enum-def']
                        txtUnit = '\n(' + rst.ref('enum-' + prefixLk) + ')'
                else:
                    txtUnit = '\n(' + rst.ref(msg.attrib['abbrev'] + '-enum-' + f.attrib['abbrev']) + ')'
                    txtLocalEnumBitField += getEnumerationDescripion(f, 'Enum ', msg.attrib['abbrev'] + '-enum-')
            elif f.find('[@unit]') is not None and (f.attrib['unit'].strip() == 'Bitfield'):
                if f.findall('value') == []:
                    if ('bitfield-def' in f.attrib):
                        prefixLk = f.attrib['bitfield-def']
                        txtUnit = '\n(' + rst.ref('bitfield-' + prefixLk) + ')'
                else:
                    txtUnit = '\n(' + rst.ref(msg.attrib['abbrev'] + '-bitfield-' + f.attrib['abbrev']) + ')'
                    txtLocalEnumBitField += getEnumerationDescripion(f, 'Bitfield ', msg.attrib['abbrev'] + '-bitfield-')

            t.add_row(name, f.attrib['abbrev'], '*' + unit + '*' + txtUnit, f.attrib['type'] + txtType, desc, frange)
        
        text += str(t)
        text += txtLocalEnumBitField

    my_group = ''
    for group in groups:
        if id >= group['min'] and id <= group['max']:
            my_group = group['name']

    open(os.path.join(src_dir, my_group + '.rst'), 'a', encoding='utf-8').write(text)

# Master document.
fd = open(os.path.join(src_dir, 'index.rst'), 'w', encoding='utf-8')
fd.write(rst.h1('IMC v%s-%s' % (release, revision)))
fd.write('\n')

descElm = root.find('description')
if descElm is not None:
    fd.write(rst.block(descElm.text))

fd.write('''
.. toctree::
   :maxdepth: 2

''')

for f in files:
    fd.write('   ' + f + '\n')
fd.close()

import subprocess
subprocess.check_call(['sphinx-build',
                       '-b', 'html',
                       '-E',
                       '-d', os.path.join(bld_dir, 'doctree'),
                       '-c', cod_dir,
                       '-D', 'version=' + version,
                       '-D', 'release=' + release,
                       '-D', 'html_title=' + 'IMC v' + release + ' Specification',
                       src_dir,
                       bld_dir
                       ])
