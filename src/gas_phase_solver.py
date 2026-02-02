import numpy as np
from scipy.integrate import solve_ivp


class GasPhaseChemistrySolver:
    def __init__(self, reaction_mechanism):
        """
        Initialize the solver with a reaction mechanism.

        :param reaction_mechanism: A dictionary containing reaction rates and species.
        """
        self.reaction_mechanism = reaction_mechanism

    def reaction_rates(self, t, concentrations):
        """
        Compute reaction rates based on the mechanism.

        :param t: Time (not used in this example, but included for generality).
        :param concentrations: Array of species concentrations.
        :return: Array of rate of change of concentrations.
        """
        rates = np.zeros_like(concentrations)
        for reaction in self.reaction_mechanism["reactions"]:
            rate_constant = reaction["rate_constant"]
            reactants = reaction["reactants"]
            products = reaction["products"]

            # Compute the rate of the reaction
            rate = rate_constant * np.prod([concentrations[species] for species in reactants])

            # Update rates for reactants and products
            for species in reactants:
                rates[species] -= rate
            for species in products:
                rates[species] += rate

        return rates

    def solve(self, initial_concentrations, t_span, t_eval):
        """
        Solve the ODEs for the gas-phase chemistry.

        :param initial_concentrations: Initial concentrations of species.
        :param t_span: Tuple (start_time, end_time).
        :param t_eval: Time points to evaluate the solution.
        :return: Solution object from solve_ivp.
        """
        solution = solve_ivp(
            fun=self.reaction_rates, t_span=t_span, y0=initial_concentrations, t_eval=t_eval, method="RK45"
        )
        return solution
