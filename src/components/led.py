from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital
from framework.units import Ohms, Volts, Milliamps


class LED(FactorNode):
    """Light-emitting diode.

    A real LED has two terminals (anode +, cathode −) and only conducts once
    the forward voltage across it exceeds V_F.  It has no internal current
    limiting, so a series resistor is mandatory in every real circuit:

        VCC ──[R_limit]──[anode → cathode]── GND

    Without R_limit the LED will burn out.  Use these constants to size it:

        R_limit = (V_supply − V_F) / I_F_TYP
        e.g.    = (5.0 − 2.0) / 0.010 = 300 Ω  → use 330 Ω

    This simulation works at logic level and does not model V_F or forward
    current numerically.  V_F, I_F_TYP, and I_F_MAX are reference constants
    for real-world calculations only.

    Ports
    -----
    anode   (IN, Digital) — connect to the driving logic output
    cathode (IN, Digital, optional) — connect to GND rail; floating = GND
    """

    V_F:     float = 2.0    # forward voltage drop, volts (typical red LED)
    I_F_TYP: float = 0.010  # typical operating current, amps (10 mA)
    I_F_MAX: float = 0.020  # absolute maximum current, amps (20 mA)

    __slots__ = ['_color', '_lit', '_ports']

    def __init__(self, color: str, domain: GroundDomain = ELECTRICAL) -> None:
        self._color = color
        self._lit = False
        self._ports = {
            'anode':   Port('anode',   Direction.IN, domain, mandatory=True,  signal_type=Digital),
            'cathode': Port('cathode', Direction.IN, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    @property
    def lit(self) -> bool:
        return self._lit

    def _evaluate(self) -> None:
        anode   = bool(Digital(self._ports['anode'].value))
        cathode = bool(Digital(self._ports['cathode'].value))
        self._lit = anode and not cathode   # conducts when anode HIGH, cathode LOW

    @classmethod
    def limit_resistor(cls, v_supply: float, i_target: float | None = None) -> Ohms:
        """Return the minimum series resistor value for this LED type.

        Uses I_F_TYP by default; pass i_target (amps) to override.

        Example
        -------
        >>> LED.limit_resistor(5.0)          # 5 V supply, default 10 mA
        Ohms(300.0)
        >>> LED.limit_resistor(3.3, 0.005)   # 3.3 V supply, 5 mA
        Ohms(260.0)
        """
        i = i_target if i_target is not None else cls.I_F_TYP
        return Ohms((v_supply - cls.V_F) / i)

    def __call__(self, signal: bool | None) -> bool:
        self._ports['anode'].drive(signal)
        self._evaluate()
        return self._lit

    def __str__(self) -> str:
        return f"{self._color}: {'ON' if self._lit else 'OFF'}"

    def __repr__(self) -> str:
        return f"LED(color='{self._color}', lit={self._lit})"
