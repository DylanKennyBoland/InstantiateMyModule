#!/usr/bin/env python3

# Author: Dylan Boland

# Modules that will be useful
import argparse
import os
import sys
import re

# Some general-info strings
helpMsg = """The path to the Verilog or SystemVerilog module description should be
given after using the '--filename' switch."""
noArgsMsg = """No input arguments were specified. Please use '--filename' followed 
by the name of the module to be instantiated."""
noSuchFileMsg = """The module file '{}' could not be located - double-check the name or file path."""
fileReadSuccess = """The module file was read in successfully."""
fileReadError = """The module file could not be read in successfully."""
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
noParamsFound = """No parameters were identified for the module."""
noInputsIdentified = """No module inputs were identified."""
noOutputsIdentified = """No module outputs were identified."""
goodbyeMsg = """Success! The instantiated module is at {}."""
# Some Header (Delimiter) Strings
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
    moduleNamePattern = re.compile(r'module\s+([a-zA-Z\_0-9]+)[\n\s]+#?[\n\s]*\(')
    moduleParamsPattern = re.compile(r'parameter\s*(?:\[[a-zA-Z0-9\_\-\:]+\])?\s*([a-zA-Z\_0-9]+)\s*=')
    moduleInputsPattern = re.compile(r'input\s*(?:wire)?\s*(?:\[[a-zA-Z0-9\_\-\:]+\])?\s*([a-zA-Z\_0-9]+)\s*,?')
    moduleOutputsPattern = re.compile(r'output\s*(?:wire|reg)?\s*(?:\[[a-zA-Z0-9\_\-\:]+\])?\s*([a-zA-Z\_0-9]+)\s*,?')
    # ==== Extract the Module Name first ====
    matches = re.findall(moduleNamePattern, moduleContents)
    # ==== Check that only one Match was found for the Module Name ====
    if (len(matches) != 1):
        print(moduleNameNotIdentified)
    else:
        moduleName = matches[0] # store the module name
    print(moduleName)

    # ==== Extract the Module Parameters (if there are any) ====
    matches = re.findall(moduleParamsPattern, moduleContents)
    # ==== Check if any Matches were found ====
    if (len(matches) == 0): # if there were zero matches
        print(noParamsFound) # print out message saying the module has no parameters (or none were identified)
        moduleHasParams = False
    else:
        moduleParams = matches # capture the list of module parameters
        print(moduleParams)
        moduleHasParams = True
    
    # ==== Extract the Module Inputs ====
    matches = re.findall(moduleInputsPattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noInputsIdentified) # print a message saying that no module inputs were found
    else:
        moduleInputs = matches # capture the list of module inputs
        print(moduleInputs)
    
    # ==== Extract the Module Outputs ====
    matches = re.findall(moduleOutputsPattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noOutputsIdentified) # print a message saying that no module outputs were found
    else:
        moduleOutputs = matches # capture the list of module outputs
        print(moduleOutputs)
    
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
                paramStr += f".{param}({param}),\n"
    
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
        print(instantiatedModule)
    else:
        instantiatedModule += f"""{moduleName} dut
        (
        {inputPortsHeader}
        {inputPortsStr}{outputPortsHeader}{outputPortsStr}
        );"""
        print(instantiatedModule)
    
    # ==== Step 5: Write the Formatted String to a File <moduleName>_instantiated.v (or .sv) ====
    outputFileName = f"{moduleName}_instantiated" + moduleFileType # name of the file to which we will write
    with open(outputFileName, "w") as p: # create (or open) the file in "write" mode
        p.write(instantiatedModule)
        print(goodbyeMsg.format(outputFileName))

    
