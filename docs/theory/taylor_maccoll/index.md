# Taylor-Maccoll

The Taylor-Maccoll equations describe steady, inviscid, irrotational supersonic flow
over a right-circular cone at zero angle of attack.

This is the high-fidelity conical-flow model in `gasdyn` and is used to map between
freestream Mach number $M_\infty$, cone half-angle $\theta_c$, and shock angle $\beta$.

## Physical Setup

Consider a right-circular cone with half-angle $\theta_c$ in a uniform freestream at
Mach number $M_\infty > 1$. For an attached conical shock:

- The shock sits at angle $\beta$ from the cone axis.
- The post-shock flow between the shock and cone surface is isentropic.
- The flow is conically self-similar, so state variables depend only on polar angle
  $\theta$, not radius $r$.

## Solver Formulation Used in `gasdyn`

`gasdyn` solves the first-order Taylor-Maccoll ODE system for
$[V_r(\theta), V_\theta(\theta)]$:

$$
\frac{dV_r}{d\theta} = V_\theta
$$

$$
\frac{dV_\theta}{d\theta}
= \frac{V_\theta^2 V_r
       - \dfrac{\gamma - 1}{2}(1 - V^2)\!\left(2 V_r + \dfrac{V_\theta}{\tan\theta}\right)}
       {\dfrac{\gamma - 1}{2}(1 - V^2) - V_\theta^2}
$$

where $V^2 = V_r^2 + V_\theta^2$ and velocities are non-dimensionalized by the
maximum speed implied by stagnation enthalpy.

Initial conditions are taken at the shock from oblique-shock relations. Integration
proceeds from $\theta = \beta$ toward the axis, and the cone surface is detected by:

$$
V_\theta(\theta_c) = 0
$$

## Derivation Details

??? details "Derivation details"
    Starting from the steady axisymmetric Euler equations in spherical coordinates,
    conical self-similarity and irrotationality give the key identity:

    $$
    \frac{dV_r}{d\theta} = V_\theta
    $$

    With isentropic closure and non-dimensional energy,

    $$
    a^{*2} = \frac{\gamma - 1}{2}\left(1 - V_r^2 - V_\theta^2\right)
    $$

    the continuity + momentum equations reduce to the Taylor-Maccoll equation shown
    above. The numerical solve is then posed as a first-order IVP beginning at the
    post-shock state $(\theta = \beta)$, where the components are:

    $$
    V_{r,0} = V_0 \cos(\beta - \delta), \qquad
    V_{\theta,0} = -V_0 \sin(\beta - \delta)
    $$

    with $\delta$ from the $\theta$-$\beta$-$M$ relation and
    $V_0 = 1 / \sqrt{1 + 2/[(\gamma-1)M_2^2]}$.

    The cone angle is the event location where $V_\theta$ crosses zero.

## References

Taylor, G. I. and Maccoll, J. W. (1933).
*The Air Pressure on a Cone Moving at High Speeds.*
Proceedings of the Royal Society A, **139**(838), 278-311.
[https://doi.org/10.1098/rspa.1933.0017](https://doi.org/10.1098/rspa.1933.0017)

Anderson, J. D. (2003).
*Modern Compressible Flow: With Historical Perspective*, 3rd ed.
McGraw-Hill, Section 10.4.
