# -*- coding: utf-8 -*-

""" Tablib - TEXT export support.
"""

import sys


if sys.version_info[0] > 2:
    from io import StringIO
else:
    from cStringIO import StringIO

import tablib

title = 'text'
extensions = ('text', 'txt')


def _wrap_row(in_row):
    out_rows = [[],]
    
    for idx, e in enumerate(in_row):
        if isinstance(e, basestring) and "\n" in e:
            pieces = e.split("\n")
            out_rows[0].append(pieces[0])
            # Add any needed extra out_rows
            while len(out_rows)<len(pieces):
                out_rows.append(["" for ignored in in_row])
            for pidx, p in enumerate(pieces[1:]):
                out_rows[pidx+1][idx] = p                    
        else:
            out_rows[0].append(e)
    return out_rows
        
def _wrap_rows(in_rows):
    out_rows = []
    for row in in_rows:
        out_rows.extend(_wrap_row(row))
    return out_rows


def _calc_col_lens(rows, col_lens):
    if not rows:
        return col_lens
    
    if not col_lens:        
        col_lens = [len(f) for f in rows[0]]
        
    for row in rows:
        row_lens = [len(str(f)) for f in row]
        col_lens = [max(f, r) for f, r in map(None, col_lens, row_lens)]

    return col_lens
    
def _dataset_2_rows(dataset):
    rows = []
    if dataset.headers:
        row = [item if item is not None else '' for item in dataset.headers]
        rows.append(row)
        first_is_header = True
    else:
        first_is_header = False
        
    for row in dataset:
        new_row = [item if item is not None else '' for item in row] 
        rows.append(new_row)

    return rows, first_is_header

def _row_2_str(row, fmt):
    try:
        return fmt % tuple(row)
    except:
        print "FMT: %r" % fmt
        print "ROW: %r" % row
        raise


def export_set(dataset):
    """TEXT representation of a Dataset."""


    rows, first_is_header = _dataset_2_rows(dataset)
    if not rows:
        return ""
        
    if first_is_header:
        header_rows = _wrap_rows(rows[:1])
        body_rows = _wrap_rows(rows[1:])        
    else:
        header_rows = []
        body_rows = _wrap_rows(rows)

    col_lens = _calc_col_lens(header_rows, [])
    col_lens = _calc_col_lens(body_rows, col_lens)
    formats = ["%%-%ss" for f in col_lens]
        
    if header_rows:
        rows = header_rows+[["="*f for f in col_lens]]+body_rows
    else:
        rows = body_rows
    
    fmt = "  ".join([f % l for l, f in map(None, col_lens, formats)])
        
    lines = []
    for idx, row in enumerate(rows):
        try:
            line = fmt % tuple(row)
        except Exception, e:            
            print e
            print "FMT: %r" % fmt
            print "ROW: %r" % row
            print 
            raise
        lines.append(line)

    data = "\n".join(lines)

    stream = StringIO()
    stream.writelines(data)
    return stream.getvalue()


def export_book(databook):
    """HTML representation of a Databook."""

    stream = StringIO()

    for i, dset in enumerate(databook._datasets):
        title = (dset.title if dset.title else 'Set %s' % (i))
        stream.write('%s:\n' % title)
        stream.write(dset.text)
        stream.write('\n')

    return stream.getvalue()
