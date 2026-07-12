# Taylor-Maccoll: Governing Equations & Derivation

## Physical Setup

Consider a right-circular cone with half-angle $\theta_c$ placed in a uniform
supersonic freestream at Mach number $M_\infty$.  For an attached conical shock
the entire flow field is **conically symmetric**: all flow quantities depend only
on the polar angle $\theta$ measured from the cone axis, not on the distance $r$
from the tip.

The shock stands at angle $\beta > \theta_c$ from the axis.  Between the shock and
the cone surface the flow is isentropic (no further shocks).

---

## Coordinate System

Spherical coordinates $(r, \theta, \varphi)$ with origin at the cone tip and
$\theta = 0$ along the cone axis.  Axisymmetry means no $\varphi$ dependence.

The velocity vector has two components:

$$\mathbf{V} = V_r(\theta)\,\hat{e}_r + V_\theta(\theta)\,\hat{e}_\theta$$

---

## Non-dimensionalisation

Velocities are non-dimensionalised by the **maximum velocity** $V_{max}$, the
speed at which all stagnation enthalpy has been converted to kinetic energy:

$$V_{max} = \sqrt{\frac{2 h_0}{\gamma - 1}} = a_0 \sqrt{\frac{2}{\gamma - 1}}$$

where $a_0$ is the stagnation speed of sound.  With this scaling the energy
equation becomes:

$$V_r^2 + V_\theta^2 + \frac{2}{\gamma - 1}\,a^{*2} = 1$$

where $a^* = a / V_{max}$ is the non-dimensional speed of sound.  Solving for
$a^{*2}$:

$$a^{*2} = \frac{\gamma - 1}{2}\left(1 - V_r^2 - V_\theta^2\right)$$

---

## Derivation of the Taylor-Maccoll ODE

Starting from the steady, isentropic Euler equations in spherical coordinates and
exploiting conical similarity ($\partial/\partial r \equiv 0$ for non-dimensional
quantities), the continuity and radial/polar momentum equations reduce to:

**Continuity:**

$$\frac{\partial}{\partial \theta}\!\left(\rho\,V_\theta \sin\theta\right)
+ \rho\,V_r\sin\theta\left(2 + \frac{\partial V_r / \partial r}{V_r}\right) = 0$$

Under conical similarity the radial gradient term vanishes and the equation
becomes:

$$\frac{d}{d\theta}\!\left(\rho\,V_\theta \sin\theta\right) + 2\rho\,V_r\sin\theta = 0$$

**Irrotationality** ($\nabla \times \mathbf{V} = 0$, $\varphi$-component):

$$\frac{dV_r}{d\theta} = V_\theta$$

This is the key relation: $V_\theta$ is the derivative of $V_r$ with respect to $\theta$.

Substituting the isentropic relation $\rho \propto a^{*2/(γ-1)}$ and the energy
equation into the continuity equation, and using the irrotationality condition,
yields the **Taylor-Maccoll equation**:

$$\frac{dV_\theta}{d\theta}
= \frac{V_\theta^2 V_r
       - \dfrac{\gamma - 1}{2}(1 - V^2)\!\left(2 V_r + \dfrac{V_\theta}{\tan\theta}\right)}
       {\dfrac{\gamma - 1}{2}(1 - V^2) - V_\theta^2}$$

where $V^2 = V_r^2 + V_\theta^2$.

---

## First-Order ODE System

The second-order equation is written as a first-order system suitable for
numerical integration:

$$\frac{dV_r}{d\theta} = V_\theta$$

$$\frac{dV_\theta}{d\theta}
= \frac{V_\theta^2 V_r
       - \dfrac{\gamma - 1}{2}(1 - V^2)\!\left(2 V_r + \dfrac{V_\theta}{\tan\theta}\right)}
       {\dfrac{\gamma - 1}{2}(1 - V^2) - V_\theta^2}$$

**State vector:** $\mathbf{y}(\theta) = [V_r(\theta),\; V_\theta(\theta)]^\top$

---

## Initial Conditions at the Shock

The integration starts at $\theta = \beta$ (the shock angle).  The post-shock
velocity components follow from the oblique shock relations and the
$\theta$-$\beta$-$M$ relation.

Let $\delta$ be the flow deflection angle (from $\theta$-$\beta$-$M$),
$M_2$ the post-shock Mach number, and $V_0 = 1/\sqrt{1 + 2/[(\gamma-1)M_2^2]}$
the non-dimensional speed just behind the shock.  Then:

$$V_{r,0} = V_0 \cos(\beta - \delta)$$

$$V_{\theta,0} = -V_0 \sin(\beta - \delta)$$

Note $V_{\theta,0} < 0$: the flow is deflected toward the cone axis behind the shock.

---

## Cone Surface Condition

The cone surface is found by integrating from $\theta = \beta$ inward toward
$\theta = 0$.  The **cone surface condition** is:

$$V_\theta(\theta_c) = 0$$

Physically: at the cone wall the flow must be parallel to the surface, so there
is no polar velocity component.  The integration stops when $V_\theta$ crosses
zero from below (negative $\to$ positive), and the polar angle at that point is
the cone half-angle $\theta_c$.

---

## References

Taylor, G. I. and Maccoll, J. W. (1933).
*The Air Pressure on a Cone Moving at High Speeds.*
Proc. Roy. Soc. A, **139**(838), 278–311.
[https://doi.org/10.1098/rspa.1933.0017](https://doi.org/10.1098/rspa.1933.0017)

Anderson, J. D. (2003).
*Modern Compressible Flow: With Historical Perspective*, 3rd ed.
McGraw-Hill. Section 10.4.
