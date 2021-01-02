from typing import List, Tuple

from nmigen import Module, Signal, Elaboratable, unsigned, Cat, ClockDomain, ClockSignal
from nmigen.lib.fifo import AsyncFIFOBuffered
from nmigen.sim import Simulator, Tick


class FT600(Elaboratable):
    def __init__(self):
        self.input_payload = Signal(16)
        self.input_ready = Signal()
        self.input_valid = Signal()

        self.output_payload = Signal(16)
        self.output_ready = Signal()
        self.output_valid = Signal()

        # Hardware interface
        self.ft_oe = Signal()
        self.ft_be = Signal(2)
        self.ft_txe = Signal()
        self.ft_rxf = Signal()
        self.ft_write = Signal()
        self.ft_read = Signal()
        self.ft_data = Signal(16)

    def elaborate(self, platform):
        m = Module()

        # TODO: Add async FIFOs internally
        # m.submodules.write_fifo = write_fifo = AsyncFIFOBuffered(...)
        # m.submodules.read_fifo = read_fifo = AsyncFIFOBuffered(...)

        if platform is None:
            # TODO: Add dummy pins for simulation
            pass
        else:
            # TODO: Extract pins
            pass

        # Signal defaults
        m.d.comb += self.ft_oe.eq(0)
        m.d.comb += self.ft_write.eq(0)
        m.d.comb += self.ft_read.eq(0)

        with m.FSM(reset="READY"):
            with m.State("READY"):
                # If there is data to read, we read it first before entering the write state
                with m.If(self.ft_rxf):
                    m.d.comb += self.ft_oe.eq(1)

                    m.next = "READ"
                with m.Elif(self.ft_txe & self.input_valid):

                    m.next = "WRITE"

            with m.State("READ"):
                m.d.comb += self.ft_oe.eq(1)

                # Connect FIFO, TODO: Add support for IO on the data and be lines
                m.d.comb += self.output_payload.eq(self.ft_data)
                m.d.comb += self.output_valid.eq(self.ft_rxf)
                m.d.comb += self.ft_read.eq(self.output_ready)

                with m.If(~self.ft_rxf):
                    m.next = "READY"

            with m.State("WRITE"):
                m.d.comb += self.ft_be.eq(0b11)

                # Connect FIFO, TODO: Add support for IO on the data and be lines
                m.d.comb += self.ft_data.eq(self.input_payload)
                m.d.comb += self.input_ready.eq(self.ft_txe)
                m.d.comb += self.ft_write.eq(self.input_valid)

                # TODO: Should we go to ready if there is data to read, or wait until write is done?
                with m.If(~self.ft_txe | ~self.input_valid):
                    m.next = "READY"

        return m

    def ft_ports(self):
        return [
            self.ft_oe,
            self.ft_be,
            self.ft_txe,
            self.ft_write,
            self.ft_data,
        ]


def main():
    # parser = main_parser()
    # args = parser.parse_args()

    m = Module()

    m.submodules.ft = ft = FT600()
    m.submodules.wfifo = wfifo = AsyncFIFOBuffered(
        width=16, depth=1024, r_domain="sync", w_domain="sync")
    m.submodules.rfifo = rfifo = AsyncFIFOBuffered(
        width=16, depth=1024, r_domain="sync", w_domain="sync")

    ft_oe = Signal()
    ft_be = Signal()
    ft_txe = Signal()

    # FT control
    m.d.comb += ft_oe.eq(ft.ft_oe)
    m.d.comb += ft_be.eq(ft.ft_be)
    m.d.comb += ft_txe.eq(ft.ft_txe)

    # FT to Write FIFO
    m.d.comb += ft.input_payload.eq(wfifo.r_data)
    m.d.comb += wfifo.r_en.eq(ft.input_ready)
    m.d.comb += ft.input_valid.eq(wfifo.r_rdy)

    # FT to Read FIFO
    m.d.comb += rfifo.w_data.eq(ft.output_payload)
    m.d.comb += rfifo.w_en.eq(ft.output_valid)
    m.d.comb += ft.output_ready.eq(rfifo.w_rdy)

    sim = Simulator(m)
    sim.add_clock(1e-7, domain="sync")      # 10 MHz FPGA clock

    def process():
        yield wfifo.w_en.eq(1)
        yield wfifo.w_data.eq(1)
        yield Tick(domain="sync")
        yield wfifo.w_data.eq(2)
        yield Tick(domain="sync")
        yield wfifo.w_data.eq(3)
        yield Tick(domain="sync")
        yield wfifo.w_data.eq(4)
        yield Tick(domain="sync")
        yield wfifo.w_data.eq(5)
        yield Tick(domain="sync")
        yield wfifo.w_data.eq(6)
        yield Tick(domain="sync")
        yield wfifo.w_data.eq(7)
        yield Tick(domain="sync")
        yield wfifo.w_en.eq(0)
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield ft.ft_txe.eq(1)
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield ft.ft_txe.eq(0)
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield ft.ft_txe.eq(1)
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield ft.ft_rxf.eq(1)
        yield Tick(domain="sync")
        yield ft.ft_data.eq(1)
        yield Tick(domain="sync")
        yield ft.ft_data.eq(2)
        yield Tick(domain="sync")
        yield ft.ft_data.eq(3)
        yield Tick(domain="sync")
        yield ft.ft_rxf.eq(0)
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")
        yield Tick(domain="sync")

    sim.add_sync_process(process)
    with sim.write_vcd("test.vcd", "test.gtkw", traces=[]):
        sim.run()


if __name__ == "__main__":
    main()
