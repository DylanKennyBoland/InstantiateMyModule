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
# Script usage:
#
# The script should be called as follows:
#
#           instantiate_module.py --filename <module_file>
#
# The instantiated module is written to an output file with the following name format:
#
#           <module_file>_instantiated.v (or .sv)
#
# For example, imagine we had a module file "accumulator.v" that we wanted to instantiate.
# We would call the script as follows:
#
#           instantiate_module.py --filename accumulator.v
#
# The text (or code) representing the instantiated module will be output to the terminal
# and also written to a file called:
#
#           accumulator_instantiated.v
#
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
given after using the '--filename' switch. For example, suppose we wanted to instantiate a module
accumulator.v. The script would be called as follows:

            instantiated_module.py --filename accumulator.v
            
The instantiated module will be written to an output file with the following name:

            accumulator_instantiated.v"""
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
    
    # ==== Read the File in Line by Line ====
    # We want to inspect each line on its own in order
    # to avoid problems that can arise when you view the
    # entire file as one long string.
    #
    # We can remove the newline characters (\n).
    with open(moduleFileName) as p:
        lines = [line.rstrip('\n') for line in p]

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
    # (?<!(?://[-\w\s]))(?<!(?://[-\w\s]{2}))(?<!(?://[-\w\s]{3})) ... (?<!(?://[-\w\s]{30}))
    #
    # The regular expression above would instruct Python to search as far back as 30 spaces.
    # 
    # The regular expressions also use "groups". A group is specified within (), and they allow us
    # to capture certain parts of pattern which might be of interest (e.g., the name of a port, the width
    # of a port etc.). The first set of () specifies the pattern associated with group 1, the second set of
    # () corresponds to the pattern for group 2 etc.
    #
    # Lastly, the regular expressions for extracting the inputs and outputs use conditional checks.
    #
    # (?(2)\s*|\s+) <- if there was a match for group 2, then match "\s*" (i.e., match 0 or more spaces), otherwise
    # match "\s+" (one or more spaces). This accounts for the following kind of port declaration:
    #
    # output wire [3:0]bank_addr, <- the designer didn't place a space between the width (i.e., [3:0]) and the port name (bank_addr).
    #
    # The above declaration is actually allowed (legal), even if it isn't neat. So, we need the regular expression to allow for
    # no space to be used between the width and the signal name *IF* there is a width. If there is a width (e.g., [3:0]) then group 2
    # will match. If there is no width specified within square brackets ([]), then group 2 will not match. In that case, we will insist
    # on one or more spaces between the type (i.e., wire, reg, logic or a user-defined type) and the name.
    #
    # output reg controller_busy <- controller_busy would be extracted from this line
    #
    # output data_valid <- the designer hasn't specified the type (e.g., wire or reg), but data_valid will still be extracted as the name of the output
    maxLookbehindDistance = 60
    notPartOfComment = r""
    moduleNamePatternStr = r""
    paramPatternStr = r""
    inputPatternStr = r""
    outputPatternStr = r""

    # ==== Form the Negative Lookbehind Expression ====
    for i in range(0, maxLookbehindDistance + 1):
        notPartOfComment += "(?<!(?://[-\w\s.,':()]{{{}}}))(?<!(?:\*[-\w\s.,':()]{{{}}}))".format(i, i)

    # ==== Create the Regular Expressions ====
    # First, create the raw strings:
    # moduleNamePatternStr = notPartOfComment + "module\s+(?:\$\[PREFIX\])([a-zA-Z\_0-9]+)"
    moduleNamePatternStr = notPartOfComment + "\s*module\s+(?:\$\[PREFIX\])?(\w+)"
    # The (?!([-`\w\s>=+]+;)) used in the regular expression for extracting parameters is a "negative lookahead". It
    # looks ahead and makes sure that the parameter declaration is *not* ending in ";", as then it would indicate that
    # the parameter declaration is happening *inside* the module. In this case, it would not be an input module parameter.
    paramPatternStr = notPartOfComment + "\s*parameter(\s*\${0,2}\[`?([-`\w+\*\$/: {}()]+)?(\$\[\w+\])?([-`\w+\*\$/: {}()]+)?\]\s*){0,2}(?(2)\s*|\s+)([\w$\[\]{}]+)\s*=(?!([-`\w\s>=+]+;))"
    parameterGroupIndex = 4 # the parameter name will be captured by the fifth group (group index 4)
    # The (\s*\${0,2}\{\w+\}) used in the regular expressions below is to allow inputs such as:
    #
    # input $${ARRAY_SIZE} mem_data
    #
    # to be captured correctly (i.e., fully).
    inputPatternStr = notPartOfComment + "\s*input(\s+\w+)?(\s*\${0,2}\{\w+\})?(\s*\${0,2}\[`?([-`\w+\*\$/: {}()]+)?(\$\[\w+\])?([-`\w+\*\$/: {}()]+)?\]\s*){0,2}(?(3)\s*|\s+)([\w$\[\]{}]+)\s*,?"
    outputPatternStr = notPartOfComment + "\s*output(\s+\w+)?(\s*\${0,2}\{\w+\})?(\s*\${0,2}\[`?([-`\w+\*\$/: {}()]+)?(\$\[\w+\])?([-`\w+\*\$/: {}()]+)?\]\s*){0,2}(?(3)\s*|\s+)([\w$\[\]{}]+)\s*,?"
    inputGroupIndex = 6 # the input port's name will be capture by the seventh group (i.e., ([\w$\[\]{}]+)), which has an index of 6
    outputGroupIndex = 6

    # Next, call the compile() method:
    moduleNamePattern    = re.compile(moduleNamePatternStr)
    moduleParamsPattern  = re.compile(paramPatternStr)
    moduleInputsPattern  = re.compile(inputPatternStr)
    moduleOutputsPattern = re.compile(outputPatternStr)

    # ==== Extract the Name, Parameters, Inputs, and Outputs ====
    moduleNames   = []
    moduleParams  = []
    moduleInputs  = []
    moduleOutputs = []
    
    for line in lines: # iterate over each line
        # Check the line to see if:
        # (1) It contains the module name
        # (2) Or one of the module's parameters (if there are any)
        # (3) Or an input of the module
        # (4) Or an output of the module
        nameMatch   = re.findall(moduleNamePattern, line)
        paramMatch  = re.findall(moduleParamsPattern, line)
        inputMatch  = re.findall(moduleInputsPattern, line)
        outputMatch = re.findall(moduleOutputsPattern, line)
        # ==== Check if we have matched a module name ====
        if (len(nameMatch) != 0):
            moduleName = nameMatch[0]
            if moduleName not in moduleNames:
                moduleNames.append(moduleName)
        # ==== Check if we have matched a module parameter ====
        if (len(paramMatch) != 0):
            parameterName = paramMatch[0][parameterGroupIndex]
            if parameterName not in moduleParams:
                moduleParams.append(parameterName)

        # ==== Check if we have matched a module input ====
        if (len(inputMatch) != 0):
            inputName = inputMatch[0][inputGroupIndex]
            if inputName not in moduleInputs:
                moduleInputs.append(inputName)
        # ==== Check if we have matched a module output ====
        if (len(outputMatch) != 0):
            outputName = outputMatch[0][outputGroupIndex]
            if outputName not in moduleOutputs:
                moduleOutputs.append(outputName)
    
    # ==== Check that only one Match was found for the Module Name ====
    if (len(moduleNames) != 1):
        print(moduleNameNotIdentified)
        exit()
    else:
        moduleName = moduleNames[0] # store the module name

    if (len(moduleInputs) == 0): # if there were no matches
        print(noInputsIdentified)
        exit()

    if (len(moduleOutputs) == 0): # if there were no matches
        print(noOutputsIdentified)
        exit()

    # ==== Check if any parameters were identified ====
    moduleHasParams = True # let's assume the module has parameters, and we'll check our assumption below
    if (len(moduleParams) == 0): # if there were zero matches
        print(noParamsFound) # print out message saying the module has no parameters (or none were identified)
        moduleHasParams = False
    
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
