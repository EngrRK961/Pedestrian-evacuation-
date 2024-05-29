import random
import math
import numpy as np

class People:
    def __init__(self, _id, _type, _loc_x, _loc_y, target_x, target_y):
        self.target_reached = False
        self.time_reached = None
        self.average_speed = 0
        self.id = _id  # ID of the person
        self.type = _type  # Direction
        self.dt =0.04 #0.02 + random.randint(0, 6) / 100  # Time interval
        self.weight = 50 + random.randint(0, 20)  # Weight
        self.radius = (10 + random.randint(0, 5)) / 2  # Size
        self.target_v = (60 + random.randint(0, 60)) / 100  # Target speed
        self.location = (_loc_x, _loc_y)  # Position
        self.target_location = (target_x, target_y)  # Target end position
        self.v = (0, 0)  # Present speed
        self.a = (0, 0)  # Present acceleration
        self.prev_location = self.location  # Previous location for calculating displacement
        self.total_displacement = 0  # Total displacement for calculating average velocity
        self.start_time = None  # Initialize start time attribute
        self.distance_covered = 0

    # Method to update time_reached and average_speed
    def update_data(self, time_reached, average_speed):
        self.time_reached = time_reached
        self.average_speed = average_speed

class PeopleList:
    def __init__(self, num_people, delta_time, center_x=540, center_y=355):
        self.delta_time = delta_time
        self.num_people = num_people
        self.list = []
        self.all_stopped = False  # Flag to track whether all people have stopped
        self.center_x = center_x  # X-coordinate of the center of the circular formation
        self.center_y = center_y  # Y-coordinate of the center of the circular formation
        self.radius_outer_circle = 200  # Radius of the outer circular formation
        self.radius_inner_circle = 100
        for i in range(num_people):
            angle = (2 * math.pi / num_people) * i
            x = self.center_x + self.radius_outer_circle * math.cos(angle)
            y = self.center_y + self.radius_outer_circle * math.sin(angle)
            quadrant = self.determine_quadrant(x, y)
            target_x = self.center_x + (self.center_x - x)
            target_y = self.center_y + (self.center_y - y)
            self.list.append(People("o" + str(i), quadrant, int(x), int(y), target_x, target_y))

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

    def calculate_instantaneous_density(self):
        # Calculate the number of people within the inner circle of radius 1 meter
        num_people_inner_circle = sum(1 for person in self.list if ((person.location[0] - self.center_x) ** 2 + (person.location[1] - self.center_y) ** 2) <= 1 ** 2)

        # Calculate the area of the inner circle
        area_inner_circle = math.pi * (1 ** 2)

        # Calculate instantaneous density
        density = num_people_inner_circle / area_inner_circle

        return density


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
            total_force_x = desired_force[0] + interaction_force[0] + wall_force[0] + social_force[0] + friction_force[0]
            total_force_y = desired_force[1] + interaction_force[1] + wall_force[1] + social_force[1] + friction_force[1]

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
        total_speed = 0
        for people in self.list:
            if 200 <= people.location[0] <= 900:  # Assuming the area of interest is defined by x-coordinates
                total_num += 1
                total_speed += math.sqrt(people.v[0] ** 2 + people.v[1] ** 2)
        average_speed = total_speed / total_num if total_num != 0 else 0
        return total_num, average_speed
