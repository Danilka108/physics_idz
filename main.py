import random
import math
import enum

# случайная велечина 'γ' (лямбда)


class NeutronPosStatus(enum.Enum):
    passed_the_plate = 0
    reflected_from_the_plate = 1
    present_within_the_plate = 2


class TrajectoryStatus(enum.Enum):
    Continue = 0
    Stop = 1


class PhysicsModelResult:
    probability_of_passing = 0
    probability_of_reflecting = 0
    probability_of_absorbing = 0

    def __init__(self, number_of_neutrons, number_of_passed_neutrons, number_of_reflected_neutron,
                 number_of_absorbed_neutron):
        self.probability_of_passing = number_of_passed_neutrons / number_of_neutrons
        self.probability_of_absorbing = number_of_absorbed_neutron / number_of_neutrons
        self.probability_of_reflecting = number_of_reflected_neutron / number_of_neutrons


class PhysicsModel:
    _number_of_passed_neutrons = 0
    _number_of_reflected_neutrons = 0
    _number_of_absorbed_neutron = 0

    _number_of_trajectories = 0
    _trajectories = []

    _section_of_capture = 0
    _section_of_scattering = 0
    _full_section = 0

    _plate_thickness = 0

    def __init__(self, number_of_trajectories, section_of_capture, section_of_scattering, plate_thickness):
        self._section_of_scattering = section_of_scattering
        self._section_of_capture = section_of_capture
        self._full_section = self._section_of_capture + self._section_of_scattering
        self._plate_thickness = plate_thickness

        self._number_of_trajectories = number_of_trajectories

        for _ in range(self._number_of_trajectories):
            self._trajectories.append([])

    def calc_probabilities(self):
        for number_of_trajectory in range(self._number_of_trajectories):
            while True:
                trajectory_status = self._handle_next_link(self._trajectories[number_of_trajectory])

                if trajectory_status == TrajectoryStatus.Stop:
                    break

        return PhysicsModelResult(self._number_of_trajectories, self._number_of_passed_neutrons,
                                  self._number_of_reflected_neutrons, self._number_of_absorbed_neutron)

    def _handle_next_link(self, links):
        prev_pos = links[-1] if len(links) > 0 else 0

        next_pos = self._calc_next_collision_pos(prev_pos, random.random(), len(links) == 0)
        links.append(next_pos)

        pos_status = self._check_neutron_pos(next_pos)

        if pos_status == NeutronPosStatus.passed_the_plate:
            self._number_of_passed_neutrons += 1
            return TrajectoryStatus.Stop

        if pos_status == NeutronPosStatus.reflected_from_the_plate:
            self._number_of_reflected_neutrons += 1
            return TrajectoryStatus.Stop

        random_value = random.random()

        if random_value < self._section_of_capture / self._full_section:
            self._number_of_absorbed_neutron += 1
            return TrajectoryStatus.Stop

        return TrajectoryStatus.Continue

    def _check_neutron_pos(self, pos):
        if pos > self._plate_thickness:
            return NeutronPosStatus.passed_the_plate

        if pos < 0:
            return NeutronPosStatus.reflected_from_the_plate

        return NeutronPosStatus.present_within_the_plate

    # разыграть велечину 'ξ' (кси)
    def _play_direction_factor(self, is_start):
        return 1 if is_start else 2 * random.random() - 1

    # Разыграть длину свободного пробега нейтрона
    def _play_free_path_length(self, random_value):
        return - (1 / self._full_section) * math.log(random_value)

    # Вычеслить абциссу следующего столкновения нейтрона с ядром
    def _calc_next_collision_pos(self, prev_collision_pos, random_value, is_start):
        return prev_collision_pos + self._play_free_path_length(random_value) * self._play_direction_factor(is_start)


a = PhysicsModel(1000, 0.3, 0.4, 1.8)
probabilities = a.calc_probabilities()
print("reflecting:", probabilities.probability_of_reflecting)
print("absorbing:", probabilities.probability_of_absorbing)
print("passing:", probabilities.probability_of_passing)
