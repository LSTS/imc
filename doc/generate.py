#############################################################################
# This Python file uses the following encoding: utf-8                       #
#############################################################################
# Copyright (C) 2016 Laboratório de Sistemas e Tecnologia Subaquática       #
# Departamento de Engenharia Electrotécnica e de Computadores               #
# Rua Dr. Roberto Frias, 4200-465 Porto, Portugal                           #
#############################################################################
# Author: Ricardo Martins                                                   #
#############################################################################

import sys
import os
import os.path
import shutil
import rst
import message
import argparse
from subprocess import check_call

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
open(os.path.join(src_dir, 'Message Format.rst'), 'w').write(text)

# Serialization.
text = rst.h2('Serialization')
text += rst.block(root.find('serialization/description').text)
ttypes = rst.Table()
ttypes.add_row('Name', 'Serialization')
for t in root.findall('serialization/type'):
    ttypes.add_row(t.attrib['name'], t.find('description').text)
text += str(ttypes)
open(os.path.join(src_dir, 'Message Format.rst'), 'a').write(text)

# Header.
text = rst.h2('Header')
text += rst.block(root.find('header/description').text)
table = rst.Table()
table.add_row('Name', 'Type', 'Fixed Value', 'Description')
for t in root.findall('header/field'):
    if 'value' in t.attrib:
        value = t.attrib['value']
    else:
        value = '-'
    table.add_row(t.attrib['name'] + '\n(*' + t.attrib['abbrev'] + '*)', t.attrib['type'], value,
                  t.find('description').text)
text += str(table)
open(os.path.join(src_dir, 'Message Format.rst'), 'a').write(text)

# Footer.
text = rst.h2('Footer')
text += rst.block(root.find('footer/description').text)
table = rst.Table()
table.add_row('Name', 'Type', 'Fixed Value', 'Description')
for t in root.findall('footer/field'):
    if 'value' in t.attrib:
        value = t.attrib['value']
    else:
        value = '-'
    table.add_row(t.attrib['name'] + '\n(*' + t.attrib['abbrev'] + '*)', t.attrib['type'], value,
                  t.find('description').text)
text += str(table)
open(os.path.join(src_dir, 'Message Format.rst'), 'a').write(text)

# Units.
text = rst.h2('Reference of Units')
text += rst.block(root.find('units/description').text)
tunits = rst.Table()
tunits.add_row('Abbreviation', 'Name')
for u in root.findall('units/unit'):
    tunits.add_row(u.attrib['abbrev'], u.attrib['name'])
text += str(tunits)
open(os.path.join(src_dir, 'Message Format.rst'), 'a').write(text)

# Messages by Group.
groups = []
for group in root.findall('groups/group'):
    name = group.attrib['name']
    min_id = int(group.attrib['min'])
    max_id = int(group.attrib['max'])
    files.append(name + '.rst')
    groups.append({'name': name, 'min': min_id, 'max': max_id})
    text = rst.h1(name + ' Messages')
    open(os.path.join(src_dir, name + '.rst'), 'w').write(text)

# Messages.
for msg in root.findall('message'):
    abbrev = msg.attrib['abbrev']
    id = int(msg.attrib['id'])

    text = '.. _%s:\n\n' % msg.get('abbrev')
    text += rst.h2(msg.attrib['name'])

    if msg.find('description') is None:
        text += rst.block('No description')
    elif msg.find('description').text is None:
        text += rst.block('No description')
    elif msg.find('description').text.strip() == '':
        text += rst.block('No description')
    elif msg.find('description').text.strip() != '':
        text += rst.block(msg.find('description').text)

    text += '- Abbreviation: ' + abbrev + '\n'
    text += '- Identification Number: ' + msg.attrib['id'] + '\n'
    text += '- Fixed Payload Size: ' + str(message.get_fixed_size(msg)) + '\n'
    text += '\n'

    if msg.findall('field') == []:
        text += 'This message has no fields.\n\n'
    else:
        t = rst.Table()
        t.add_row('Name', 'Abbreviation', 'Unit', 'Type', 'Description', 'Range')
        for f in msg.findall('field'):
            if f.find('description') is None:
                desc = ''
            else:
                desc = f.find('description').text

            unit = '-'
            if 'unit' in f.attrib:
                unit = f.attrib['unit'].strip()

            frange = 'Same as field type'

            name = f.attrib['name'].strip()
            t.add_row(name, f.attrib['abbrev'], '*' + unit + '*', f.attrib['type'], desc, frange)
        text += str(t)

    my_group = ''
    for group in groups:
        if id >= group['min'] and id <= group['max']:
            my_group = group['name']

    open(os.path.join(src_dir, my_group + '.rst'), 'a').write(text)

# Master document.
fd = open(os.path.join(src_dir, 'index.rst'), 'w')
fd.write(rst.h1('IMC v%s-%s' % (release, revision)))
fd.write('\n')

fd.write(rst.block(root.find('description').text))

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
