#!/usr/bin/python

import re
import sys
import getopt

#
# find C-style functions
#
def find_c_function_declaration(line):
   candidate = re.compile(r'([a-zA-Z0-9]+)\(([a-zA-Z0-9\*\s,&]+)\)(;)?(\{)?')
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
# Is the trailing non-white space character a open bracket...
#
def is_trailing_char_bracket(line):
   for c in line[::-1]:
       if c == ' ' or c == '\n':
           continue
       else:
           # the actual test
           if c == '{':
               return True
           else:
               return False
   return False

#
# Is the leading non-white space character an open bracket
#
def is_leading_char_bracket(line):
   for c in line:
       if c == ' ' or c == '\t':
           continue
       else:
           # the actual test
           if c == '{':
               return True
           else:
               return False

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
   macro_bot = "\tdo { fprintf(stdout,\"%s:%d:%s(): \" fmt \"\\n\",__FILE__,__LINE__,__func__,__VA_ARGS__); } while(0)\n"
   macro = macro_top + macro_bot
   return macro

#
# insert macro call
#
def write_macro_call(macro_name):
    if type(macro_name) != type(''):
        print "ERROR macro name is not a string: ",macro_name
    macrostr = macro_name + '("","");\n'
    return macrostr

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
# Is using an existing macro
#
def is_using_macro(fhandle):
    # macro definition candidates...
   candidates = ['DPRINTF','DTELL']
   fhandle.seek(0)
   fstring = fhandle.read()
   fhandle.seek(0)
   for candidate in candidates:
       needle = re.compile(candidate)
       if needle.search(fstring):
           return candidate
       else:
           continue
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
# remove lines with the expression
#
def remove_lines_with_expression(infhandle,exp):
    rexp = re.compile(exp)
    infhandle.seek(0)
    lines = []
    for line in infhandle.readlines():
        if rexp.search(line):
            continue
        else:
            lines.append(line)

    fname = infhandle.name
    infhandle.close()
    fhandle = open(fname,'w')
    fhandle.write( ''.join(lines) )
    fhandle.close()
    infhandle = open(fname,'r')
    return infhandle

#
# find line # with expression
#
def find_line_num_with_expression(infhandle,exp):
    rexp = re.compile(exp)
    infhandle.seek(0)
    iline = 0
    for line in infhandle.readlines():
        if rexp.search(line):
            return iline
        iline = iline + 1
    return None

#
# does line # contain expression
#
def does_line_num_contain_expression(infhandle,lnum,exp):
    rexp = re.compile(exp)
    infhandle.seek(0)
    iline = 0
    for line in infhandle.readlines():
        if iline == lnum and rexp.search(line):
            return True
        elif iline == lnum:
            return False
        iline = iline + 1
    return False
#
# insert macro...
#
def insert_macro_and_save_file(fhandle,mname,mline):
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
# Clean up
#
def clean(file_name):

    infhandle = open(file_name,'r')

    # grab the macro name
    macro_short_string = is_using_macro(infhandle)

    if not macro_short_string:
        print "Unable to find a macro to clean up in file ",file_name
        return False

    # get rid of all the macro calls
    infhandle.seek(0)
    ereg      = macro_short_string + "[^\s]+;$"
    infhandle = remove_lines_with_expression(infhandle,ereg)
    
    # now get rid of the macro definition itself
    ereg = macro_short_string + "[\(a-z]+"
    macro_def_line = find_line_num_with_expression(infhandle,ereg)
    macro_end_line = does_line_num_contain_expression(infhandle,macro_def_line+1,"__FILE__,__LINE__")
    if macro_end_line:
        # we've found our macro def...  get rid of two lines
        infhandle.seek(0)
        flines = infhandle.readlines()
        flines.remove(flines[macro_def_line])
        flines.remove(flines[macro_def_line])
        infhandle.close()
        infhandle = open(file_name,'w')
        infhandle.write(''.join(flines))
        infhandle.close()
    else:
        print "Unable to find the macro definition for ",file_name
        return False

    return True
    
#
# Main function
#
def main(file_name):

   # open the file
   infhandle = open( file_name, 'r' )

   # determine a candidate for the macro definition
   name      = find_macro_candidate(infhandle)
   if name == None:
       print "Couldn't find a macro-name candidate for file ",file_name
       return False

   # find a good insertion point for the DEBUG macro
   last_line_of_header = find_header(infhandle)

   # insert the macro to enable logging...
   infhandle = insert_macro_and_save_file(infhandle,name,last_line_of_header)

   # now comes the more interesting parts
   # ideally we allow certain functions to be instrumented
   # etc, but let's leave that for another day
   # so instead we insert our debug function into the first
   # in a function definition.
   infhandle.seek(0)

   in_c_func = False
   insertion_pts = []
   line_index    = 0

   for line in infhandle:
       # iterate through each line in our file and determine if we're at
       # the start of a C function
       ltple = find_c_function_declaration(line)

       if ltple == None:
           decl = 'none'
       else:
           decl  = ltple[2]

       if decl == 'definition':
           # we've found a C/C++ style definition
           # if the last (non-white space) character is { then
           # we're in business to add our macro call,
           in_c_func = True

       if in_c_func and (is_trailing_char_bracket(line) or is_leading_char_bracket(line)):
           in_c_func = False
           # record the insertion point
           insertion_pts.append(line_index+1)

       # increment the line index
       line_index = line_index + 1

   #
   # rewind the file... read it as an array and insert the macro at each insertion point
   #
   infhandle.seek(0)
   filelines = infhandle.readlines()
   macrostr = write_macro_call(name)
   ii       = 0
   
   for index in insertion_pts:
       filelines.insert(index + ii,macrostr)
       # increment the offset
       ii = ii + 1 

   infhandle.close()
   infhandle = open(file_name,'w')
   infhandle.write( ''.join(filelines) )
   infhandle.close()
   return True

#
# use the script as a program
#
if __name__ == "__main__":

   nargs = len(sys.argv)

   if nargs < 2 or nargs > 3:
       print_usage()
       sys.exit(1)

   try:
       optlist, args = getopt.getopt(sys.argv[1:],'x',['clean','list'])
   except getopt.GetoptError, err:
       print str(err)
       print_usage()

   filename = args[0]
   opts = None
   if nargs == 3:
       opts = args[1]

   if opts == '--clean':
       clean(filename)
   elif opts == '--list':
       print "This isn't built just yet..."
   else:
       main(filename)

