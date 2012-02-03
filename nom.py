#!/usr/bin/env python
#Copyright (c) 2012 Igor Kaplounenko
#This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.

import ply.lex as lex
import ply.yacc as yacc
import logging

__all__=['nom']

tokens = (
        'LCURLY',
        'RCURLY',
        'ITEM',
        'SEPARATOR',
        )

precedence = (
        ('left', 'SEPARATOR'),
        )

t_LCURLY                    = r'\{'
t_RCURLY                    = r'\}'
t_SEPARATOR             = r'='
t_ITEM                      = r'[a-zA-Z0-9_\-\.]+|\'.+\'|\".+\"'
t_ignore                    = ' \t\r\n'
t_ignore_COMMENT    = r'\#.*'

def t_error(t):
    logging.error("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer=lex.lex()

def p_item_separator_item(p):
    'expression : ITEM SEPARATOR ITEM'
    p[0]=[(p[1],p[3])]

def p_item_separator_curlies(p):
    'expression : ITEM SEPARATOR LCURLY RCURLY'
    p[0]=[(p[1],None)]

def p_item_separator_expression(p):
    'expression : ITEM SEPARATOR expression'
    p[0]=[(p[1],p[3])]

def p_curly_expression_curly(p):
    'expression : LCURLY expression RCURLY'
    p[0]=toDict(p[2])

def p_expression_expression(p):
    'expression : expression expression'
    p[0]=p[1]+p[2]

def p_error(p):
    logging.error("Error parsing '%s'." % p)

parser=yacc.yacc()

def toDict(l):
    if not l:
        l={}
    d={}
    for key, value in l:
        if key not in d and not key.startswith('add_') and not key.startswith('remove_'):
            d[key]=value
        else:
            try:
                d[key].append(value)
            except AttributeError:
                d[key]=[d[key],value]
            except KeyError:
                d[key]=[value]
    return d

def nom(buf):
    if len(buf.strip()):
        return toDict(parser.parse(buf))
    else:
        return {}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description="Consumes EU3 text data and generates a dictionary from it.")
    p.add_argument('file',nargs=1,help="file to parse")
    p.add_argument('--verbose','-v',action='store_true',help="print debugging messages")
    options=p.parse_args()
    loglevel=logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(level=loglevel)
    with open(options.file[0],'rb') as f:
        buf=f.read()