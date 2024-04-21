import random
import math
import numpy as np


class People:
    def __init__(self, _id, _type, _loc_x, _loc_y, target_x, target_y):
        self.target_reached = False
        self.id = _id  # ID of the person
        self.type = _type  # Direction
        self.dt = 0.02 + random.randint(0, 6) / 100  # Time interval
        self.weight = 50 + random.randint(0, 20)  # Weight
        self.radius = 5 #(10 + random.randint(0, 5)) / 2  # Size
        self.target_v =(60 + random.randint(0, 60)) / 100  # Target speed
        self.location = (_loc_x, _loc_y)  # Position
        self.target_location = (target_x, target_y)  # Target end position
        self.v = (0, 0)  # Present speed
        self.a = (0, 0)  # Present acceleration
        self.prev_location = self.location  # Previous location for calculating displacement
        self.total_displacement = 0  # Total displacement for calculating average velocity
        self.start_time = None  # Initialize start time attribute
        self.distance_covered = 0

    def start_movement(self, start_time):
        self.start_time = start_time

    def reach_destination(self):
        return self.start_time if self.start_time else 0

    def ped_repulsive_force(self):
        """ Calculate the repulsive force between pedestrians and other pedestrians.

        Using the formula:
            f_i = ∑(j)f_ij Result
            f_ij = A * e^((r_ij - d_ij) / B) * n_ij
            r_ij = r_i + r_j Sum of the radii
            d_ij = ||r_i - r_j|| Distance between the centers
            n_ij = (r_i - r_j) / d_ij Unit direction vector

        :return: The combined force exerted by other pedestrians on this person f_i
        """
        others = list(self.scene.peds)
        others.remove(self)
        force = Vector2D(0.0, 0.0)
        for other in others:
            d_vec = self.distance_to(other)
            d = d_vec.norm()
            n = d_vec / d   # n is a unit vector
            radius_sum = self.radius + other.radius
            force += param['A'] * math.exp((radius_sum - d) / param['B']) * n
        return force

    def wall_repulsive_force(self):
        """ Calculate the repulsive force from obstacles or walls

        Use the formula:
            ∑(W)f_iW result
            f_iW = A * e^((ri-diW)/B) * niW
        Note that niW is a vector, and the direction of niW is from the wall to the pedestrian.

        :return: The combined force of all walls and obstacles on the person
        """
        force = Vector2D(0.0, 0.0)
        for box in self.scene.boxes:
            d_vec = self.distance_to(box)
            if d_vec.norm() == 0:
                print("Hit the wall")
                continue
            n = d_vec / d_vec.norm()    # n is a vector
            force += param['A'] * math.exp((self.radius - d_vec.norm()) / param['B']) * n
        return force

    def desired_force(self):
        """ Calculate expected power
        Use formula:
            m * (v * e - vc) / t_c
            m is the mass, v is the desired velocity, and e is the desired direction(get_direction())
            vc is the current speed, t_c is the characteristic time
        :return: expectancy
        """
        e = SFM.PathFinder.get_direction(self.scene, self)
        return (param['desired_speed'] * e - self.vel) / param['ch_time'] * self.mass

    def get_force(self):
        """ Calculate net force"""
        f1 = self.ped_repulsive_force()
        f2 = self.wall_repulsive_force()
        f3 = self.desired_force()
        if path_finder_test:
            return f3
        return f1 + f2 + f3

    def accleration(self):
        """ Calculate acceleration based on resultant force and mass
        :return: acceleration
        """
        acc = self.get_force() / self.mass
        if acc.norm() > 5:
            acc = acc / acc.norm() * 4
        return acc

    def compute_next(self, scene):
        self.scene = scene
        self.next_pos = self.pos + self.vel * param['time_step']
        acc = self.accleration()
        self.next_vel = self.vel + acc * param['time_step']

    def update_status(self):
        """ Update the person's location and velocity
        Pre-conditions: First call compute_next()

Note that all pedestrians should update their position and velocity simultaneously
        """
        self.pos = self.next_pos
        self.vel = self.next_vel


class PeopleList:
    def __init__(self, num_people, delta_time, center_x=540, center_y=355, radius_inner_circle=1):
        self.delta_time = delta_time
        self.num_people = num_people
        self.densities = {}
        self.list = []
        self.all_stopped = False  # Flag to track whether all people have stopped
        self.center_x = center_x  # X-coordinate of the center of the circular formation
        self.center_y = center_y  # Y-coordinate of the center of the circular formation
        self.radius_inner_circle = radius_inner_circle  # Radius of the inner circular formation
        radius_outer_circle = 200  # Radius of the outer circular formation
        for i in range(num_people):
            angle = (2 * math.pi / num_people) * i
            x = self.center_x + radius_outer_circle * math.cos(angle)
            y = self.center_y + radius_outer_circle * math.sin(angle)
            quadrant = self.determine_quadrant(x, y)
            target_x = self.center_x + (self.center_x - x)
            target_y = self.center_y + (self.center_y - y)
            self.list.append(People("o" + str(i), quadrant, int(x), int(y), target_x, target_y))

    def print_total_displacement(self):
        for person in self.list:
            print(f"Total displacement for pedestrian {person.id}: {person.total_displacement}")

    def calculate_density(self, radius_outer_circle):
        # Calculate density within the outer circle
        for person in self.list:
            count = 0
            for other_person in self.list:
                if other_person != person:
                    # Calculate the distance between the two pedestrians
                    distance_squared = (person.location[0] - other_person.location[0]) ** 2 + \
                                       (person.location[1] - other_person.location[1]) ** 2
                    distance = math.sqrt(distance_squared)
                    # Check if the other person is within the outer circle
                    if distance <= radius_outer_circle:
                        count += 1
            # Calculate density based on the count of pedestrians within the circle
            area_circle = math.pi * radius_outer_circle ** 2
            density = count / area_circle
            self.densities.setdefault(person.id, []).append(density)

        # Calculate density within the inner circle
        count_inner_circle = 0
        for person in self.list:
            # Check if the person is within the inner circle
            if math.sqrt((person.location[0] - self.center_x) ** 2 + (person.location[1] - self.center_y) ** 2) <= self.radius_inner_circle:
                count_inner_circle += 1

        area_inner_circle = math.pi * self.radius_inner_circle ** 2
        density_inner_circle = count_inner_circle / area_inner_circle
        self.densities['inner_circle'] = density_inner_circle

    @staticmethod
    def determine_quadrant(x, y):
        if x >= 540 and y <= 355:
            return 1
        elif x < 540 and y <= 355:
            return 2
        elif x < 540 and y > 355:
            return 3
        else:
            return 4




    def calculate(self, arg_A, arg_B, arg_C):
        for people in self.list:
            # Initialize force components
            interaction_force = (0, 0)
            wall_force = (0, 0)
            social_force = (0, 0)
            friction_force = (0, 0)  # Initialize friction force

            # Calculate desired force using the provided equation
            e_x = (people.target_location[0] - people.location[0]) / 100
            e_y = (people.target_location[1] - people.location[1]) / 100
            tmp = math.sqrt(e_x ** 2 + e_y ** 2)
            e_x /= tmp
            e_y /= tmp
            f_d_x = people.weight * (people.target_v * e_x - people.v[0]) / people.dt
            f_d_y = people.weight * (people.target_v * e_y - people.v[1]) / people.dt
            desired_force = (f_d_x, f_d_y)

            # Calculate interaction force with other pedestrians
            for p in self.list:
                if p.id == people.id:
                    continue
                d_x = (people.location[0] - p.location[0]) / 100
                d_y = (people.location[1] - p.location[1]) / 100
                dis = math.sqrt(d_x ** 2 + d_y ** 2)
                d_x /= dis
                d_y /= dis
                dis = (dis * 100 - p.radius - people.radius) / 100
                f_s_x = arg_A * math.exp(dis / arg_B) * d_x
                f_s_y = arg_A * math.exp(dis / arg_B) * d_y
                interaction_force = (interaction_force[0] + f_s_x, interaction_force[1] + f_s_y)

            # Calculate social force using the provided equation
            social_force_x = arg_C * (p.v[0] - people.v[0])
            social_force_y = arg_C * (p.v[1] - people.v[1])
            social_force = (social_force[0] + social_force_x, social_force[1] + social_force_y)

            # Calculate wall force (if applicable)
            if 40 <= people.location[1] <= 640:
                if people.location[1] < 200:
                    d_iW = people.location[1] - 40
                    wall_force = (0, arg_A * math.exp(d_iW / (100 * arg_B)))
                elif people.location[1] > 480:
                    d_iW = 640 - people.location[1]
                    wall_force = (0, -arg_A * math.exp(d_iW / (100 * arg_B)))

            # Calculate total force
            total_force_x = desired_force[0] + interaction_force[0] + wall_force[0] + social_force[0] + friction_force[
                0]
            total_force_y = desired_force[1] + interaction_force[1] + wall_force[1] + social_force[1] + friction_force[
                1]

            # Calculate acceleration
            acceleration_x = total_force_x / people.weight
            acceleration_y = total_force_y / people.weight

            # Update acceleration
            people.a = (acceleration_x, acceleration_y)

    def move(self, delta_time):
        for people in self.list:
            if people.target_reached:
                continue

            new_vx = people.v[0] + people.a[0] * delta_time
            new_vy = people.v[1] + people.a[1] * delta_time
            l_x = (people.v[0] + new_vx) / 2 * delta_time * 100
            l_y = (people.v[1] + new_vy) / 2 * delta_time * 100
            people.total_displacement += math.sqrt(l_x ** 2 + l_y ** 2)  # Add displacement to total displacement
            people.location = (people.location[0] + l_x, people.location[1] + l_y)
            people.v = (new_vx, new_vy)

            # Calculate distance covered
            current_distance = math.sqrt((people.prev_location[0] - people.location[0]) ** 2 +
                                         (people.prev_location[1] - people.location[1]) ** 2)
            people.distance_covered += current_distance

            # Update previous location for next iteration
            people.prev_location = people.location

            # Check if the person has reached their destination
            distance_to_target = math.sqrt((people.location[0] - people.target_location[0]) ** 2 +
                                           (people.location[1] - people.target_location[1]) ** 2)
            if distance_to_target < 5:
              #  print(f"Pedestrian {people.id} reached its destination")
                people.target_reached = True  # Set the flag to indicate that the target is reached

        # Check if all people have stopped
        if all(people.target_reached for people in self.list):
            self.all_stopped = True

    def count_size_and_v(self):
        total_num = 0
        total_v = 0
        for people in self.list:
            if 200 <= people.location[0] <= 900:
                total_num += 1
                total_v += math.sqrt(people.v[0] ** 2 + people.v[1] ** 2)
        if total_num != 0:
            total_v /= total_num
        return total_num, total_v
