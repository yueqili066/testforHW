from enum import Enum

# simulation settings
POP_SIZE = 2000         # cohort population size
SIM_TIME_STEPS = 50    # length of simulation (years)

class HealthState(Enum):
    """ health states of patients """
    WELL = 0
    STROKE = 1
    POST_STROKE = 2
    STROKE_DEATH = 3
    NON_STROKE_DEATH = 4

# transmission rate matrix without anticoagulation
TRANS_RATE_MATRIX_1 = [
    [0, 1763.8/100000, 0, 0, 0],
    [0, 0, 52.14, 0, 0],
    [0, 133.875/100000, 0, 57.375/100000, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

# transmission rate matrix with anticoagulation
TRANS_RATE_MATRIX_2 = [
    [0, 1763.8/100000, 0, 0, 0],
    [0, 0, 52.14, 0, 0],
    [0, 68.37/100000, 0, 38.82/100000, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]