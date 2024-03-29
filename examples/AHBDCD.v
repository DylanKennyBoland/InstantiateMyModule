
module AHBDCD
	(
	input wire [31:0]HADDR,   // AHB bus address  
	output wire HSEL_S0,      // slave select line 0
	output wire HSEL_S1,
	output wire HSEL_S2,
	output wire HSEL_S3,
	output wire HSEL_S4,
	output wire HSEL_S5,
	output wire HSEL_S6,
	output wire HSEL_S7,
	output wire HSEL_S8,
	output wire HSEL_S9,      // slave select line 9
	output wire HSEL_NOMAP,   // indicates invalid address  
	output reg [3:0] MUX_SEL  // multiplexer control signal
    );

reg [15:0] dec; // 16-bit one-hot signal for slave select

// Extract the individual slave select signals
assign HSEL_S0 = dec[0];   //0x0000_0000 to 0x00FF_FFFF  16 MB
assign HSEL_S1 = dec[1];   //0x2000_0000 to 0x20FF_FFFF  16 MB	
assign HSEL_S2 = dec[2];   
assign HSEL_S3 = dec[3];  
assign HSEL_S4 = dec[4];   // More slave select lines for other slaves
assign HSEL_S5 = dec[5];   
assign HSEL_S6 = dec[6];   
assign HSEL_S7 = dec[7];   
assign HSEL_S8 = dec[8];   
assign HSEL_S9 = dec[9];   
assign HSEL_NOMAP = dec[15]; // Output for invalid address

// This is the address decoding logic to implement the address map   
always @ (HADDR)
  case(HADDR[31:24])    // Just check the top 8 bits of the address
    8'h00: 				// Address range 0x0000_0000 to 0x00FF_FFFF  16MB
      begin
        dec = 16'b0000_0000_00000001;  // one-hot code for slave select
        MUX_SEL = 4'd0;                // 4-bit slave number for multiplexer
      end
    8'h20: 				// Address range 0x2000_0000 to 0x20FF_FFFF  16MB
        begin
          dec = 16'b0000_0000_00000010;  // one-hot code 
          MUX_SEL = 4'd1;                // slave number 
        end
    8'h50: 				// Address range 0x5000_0000 to 0x50FF_FFFF  16MB
		  begin
			dec = 16'b0000_0000_00000100;  // one-hot code for slave select
			MUX_SEL = 4'd2;                // 4-bit slave number for multiplexer
		  end
    
    8'h51: 				// Address range 0x51000_0000 to 0x51FF_FFFF  16MB
        begin
          dec = 16'b0000_0000_00001000;  // one-hot code for slave select
          MUX_SEL = 4'd3;                // 4-bit slave number for multiplexer
        end
	
	// display	
	8'h52: 				// Address range 0x5200_0000 to 0x52FF_FFFF  16MB
        begin
          dec = 16'b0000_0000_00010000;  // one-hot code for slave select
          MUX_SEL = 4'd4;                // 4-bit slave number for multiplexer
        end
    
    // spi master    
    8'h53: 				// Address range 0x5300_0000 to 0x53FF_FFFF  16MB
        begin
          dec = 16'b0000_0000_00100000;  // one-hot code for slave select
          MUX_SEL = 4'd5;                // 4-bit slave number for multiplexer
        end
                // Add more cases here if there are more slaves

    default: 			// Address not mapped to any slave
      begin
        dec = 16'b1000_0000_00000000;   // activate NOMAP output
        MUX_SEL = 4'd15;                // dummy slave 
      end
  endcase

endmodule
