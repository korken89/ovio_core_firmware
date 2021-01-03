from nmigen import Elaboratable, Signal, Module, Repl, ClockDomain, ClockSignal, DomainRenamer
from nmigen.build import Platform
from nmigen.lib.fifo import AsyncFIFOBuffered
from ..utils.ecp5pll import ECP5PLL, ECP5PLLConfig


class FT600_Test(Elaboratable):
    def elaborate(self, platform: Platform):
        led1 = platform.request("led", 0)
        led2 = platform.request("led", 1)
        led3 = platform.request("led", 2)
        led4 = platform.request("led", 3)

        ft600_resource = platform.request("ft600")

        m = Module()

        # Connect pseudo power pins for the FT600 and DDR3 banks
        pseudo_power = platform.request("pseudo_power")
        m.d.comb += pseudo_power.ddr.o.eq(Repl(1, len(pseudo_power.ddr)))
        m.d.comb += pseudo_power.ft.o.eq(Repl(1, len(pseudo_power.ft)))

        m.submodules.pll = ECP5PLL(clock_signal_name="pll_clk25",
                                   clock_config=[
                                       ECP5PLLConfig("sync", 25),
                                   ])

        m.domains += ClockDomain("ft600")
        m.d.comb += ClockSignal("ft600").eq(ft600_resource.clk)

        m.submodules.ft600 = ft600 = DomainRenamer("ft600")(FT600(
            ft600_resource,
        ))

        m.submodules.fifo = fifo = AsyncFIFOBuffered(
            width=16, depth=2048, r_domain="ft600", w_domain="sync")

        # FT to Write FIFO
        m.d.comb += ft600.input_payload.eq(fifo.r_data)
        m.d.comb += fifo.r_en.eq(ft600.input_ready)
        m.d.comb += ft600.input_valid.eq(fifo.r_rdy)

        # Write data into FIFO
        m.d.comb += fifo.w_data.eq(0xABCD)
        m.d.comb += fifo.w_en.eq(1)

        led_counter = Signal(10)

        with m.If(fifo.w_rdy):
            m.d.sync += led_counter.eq(led_counter + 1)

        # Connect LEDs
        m.d.comb += led1.o.eq(ft600_resource.write)
        m.d.comb += led2.o.eq(ft600_resource.txe)
        m.d.comb += led3.o.eq(fifo.w_level > 2000)
        m.d.comb += led4.o.eq(led_counter[-1])

        return m


class FT600(Elaboratable):
    def __init__(self, ft600_resource):
        self.input_payload = Signal(16)
        self.input_ready = Signal()
        self.input_valid = Signal()

        self.output_payload = Signal(16)
        self.output_ready = Signal()
        self.output_valid = Signal()

        self.ft = ft600_resource

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # Signal defaults
        m.d.comb += self.ft.oe.o.eq(0)
        m.d.comb += self.ft.write.o.eq(0)
        m.d.comb += self.ft.read.o.eq(0)

        with m.FSM():
            with m.State("READY"):
                # If there is data to read, we read it first before entering the write state
                with m.If(self.ft.rxf.i):
                    m.d.comb += self.ft.oe.o.eq(1)

                    m.d.comb += self.ft.data.oe.eq(0)
                    m.d.comb += self.ft.be.oe.eq(0)

                    m.next = "READ"
                with m.Elif(self.ft.txe.i & self.input_valid):
                    m.d.comb += self.ft.data.oe.eq(1)
                    m.d.comb += self.ft.be.oe.eq(1)

                    m.next = "WRITE"

            with m.State("READ"):
                m.d.comb += self.ft.oe.o.eq(1)

                # Set pins in correct direction (input)
                m.d.comb += self.ft.data.oe.eq(0)
                m.d.comb += self.ft.be.oe.eq(0)

                # Connect FIFO
                m.d.comb += self.output_payload.eq(self.ft.data.i)
                m.d.comb += self.output_valid.eq(self.ft.rxf.i)
                m.d.comb += self.ft.read.o.eq(self.output_ready)

                with m.If(~self.ft.rxf.i):
                    m.next = "READY"

            with m.State("WRITE"):
                # Set pins in correct direction (output)
                m.d.comb += self.ft.data.oe.eq(1)
                m.d.comb += self.ft.be.oe.eq(1)

                # All bytes are valid
                m.d.comb += self.ft.oe.o.eq(0)
                m.d.comb += self.ft.be.o.eq(0b11)

                # Connect FIFO
                m.d.comb += self.ft.data.o.eq(self.input_payload)
                m.d.comb += self.input_ready.eq(self.ft.txe.i)
                m.d.comb += self.ft.write.o.eq(self.input_valid)

                # TODO: Should we go to ready if there is data to read, or wait until write is done?
                with m.If(~self.ft.txe.i | ~self.input_valid):
                    m.next = "READY"

        return m

    # def read_fifo_port(self) -> List[Signal]:
    #     return []
    # def write_fifo_port(self) -> List[Signal]:
    #     return []
    # def ft_ports(self):
    #     return [
    #         self.ft_oe,
    #         self.ft_be,
    #         self.ft_txe,
    #         self.ft_write,
    #         self.ft_data,
    #     ]
