from nmigen import Elaboratable, Signal, Module, Repl
from nmigen.build import Platform
from nmigen.lib.fifo import AsyncFIFOBuffered
from ..utils.ecp5pll import ECP5PLL, ECP5PLLConfig


class PllTimer(Elaboratable):
    def elaborate(self, platform: Platform):
        led1 = platform.request("led", 0)
        led4 = platform.request("led", 3)

        timer1 = Signal(25)
        fifo_buf = Signal(16)

        m = Module()

        # Connect pseudo power pins for the FT600 and DDR3 banks
        pseudo_power = platform.request("pseudo_power")
        m.d.comb += pseudo_power.ddr.o.eq(Repl(1, len(pseudo_power.ddr)))
        m.d.comb += pseudo_power.ft.o.eq(Repl(1, len(pseudo_power.ft)))

        m.submodules.pll = ECP5PLL(clock_signal_name="pll_clk25",
                                   clock_config=[
                                       ECP5PLLConfig("sync", 25),
                                       ECP5PLLConfig("fast", 100, error=0),
                                       ECP5PLLConfig("fast2", 100, error=0),
                                       ECP5PLLConfig("fast3", 150, error=0),
                                   ])

        m.submodules.fifo = fifo = AsyncFIFOBuffered(
            width=16, depth=1024, r_domain="fast", w_domain="sync")

        # Write the FIFO using the timer data
        m.d.sync += timer1.eq(timer1 + 1)
        with m.If(fifo.w_rdy):
            m.d.comb += fifo.w_data.eq(timer1[9:25])
        m.d.comb += fifo.w_en.eq(1)

        # Read the FIFO in the `fast` domain, the LEDs should blink at the same time
        with m.If(fifo.r_rdy):
            m.d.fast += fifo_buf.eq(fifo.r_data)

        m.d.comb += fifo.r_en.eq(1)

        # Combinatorial logic
        m.d.comb += led1.o.eq(timer1[-1])
        m.d.comb += led4.o.eq(fifo_buf[-1])

        return m
