# GRI-Mech 3.0 Information
# ========================
#
# GRI-Mech 3.0 is a well-validated mechanism for natural gas combustion.
# It is included with Cantera and can be loaded using "gri30.yaml".
#
# Reference:
#   G.P. Smith, D.M. Golden, M. Frenklach, N.W. Moriarty, B. Eiteneer,
#   M. Goldenberg, C.T. Bowman, R.K. Hanson, S. Song, W.C. Gardiner, Jr.,
#   V.V. Lissianski, and Z. Qin
#   http://combustion.berkeley.edu/gri-mech/version30/text30.html
#
# Mechanism Statistics:
# ---------------------
# - 53 species
# - 325 reactions
# - Temperature range: 1000-2500 K
# - Pressure range: 0.1-10 atm
#
# Key Species:
# ------------
# - Fuels: CH4, C2H6, C3H8
# - Oxidizer: O2
# - Major products: CO2, H2O, CO
# - Radicals: H, O, OH, HO2, H2O2
# - Nitrogen species: N2, NO, NO2, N2O, HCN, NH3
#
# Soot Precursors (not in GRI-Mech 3.0):
# -------------------------------------
# Note: GRI-Mech 3.0 does not include PAH species like pyrene (A4).
# For soot formation studies, consider using:
# - ABF mechanism (Appel, Bockhorn, Frenklach)
# - KAUST mechanism
# - CRECK mechanism
#
# For this simulator, nucleation can be disabled or the mechanism
# extended with PAH chemistry.
