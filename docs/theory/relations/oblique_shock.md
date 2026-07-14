# Oblique Shock Relations

Oblique shocks satisfy the theta-beta-Mach relation for a wedge or local turning angle in supersonic flow.

## Theta-Beta-Mach Relation

For upstream Mach number $M$, shock angle $\beta$, deflection angle $\theta$, and $\gamma$:

$$
\tan\theta = \frac{2\cot\beta\,(M^2\sin^2\beta - 1)}{M^2(\gamma + \cos 2\beta)+2}
$$

The normal component is handled using normal-shock relations:

$$
M_{n1} = M\sin\beta
$$

Then $M_{n2}$ is computed from normal-shock equations, and full downstream Mach is:

$$
M_2 = \frac{M_{n2}}{\sin(\beta-\theta)}
$$

## References

Anderson, J. D. (2003).
*Modern Compressible Flow: With Historical Perspective*, 3rd ed.
McGraw-Hill, Chapter 4.
