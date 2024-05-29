import csv
import math
import matplotlib.pyplot as plt

from peoplecircle import PeopleList
from guicircle import GUI

def is_in_inner_circle(person, people_list):
    
    distance_to_center = math.sqrt(
        (person.location[0] - people_list.center_x) ** 2 + (person.location[1] - people_list.center_y) ** 2)
    return distance_to_center <= people_list.radius_inner_circle

num_people = 50  
delta_time = 0.005
arg_A = 2000
arg_B = -0.08
arg_C = 0.2
pixels_to_meters = 0.02

# Initialize GUI
gui = GUI()

# Initialize PeopleList
people_list = PeopleList(num_people, delta_time)

# Simulation loop
time = 0
tmp_time = 0
time_values = []
individual_data = {}  
trajectory_data = {}  
density_data = []  
time_inside_inner_circle = {}  
unique_id_data = {}

while any(not person.target_reached for person in people_list.list):
  
    people_list.calculate(arg_A, arg_B, arg_C)
    for i in range(len(people_list.list)):
        gui.del_oval(people_list.list[i].id)
    people_list.move(delta_time)
    for person in people_list.list:
        gui.add_oval(person.location[0], person.location[1], person.radius, person.id, person.type)

        # Record trajectory data
        if person.id not in trajectory_data:
            trajectory_data[person.id] = []
        trajectory_data[person.id].append((time, person.location))

        # Check if person is inside the inner circle and update time_inside_inner_circle
        if is_in_inner_circle(person, people_list):
            time_inside_inner_circle[person.id] = time  # Use person.id as key
        elif person.id in time_inside_inner_circle:
            time_inside_inner_circle.pop(person.id)

    # Update time and collect data at intervals
    time += delta_time
    if time - tmp_time > 0.25:
        tmp_time += 0.25
        for person in people_list.list:
            if person.id not in individual_data:
                individual_data[person.id] = {'time_reached': None, 'average_speed': None}
            if person.target_reached and individual_data[person.id]['time_reached'] is None:
                individual_data[person.id]['time_reached'] = tmp_time
                individual_data[person.id]['average_speed'] = math.sqrt(person.v[0] ** 2 + person.v[1] ** 2)

        # Calculate the area of the inner circle
        inner_radius_meters = people_list.radius_inner_circle * pixels_to_meters
        inner_circle_area = math.pi * inner_radius_meters ** 2

        # Count people in the inner circle
        count_inner_circle = sum(1 for person in people_list.list if is_in_inner_circle(person, people_list))

        # Calculate density
        density = count_inner_circle / inner_circle_area
        density_data.append([tmp_time, density, person.id])

        # Calculate mean time taken by people inside the inner circle
        mean_time_inside_inner_circle = sum(time_inside_inner_circle.values()) / len(time_inside_inner_circle) if time_inside_inner_circle else 0

        # Print number of people, time, density, and mean time inside inner circle
        print(f"Number of people in the inner circle: {count_inner_circle}")
        print(f"Time: {tmp_time}")
        print(f"Density: {density}")
        print(f"Mean Time Inside Inner Circle: {mean_time_inside_inner_circle}")

    gui.update_time(str(round(time, 3)))
    gui.update_gui()

# Save density data to CSV file
csv_filename = r"D:"
try:
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Density'])
        writer.writerows(density_data)

    print("Density data saved successfully to", csv_filename)
except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))
except Exception as e:
    print("Unexpected error:", e)

# Plot positions of people over time
def plot_positions_over_time(trajectory_data):
    """Plot positions of people over time"""
    plt.figure(figsize=(8, 6))
    for person_id, trajectory in trajectory_data.items():
        x = [pos[1][0] for pos in trajectory]
        y = [pos[1][1] for pos in trajectory]
        plt.plot(x, y, label=f'Person {person_id}')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Position of People Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

plot_positions_over_time(trajectory_data)

# Plotting
fig = plt.figure(figsize=(8, 6))

# Plotting
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
for person_id, data in individual_data.items():
    if data['time_reached'] is not None:
        ax.scatter(data['time_reached'], 1, data['average_speed'], c='r')  # Plotting time reached vs average speed
ax.set_xlabel('Time Reached Destination')
ax.set_ylabel('Pedestrian ID')
ax.set_zlabel('Average speed')
# Show the plot
plt.title('Average Speed vs. Time Reached Destination')
plt.show()
