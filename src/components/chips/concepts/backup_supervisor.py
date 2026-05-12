from typing import Annotated, ClassVar
from math import exp

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Analog, Digital


@register('BackupSupervisor')
class BackupSupervisor(FactorNode):
    """System-level supervisor that models the TIDA-03031 power path.

    A voltage-only steady-state graph cannot solve the switching-
    converter dynamics (DCM boost charging, constant-on-time buck
    regulation, RC time constants).  This cell holds the system's
    macroscopic state — input level, bulk-hold-up-capacitor voltage,
    fault flags — and computes the resulting output voltage at each
    evaluate.  The surrounding composite advances `_bulk_v` between
    calls (energy-conserving: ½·C·ΔV² per second on the load side),
    which is the same Python-level escape hatch the doorbell's
    Monostable cell uses for its `_remaining_ms` countdown.

    Ports
    -----
        vin_v          Analog IN  — primary supply voltage, V.
        flt_b          Digital OUT — TPS2660 fault flag (active LOW;
                       HIGH means the eFuse is conducting and primary
                       is in spec).
        vout_v         Analog OUT — voltage at the system bus.
        bulk_v         Analog OUT — instantaneous bulk-cap voltage,
                       useful for tracing.
        backup_active  Digital OUT — HIGH while the LM5160 is
                       sourcing the bus from the bulk capacitor.

    Operating regions
    -----------------
    Normal:   V_uv ≤ VIN ≤ V_ov.  FLT_B HIGH, LM5002 boosts the bulk
              cap toward V_boost_target (charges with τ =
              charge_time_constant_ms).  LM5160 idle: VOUT = VIN.
    Brown-out: VIN < V_uv (or > V_ov for OVP).  FLT_B LOW, LM5002
              disabled, no more charging.  If bulk_v ≥ V_buck_uvlo
              the LM5160 regulates VOUT to V_buck_reg drawing from
              the bulk cap; below that, the system has run out of
              hold-up and VOUT collapses to 0 V.
    """

    __slots__ = (
        '_ports',
        '_bulk_v', '_bulk_uf',
        '_v_boost_target', '_v_buck_reg', '_v_buck_uvlo',
        '_v_uv_threshold', '_v_ov_threshold',
        '_charge_time_constant_ms',
        '_load_w_normal', '_load_w_backup',
        '_buck_efficiency',
    )

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = (
        'bulk_capacitance_uf', 'v_boost_target', 'v_buck_reg',
        'v_buck_uvlo', 'v_uv_threshold', 'v_ov_threshold',
        'charge_time_constant_ms', 'load_w_normal', 'load_w_backup',
        'buck_efficiency',
    )
    _SERIALIZE_ATTRS: ClassVar[dict[str, str]] = {
        'bulk_capacitance_uf': '_bulk_uf',
    }

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        bulk_capacitance_uf: Annotated[float, Field(gt=0)] = 1200.0,
        v_boost_target:      Annotated[float, Field(gt=0)] = 48.0,
        v_buck_reg:          Annotated[float, Field(gt=0)] = 17.0,
        v_buck_uvlo:         Annotated[float, Field(gt=0)] = 19.0,
        v_uv_threshold:      Annotated[float, Field(gt=0)] = 18.0,
        v_ov_threshold:      Annotated[float, Field(gt=0)] = 30.0,
        charge_time_constant_ms: Annotated[float, Field(gt=0)] = 400.0,
        load_w_normal:       Annotated[float, Field(gt=0)] = 25.0,
        load_w_backup:       Annotated[float, Field(gt=0)] = 7.0,
        buck_efficiency:     Annotated[float, Field(gt=0, le=1.0)] = 0.9,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._bulk_uf                 = float(bulk_capacitance_uf)
        self._v_boost_target          = float(v_boost_target)
        self._v_buck_reg              = float(v_buck_reg)
        self._v_buck_uvlo             = float(v_buck_uvlo)
        self._v_uv_threshold          = float(v_uv_threshold)
        self._v_ov_threshold          = float(v_ov_threshold)
        self._charge_time_constant_ms = float(charge_time_constant_ms)
        self._load_w_normal           = float(load_w_normal)
        self._load_w_backup           = float(load_w_backup)
        self._buck_efficiency         = float(buck_efficiency)
        self._bulk_v: float           = 0.0
        self._ports = {
            'vin_v':         Port('vin_v',         Direction.IN,  domain, mandatory=False, signal_type=Analog),
            'flt_b':         Port('flt_b',         Direction.OUT, domain, mandatory=False, signal_type=Digital),
            'vout_v':        Port('vout_v',        Direction.OUT, domain, mandatory=False, signal_type=Analog),
            'bulk_v':        Port('bulk_v',        Direction.OUT, domain, mandatory=False, signal_type=Analog),
            'backup_active': Port('backup_active', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    # --- read-only state accessors ----------------------------------------

    @property
    def bulk_v(self) -> float:
        return self._bulk_v

    @property
    def bulk_capacitance_uf(self) -> float:
        return self._bulk_uf

    @property
    def v_boost_target(self) -> float:
        return self._v_boost_target

    @property
    def v_buck_reg(self) -> float:
        return self._v_buck_reg

    @property
    def v_buck_uvlo(self) -> float:
        return self._v_buck_uvlo

    @property
    def v_uv_threshold(self) -> float:
        return self._v_uv_threshold

    @property
    def v_ov_threshold(self) -> float:
        return self._v_ov_threshold

    # --- helpers used by the wrapping composite to step time --------------

    def vin_in_spec(self, vin: float) -> bool:
        """True iff VIN is inside the eFuse's [V_uv, V_ov] window."""
        return self._v_uv_threshold <= vin <= self._v_ov_threshold

    def charge_bulk(self, elapsed_ms: float) -> None:
        """LM5002 in DCM is approximated as a first-order charge of
        the bulk capacitor toward `v_boost_target` with the configured
        time constant.  The composite calls this each tick while
        FLT_B is HIGH (primary in spec)."""
        if elapsed_ms <= 0.0:
            return
        target = self._v_boost_target
        # Δv = (target - bulk) × (1 - exp(-Δt / τ))
        delta = (target - self._bulk_v) * (1.0 - exp(-elapsed_ms / self._charge_time_constant_ms))
        self._bulk_v = min(target, self._bulk_v + delta)

    def discharge_bulk(self, elapsed_ms: float, load_w: float | None = None) -> None:
        """During a brown-out the LM5160 draws `load_w` watts from
        the bulk capacitor at `v_buck_reg` output.  Conservation of
        energy: dE/dt = -P_in = -P_out / η.  With E = ½·C·V² this
        gives dV/dt = -P_in / (C·V).  Stops at zero so we never go
        negative."""
        if elapsed_ms <= 0.0 or self._bulk_v <= 0.0:
            return
        load = float(self._load_w_backup if load_w is None else load_w)
        p_in = load / self._buck_efficiency
        cap_f = self._bulk_uf * 1e-6
        # Use an explicit Euler step against the cap's instantaneous
        # voltage; for tiny enough elapsed_ms this is a good
        # approximation, and the test fixtures keep dt well below
        # the 100-ms backup-time scale.
        dv = (p_in / max(self._bulk_v, 0.1)) * (elapsed_ms / 1000.0) / cap_f
        self._bulk_v = max(0.0, self._bulk_v - dv)

    # --- evaluate ---------------------------------------------------------

    def evaluate(self) -> None:
        vin = self._ports['vin_v'].value
        v_in_f = 0.0 if vin is None else float(vin)
        in_spec = self.vin_in_spec(v_in_f)

        # FLT_B is active-LOW: HIGH = primary OK, LOW = fault.
        self._ports['flt_b'].drive(in_spec)
        self._ports['bulk_v'].drive(self._bulk_v)

        if in_spec:
            # Primary path: eFuse passes the input straight to the bus.
            self._ports['vout_v'].drive(v_in_f)
            self._ports['backup_active'].drive(False)
        elif self._bulk_v >= self._v_buck_uvlo:
            # Brown-out, LM5160 still has enough headroom to regulate.
            self._ports['vout_v'].drive(self._v_buck_reg)
            self._ports['backup_active'].drive(True)
        else:
            # Cap depleted below the buck UVLO — system rail collapses.
            self._ports['vout_v'].drive(0.0)
            self._ports['backup_active'].drive(False)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, vin_v: float) -> float:
        """Standalone-test invocation: drive VIN, evaluate, return VOUT.

        Time does not advance in this path; set `_bulk_v` directly
        between calls to walk the brown-out trajectory."""
        self._assert_no_inputs_wired()
        self._ports['vin_v'].drive(vin_v)
        self.evaluate()
        return float(self._ports['vout_v'].value)

    def __repr__(self) -> str:
        return (f"BackupSupervisor(bulk_v={self._bulk_v!r}, "
                f"v_boost_target={self._v_boost_target!r}, "
                f"v_buck_reg={self._v_buck_reg!r})")
