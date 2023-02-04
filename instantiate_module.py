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
    # NOTE: the patterns for looking for the inputs and outputs in the module
    # contents use an idea called "negative lookbehind".
    #
    # (?<!(?: |/|[a-zA-Z\_])) <- The negative lookbehind expression.
    #
    # We don't want to capture or match the words "input", "output" or "parameter" when they appear
    # in a comment. In order to achieve this, we make sure that any match for "input", "output"
    # or "parameter" is not preceded by any of the following:
    # (1) A space (e.g., '// wdata is an input to the module')
    # (2) A slash (e.g., '//output wdata')
    # (3) A character (like an underscore) (e.g., '// the reference voltage input, "vref_input"')
    #
    # NOTE: the quantifier {0,2} that is used in some of the regular expressions below
    # is to allow for one- and two-dimensional inputs, outputs or parameters - e.g.,
    # "input [31:0][7:0] data," <- Two dimensions
    # "input [7:0] addr,"       <- One dimension
    # "input sel,"              <- Single-bit input
    #
    # A pattern inside brackets "()" is a group, and Python regex supports group capture so
    # that you can extract particular parts of a matched expression. We only want to capture certain
    # parts of the matched expression, like the name of the input, output, or parameter. For any groups
    # which we don't want to capture, we use "?:" at beginning - e.g.,
    #
    # "input(?:\s+wire\b|\s+reg\b)?..." <- The pattern "input" might be (?) followed by "wire" or "reg"... but don't capture them
    #
    # Lastly, we use "\b" in order to match whole words only. The "\b" means the pattern must be followed
    # by a word boundary (e.g., a space or some non-word character).
    #
    # The backward tick (`) used in some of the character sets (e.g., [`a-zA-Z0-9\_\-\+\:\*/ ]) is to allow
    # macros to be used when defining a signal's width (although parameters are usually used for this) - e.g.,
    #
    # "input [`ADDR_WIDTH - 1:0] addr; // the address lines (bus)"
    #
    # The "\*" and "\" used in some of the character sets are to allow the multiply-by (*) and divide-by (\) operators
    # to be used when defining a signal's width - e.g.,
    #
    # "input [RX_BUFF_SZ_BITS/8 - 1:0] rx_byte_en; // the byte-enable bus for the receive buffer"
    #
    # "output [NUM_DEVICES*4 - 1:0] fault_status; // each device has four fault-status bits"
    moduleNamePattern    = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))module\s+([a-zA-Z\_0-9]+)[\n\s]*#?[\n\s]*\(')
    moduleParamsPattern  = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))parameter\s*(?:\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]\s*){0,2}\s*([a-zA-Z\_0-9]+)\s*=')
    moduleInputsPattern  = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))input(?:\s+wire\b|\s+reg\b)?\s*(?:\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]\s*){0,2}\s*([a-zA-Z\_0-9]+)\s*,?')
    moduleOutputsPattern = re.compile(r'(?<!(?: |/|[a-zA-Z\_]))output(?:\s+wire\b|\s+reg\b)?\s*(?:\[[`a-zA-Z0-9\_\-\+\:\*/ ]+\]\s*){0,2}\s*([a-zA-Z\_0-9]+)\s*,?')
    # ==== Extract the Module Name first ====
    matches = re.findall(moduleNamePattern, moduleContents)
    # ==== Check that only one Match was found for the Module Name ====
    if (len(matches) != 1):
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

    
