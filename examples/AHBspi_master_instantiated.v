AHBspi_master dut
        (
        // ==== Inputs ====
        .HCLK(HCLK),
	.HRESETn(HRESETn),
	.HSEL(HSEL),
	.HREADY(HREADY),
	.HADDR(HADDR),
	.HTRANS(HTRANS),
	.HWRITE(HWRITE),
	.HWDATA(HWDATA),
	.MISO(MISO),
	// ==== Outputs ====
	.HRDATA(HRDATA),
	.MOSI(MOSI),
	.SCLK(SCLK),
	.ACCELEROMETER_SELECT_N(ACCELEROMETER_SELECT_N),
	.HREADYOUT(HREADYOUT)
        );