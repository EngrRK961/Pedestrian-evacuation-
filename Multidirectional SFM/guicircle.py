import csv
import math
import matplotlib.pyplot as plt
from peoplecircle import PeopleList
from guicircle import GUI
from peoplecircle import CircleDensityCalculator

# Function to save pedestrian data to CSV file
def save_pedestrian_data_to_csv(people_list, csv_filename, individual_data, pixels_to_meters):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pedestrian ID', 'Time Reached', 'Average Speed', 'Total Distance', 'Velocity X', 'Velocity Y'])
        for person in people_list.list:
            total_distance = person.total_displacement * pixels_to_meters
            time_reached = individual_data[person.id]['time_reached'] if person.target_reached else None
            average_speed = math.sqrt(person.v[0] ** 2 + person.v[1] ** 2)
            writer.writerow([
                person.id,
                time_reached,
                average_speed,
                total_distance,
                person.v[0],
                person.v[1]
            ])

# Constants and initializations
num_people =48  # Number of people in the circular formation
delta_time = 0.005
arg_A = 2000
arg_B = -0.08
arg_C = 0.2
pixels_to_meters = 0.02

center_x = 540
center_y = 355
radius_inner_circle = 100

# File paths
csv_filename_velocity = 'D:\multidirectional flow modeling Final\velocity_data.csv'  # CSV file to save the velocity data
csv_filename_distance = 'D:\multidirectional flow modeling Final\distance_data.csv'  # CSV file to save the distance data
trajectory_filename = 'trajectory_data.csv'  # CSV file to save trajectory data
density_filename = 'density_data.csv'  # CSV file to save density data

# Initialize GUI, PeopleList, and DensityCalculator
gui = GUI()
people_list = PeopleList(num_people, delta_time)
density_calculator = CircleDensityCalculator(center_x, center_y, radius_inner_circle, people_list)

# Simulation loop
time = 0
tmp_time = 0
time_values = []
individual_data = {}  # Dictionary to store individual pedestrian data
trajectory_data = {}  # Dictionary to store trajectory data for each pedestrian

while any(not person.target_reached for person in people_list.list):
    # Calculate densities after the simulation
    densities = density_calculator.calculate_density(radius_inner_circle)

    # Calculate forces between people
    people_list.calculate(arg_A, arg_B, arg_C)

    # Remove existing ovals from GUI
    for i in range(len(people_list.list)):
        gui.del_oval(people_list.list[i].id)

    # Move people and update GUI
    people_list.move(delta_time)
    for person in people_list.list:
        gui.add_oval(person.location[0], person.location[1], person.radius, person.id, person.type)

        # Record trajectory data
        if person.id not in trajectory_data:
            trajectory_data[person.id] = []
        trajectory_data[person.id].append((time, person.location))

    # Update time and collect data at intervals
    time += delta_time
    if time - tmp_time > 0.25:
        tmp_time += 0.25
        n, v = people_list.count_size_and_v()
        time_values.append(tmp_time)
        for person in people_list.list:
            if person.id not in individual_data:
                individual_data[person.id] = {'time_reached': None, 'average_speed': None}
            if person.target_reached and individual_data[person.id]['time_reached'] is None:
                individual_data[person.id]['time_reached'] = tmp_time
                individual_data[person.id]['average_speed'] = math.sqrt(person.v[0] ** 2 + person.v[1] ** 2)

    gui.update_time(str(round(time, 3)))
    gui.update_gui()

# Save individual pedestrian distance data to CSV file
save_pedestrian_data_to_csv(people_list, csv_filename_distance, individual_data, pixels_to_meters)

# Save trajectory data to CSV file
with open(trajectory_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Pedestrian ID', 'Time', 'X', 'Y'])
    for person_id, trajectory in trajectory_data.items():
        for time, location in trajectory:
            writer.writerow([person_id, time, location[0], location[1]])

# Save density data to CSV file
with open(density_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Circle', 'Density'])

    # Write density for inner circle
    if 'inner_circle' in people_list.densities:
        if isinstance(people_list.densities['inner_circle'], list):
            average_density_inner_circle = sum(people_list.densities['inner_circle']) / len(people_list.densities['inner_circle'])
        else:
            average_density_inner_circle = people_list.densities['inner_circle']
        writer.writerow(['Inner Circle', average_density_inner_circle])

    # Write density for outer circle
    if 'outer_circle' in people_list.densities:
        if isinstance(people_list.densities['outer_circle'], list):
            for density in people_list.densities['outer_circle']:
                writer.writerow(['Outer Circle', density])
        else:
            writer.writerow(['Outer Circle', people_list.densities['outer_circle']])

# Plotting
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
for index, (person_id, data) in enumerate(individual_data.items()):
    if data['time_reached'] is not None:
        ax.scatter(data['time_reached'], index, data['average_speed'], c='r')  # Plotting time reached vs average speed

ax.set_xlabel('Time Reached Destination')
ax.set_ylabel('Pedestrian Index')
ax.set_zlabel('Average speed')
plt.title('Average Speed vs. Time Reached Destination')
plt.show()
