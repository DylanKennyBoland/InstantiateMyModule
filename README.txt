Project Name: InstantiateMyModule
Author: Dylan Boland

Instantiating modules with many, many ports (possible 100s!) can be tedious and
take a long time, leading to a sore wrist and a sad mouse :/

This repo. contains a Python script, instantiate_module.py, that accepts, as an
argument, a path to a Verilog (.v) or SystemVerilog (.sv) module file. It then
tries to identify the modules parameters and ports. Using this information, it
instantiates the module, and writes the instantiated module to both the console as
well as an output file.

Q: How is the script used?

	"py instantiate_module.py --filename <path_to_your_module>"

A good idea is to add the path to the script to your PATH environment variable. 
This will allow you to use the script anywhere in your Linux environment.

For example, suppose you keep the script at:

	"/c/Users/Kenny/Desktop/InstantiateMyModule/instantiate_module.py"
	
You could add the following line to your shell run-command (.rc) file (assuming a bash shell):

	'export PATH="/c/Users/Kenny/Desktop/InstantiateMyModule/instantiate_module.py":$PATH'

*Alternatively, you could simply create an alias in your ~/.alias file. For example, you could
add the following line to your .alias file (normally located in your home (~) directory):

	"alias instantiate_module='py /c/Users/Kenny/Desktop/InstantiateMyModule/instantiate_module.py'"

Then, regardless of where you are in your Linux environment, you could just use (after sourcing your
.alias file):

	"instantiate_module --filename <path_to_your_module>"

I hope it helps! And do message if you see any bugs or ways in which the script could be improved!

*Usage notes:
(1) Try and define each module input and output on its own line.
(2) Try and include a space between a ports's width and its name. For example,
"input [DATA_WIDTH-1:0] wdata" is preferable than "input [DATA_WIDTH-1:0]wdata".
(3) If you see an error message saying that no module inputs or outputs were identified, and
the module does, in fact, have inputs and outputs defined, then highlight the whole port list
and shift it left by 1 space, before shifting it back to the right by 1 space. Save the file again, and
rerun the Python script - the issue will hopefully be resolved.
(4) When defining the module parameters, use the keyword "parameter".



