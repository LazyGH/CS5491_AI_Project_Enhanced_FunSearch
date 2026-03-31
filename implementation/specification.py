specification = r'''
import numpy as np
import math

def max_index_except(arr: np.ndarray, exclude_indices: list) -> int:
    """Return the index of the maximum value in the array, excluding the given indices."""
    # Flatten the 2D list of exclude_indices
    exclude_indices = [item for sublist in exclude_indices for item in sublist]
    exclude_indices = list(set(exclude_indices))
    # Create a mask of True values and exclude the given indices
    mask = np.ones_like(arr, dtype=bool)
    mask[exclude_indices] = False
    # Get the values that are not excluded
    filtered_arr = arr[mask]
    # Get the index of the maximum value in the filtered array
    max_index = np.argmax(filtered_arr)
    # Get the original index of the maximum value
    original_max_index = np.arange(arr.size)[mask][max_index]
    return original_max_index

def cvrp(capacity: int, demand: np.ndarray, edge_weight: np.ndarray) -> tuple[list, float]:
    """Performs the delivery of goods to a number of cities from a central depot."""
    # A list to store the routes for each vehicle.
    routes = []
    # A temporary variables.
    route = []
    dis = 0
    # Copy the edge_weight matrix to avoid modifying the original matrix
    edge_weight = edge_weight.copy()
    # Total distance covered by all vehicles.
    dis_sum = 0
    # The current load of the vehicle.
    load = 0
    # The city where the vehicle is currently located, starting with the depot (city 0).
    current_city = 0
    # A counter to keep track of the number of cities visited
    counter = 0
    # Store the distance from all cities to the depot
    depot_dis = edge_weight[:, 0].copy()
    # Set the distance from any city to the depot to a very large number to avoid returning to the depot prematurely
    edge_weight[:, 0] = math.pow(10, 4)
    # Set the distance from any city to itself to a very large number to avoid self-loops
    for i in range(len(edge_weight)):
        edge_weight[i, i] = math.pow(10, 4)
    while counter < len(demand) - 1:
        # Determine the next city to visit based on some priority
        priorities = priority(current_city, edge_weight.copy(), capacity-load, demand)
        # Mask the current routes to avoid revisit (double check)
        next_city = max_index_except(priorities, routes+[[current_city]+route])
        # If the vehicle's remaining capacity is sufficient to meet the demand of the next city, it proceeds to that city
        if load + demand[next_city] <= capacity and next_city != 0:
            # Update the distance and load for the current route
            dis += edge_weight[current_city, next_city]
            load += demand[next_city]
            # Add the next city to the current route
            route.append(next_city)
            # Increment the counter for cities visited
            counter += 1
            # Apply penalty to avoid revisiting
            edge_weight[:, next_city] = math.pow(10,4)
            # Update the current city to the next city
            current_city = next_city
        else:
            # If the vehicle's capacity is not sufficient, it completes the current route by returning to the depot, updates the total distance, and starts a new route.
            dis += depot_dis[current_city]
            dis_sum += dis
            # Add the completed route to the list of routes
            routes.append(route)
            # Reset variables for the next route
            current_city = 0
            dis = 0
            load = 0
            route = []
    # After visiting all cities, if the last vehicle is not at the depot, it returns to the depot to complete the final route.
    if current_city != 0:
        dis += depot_dis[current_city]
        dis_sum += dis
        routes.append(route)
    return routes, dis_sum

@funsearch.run
def evaluate(instances: dict) -> float:
    """Evaluate heuristic function on a set of CVRP instances."""
    # List total route cost for each instance.
    costs = []
    # Perform cvrp for each instance.
    for name in instances:
        instance = instances[name]
        # Read instance data.
        capacity = instance['capacity']
        demand = instance['demand']
        edge_weight = instance['edge_weight']
        routes, cost = cvrp(capacity, demand, edge_weight)
        # Calculate the total cost of the route for current instance.
        costs.append(cost)
    # Score of heuristic function is negative of average number of total route cost
    # across instances (as we want to minimize costs).
    return -np.mean(costs)

@funsearch.evolve
def priority(current_city: int, edge_weight: np.ndarray, remaining_capacity: int, demand: np.ndarray) -> np.ndarray:
    """Returns priority for which we want to select the next city,

    Args:
        current_city: Number of the current city.
        edge_weight: The current global distance matrix.
        remaining_capacity: The remaining capacity of the current vehicle.
        demand: The demand of each city.

    Return:
        Array of the size of the number of cities with priority score of each city.
    """
    priority = edge_weight[current_city]
    for i in range(len(priority)):
        if remaining_capacity >= demand[i]:
            priority[i] -= math.sqrt(demand[i])
        else:
            if priority[i] > 0:
                priority[i] += math.sqrt(demand[i])
            else:
                priority[i] -= math.sqrt(demand[i])

    return -priority
'''