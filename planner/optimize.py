import time

from mip import Model, CBC, MAXIMIZE, MINIMIZE, BINARY, INTEGER, xsum, OptimizationStatus

N_CITIES = 4

def get_distance_matrix():
    return [
        [0.0, 1.0, 5.0, 8.0],
        [1.0, 0.0, 2.0, 6.0],
        [5.0, 2.0, 0.0, 3.0],
        [8.0, 6.0, 3.0, 0.0],
    ]

def solve_tsp_no_input():
    n = N_CITIES
    distance_matrix = get_distance_matrix()

    # Create the model, explicitly using CBC
    m = Model(solver_name=CBC)

    # Decision variables x_ij: 1 if we travel from city i to city j, 0 otherwise
    # mip.add_var() creates a single variable
    # We use a dictionary comprehension to create all x_ij variables
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[(i, j)] = m.add_var(name=f"x_{i}_{j}", var_type=BINARY)

    # Auxiliary variables u_i for subtour elimination (MTZ constraints)
    # u_i: the order in which city i is visited (1 to N_CITIES)
    u = {}
    # Note: MTZ constraints require u[0] to be fixed, often to 1.
    # The original Rust code had min 1.0, max n as f64 for all u_i.
    # We will enforce u[0] = 1 implicitly or via a constraint later if needed.
    for i in range(n):
        # The bounds are important for MTZ. u[0] often fixed, others can vary.
        # For simplicity, we'll keep bounds consistent with original for now,
        # but typical MTZ fixes u[0] to 1.
        u[i] = m.add_var(name=f"u_{i}", var_type=INTEGER, lb=1.0, ub=float(n))


    # Objective Function: Minimize total travel distance
    # Sum of distance_ij * x_ij for all i != j
    m.objective = xsum(distance_matrix[i][j] * x[(i, j)] for i in range(n) for j in range(n) if i != j)
    m.sense = MINIMIZE  # Set the sense of optimization here

    # Constraints:

    # 1. Each city must be entered exactly once
    for j in range(n):
        m.add_constr(xsum(x[(i, j)] for i in range(n) if i != j) == 1, name=f"enter_city_{j}")

    # 2. Each city must be exited exactly once
    for i in range(n):
        m.add_constr(xsum(x[(i, j)] for j in range(n) if i != j) == 1, name=f"exit_city_{i}")

    # 3. Subtour Elimination Constraints (MTZ formulation)
    # u_i - u_j + N * x_ij <= N - 1 for i, j = 1..N-1 (excluding city 0)
    # The original code had u[i] - u[j] + (n as f64) * x[i][j].unwrap() <= (n - 1) as f64
    # The MTZ constraints usually apply to all cities *except* the starting city (e.g., city 0).
    # So i and j usually range from 1 to n-1.
    # Also, typically x_ij must be binary (which it is), and u_i integers.

    # We use i and j from 1 to n-1 (assuming city 0 is the fixed start)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                # MTZ constraint: u_i - u_j + n * x_ij <= n - 1
                m.add_constr(u[i] - u[j] + n * x[(i, j)] <= n - 1, name=f"mtz_{i}_{j}")

    # Optionally, fix the starting city's order for MTZ
    # m.add_constr(u[0] == 1, name="u0_fixed")


    # Optimize the model
    print("Starting optimization...")
    status = m.optimize()
    print(f"Optimization status: {status}")

    if status == OptimizationStatus.OPTIMAL:
        print(f"Optimal objective value: {m.objective_value}")

        # Reconstruct the tour
        tour = []
        current_city = 0 # Start at city 0
        tour.append(current_city)

        while len(tour) < n:
            next_city_found = False
            for j in range(n):
                if current_city != j:
                    if x[(current_city, j)].x > 0.5: # Check if the variable is active (close to 1)
                        tour.append(j)
                        current_city = j
                        next_city_found = True
                        break
            if not next_city_found:
                print("Could not find next city in tour (subtour might exist or problem infeasible).")
                break # Exit if no next city found (e.g., if problem is not fully solved or issue)

        print(f"Tour: {tour}")
        return tour
    else:
        print("No optimal solution found.")
        # Depending on your needs, you might raise an exception or return an empty list
        return []
# Modified solve_tsp function to accept distance_matrix
def solve_tsp(distance_matrix: list[list[float]]): # Add type hint for clarity
    # n will now be derived from the input distance_matrix
    n = len(distance_matrix)

    m = Model(solver_name=CBC)

    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[(i, j)] = m.add_var(name=f"x_{i}_{j}", var_type=BINARY)

    u = {}
    for i in range(n):
        u[i] = m.add_var(name=f"u_{i}", var_type=INTEGER, lb=1.0, ub=float(n))

    m.objective = xsum(distance_matrix[i][j] * x[(i, j)] for i in range(n) for j in range(n) if i != j)
    m.sense = MINIMIZE  # Set the sense of optimization here

    for j in range(n):
        m.add_constr(xsum(x[(i, j)] for i in range(n) if i != j) == 1, name=f"enter_city_{j}")

    for i in range(n):
        m.add_constr(xsum(x[(i, j)] for j in range(n) if i != j) == 1, name=f"exit_city_{i}")

    for i in range(1, n): # MTZ constraints usually apply to non-origin cities
        for j in range(1, n):
            if i != j:
                m.add_constr(u[i] - u[j] + n * x[(i, j)] <= n - 1, name=f"mtz_{i}_{j}")

    # --- Start timing the optimization here ---
    start_time_optimize = time.time()
    status = m.optimize()
    end_time_optimize = time.time()
    elapsed_time_optimize = end_time_optimize - start_time_optimize
    # --- End timing the optimization here ---

    print(f"Time taken for MIP optimization in solve_tsp: {elapsed_time_optimize:.4f} seconds")

    print(f"Optimization status: {status}")

    if status == OptimizationStatus.OPTIMAL:
        print(f"Optimal objective value: {m.objective_value}")

        tour = []
        current_city = 0 # Assuming start at city 0
        tour.append(current_city)

        while len(tour) < n:
            next_city_found = False
            for j in range(n):
                if current_city != j:
                    if x[(current_city, j)].x > 0.5:
                        tour.append(j)
                        current_city = j
                        next_city_found = True
                        break
            if not next_city_found:
                print("Could not find next city in tour (subtour might exist or problem infeasible).")
                break

        # This part of the code now returns the tour of indices
        # The calling function (optimise_routes) will need to map these indices back to actual sights
        return tour
    else:
        print("No optimal solution found.")
        return [] # Or raise an error, depending on desired behavior
# Example usage (if you run this script directly)
if __name__ == "__main__":
    found_tour = solve_tsp()
    if found_tour:
        print(f"Final Tour: {found_tour}")
        # You could also calculate the total distance from the tour here
        total_dist = 0.0
        dist_matrix = get_distance_matrix()
        for i in range(len(found_tour) - 1):
            total_dist += dist_matrix[found_tour[i]][found_tour[i+1]]
        total_dist += dist_matrix[found_tour[-1]][found_tour[0]] # Return to start
        print(f"Calculated Total Distance: {total_dist}")
    print("Running solve_tsp()...")
    # Define a dummy distance matrix for testing
    dummy_distance_matrix = [
        [0.0, 1.0, 5.0, 8.0],
        [1.0, 0.0, 2.0, 6.0],
        [5.0, 2.0, 0.0, 3.0],
        [8.0, 6.0, 3.0, 0.0],
    ]
    found_tour_indices = solve_tsp(dummy_distance_matrix)  # Pass the matrix now!

    if found_tour_indices:
        print(f"Final Tour Indices from solve_tsp: {found_tour_indices}")
        total_dist = 0.0
        # Re-using dummy_distance_matrix for calculation here
        for i in range(len(found_tour_indices) - 1):
            total_dist += dummy_distance_matrix[found_tour_indices[i]][found_tour_indices[i + 1]]
        total_dist += dummy_distance_matrix[found_tour_indices[-1]][found_tour_indices[0]]  # Return to start
        print(f"Calculated Total Distance: {total_dist}")