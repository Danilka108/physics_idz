import random
import math
import enum
import matplotlib.pyplot as plt

# Статус позиции нейтрона
class NeutronPosStatus(enum.Enum):
    # прошел через пластину
    passed_the_plate = 0
    # отразился от пластины
    reflected_from_the_plate = 1
    # Остался в пределах пластины
    present_within_the_plate = 2


# Статус расчета траектории
class TrajectoryStatus(enum.Enum):
    # продолжить расчет траектории
    Continue = 0
    # остановить расчет траектории
    Stop = 1


# Класс, содержащий результаты вычисления модели
class PhysicsModelResult:
    # вероятность прохождения через пластину
    probability_of_passing = 0
    # вероятность отражения от пластины
    probability_of_reflecting = 0
    # вероятность поглощения атомом
    probability_of_absorbing = 0

    def __init__(self, number_of_neutrons, number_of_passed_neutrons, number_of_reflected_neutron,
                 number_of_absorbed_neutron):
        self.probability_of_passing = number_of_passed_neutrons / number_of_neutrons
        self.probability_of_absorbing = number_of_absorbed_neutron / number_of_neutrons
        self.probability_of_reflecting = number_of_reflected_neutron / number_of_neutrons


# Класс математической модели задания
class Model:
    # Количество пройденных нейтронов
    _number_of_passed_neutrons = 0
    # количество отразившихся нейтронов
    _number_of_reflected_neutrons = 0
    # количество проглотившихся нейтронов
    _number_of_absorbed_neutron = 0

    # количество траекторий, которые будут просчитаны
    _number_of_trajectories = 0
    # массив траекторий, каждая траектория состоит из массива позиций
    _trajectories = []

    # сечение поглощения
    _section_of_capture = 0
    # сечение рассеяния
    _section_of_scattering = 0
    # полное сечение
    _full_section = 0

    # толщина пластины
    _plate_thickness = 0

    # Конструктор класса
    def __init__(self, number_of_trajectories, section_of_capture, section_of_scattering, plate_thickness):
        self._section_of_scattering = section_of_scattering
        self._section_of_capture = section_of_capture
        self._full_section = self._section_of_capture + self._section_of_scattering
        self._plate_thickness = plate_thickness

        self._number_of_trajectories = number_of_trajectories

        for _ in range(self._number_of_trajectories):
            self._trajectories.append([])

    # Отобразить гистограмму с вероятностями прохождения, отражения, поглощения
    def display(self):
        # значения вероятностей
        probabilities = self.calc_probabilities()

        # имена столбцов
        labels = ["прохождение", "отражение", "поглощение"]

        # высоты столбцов, выраженных в вероятностях
        means = [
            probabilities.probability_of_passing,
            probabilities.probability_of_reflecting,
            probabilities.probability_of_absorbing
        ]

        # ширина столбцов
        width = 0.8

        # рисуем гистограмму с помощью matplotlib
        fig, ax = plt.subplots()
        bar = ax.bar(labels, means, width)

        ax.bar_label(bar, label_type="center")
        plt.show()

    # Рассчитать вероятности
    def calc_probabilities(self):
        # проходимся по траекториям нейтронов
        for number_of_trajectory in range(self._number_of_trajectories):
            # рассчитываем траекторию
            while True:
                # рассчитываем следующее звено траектории
                trajectory_status = self._calc_next_link(self._trajectories[number_of_trajectory])

                # останавливаем расчет траектории если нейтрон
                # отразился, поглотился или вылетел за пределы пластины
                if trajectory_status == TrajectoryStatus.Stop:
                    break

        return PhysicsModelResult(self._number_of_trajectories, self._number_of_passed_neutrons,
                                  self._number_of_reflected_neutrons, self._number_of_absorbed_neutron)

    # рассчитать звено траектории нейтрона
    def _calc_next_link(self, links):
        # предыдущая позиция нейтрона
        prev_pos = links[-1] if len(links) > 0 else 0

        # следующая позиция нейтрона
        next_pos = self._calc_next_collision_pos(prev_pos, random.random(), len(links) == 0)
        # добавляем новую позицию в массив позиций нейтрона
        links.append(next_pos)

        # где находится нейтрон
        pos_status = self._check_neutron_pos(next_pos)

        # Нейтрон покинул пластину
        if pos_status == NeutronPosStatus.passed_the_plate:
            # увеличиваем количество покинувших нейтронов на 1
            self._number_of_passed_neutrons += 1
            return TrajectoryStatus.Stop

        # нейтрон отразился от пластины
        if pos_status == NeutronPosStatus.reflected_from_the_plate:
            # увеличиваем количество отразившихся нейтронов на 1
            self._number_of_reflected_neutrons += 1
            return TrajectoryStatus.Stop

        random_value = random.random()

        # нейтрон поглощается атомом
        if random_value < self._section_of_capture / self._full_section:
            # увеличиваем количество проглотивших нейтронов на 1
            self._number_of_absorbed_neutron += 1
            return TrajectoryStatus.Stop

        # продолжаем расчет траектории нейтрона
        return TrajectoryStatus.Continue

    # Обработать позицию нейтрона
    #
    # Если позиция дальше ширины пластины, то нейтрон покинул пластину
    # Если позиция меньше нуля, то нейтрон отразился от пластины
    # В ином случае нейтрон остался в пределах пластины
    def _check_neutron_pos(self, pos):
        if pos > self._plate_thickness:
            return NeutronPosStatus.passed_the_plate

        if pos < 0:
            return NeutronPosStatus.reflected_from_the_plate

        return NeutronPosStatus.present_within_the_plate

    # разыграть величину 'ξ' (кси)
    def _play_direction_factor(self, is_start):
        return 1 if is_start else 2 * random.random() - 1

    # Разыграть длину свободного пробега нейтрона
    def _play_free_path_length(self, random_value):
        return - (1 / self._full_section) * math.log(random_value)

    # Вычислить абсциссу следующего столкновения нейтрона с ядром
    def _calc_next_collision_pos(self, prev_collision_pos, random_value, is_start):
        return prev_collision_pos \
            + self._play_free_path_length(random_value) \
            * self._play_direction_factor(is_start)


# создаем экземпляр модели
a = Model(1000, 0.3, 0.4, 1.8)
# отобразить гистограмму
a.display()
