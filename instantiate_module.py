#!/usr/bin/env python3

# Author: Dylan Boland

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
helpMsg    = """The path to the Verilog or SystemVerilog module description should be
given after using the '--filename' switch."""
noArgsMsg  = """No input arguments were specified. Please use '--filename' followed 
by the name of the module to be instantiated."""
noSuchFileMsg   = errorTag + """The module file '{}' could not be located - double-check the name or file path."""
fileReadSuccess = successTag + """The module file was read in successfully."""
fileReadError   = errorTag + """The module file could not be read in successfully."""
moduleNameNotIdentified = """The module name could not be identified. Please ensure that you have used
a standard or conventional structure. An example is shown below:
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
\t===========================================================================
\t\tSuccess! The instantiated module is at {}.
\t==========================================================================="""

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
            print(fileReadSuccess + "\n" + moduleContents)
        except:
            print(fileReadError)
            exit()
    

    # ==== Define the Patterns to Look For ====
    # NOTE: the patterns for looking for the inputs and outputs in the module
    # contents use an idea called "negative lookbehind".
    #
    # (?<!(?: |/|[a-zA-Z\_])) <- The negative lookbehind expression.
    #
    # We do not wish to capture or match the word "input" or "output" when it appears
    # as part of a comment. In order to achieve this, we make sure that any match for "input" or
    # "output" is not preceded by any of the following:
    # (1) A space (e.g., '// wdata is an input to the module')
    # (2) A slash (e.g., '//input voltage data to the module')
    # (3) A character (e.g., '// the reference voltage input, "vref_input"')
    #
    # NOTE: the quantifier {0,2} that is used in some of the regular expressions below
    # is to allow for one- and two-dimensional inputs or outputs - e.g.,
    # "input [31:0][7:0] data"
    moduleNamePattern = re.compile(r'module\s+([a-zA-Z\_0-9]+)[\n\s]*#?[\n\s]*\(')
    moduleParamsPattern = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))parameter\s+(?:\[[a-zA-Z0-9\_\-\:]+\]){0,2}\s*([a-zA-Z\_0-9]+)\s*=')
    moduleInputsPattern = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))input\s+(?:wire)?\s*(?:\[[a-zA-Z0-9\_\-\:]+\]\s*){0,2}\s*([a-zA-Z\_0-9]+)\s*,?')
    moduleOutputsPattern = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))output\s+(?:wire|reg)?\s*(?:\[[a-zA-Z0-9\_\-\:]+\]\s*){0,2}\s*([a-zA-Z\_0-9]+)\s*,?')
    # ==== Extract the Module Name first ====
    matches = re.findall(moduleNamePattern, moduleContents)
    # ==== Check that only one Match was found for the Module Name ====
    if (len(matches) != 1):
        print(moduleNameNotIdentified)
    else:
        moduleName = matches[0] # store the module name

    # ==== Extract the Module Parameters (if there are any) ====
    matches = re.findall(moduleParamsPattern, moduleContents)
    # ==== Check if any Matches were found ====
    if (len(matches) == 0): # if there were zero matches
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

    
