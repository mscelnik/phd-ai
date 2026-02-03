# Acetylene references

- Source: https://en.wikipedia.org/wiki/Acetylene (last accessed Feb 2026).
- Relevant data extracted:
  * Partial oxidation reaction `C2H2 + O2 -> CO + H2O` and dehydrogenation routes inform the combustion reaction set.
  * Physical constants (heat of formation, autoignition) justify the simulation time horizons.
  * Acetylene is unstable above 15 psi, so the gas-phase solver uses conservative concentrations to avoid explosion artifacts.
