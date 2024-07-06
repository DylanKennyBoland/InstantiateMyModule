#!/usr/bin/env python3
#
# Author: Dylan Boland
#
# Notes:
# (1) Works with Verilog (.v) and SystemVerilog (.sv) files.
# (2) Consult the README file for instructions on how to use the script.
# Alternatively, you can print the help message by running:
#       instantiate_module.py --help
#

# Modules that will be useful
import argparse
import os
import sys
import re

# ==== Some General-info Strings ====
# Tags - define these here so they can be quickly and easily changed
errorTag   = """\t***Error: """
successTag = """\t***Success: """
infoTag    = """\t***Info: """

# Standard help & error messages
helpMsg    = infoTag + """The path to the Verilog or SystemVerilog module description should be
given after using the '--filename' switch."""
noArgsMsg  = errorTag + """No input arguments were specified. Please use '--filename' followed
\tby the name of the module to be instantiated."""
noSuchFileMsg   = errorTag + """The module file '{}' could not be located - double-check the name or file path."""
fileReadSuccess = successTag + """The module file was read in successfully."""
fileReadError   = errorTag + """The module file could not be read in successfully."""
moduleNameNotIdentified = errorTag + """The module name could not be identified. Please ensure that you have used
\ta standard or conventional structure. An example is shown below:
            module serialTX #
                (
                parameter INCR = 26'd25770 // amount by which the accumulator is incremented
                )
                (
                input clk,
                input reset,
                input [7:0] data,
                input send,
                output reg txOut,
                output busy
                );
                // The module description or logic goes below
"""
noParamsFound       = infoTag + """No parameters were identified for this module."""
noInputsIdentified  = errorTag + """No module inputs were identified."""
noOutputsIdentified = errorTag + """No module outputs were identified."""

# Instantiated module print-out message
jobDoneMsg = """
\n\n\t===========================================================================
\t\tAdditionally, you can see the instantiated module below!
\t==========================================================================="""

# Goodbye message
goodbyeMsg = """
\t===========================================================================================
\t\tSuccess! The instantiated module is at {}.
\t==========================================================================================="""

# Some Header (Delimiter) Strings
# These allow us to cleary separate input and
# output ports when instantiating the module
inputPortsHeader = """// ==== Inputs ===="""
outputPortsHeader = """// ==== Outputs ====\n\t"""
paramsHeader = """// ==== Parameters ===="""

# Function to handle the input arguments
def parsingArguments():
    parser = argparse.ArgumentParser(description = "The file containing the Verilog or SystemVerilog module description.")
    parser.add_argument('--filename', type = str, help = helpMsg)
    return parser.parse_args()

if __name__ == "__main__":
    args = parsingArguments() # parse the input arguments (if there are any)
    if len(sys.argv) == 1:
        print(noArgsMsg)
        exit()
    moduleFileName = args.filename # get the file name (or path) from the input arguments
    moduleFileType = os.path.splitext(moduleFileName)[1] # get the file extension type (either ".v" or ".sv")
    # ==== Check if the File (path) Exists ====
    if os.path.isfile(moduleFileName) is False:
        print(noSuchFileMsg.format(moduleFileName))
        exit()
    
    # ==== Try to Read the Module File in ====
    with open(moduleFileName) as p:
        try:
            moduleContents = p.read() # read the file into a string
            print(fileReadSuccess)
        except:
            print(fileReadError)
            exit()
    
    # ==== Define the Patterns to Look For ====
    #
    # The regular expressions (patterns) below use an idea called
    # "negative lookbehind". This allows us to *avoid* matching the
    # words "module", "parameter", "input", and "output" when they
    # appear in a comment or as part of a longer word. For example, we
    # wouldn't want to match the following instances of the word "output"
    # when trying to extract the module's outputs:
    #
    # // output current_exceeded, <- part of a comment, so it's not an actual output port
    # // this output goes to the clock/reset-management block <- the word has simply appeared in a comment
    # * After 5 clock cycles, the controller-busy output will be de-asserted <- the word has simply popped up in a multi-line comment
    # input wire [7:0] kp_multiplier_output <- the word has appeared in the name of an input!
    #
    # The negative-lookbehind expression is shown below:
    #
    # (?<!(?://[-\w\s]))(?<!(?:\*[-\w\s]))
    #
    # The above will avoid the following kinds of statements from being matched:
    #
    # // output current_threshold,
    # *voutput
    # //output will be in one-hot format
    #
    # However, the 're' module in Python requires that the lookbehind expression be of fixed
    # width. The expression (?<!(?://[-\w\s])) has a width of 3: the two "/" symbols, and 
    # one alphanumeric character (\w) or one space (\s). This is a problem, as a keyword
    # may appear *anywhere* in a comment. Consider the comment below:
    #
    # //                       output dram_bank_closed
    #
    # We want Python to see "output", and then look back and say "Oh, this is part of a
    # comment, so I will skip this line". But for Python to know it is part of a comment
    # it needs to look back further than a space or two.
    #
    # We will use a 'for' loop to create the following kind of string which we will use in our
    # regular expressions:
    #
    # (?<!(?://[-\w\s]))(?<!(?://[-\w\s]{2}))(?<!(?://[-\w\s]{3})) ... (?<!(?://[-\w\s]{20}))
    #
    # The regular expression above would instruct Python to search as far back as 20 spaces.
    maxLookbehindDistance = 30
    notPartOfComment = r""
    moduleNamePatternStr = r""
    paramPatternStr = r""
    inputPatternStr = r""
    outputPatternStr = r""

    # ==== Form the Negative Lookbehind Expression ====
    for i in range(0, maxLookbehindDistance + 1):
        notPartOfComment += "(?<!(?://[-\w\s]{{{}}}))(?<!(?:\*[-\w\s]{{{}}}))".format(i, i)

    # ==== Create the Regular Expressions ====
    # First, create the raw strings:
    moduleNamePatternStr = notPartOfComment + "module\s+(?:\$\[PREFIX\])([a-zA-Z\_0-9]+)"
    paramPatternStr = notPartOfComment + "\s*parameter(?:\s*\${0,2}\[[-`\w+:*/{}$ \[\]]+\]){0,2}\s+([\w\$\[\]]+)\s*="
    inputPatternStr = notPartOfComment + "\s*input(?:\s+\w+)?(?:\s*\${0,2}\[[-`\w+:*/{}()$ \[\]]+\]){0,2}\s+([\w+\$\[\]{}]+)\s*,?"
    outputPatternStr = notPartOfComment + "\s*output(?:\s+\w+)?(?:\s*\${0,2}\[[-`\w+:*/{}()$ \[\]]+\]\s*){0,2}\s+([\w\$\[\]{}]+)\s*,?"

    # Next, call the compile() method:
    moduleNamePattern    = re.compile(moduleNamePatternStr)
    moduleParamsPattern  = re.compile(paramPatternStr)
    moduleInputsPattern  = re.compile(inputPatternStr)
    moduleOutputsPattern = re.compile(outputPatternStr)

    # ==== Extract the Module Name first ====
    matches = re.findall(moduleNamePattern, moduleContents)

    # ==== Check that only one Match was found for the Module Name ====
    if (len(matches) != 1):
        print(matches)
        print(moduleNameNotIdentified)
        exit()
    else:
        moduleName = matches[0] # store the module name

    # ==== Extract the Module Parameters (if there are any) ====
    matches = re.findall(moduleParamsPattern, moduleContents)
    # ==== Check if any Matches were found ====
    if (len(matches) == 0):  # if there were zero matches
        print(noParamsFound) # print out message saying the module has no parameters (or none were identified)
        moduleHasParams = False
    else:
        moduleParams = matches # capture the list of module parameters
        moduleHasParams = True
    
    # ==== Extract the Module Inputs ====
    matches = re.findall(moduleInputsPattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noInputsIdentified) # print a message saying that no module inputs were found
    else:
        moduleInputs = matches # capture the list of module inputs
    
    # ==== Extract the Module Outputs ====
    matches = re.findall(moduleOutputsPattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noOutputsIdentified) # print a message saying that no module outputs were found
    else:
        moduleOutputs = matches # capture the list of module outputs
    
    # ==== Instantiate the Module ====
    #
    # ==== Step 1: Create the Parameter Part of the String (if there are any parameters) ====
    if (moduleHasParams):
        paramStr = ""
        numParams = len(moduleParams) # get the number of parameters
        for i, param in enumerate(moduleParams):
            if (i == numParams - 1):
                paramStr += f".{param}({param})"
            else:
                paramStr += f".{param}({param}),\n\t"
    
    # ==== Step 2: Create Part of the String with the Inputs ====
    inputPortsStr = ""
    for inputPort in moduleInputs:
        inputPortsStr += f".{inputPort}({inputPort}),\n\t"

    # ==== Step 3: Create Part of the String with the Outputs ====
    outputPortsStr = ""
    numOutputs = len(moduleOutputs) # number of outputs for the module
    for i, outputPort in enumerate(moduleOutputs):
        if (i != numOutputs - 1):
            outputPortsStr += f".{outputPort}({outputPort}),\n\t"
        else:
            outputPortsStr += f".{outputPort}({outputPort})"
    
    # ==== Step 4: Form the Final String =====
    instantiatedModule = "" # empty at the moment
    if (moduleHasParams):
        # ==== Using f (formatted) Strings ====
        instantiatedModule += f"""{moduleName} #
        (
        {paramsHeader}
        {paramStr}
        ) dut
        (
        {inputPortsHeader}
        {inputPortsStr}{outputPortsHeader}{outputPortsStr}
        );"""
    else:
        instantiatedModule += f"""{moduleName} dut
        (
        {inputPortsHeader}
        {inputPortsStr}{outputPortsHeader}{outputPortsStr}
        );"""
    
    # ==== Step 5: Write the Formatted String to a File <moduleName>_instantiated.v (or .sv) ====
    outputFileName = f"{moduleName}_instantiated" + moduleFileType # name of the file to which we will write
    with open(outputFileName, "w") as p: # create (or open) the file in "write" mode
        p.write(instantiatedModule)
        print(goodbyeMsg.format(outputFileName))
        print(jobDoneMsg)
        print("\n" + instantiatedModule)
