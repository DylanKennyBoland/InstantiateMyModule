// Author: Dylan Boland (Student)
//
// A Verilog description of a basic serial transmit module.
// It takes in a byte to send, and sends the byte bit by bit.
// The least-significant bit (LSB) is sent first.
// The rate at which the bits are sent can be controlled by changing
// the frequency of the bitPulse signal - this is altered by changing
// the module parameter "INCR", which controls by what amount the accumulator
// is incremented on each rising edge of the clock. Incrementing by a greater
// amount will cause the accumulator to overflow more rapidly, leading to a 
// bitPulse frequency, thereby leading to a higher transmit frequency.
//
//
module serialTX
	#(parameter INCR = 26'd25770)
	(input clk,
	input reset,
	input [7:0] data,
	input send,
	output reg txOut,
	output busy );
	
	// ==== Define some useful Internal Signals ====
	reg [25:0] accum; // 26-bit accumulator for bit timing
	reg [7:0] dataReg; // 8-bit data register - holds the data to be transmitted
	reg [3:0] bitCount; // count bits that are still to be sent
	wire load = send & ~busy; // the load signal; dictates when dataReg is updated
	
	// ==== Define the "busy" signal - drive it ====
	// note that "busy" has already been defined in the port list
	// of the module:
	assign busy = (bitCount != 4'd0); // if bitCount does not equal 0, then there are still bits to send - so we are busy (busy == 1)
	
	
	// ==== Define the dataReg logic ====
	// a procedure or always block will be used
	always @ (posedge clk)
		if (reset) dataReg <= 8'b0; // clear all the flip-flops
		else if (load) dataReg <= data; // load in the next 8 bits (new byte)
		else dataReg <= dataReg; // otherwise, hold the current byte
	
	// ==== Define the Bit-select Logic ====
	always @ (bitCount, dataReg) // sensitivity list. No clk, as we are describing comb. logic
		case (bitCount)
			4'd9: txOut = 1'b0;
			4'd8: txOut = dataReg[0]; // send the LSB first; if we wished to send MSB first we would have: txOut = dataReg[7];
			4'd7: txOut = dataReg[1];
			4'd6: txOut = dataReg[2];
			4'd5: txOut = dataReg[3];
			4'd4: txOut = dataReg[4];
			4'd3: txOut = dataReg[5];
			4'd2: txOut = dataReg[6];
			4'd1: txOut = dataReg[7]; // send the MSB
			default: txOut = 1'b1; // stop bit or idle
		endcase
	
	// ==== Define the Logic for Pulse Generation (used for timing the tx of bits) ====
	wire [26:0] accumSum = accum + INCR; // 27-bit sum (we are adding two 26-bit numbers)
	wire bitPulse = accumSum[26]; // the MSB will act as a pulse on a count overflow
	// accumulator register logic
	always @ (posedge clk)
		if (reset) accum <= 26'b0; // reset all the flip-flops in the accumulator
		else accum = accumSum[25:0]; // take the lower 26 bits of accumSum signal vector
		
	
	// ==== Bit-counter Logic ====
	always @ (posedge clk)
		if (reset) bitCount <= 4'd0;
		else if (load) bitCount <= 4'd10; // we have 10 bits to send: 1 start bit, 8 data bits, and 1 stop bit
		else if (bitPulse & busy) bitCount <= bitCount - 4'd1; // decrease the bitCount by 1, as another bit has been sent
	
	// // ==== State machine - defining names and values for the states ====
	// // parameters names are in all capitals
	// // we have 11 states, so we need at least 4 bits to describe each state uniquely (2^4 = 16 > 11):
	// localparam [3:0] IDLE = 4'd0, WAIT = 4'd1, START = 4'd2, BIT0 = 4'd3, BIT1 = 4'd4, BIT2 = 4'd5, BIT3 = 4'd6,
		// BIT4 = 4'd7, BIT5 = 4'd8, BIT6 = 4'd9, BIT7 = 4'd10;
		
	// reg [3:0] currState, nextState // 4-bit state registers; these are internal signals of the module
	// // ==== currState Register Logic ====
	// always @ (posedge clk or posedge reset)
		// if (reset) currState <= IDLE; // active-high (reset must make a low-to-high (0->1) transition) asynchronous reset
		// else currState <= nextState; // else, move to the nextState
	
	// // ==== nextState Logic ====
	// always @ (currState or send or bitPulse) // a change in any of these three signals should update the nextState
		// begin
			// nextState = currState; // default behaviour is that there should be no change
			// case (currState) // we need to consider each possible state:
				// IDLE: if (send) nextState = WAIT;
				// WAIT: if (bitPulse) nextState = START;
				// START: if (bitPulse) nextState = BIT0;
				// BIT0: if (bitPulse) nextState = BIT1;
				// BIT1: if (bitPulse) nextState = BIT2;
				// BIT2: if (bitPulse) nextState = BIT3;
				// BIT3: if (bitPulse) nextState = BIT4;
				// BIT4: if (bitPulse) nextState = BIT5;
				// BIT5: if (bitPulse) nextState = BIT6;
				// BIT6: if (bitPulse) nextState = BIT7;
				// BIT7: if (bitPulse) nextState = IDLE;
				// default: nextState = IDLE; // a safe state, since we have not explicitly defined what occurs for all 2^4 or 16 states
			// endcase
		// end
endmodule		
				
	
			