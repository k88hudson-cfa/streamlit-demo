import streamlit as st
from model_state import ModelState


class SIR1State(ModelState):
    def __init__(self, S: int, I: int, R: int, seed: int):
        super().__init__(
            seed=seed,
            states=[
                ("S", "#0057b7", S),
                ("I", "#fb4d4d", I),
                ("R", "#3AF4A3", R),
            ],
        )

    def infect(self, count: int = 1):
        if count > self.S:
            raise ValueError("Cannot infect more individuals than susceptible.")
        self.S -= count
        self.I += count

    def recover(self, count: int = 1):
        if count > self.I:
            raise ValueError("Cannot recover more individuals than infected.")
        self.I -= count
        self.R += count


def model(state: ModelState, r0: float, infectious_period: float, max_time: float):
    if max_time <= state.t:
        raise ValueError("max_time must be greater than the initial time t.")

    while state.t < max_time:
        beta = r0 / infectious_period
        gamma = 1 / infectious_period

        rate_infection = beta * state.S * state.I / state.population_count()
        rate_recovery = gamma * state.I
        rate_total = rate_infection + rate_recovery

        if rate_total == 0:
            break

        dt_i = state.rng.exponential(1 / rate_infection)
        dt_r = state.rng.exponential(1 / rate_recovery)

        if dt_i < dt_r:
            state.infect()
            state.t += dt_i
        else:
            state.recover()
            state.t += dt_r

        state.tabulate()

    return state


def render():
    st.title("Demo")

    population_size = st.sidebar.number_input("Population size", 10, 2000, 1000)
    initial_infectious = st.sidebar.slider("Initial infections", 1, population_size, 10)
    initial_state = SIR1State(
        seed=st.sidebar.number_input("Random seed", value=42, min_value=0),
        S=population_size - initial_infectious,
        I=initial_infectious,
        R=0,
    )

    r0 = st.sidebar.slider("Reproductive Number (R0)", 1.0, 3.0, 1.5)
    infectious_period = st.sidebar.slider("Infectious Period", 1, 5, 3)

    max_time = st.sidebar.slider("Maximum time (days)", 0.0, 200.0, 100.0, step=1.0)

    results = model(initial_state, r0, infectious_period, max_time)

    st.altair_chart(
        results.as_chart().properties(title=f"r0={r0}, N={population_size}"),
        use_container_width=True,
    )
    st.write(results.as_data_frame())


render()
