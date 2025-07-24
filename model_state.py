import pandas as pd
import numpy as np
import altair as alt
from dataclasses import dataclass, field


@dataclass
class ModelState:
    seed: int = field()
    states: list[tuple[str, str, int]] = field(default_factory=list)

    t: float = field(default=0.0)
    rng: np.random.Generator = field(init=False)

    current_state: dict[str, int] = field(init=False)
    tabulator: list = field(default_factory=list, init=False)

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)
        self.current_state = {
            name: initial_count for name, _, initial_count in self.states
        }
        self.tabulate()

    # Generates getters for each compartment, e.g. state.S, state.I
    def __getattr__(self, name):
        if "states" in self.__dict__ and name in self.names:
            return self.current_state[name]
        raise AttributeError(f"{type(self).__name__!r} has no attribute {name!r}")

    # Generates setters for each compartment, e.g. state.S += 1
    def __setattr__(self, name, value):
        if name != "states" and "states" in self.__dict__ and name in self.names:
            self.current_state[name] = value
        else:
            super().__setattr__(name, value)

    @property
    def names(self):
        return [i[0] for i in self.states]

    @property
    def colors(self):
        return [i[1] for i in self.states]

    def population_count(self):
        return sum(self.current_state.values())

    def tabulate(self):
        self.tabulator.append((self.t, *self.current_state.values()))
        return self.tabulator

    def as_data_frame(self):
        return pd.DataFrame(self.tabulator, columns=["t", *self.names])

    def as_chart(self):
        df_long = self.as_data_frame().melt(
            id_vars=["t"], var_name="compartment", value_name="count"
        )
        return (
            alt.Chart(df_long)
            .mark_line()
            .encode(
                x=alt.X("t", title="Time (days)"),
                y=alt.Y("count", title="Count"),
                color=alt.Color(
                    "compartment:N",
                    title="Compartment",
                    scale=alt.Scale(
                        domain=self.names,
                        range=self.colors,
                    ),
                ),
            )
        )
