#############################################################################
# This Python file uses the following encoding: utf-8                       #
#############################################################################
# Copyright (C) 2016 Laboratório de Sistemas e Tecnologia Subaquática       #
# Departamento de Engenharia Electrotécnica e de Computadores               #
# Rua Dr. Roberto Frias, 4200-465 Porto, Portugal                           #
#############################################################################
# Author: Ricardo Martins                                                   #
#############################################################################

class Table:
    def __init__(self):
        self._rows = []

    def pad_col(col, desired_size):
        pad = desired_size - len(col)
        for p in range(0, pad):
            col.append('')
        return col

    def _get_col_width(col):
        return max([len(line) + 1 for line in col])

    def _clean_blank_lines(lines):
        if len(lines) == 0:
            return lines

        cleaned = []

        # Remove leading and duplicated blank lines.
        is_blank = True
        for line in lines:
            if line.strip() == '':
                if is_blank:
                    pass
                else:
                    cleaned.append(line.strip())
                is_blank = True
            else:
                cleaned.append(line)
                is_blank = False

        if len(cleaned) == 0:
            return []

        if cleaned[-1].strip() == '':
            cleaned.pop()

        return cleaned

    def _split_lines(block):
        lines = block.expandtabs().splitlines()
        lines = [line.rstrip() for line in lines]
        lines = Table._clean_blank_lines(lines)

        n = 0
        for line in lines:
            if line.strip() != '':
                break
            n = n + 1

        lines = lines[n:]

        if len(lines) > 0:
            n = 0
            for c in range(0, len(lines[0])):
                if lines[0][c] != ' ':
                    break
                n = n + 1

        return [line[n:] for line in lines]

    # Compute max width of all columns.
    def _get_col_widths(self):
        self._ncols = len(self._rows[0])
        self._col_widths = [0] * self._ncols

        for col_i in range(0, self._ncols):
            for row in self._rows:
                width = Table._get_col_width(row[col_i])
                if width > self._col_widths[col_i]:
                    self._col_widths[col_i] = width

    def add_row(self, *cols):
        cols = [Table._split_lines(col) for col in cols]
        col_nlines = max([len(col) for col in cols])
        cols = [Table.pad_col(col, col_nlines) for col in cols]
        self._rows.append(cols)

    def _make_separators(self):
        self.sep_h = '+'
        self.sep_r = '+'
        for c in range(0, self._ncols):
            self.sep_r += ('-' * (self._col_widths[c] + 1)) + '+'
            self.sep_h += ('=' * (self._col_widths[c] + 1)) + '+'
        self.sep_h += '\n'
        self.sep_r += '\n'

    def print_row(self, row):
        height = len(row[0])

        rv = ''
        for line_i in range(0, height):
            s = '| '
            for col_i in range(0, len(row)):
                s += row[col_i][line_i].ljust(self._col_widths[col_i]) + '| '
            rv += s + '\n'
        return rv

    def __str__(self):
        self._get_col_widths()
        self._make_separators()

        s = self.sep_r
        header = self._rows.pop(0)
        s += self.print_row(header)
        s += self.sep_h

        for row in self._rows:
            s += self.print_row(row)
            s += self.sep_r

        return s + '\n'

def h1(s):
    s = s.strip() + '\n'
    return s + ('=' * len(s)) + '\n\n'


def h2(s):
    s = s.strip() + '\n'
    return s + ('-' * len(s)) + '\n\n'

def h3(s):
    s = s.strip() + '\n'
    return s + ('^' * len(s)) + '\n\n'

def block(s):
    s = s.expandtabs()
    if s.strip() == '':
        return ''

    lines = s.splitlines()

    if len(lines) == 1:
        return lines[0] + '\n\n';

    n = 0
    for line in lines:
        if line.strip() != '':
            break
        n = n + 1

    lines = lines[n:]

    n = 0
    for c in range(0, len(lines[0])):
        if lines[0][c] != ' ':
            break
        n = n + 1

    return '\n'.join([line[n:] for line in lines]) + '\n'

def ref(s):
    s = s.strip()
    return ':ref:`' + s + '`'