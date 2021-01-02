# import os
# import subprocess

from nmigen.build import Resource, Pins, PinsN, Clock, Attrs
from nmigen.vendor.lattice_ecp5 import LatticeECP5Platform
from nmigen_boards.resources import LEDResources
# from .parallel_camera import ParallelCameraResource


__all__ = ["OvioCorePlatform"]

from nmigen import *
from nmigen.build import *


class OvioCorePlatform(LatticeECP5Platform):
    device = "LFE5U-85F"
    package = "BG381"
    speed = 6

    resources = [
        # This clock can only be an input to the PLL
        Resource("pll_clk25", 0, Pins("U16", dir="i"),  # Input to LRC_GPLLOT
                 Clock(25e6), Attrs(IO_TYPE="LVCMOS33")),

        *LEDResources(pins="B17 C17 A17 B18", invert=False,
                      attrs=Attrs(IO_TYPE="LVCMOS33")),

        Resource("ft600", 0,
                 Subsignal("clk", Pins("J19", dir="i"), Clock(
                     100e6), Attrs(IO_TYPE="LVCMOS33")),
                 Subsignal("data", Pins(
                     "C20 C18 D20 D19 E20 E19 F20 F19 G20 G19 H20 J17 J16 H16 H18 G18", dir="io"),
                     Attrs(IO_TYPE="LVCMOS33", DRIVE="16")),
                 Subsignal("be", Pins("H17 G16", dir="io"),
                           Attrs(IO_TYPE="LVCMOS33", DRIVE="16")),
                 Subsignal("rd", PinsN("E18", dir="o"),
                           Attrs(IO_TYPE="LVCMOS33", DRIVE="16")),
                 Subsignal("wr", PinsN("F17", dir="o"),
                           Attrs(IO_TYPE="LVCMOS33", DRIVE="16")),
                 Subsignal("oe", PinsN("E17", dir="o"),
                           Attrs(IO_TYPE="LVCMOS33", DRIVE="16")),
                 Subsignal("txe", PinsN("F16", dir="i"),
                           Attrs(IO_TYPE="LVCMOS33")),
                 Subsignal("rxf", PinsN("F18", dir="i"),
                           Attrs(IO_TYPE="LVCMOS33")),
                 Subsignal("reset", PinsN("D18", dir="o"),
                           Attrs(IO_TYPE="LVCMOS33")),
                 Subsignal("gpio0", Pins("D17", dir="i"),
                           Attrs(IO_TYPE="LVCMOS33")),
                 Subsignal("gpio1", Pins("E16", dir="i"),
                           Attrs(IO_TYPE="LVCMOS33")),
                 ),

        # The board has pseudo power pins, connect these with a constant `1`
        Resource("pseudo_power", 0,
                 Subsignal("ft", Pins("J18", dir="o"), Attrs(
                     IO_TYPE="LVCMOS33", DRIVE="16")),
                 Subsignal("ddr", Pins("J5 M5 L3 N1 A3 D3 D2 H3", dir="o"), Attrs(
                     IO_TYPE="LVCMOS15")),
                 ),
    ]
    connectors = [
    ]

    def toolchain_program(self, products, name):
        raise NotImplementedError("Not implemented")
