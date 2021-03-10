import numpy as np
import SimPy.Plots.SamplePaths as Path
from Input import HealthState
import SimPy.Markov as Markov
import SimPy.RandomVariateGenerators as RVGs

class Patient:
    def __init__(self, id, trans_rate_matrix):

        self.id = id
        self.transRateMatrix = trans_rate_matrix
        self.stateMonitor = PatientStateMonitor()

    def simulate(self, sim_length):

        # random number generator
        rng = np.random.RandomState(seed=self.id)
        gillespie = Markov.Gillespie(transition_rate_matrix=self.transRateMatrix)

        t = 0   # simulation time
        if_stop = False

        while not if_stop:
            # find time until next event (dt), and next state
            # (note that the gillespie algorithm returns None for dt if the process
            # is in an absorbing state)
            dt, new_state_index = gillespie.get_next_state(
                current_state_index=self.stateMonitor.currentState.value,
                rng=rng)

            # stop if time to next event (dt) is None (i.e. we have reached an absorbing state)
            if dt is None:
                if_stop = True

            else:
                # else if next event occurs beyond simulation length
                if dt + t > sim_length:
                    # advance time to the end of the simulation and stop
                    t = sim_length
                    # the individual stays in the current state until the end of the simulation
                    new_state_index = self.stateMonitor.currentState
                    if_stop = True
                else:
                    # advance time to the time of next event
                    t += dt
                # update health state
                self.stateMonitor.update(time= t, new_state= HealthState(new_state_index))



class PatientStateMonitor:
    def __init__(self):

        self.currentState = HealthState.WELL    # assuming everyone starts in "Well"
        self.survivalTime = None
        self.nStrokes = 0

    def update(self, time, new_state):

        if self.currentState == HealthState.STROKE:
            self.nStrokes += 1

        if self.currentState == HealthState.NON_STROKE_DEATH or self.currentState == HealthState.STROKE_DEATH:
            self.survivalTime = time

        self.currentState = new_state


class Cohort:
    def __init__(self, id, pop_size, transition_rate_matrix):
        self.id = id
        self.popSize = pop_size
        self.transitionRateMatrix = transition_rate_matrix
        self.cohortOutcomes = CohortOutcomes()

    def simulate(self, n_time_steps):

        patients = []
        for i in range(self.popSize):
            patient = Patient(
                id=self.id * self.popSize + i, trans_rate_matrix = self.transitionRateMatrix)
            patients.append(patient)

        for patient in patients:
            patient.simulate(n_time_steps)

        self.cohortOutcomes.extract_outcomes(patients)


class Cohort:
    def __init__(self, id, pop_size, trans_rate_matrix):
        """ create a cohort of patients
        :param id: cohort ID
        :param pop_size: population size of this cohort
        :param trans_rate_matrix: transition rate matrix
        """
        self.id = id
        self.popSize = pop_size
        self.transRateMatrix = trans_rate_matrix
        self.cohortOutcomes = CohortOutcomes()  # outcomes of the this simulated cohort

    def simulate(self, sim_length):
        """ simulate the cohort of patients over the specified number of time-steps
        :param sim_length: simulation length
        """

        # populate the cohort
        patients = []
        for i in range(self.popSize):
            # create a new patient (use id * pop_size + n as patient id)
            patient = Patient(id=self.id * self.popSize + i,
                              trans_rate_matrix=self.transRateMatrix)
            # add the patient to the cohort
            patients.append(patient)

        # simulate all patients
        for patient in patients:
            # simulate
            patient.simulate(sim_length)

        # store outputs of this simulation
        self.cohortOutcomes.extract_outcomes(simulated_patients=patients)



class CohortOutcomes:
    def __init__(self):

        self.survivalTimes = []
        self.nStrokes = []
        self.nLivingPatients = None # survival curve
        self.meanSurvivalTime = None
        self.meanStroke = None

    def extract_outcomes(self, simulated_patients):
        for patient in simulated_patients:
            if patient.stateMonitor.survivalTime is not None:
                self.survivalTimes.append(patient.stateMonitor.survivalTime)
            self.nStrokes.append(patient.stateMonitor.nStrokes)

        self.meanSurvivalTime = sum(self.survivalTimes) / len(self.survivalTimes)
        self.meanStroke = sum(self.nStrokes)/len(self.nStrokes)

        # survival curve
        self.nLivingPatients = Path.PrevalencePathBatchUpdate(
            name='# of living patients',
            initial_size= len(simulated_patients),
            times_of_changes=self.survivalTimes,
            increments=[-1]*len(self.survivalTimes)
        )