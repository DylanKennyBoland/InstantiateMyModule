`timescale 1ns / 1ns
// Authors: Dylan Boland, James Callanan, Cuan De Burca.

module AHBspi_master (
		// ==== Inputs ====
		input wire HCLK,			// bus clock
		input wire HRESETn,			// bus reset, active low
		input wire HSEL,			// selects this slave
		input wire HREADY,			// indicates previous transaction completing
		input wire [31:0] HADDR,	// address
		input wire [1:0] HTRANS,	// transaction type (only bit 1 used)
		input wire HWRITE,			// write transaction
		// input wire [2:0] HSIZE,  // transaction width ignored
		input wire [31:0] HWDATA,	// write data
		input wire MISO,            // from selected slave
		// ==== Outputs ====
		output wire [31:0] HRDATA,	        // read data from slave
		output reg MOSI,                    // to slaves
		output wire SCLK,                   // to slaves
		output wire ACCELEROMETER_SELECT_N,	// to accelerometer slave
		output wire HREADYOUT		
    );
	
	// ==== Internal Signal ====
	// Registers to hold signals from address phase
	reg [1:0] rHADDR;	// only need two bits of address
	reg rWrite;	        // write enable signals
	wire send = (rWrite && (rHADDR == 2'b01) && ~busy);
	// Registers for the counter
    reg [7:0] NEXT_COUNT;
	reg [7:0] COUNT;
    wire busy;
	wire SCLK;
    assign busy = ~COUNT[7];
    assign SCLK = COUNT[3];
	// SPICON signals
    reg ACCELEROMETER_SELECT_REG;
	wire [7:0] SPICON;	// holds interrupt enable bits
    // Read-data signals
    reg [7:0] READ_DATA;
    reg [7:0] SHIFT_REG;
	// TX-data signals
	reg [7:0] TX_DATA;	// holds interrupt enable bits
	
 	// ==== Capture Bus Signals in Address Phase ====
	always @(posedge HCLK) begin
		if(!HRESETn) begin
			rHADDR <= 2'b00;
			rWrite <= 1'b0;
		end else if(HREADY) begin
			rHADDR <= HADDR[3:2];                // capture address bits for for use in data phase
			rWrite <= HSEL & HWRITE & HTRANS[1]; // slave selected for write transfer       
		end
	end
	
	// ==== Logic for Ready-out Signal ====
    assign HREADYOUT = 1'b1; // always ready - no wait states for now
	
	// ==== Counter Logic ====
    // COUNT is an 8-bit counter where 
    // COUNT[6:4] are used to select MOSI and MISO bits
    // Also, busy and SCLK wires depend on COUNT[7] and COUNT[3] respectively
	
	// ==== Logic for Counter ====
	always @(posedge HCLK) begin
       if (!HRESETn) begin
		  COUNT <= 8'h80;  // reset to max value
	   end else begin
		  COUNT <= NEXT_COUNT; // take on the next count value
	   end
    end
	
	// ==== Logic for the Shift Signal ====
	wire shift = (COUNT[3:0] == 4'b0111);	// shift at posedge of SCLK
	
	// ==== (Combinational) Logic for Next Count ====
	always @(*) begin
       if (busy) NEXT_COUNT = COUNT + 1'b1;
	   else if (send) NEXT_COUNT = 8'h00;
	   else NEXT_COUNT = 8'h80;
    end
	
	// ==== Accelerometer-select Register Logic ====
	always @(posedge HCLK) begin
        if (!HRESETn) begin
           ACCELEROMETER_SELECT_REG <= 1'b0;    
        end else begin
            if (rWrite && (rHADDR == 2'b00) && ~busy) begin 
				ACCELEROMETER_SELECT_REG <= HWDATA[0];
			end
        end
     end
	
	// ==== SPICON and Chip-select (CS) Logic ====
	assign SPICON = {busy, 6'b0, ACCELEROMETER_SELECT_REG};
    assign ACCELEROMETER_SELECT_N = ~ACCELEROMETER_SELECT_REG;
	
	// ==== TX-data Logic ====
	always @(posedge HCLK) begin
        if (!HRESETn) TX_DATA <= 8'b0;   
        else if (send) TX_DATA <= HWDATA[7:0];
	end
	
	// ==== MOSI Logic ====
    always @(*) begin
        case (COUNT[6:4])
            3'b000:  MOSI = TX_DATA[7];
            3'b001:  MOSI = TX_DATA[6];
            3'b010:  MOSI = TX_DATA[5];
            3'b011:  MOSI = TX_DATA[4];
            3'b100:  MOSI = TX_DATA[3];
            3'b101:  MOSI = TX_DATA[2];
            3'b110:  MOSI = TX_DATA[1];
            3'b111:  MOSI = TX_DATA[0];
        endcase
	end
    
	// ==== Read-data Logic ====
    always @(*) begin
        case (rHADDR)
            2'b00:  READ_DATA = SPICON;
            2'b01:  READ_DATA = TX_DATA;
            2'b10:  READ_DATA = SHIFT_REG;
            2'b11:  READ_DATA = SPICON;
        endcase
     end
     
    // ==== HRDATA Logic ====
	assign HRDATA = {24'd0, READ_DATA}; // pad signal with 0s
	
	// ==== Shift-register Logic ====
	always @(posedge HCLK) begin
		if (!HRESETn) SHIFT_REG <= 8'b0;
		else if (shift) SHIFT_REG <= {SHIFT_REG[6:0], MISO};
	end

endmodule
