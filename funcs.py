#!/usr/bin/python

import re
import sys
import pdb

#
# find C-style functions
#
def find_c_function_declaration(line):
    candidate = re.compile(r'([a-zA-Z0-9]+)\(([a-zA-Z0-9\*\s,&]+)\)(;)?')
    matches   = candidate.search(line)
    if matches:
        func_name = matches.group(1)
        func_args = matches.group(2)
        func_term = matches.group(3)
        if func_term:
            func_description = (func_name, func_args, 'declaration')
        else:
            func_description = (func_name, func_args, 'definition' )
        return func_description
    else:
        return None

#
# usage function
#
def print_usage():
    pname = sys.argv[0]
    print "USAGE: %s <infile> <optional-outfile>" % (pname)

#
# insert C-style macro definition
#
def write_macro(macro_name):
    macro_top = "#define %s(fmt, ...) \\\n" % (macro_name)
    macro_bot = "\tdo { fprintf(stdout,\"%s:%d:%s(): \" fmt,__FILE__,__LINE__,__func__,__VA_ARGS__); } while(0)\n"
    macro = macro_top + macro_bot
    return macro

#
# find_macro_candidate
#
def find_macro_candidate(fhandle):
    # macro definition candidates...
    candidates = ['DPRINTF','DTELL']
    fhandle.seek(0)
    fstring = fhandle.read()
    fhandle.seek(0)
    for candidate in candidates:
        needle = re.compile(candidate)
        if needle.search(fstring):
            continue
        else:
            return candidate
    return None
    

#
# Find the end of the header
#
def find_header(fhandle):
    fhandle.seek(0)
    iline = 0
    last_line = 0
    blank_line = 0
    increment_blank = False
    increg = re.compile(r'(#import)|(#include)')
    for line in fhandle:
        iline = iline + 1
        if increg.findall(line):
            last_line = iline
            increment_blank = True
        if increment_blank and len(line) <= 1:
            blank_line = iline
            increment_blank= False

    # done finding the header
    fhandle.seek(0)
    # increment to be sure
    last_line = blank_line
    return last_line

#
# insert macro...
#
def insert_macro_and_save_file(fhandle,mname,mline):
    pdb.set_trace()
    fhandle.seek(0)
    fname  = fhandle.name
    flines = fhandle.readlines()
    fhandle.close()
    fmacro = write_macro(mname)
    flines.insert(mline,fmacro)
    fhandle = open(fname,'w')
    fhandle.write(''.join(flines))
    fhandle.close()
    fhandle = open(fname,'r')
    return fhandle


#
# Main function
#
def main(file_name):
    
    # open the file
    infhandle = open( file_name, 'r' )

    # determine a candidate for the macro definition
    name      = find_macro_candidate(infhandle)

    # find a good insertion point for the DEBUG macro
    last_line_of_header = find_header(infhandle)

    # insert the macro to enable logging...
    infhandle = insert_macro_and_save_file(infhandle,name,last_line_of_header)

    # now comes the more interesting parts
    # ideally we allow certain functions to be instrumented
    # etc, but let's leave that for another day
    # so instead we insert our debug function into the first
    # in a function definition.
    
#
# use the script as a program
#
if __name__ == "__main__":

    nargs = len(sys.argv)

    if nargs < 2 or nargs > 3:
        print_usage()
        sys.exit(1)

    print "Reading..."
    
    main(sys.argv[1])
    
    
