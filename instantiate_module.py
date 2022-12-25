#!/usr/bin/env python3

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
    module_name_pattern = re.compile(r'module\s+([a-zA-Z\_0-9]+)[\n\s]+#?[\n\s]*\(')
    module_parameters_pattern = re.compile(r'parameter\s*([a-zA-Z\_0-9]+)\s*=')
    module_inputs_pattern = re.compile(r'input\s*(?:wire)?\s*(?:\[[a-zA-Z0-9\_\-\:]+\])?\s*([a-zA-Z\_0-9]+)\s*,')
    # ==== Extract the Module Name first ====
    matches = re.findall(module_name_pattern, moduleContents)
    # ==== Check that only one Match was found for the Module Name ====
    if (len(matches) != 1):
        print(moduleNameNotIdentified)
    else:
        module_name = matches[0] # store the module name
    print(module_name)

    # ==== Extract the Module Parameters (if there are any) ====
    matches = re.findall(module_parameters_pattern, moduleContents)
    # ==== Check if any Matches were found ====
    if (len(matches) == 0): # if there were zero matches
        print(noParamsFound) # print out message saying the module has no parameters (or none were identified)
    else:
        module_parameters = matches # capture the list of module parameters
        print(module_parameters)
    
    # ==== Extract the Module Inputs ====
    matches = re.findall(module_inputs_pattern, moduleContents)
    if (len(matches) == 0): # if there were no matches
        print(noInputsIdentified) # print a message saying that no module inputs were found
    else:
        module_inputs = matches
        print(module_inputs)


