accumulator #
        (
        // ==== Parameters ====
        .ACCUM_SZ(ACCUM_SZ),
	.DATA_SZ(DATA_SZ)
        ) dut
        (
        // ==== Inputs ====
        .clk(clk),
	.reset_n(reset_n),
	.data_in(data_in),
	// ==== Outputs ====
	.accum_out(accum_out)
        );