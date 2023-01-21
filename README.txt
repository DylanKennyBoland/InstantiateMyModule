Project Name: InstantiateMyModule
Author: Dylan Boland

Instantiating modules with many, many ports (possible 100s!) can be tedious and
take a long time, leading to a sore wrist and a sad mouse :/

This repo. contains a Python script, instantiate_module.py, that accepts, as an
argument, a path to a Verilog (.v) or SystemVerilog (.sv) module file. It then
tries to identify the modules parameters and ports. Using this information, it
instantiates the module, and writes the instantiated module to both the console as
well as an output file.

Q: How to use the script?

	"py instantiate_module.py --filename <path_to_your_module>"

A good idea is to add the path to the script to your PATH environment variable. 
This will allow you to use the script anywhere in your Linux environment.

For example, suppose you keep the script at:

	"/c/Users/Kenny/Desktop/InstantiateMyModule/instantiate_module.py"
	
You could add the follow line to your shell run-command (.rc) file (assuming a bash shell):

	'export PATH="/c/Users/Kenny/Desktop/InstantiateMyModule/instantiate_module.py":$PATH'

*Alternatively, you could simply create an alias in your ~/.alias file. For example, you could
add:

	"alias instantiate_module='py /c/Users/Kenny/Desktop/InstantiateMyModule/instantiate_module.py'"

I hope it helps! And do message if you see any bugs or ways in which it could be made a little better!
