# tour_planner_orchestrator.py
from collections import defaultdict
import math
from typing import Dict, List, Tuple
from shapely.geometry import Point as ShapelyPoint
from meteostat import Point as MeteostatPoint

# --------- 1. Distance helpers -------------------------------------------------
from meteostat import Point

from .sights import Sight


def haversine(coord1, coord2):
    #print(f"[DEBUG] Raw coord1: {coord1}, type: {type(coord1)}")
    #print(f"[DEBUG] Raw coord2: {coord2}, type: {type(coord2)}")

    # Convert coord1
    if isinstance(coord1, (MeteostatPoint, ShapelyPoint)):
        coord1 = (coord1.lat, coord1.lon) if isinstance(coord1, MeteostatPoint) else (coord1.y, coord1.x)

    # Convert coord2
    if isinstance(coord2, (MeteostatPoint, ShapelyPoint)):
        coord2 = (coord2.lat, coord2.lon) if isinstance(coord2, MeteostatPoint) else (coord2.y, coord2.x)

    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    #print(f"[DEBUG] Radians: lat1={lat1}, lon1={lon1}, lat2={lat2}, lon2={lon2}")

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    r = 6371  # Earth radius in kilometers
    distance = c * r
    #print(f"[DEBUG] Haversine distance: {distance} km")
    return distance

def build_distance_matrix(sights):
    n = len(sights)
    mat = [[0.0]*n for _ in range(n)]
    for i in range(n):
        # Determine (lat_i, lon_i)
        if isinstance(sights[i].location, ShapelyPoint):  # <-- Use ShapelyPoint here
            # Assuming ShapelyPoint stores (longitude, latitude) as per your debug: POINT (2.347 48.8529)
            # So, .x is longitude, .y is latitude.
            # We need (latitude, longitude) for haversine.
            lat_i, lon_i = sights[i].location.y, sights[i].location.x
        elif isinstance(sights[i].location, MeteostatPoint):  # <-- Handle MeteostatPoint
            # Meteostat Point objects typically have .lat and .lon attributes
            lat_i, lon_i = sights[i].location.lat, sights[i].location.lon
        elif isinstance(sights[i].location, tuple):
            # If it's already a tuple (lat, lon)
            lat_i, lon_i = sights[i].location
        else:
            raise TypeError(
                f"Unsupported location type for sight {sights[i].name} at index {i}: {type(sights[i].location)}")

        for j in range(i+1, n):
            # Determine (lat_j, lon_j)
            if isinstance(sights[j].location, ShapelyPoint):  # <-- Use ShapelyPoint here
                lat_j, lon_j = sights[j].location.y, sights[j].location.x
            elif isinstance(sights[j].location, MeteostatPoint):  # <-- Handle MeteostatPoint
                lat_j, lon_j = sights[j].location.lat, sights[j].location.lon
            elif isinstance(sights[j].location, tuple):
                lat_j, lon_j = sights[j].location
            else:
                raise TypeError(
                    f"Unsupported location type for sight {sights[j].name} at index {j}: {type(sights[j].location)}")

            d = haversine((lat_i, lon_i), (lat_j, lon_j)) / 1000  # km
            mat[i][j] = mat[j][i] = d
    return mat

# --------- 3. Route optimisation per group (Rust MILP) -------------------------
#from rust_milp_tsp import solve_tsp  # compiled with maturin
# NEW PLAN: optimize with python-mip
from .optimize import solve_tsp


def optimise_routes(groups) -> Dict[str, List]:
    optimised = {}
    for w, sights in groups.items():
        if len(sights) <= 2:
            optimised[w] = sights
            continue
        mat = build_distance_matrix(sights)
        order = solve_tsp(mat)
        optimised[w] = [sights[i] for i in order]
    return optimised


# --------- 2. Weather-aware grouping helpers -----------------------------------
def initial_balanced_groups(sights, slot_counts: Dict[str, int], city_center):
    """
    Assigns all sights to initial weather-based groups.
    Prioritizes primary weather suitability, then "any" sights.
    """
    grouped = defaultdict(list)

    # First, try to assign each sight to its primary weather category
    # If a sight has multiple weather suitabilities, it goes into the group
    # of its first suitability tag.
    # If no suitability, it's treated as 'any'.
    for s in sights:
        tag = s.weather_suitability[0] if s.weather_suitability else "any"
        grouped[tag].append(s)

    # Now, distribute all sights into the weather categories that exist in slot_counts.
    # If a sight's primary tag is not in slot_counts (i.e., not a forecasted weather),
    # it needs to be handled, likely by putting it into an "any" pool or distributing directly.
    # For simplicity, we'll ensure all sights are now in a group that maps to a forecast.

    final_groups = defaultdict(list)
    all_assigned_sights = set()  # To keep track of assigned sights

    # 1. Assign sights to direct weather matches first
    for weather_cat, count_slots in slot_counts.items():
        if weather_cat in grouped:
            # Add all sights from this direct weather category to the final_groups
            # No longer slicing with [:target] here.
            for s in grouped[weather_cat]:
                final_groups[weather_cat].append(s)
                all_assigned_sights.add(s.name)  # Use name for set tracking, assuming unique names

    # 2. Distribute "any" sights and other unassigned sights
    # Gather sights that were not directly assigned above (e.g., from 'any' or unforecasted tags)
    unassigned_sights = [s for s in sights if s.name not in all_assigned_sights]

    if unassigned_sights:
        # Sort unassigned by distance to city_center for a more logical distribution
        unassigned_sights_sorted = sorted(unassigned_sights, key=lambda s: haversine(city_center, s.location))

        # Round-robin distribute unassigned sights to available forecast weather categories
        forecast_weather_categories = list(slot_counts.keys())
        if not forecast_weather_categories:  # Fallback if no specific forecast categories
            # This should ideally not happen if forecast is populated, but good for robustness
            forecast_weather_categories = ["any"]  # Use 'any' if forecast is empty

        for i, s in enumerate(unassigned_sights_sorted):
            target_w = forecast_weather_categories[i % len(forecast_weather_categories)]
            final_groups[target_w].append(s)

    return final_groups


def balance_by_stealing_old(groups: Dict[str, List[Sight]], slot_counts: Dict[str, int]) -> Dict[str, List[Sight]]:
    """
    Attempts to balance the number of sights per weather group,
    proportional to the number of time slots each weather category covers in the forecast.
    Moves sights from larger groups to smaller ones, prioritizing 'any' sights or
    those suitable for the target group's weather.
    """
    new_groups = {w: list(sights) for w, sights in groups.items()}

    total_sights_in_groups = sum(len(v) for v in new_groups.values())

    # Calculate the total number of time slots in the forecast (e.g., 3 for morning, afternoon, evening)
    total_time_slots_in_forecast = sum(slot_counts.values())

    if total_time_slots_in_forecast == 0 or total_sights_in_groups == 0:
        return new_groups

    # Calculate the ideal average number of sights per *single time slot*
    sights_per_ideal_slot = total_sights_in_groups / total_time_slots_in_forecast

    # Determine the target size for each weather category based on how many slots it covers.
    # This is the proportionally weighted target.
    target_sizes_for_categories = {
        w_cat: sights_per_ideal_slot * count_slots
        for w_cat, count_slots in slot_counts.items()
    }

    # Perform multiple passes to allow balancing to propagate
    for _ in range(5):  # Iterate a few times for better convergence
        has_balanced_this_pass = False

        # Sort groups by their current size (smallest first) to identify potential receivers
        # We only consider categories that are actually in our target_sizes_for_categories (i.e., in the forecast)
        sorted_keys_by_size_asc = sorted(
            [w for w in new_groups if w in target_sizes_for_categories],
            key=lambda w: len(new_groups[w])
        )

        for w_target in sorted_keys_by_size_asc:
            current_target_size = len(new_groups[w_target])
            # Get the *proportional target size* for this specific weather category
            target_ideal_size = target_sizes_for_categories[w_target]

            # If this group is significantly smaller than its proportional ideal size, try to grow it
            # Using a threshold (e.g., if it's less than 90% of its ideal target)
            if current_target_size < target_ideal_size * 0.9:

                # Find a donor group that is significantly larger than its proportional ideal size
                sorted_keys_by_size_desc = sorted(
                    [w for w in new_groups if w in target_sizes_for_categories],
                    key=lambda w: len(new_groups[w]), reverse=True
                )
                for w_donor in sorted_keys_by_size_desc:
                    current_donor_size = len(new_groups[w_donor])
                    donor_ideal_size = target_sizes_for_categories[w_donor]

                    # Conditions for a valid donor:
                    # 1. Not the same as the target group
                    # 2. Must be significantly larger than its proportional ideal size (e.g., 110% of ideal target)
                    # 3. Must have more than 1 sight to give away (so it doesn't empty itself)
                    if (w_donor == w_target or
                            current_donor_size < donor_ideal_size * 1.1 or
                            len(new_groups[w_donor]) <= 1):  # Ensure donor doesn't become empty or too small
                        continue

                    # How many sights to attempt to steal from the donor
                    # Aim to bring target closer to its ideal, and ensure donor doesn't drop too low
                    # Calculate how many sights target needs to reach its ideal
                    needed_by_target = max(0, int(target_ideal_size - current_target_size))
                    # Calculate how many sights donor can give while staying above its ideal
                    can_give_by_donor = max(0, int(current_donor_size - donor_ideal_size))

                    # Steal a reasonable amount, e.g., up to 3 sights per attempt, limited by what's needed/can be given
                    num_to_steal = min(needed_by_target, can_give_by_donor, 3)

                    if num_to_steal == 0:
                        continue  # No effective stealing quantity for this pair

                    pool_to_steal_from = new_groups[w_donor]
                    stolen_candidates = []
                    for s in pool_to_steal_from:
                        # Prioritize sights suitable for the target weather category or 'any'
                        if "any" in s.weather_suitability or w_target in s.weather_suitability:
                            stolen_candidates.append(s)
                        if len(stolen_candidates) >= num_to_steal:
                            break  # Found enough candidates

                    if len(stolen_candidates) > 0:
                        sights_actually_stolen = stolen_candidates[:num_to_steal]
                        for s in sights_actually_stolen:
                            if s in pool_to_steal_from:  # Defensive check
                                pool_to_steal_from.remove(s)
                                new_groups[w_target].append(s)

                        has_balanced_this_pass = True
                        # If a successful balance happened, it's possible group sizes have changed.
                        # Break to re-evaluate the target/donor lists in the next pass.
                        break

        if not has_balanced_this_pass:  # If no balancing occurred in a full pass, we are stable
            break

    return new_groups


# In planner/base_planner.py (or where calculate_centroid is defined)

def calculate_centroid(sights: List['Sight']) -> Tuple[float, float]:
    """Calculates the geographical centroid (average lat/lon) of a list of sights."""
    if not sights:
        return (0.0, 0.0)

    total_lat = 0.0
    total_lon = 0.0
    for s in sights:
        # Assuming s.location is a Point object with .y (latitude) and .x (longitude)
        total_lat += s.location.y  # Latitude
        total_lon += s.location.x  # Longitude

    return (total_lat / len(sights), total_lon / len(sights))


def balance_by_stealing(groups: Dict[str, List['Sight']], slot_counts: Dict[str, int],
                        city_center: Tuple[float, float]) -> Dict[str, List['Sight']]:
    """
    Attempts to balance the number of sights per weather group,
    proportional to the number of time slots each weather category covers in the forecast.
    Moves sights from larger groups to smaller ones, prioritizing 'any' sights or
    those suitable for the target group's weather, and favoring sights geographically
    closer to the target group's intended location.
    """
    new_groups = {w: list(sights) for w, sights in groups.items()}

    total_sights_in_groups = sum(len(v) for v in new_groups.values())

    total_time_slots_in_forecast = sum(slot_counts.values())

    if total_time_slots_in_forecast == 0 or total_sights_in_groups == 0:
        return new_groups

    sights_per_ideal_slot = total_sights_in_groups / total_time_slots_in_forecast

    target_sizes_for_categories = {
        w_cat: sights_per_ideal_slot * count_slots
        for w_cat, count_slots in slot_counts.items()
    }

    for _ in range(5):  # Multiple passes for better convergence
        has_balanced_this_pass = False

        # Only consider categories that are actually in our target_sizes_for_categories (i.e., in the forecast)
        sortable_keys_asc = [w for w in new_groups if w in target_sizes_for_categories]
        sorted_keys_by_size_asc = sorted(sortable_keys_asc, key=lambda w: len(new_groups[w]))

        for w_target in sorted_keys_by_size_asc:
            current_target_size = len(new_groups[w_target])
            target_ideal_size = target_sizes_for_categories[w_target]

            if current_target_size < target_ideal_size * 0.9:  # Target group is significantly smaller

                # Determine the geographical center for the target group for stealing proximity.
                # If target group is currently empty, use city_center as a reference.
                target_centroid = calculate_centroid(new_groups[w_target])
                if target_centroid == (0.0, 0.0) and not new_groups[
                    w_target]:  # Check if calculate_centroid returned default for empty list
                    target_centroid = city_center

                sortable_keys_desc = [w for w in new_groups if w in target_sizes_for_categories]
                sorted_keys_by_size_desc = sorted(sortable_keys_desc, key=lambda w: len(new_groups[w]), reverse=True)
                for w_donor in sorted_keys_by_size_desc:
                    current_donor_size = len(new_groups[w_donor])
                    donor_ideal_size = target_sizes_for_categories[w_donor]

                    if (w_donor == w_target or
                            current_donor_size < donor_ideal_size * 1.1 or  # Donor not significantly larger
                            len(new_groups[w_donor]) <= 1):  # Donor has too few sights to give
                        continue

                    needed_by_target = max(0, int(target_ideal_size - current_target_size))
                    can_give_by_donor = max(0, int(current_donor_size - donor_ideal_size))

                    num_to_steal = min(needed_by_target, can_give_by_donor, 1)

                    if num_to_steal == 0:
                        continue

                        # Build a list of potential sights to steal, prioritizing by suitability and proximity
                    potential_sights_to_steal_with_dist = []
                    for s in new_groups[w_donor]:
                        # Calculate distance to target centroid
                        dist_to_target = haversine(target_centroid, s.location)

                        # Assign a 'priority score' for stealing:
                        # Lower score = higher priority
                        # 'any' suitability gets a bonus (lower score)
                        # suitability for target category gets a bonus
                        # Distance is a primary factor
                        priority_score = dist_to_target
                        if "any" in s.weather_suitability:
                            priority_score *= 0.5  # Halve distance cost if 'any'
                        elif w_target in s.weather_suitability:
                            priority_score *= 0.8  # Slightly reduce distance cost if directly suitable

                        potential_sights_to_steal_with_dist.append((s, priority_score))

                    # Sort candidates by their priority score (lowest score first)
                    potential_sights_to_steal_with_dist.sort(key=lambda x: x[1])

                    # Extract the actual sights from the sorted list
                    sights_actually_stolen = [s for s, score in potential_sights_to_steal_with_dist[:num_to_steal]]

                    if len(sights_actually_stolen) > 0:
                        for s in sights_actually_stolen:
                            if s in new_groups[w_donor]:  # Defensive check
                                new_groups[w_donor].remove(s)
                                new_groups[w_target].append(s)

                        has_balanced_this_pass = True
                        break

        if not has_balanced_this_pass:
            break

    return new_groups


def plan_citytour_iterative(
        sights: List[Sight],
        city_center: tuple,
        weather_forecast: Dict[str, str],  # e.g., {'morning':'cloudy','afternoon':'sunny','evening':'cloudy'}
        max_iters: int = 4
) -> Dict[str, List[Sight]]:  # Now explicitly returns slot-keyed dictionary
    """
    sights: list of Sight objects, each with .location (lat,lon) & .weather_suitability (list[str])
    weather_forecast: {'morning':'cloudy','afternoon':'sunny','evening':'cloudy'}
    Returns dict time_slot->ordered list of sights
    """
    # 1. Determine slot counts for each weather category based on forecast
    slot_counts = defaultdict(int)
    for slot, w_cat in weather_forecast.items():
        slot_counts[w_cat] += 1

    # 2. Initial grouping of sights into weather categories
    # This now ensures all sights are initially placed into a group
    groups = initial_balanced_groups(sights, slot_counts, city_center)

    # 3. Iteratively optimize routes within groups and rebalance
    # The 'groups' will be refined over iterations, and sights within them will be optimally ordered.
    for _ in range(max_iters):
        # Optimize routes within each weather group using MILP
        optimised_weather_groups = optimise_routes(groups)  # This returns weather-keyed groups, ordered

        # Rebalance sights across groups (primarily to fill empty ones or re-distribute)
        new_groups = balance_by_stealing(optimised_weather_groups, slot_counts, city_center)

        # Check for stabilization (if groups haven't changed much)
        if new_groups == groups:
            break
        groups = new_groups

    # 4. Final step: Distribute the optimally ordered sights (from 'groups') into actual time slots
    # Initialize the final tour plan structure with all time slots from the forecast
    final_tour_plan = {slot: [] for slot in weather_forecast.keys()}

    # Create a reverse map: from weather category to the actual time slots it covers
    # Example: {'cloudy': ['morning', 'evening'], 'sunny': ['afternoon']}
    weather_to_slots_map = defaultdict(list)
    for slot_name, weather_category in weather_forecast.items():
        weather_to_slots_map[weather_category].append(slot_name)

    # Iterate through the final, optimized weather-based groups
    for weather_category_key, ordered_sights_in_group in groups.items():

        # Get the list of time slots that have this weather category in the forecast
        matching_slots = weather_to_slots_map.get(weather_category_key, [])

        if not matching_slots:
            # This handles cases where a sight might end up in a weather_category_key (e.g., 'dry')
            # that wasn't explicitly in the current day's weather_forecast for any slot.
            print(
                f"Warning: Weather category '{weather_category_key}' has no matching slots in forecast. Sights from this group may not be assigned to a specific time slot.")
            # For robustness, you could assign these to the first available slot or a default 'any' slot.
            # For now, we'll skip if no specific matching slots, ensuring they are not double-counted later.
            continue

        num_sights_in_group = len(ordered_sights_in_group)
        num_matching_slots = len(matching_slots)

        if num_sights_in_group == 0:
            continue  # Nothing to assign for this weather group

        # If there's only one slot for this weather type, assign all sights to it
        if num_matching_slots == 1:
            final_tour_plan[matching_slots[0]].extend(ordered_sights_in_group)
        else:
            # If multiple slots for this weather type (e.g., morning and evening both cloudy),
            # distribute sights evenly or round-robin among them.
            # This is similar to the logic you had in create_weather_aware_tour.
            for i, sight in enumerate(ordered_sights_in_group):
                slot_to_assign = matching_slots[i % num_matching_slots]
                final_tour_plan[slot_to_assign].append(sight)

    return final_tour_plan

