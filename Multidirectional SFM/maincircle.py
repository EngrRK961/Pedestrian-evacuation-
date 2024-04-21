import csv
import math
import matplotlib.pyplot as plt
from peoplecircle import PeopleList
from guicircle import GUI

def save_pedestrian_distance_to_csv(people_list, csv_filename, time, pixels_to_meters):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pedestrian ID', 'time_reached', 'Average Speed', 'Total Distance'])
        for person in people_list.list:
            total_distance = person.total_displacement * pixels_to_meters
            writer.writerow([person.id, time, math.sqrt(person.v[0] ** 2 + person.v[1] ** 2), total_distance])

# Constants and initializations
num_people = 30  # Number of people in the circular formation
delta_time = 0.005
arg_A = 2000
arg_B = -0.08
arg_C = 0.2
pixels_to_meters = 0.02
radius_outer_circle = 100  # Radius of the outer circle for density calculation

# File paths
csv_filename_velocity = 'velocity_data.csv'  # CSV file to save the velocity data
csv_filename_distance = 'distance_data.csv'  # CSV file to save the distance data
trajectory_filename = 'trajectory_data.csv'  # CSV file to save trajectory data
density_filename = 'density_data.csv'  # CSV file to save density data

# Initialize GUI and PeopleList
gui = GUI()
people_list = PeopleList(num_people, delta_time)

# Simulation loop
time = 0
tmp_time = 0
time_values = []
individual_data = {}  # Dictionary to store individual pedestrian data
trajectory_data = {}  # Dictionary to store trajectory data for each pedestrian

# Main simulation loop
while any(not person.target_reached for person in people_list.list):
    # Calculate densities after the simulation
    people_list.calculate_density(radius_outer_circle)
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

# Save individual pedestrian distance data to CSV file (distance)
save_pedestrian_distance_to_csv(people_list, csv_filename_distance, time, pixels_to_meters)

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
    writer.writerow(['Pedestrian ID', 'Density'])
    for person_id, density in people_list.densities.items():
        if person_id == 'inner_circle':
            if isinstance(density, list):
                average_density_inner_circle = sum(density) / len(density)
            else:
                average_density_inner_circle = density
            writer.writerow(['Inner Circle', average_density_inner_circle])
        else:
            if isinstance(density, list):
                for d in density:
                    writer.writerow([person_id, d])
            else:
                writer.writerow([person_id, density])


# Plotting
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
for person_id, data in individual_data.items():
    if data['time_reached'] is not None:
        ax.scatter(data['time_reached'], 1, data['average_speed'], c='r')  # Plotting time reached vs average speed

ax.set_xlabel('Time Reached Destination')
ax.set_ylabel('Pedestrian ID')
ax.set_zlabel('Average speed')
plt.title('Average Speed vs. Time Reached Destination')
plt.show()
