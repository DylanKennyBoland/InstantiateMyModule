// Author: Dylan Boland

module accumulator #
	(
	// ==== Parameters ====
	parameter ACCUM_SZ = 32, // the size (in bits) of the accumulator register
	parameter DATA_SZ = 16   // the number of bits in the input to the accumulator module
	)
	(
	// ==== Inputs ====
	input clk,
	input reset_n, // active-low asynchronous reset
	input [DATA_SZ-1:0] data_in, // the data in - interpret as a two's complement signed value
	// ==== Outputs ====
	output [ACCUM_SZ-1:0] accum_out // the output of the accumulator - a signed value in two's complement form
	);
	
	// ==== Local Parameters ====
	// If adding the input to the current value in the accumulator
	// causes an overflow then positive saturation is performed. This
	// means that the accumulator is loaded with the maximum value that
	// it can store - i.e., all the bits are set (1'b1) and the sign bit
	// (MSB) is 0, indicating a positive number.
	//
	// If adding the input causes an underflow then negative saturation
	// is performed. This means that the accumulator stores the most
	// negative number it can hold - i.e., all the bits are cleared
	// (1'b0) except for the sign bit (MSB), which is set (1'b1).
	localparam [ACCUM_SZ-1:0] SAT_HIGH_VAL = {1'b0, {(ACCUM_SZ-1){1'b1}}};
	localparam [ACCUM_SZ-1:0] SAT_LOW_VAL = {1'b1, {(ACCUM_SZ-1){1'b0}}};
	
	// ==== Internal Signals ====
	reg [ACCUM_SZ-1:0] accum_reg;       // the accumulator register
	wire [ACCUM_SZ-1:0] curr_accum_val; // the current value in the accumulator
	wire [ACCUM_SZ:0] adder_out;        // the output from the adder; 1-bit wider than the widest input
	wire sat_high;                      // if asserted, it indicates that positive saturation should occur (saturate to the highest value)
	wire sat_low;                       // if asserted, it indicates that negative saturation should occur (saturate to the lowest value)
	wire [1:0] adder_out_two_msbs;      // the two MSBs of the output of the adder
	
	// ==== Combinational Logic ====
	assign curr_accum_val = accum_reg;
	assign adder_out = data_in + curr_accum_val;
	assign adder_out_two_msbs = adder_out[ACCUM_SZ-1:ACCUM_SZ-2];
	
	// ==== Logic for the Saturation (Flag) Signals ====
	assign sat_high = (adder_out_two_msbs == 2'b01) ? 1'b1 : 1'b0;
	assign sat_low = (adder_out_two_msbs == 2'b10) ? 1'b1 : 1'b0;
	
	// ==== Drive the Output ====
	assign accum_out = accum_reg; // the output is driven with whatever value is in the accumulator register
	
	// ==== Logic for Updating the Accumulator Register ====
	always @ (posedge clk or negedge reset_n) begin
		if (!reset_n) begin
			accum_reg <= {ACCUM_SZ{1'b0}};
		end else begin
			if (sat_high) begin
				accum_reg <= SAT_HIGH_VAL;
			end else if (sat_low) begin
				accum_reg <= SAT_LOW_VAL;
			end else begin
				accum_reg <= adder_out[ACCUM_SZ-1:0]; // take the lower ACCUM_SZ bits of the output from the adder
			end
		end
	end

endmodule
		
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	