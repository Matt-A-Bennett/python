#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smalll code snippets that I found myself repeating.

Created by Matthew A. Bennett (Fri Jul 12 11:06:58 2019)
Matthew.Bennett@glasgow.ac.uk
"""

#%% =============================================================================
# imports
import os
from warnings import warn

#%% =============================================================================
def bash(commands):
    """Execute one or more commands in bash.

    Mandatory arguments:
    commands: a string or list of on or more strings where
              each string is a line to be executed.
    """

    if type(commands) == str:
        commands = [commands]

    # check arguments are in correct format
    elif type(commands) != list:
        raise Exception("The argument 'commands' must be a string or a list of one or more strings.")

    # run each command in bash
    for command in commands:
        print(command)
        os.system(command)

    return None

#%% =============================================================================
def add_extesnion_if_missing(filename, extension, verbose=False):
    """If a filenmae does not have specified extension, this will be added.

        Mandatory arguments:
        filename: a name which may or may not need an extension.

        extension: what to append if not found to be on the end of filename

        Optional arguments:
        verbose: if True, the function will alert the user when making assumptions
    """
    if verbose and '.' in filename:

        warn(f'filename: {filename} may already have an extension')
        warn("(a '.' character was found in filename)")
        warn('we will go ahead anyway')
        print('')

    if '.' not in extension:
        extension = '.' + extension

    if extension not in filename:
        if verbose: warn(f'{extension} not found in filename - adding {extension} now')
        filename += extension

    if verbose: print('new filename is: ' + filename)
    return filename

#%% =============================================================================
def inject_substring_before_extension(filename, substr, extension='', force_append=False,
                                      verbose=False):
    """Add a substring to the end of a filename before the extension.

        Mandatory arguments:
        filename: the filename (e.g. myfile.ext)

        substr: substring to be appended (e.g. '_append')

        Optional arguments:
        extension: the extension that exists at the end of the filename (e.g. '.ext')

        force_append: append the substr even if no extension provided or found

        The above would become: myfile_append.ext

        verbose: if True, the function will alert the user when making assumptions
    """

    if extension == '':
        if verbose: warn('no extension provided')
        if '.' in filename:
            index = filename.rfind('.')
            extension = filename[index:]
            if verbose: warn(f'assuming extension is {extension}')
        else:
            if not force_append:
                raise Exception('could not find an existing extension in filename')
            else:
                if verbose: print('appending no matter what')
                extension = filename[-1]

    elif extension not in filename:
        raise Exception('extension is not in filename')

    index = filename.rfind(extension)

    if filename[index:] != extension:
       raise Exception('filename does not end with provided extension')

    filename = filename[:index] + substr + extension

    if verbose: print('new filename is: ' + filename)
    return filename


