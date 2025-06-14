from .aware_tour import split_day_into_slots, is_weather_suitable, optimize_route
from .get_route import generate_information_full_day_tour
from .weather import get_weather_condition #p
from .postcard import generate_postcard #p
from abc import ABC, abstractmethod
import math
from collections import defaultdict
from .tour_planner_orchestrator import plan_citytour_iterative

import time

class Planner(ABC):
    @abstractmethod
    def plan(self, sights, city_center, mode, weather_forecast):
        pass

# --- DayPlanner Class ---
class DayPlanner(Planner):
    async def plan(self, sights, city_center, mode, weather_forecast):
        """
        Plans a full-day tour using both weather-aware and iterative strategies,
        and generates comprehensive information for each, including total route
        length and duration using efficient OSRM calls.

        Returns a dictionary containing details for both plans suitable for table display.
        """
        results = {}

        # --- Weather-Aware Tour Planning and Information Generation ---
        print("\n--- Measuring create_weather_aware_tour ---")
        start_time_aware_planning = time.time()
        tour_plan_aware = create_weather_aware_tour(sights, weather_forecast, city_center, mode=mode)
        end_time_aware_planning = time.time()
        elapsed_time_aware_planning = end_time_aware_planning - start_time_aware_planning
        print(f"Time taken for weather-aware plan generation: {elapsed_time_aware_planning:.4f} seconds")

        # Calculate full tour information for weather-aware plan using the efficient function
        start_time_aware_routing = time.time()
        aware_tour_info = await  generate_information_full_day_tour(tour_plan_aware, city_center, mode)
        end_time_aware_routing = time.time()
        elapsed_time_aware_routing = end_time_aware_routing - start_time_aware_routing
        print(f"Time taken for weather-aware full route calculation: {elapsed_time_aware_routing:.4f} seconds")

        results["aware_plan"] = {
            "tour_plan": tour_plan_aware,
            "planning_time_seconds": elapsed_time_aware_planning,
            "routing_time_seconds": elapsed_time_aware_routing,
            "total_length_meters": aware_tour_info.get('total_subtour_length_meters', 0.0),
            "total_duration_seconds": aware_tour_info.get('total_duration_seconds', 0.0),
            "full_route_geojson": aware_tour_info.get('full_route_geojson'),
            "message": aware_tour_info.get('message'),
            "haversine_total_length_meters": aware_tour_info.get('haversine_total_length_meters', 0.0),
            "haversine_subtour_lengths_meters": aware_tour_info.get('haversine_subtour_lengths_meters', {}),
            "haversine_total_subtour_length_meters": aware_tour_info.get('haversine_total_subtour_length_meters', 0.0)
        }

        # --- Iterative Tour Planning and Information Generation ---
        print("\n--- Measuring plan_citytour_iterative ---")
        start_time_iterative_planning = time.time()
        tour_plan_iterative = plan_citytour_iterative(
            sights=sights,
            city_center=city_center,
            weather_forecast=weather_forecast # iterative might not strictly need weather but pass for consistency
        )
        end_time_iterative_planning = time.time()
        elapsed_time_iterative_planning = end_time_iterative_planning - start_time_iterative_planning
        print(f"Time taken for iterative plan generation: {elapsed_time_iterative_planning:.4f} seconds")

        # Calculate full tour information for iterative plan using the efficient function
        start_time_iterative_routing = time.time()
        iterative_tour_info = await generate_information_full_day_tour(tour_plan_iterative, city_center, mode)
        end_time_iterative_routing = time.time()
        elapsed_time_iterative_routing = end_time_iterative_routing - start_time_iterative_routing
        print(f"Time taken for iterative full route calculation: {elapsed_time_iterative_routing:.4f} seconds")

        results["iterative_plan"] = {
            "tour_plan": tour_plan_iterative,
            "planning_time_seconds": elapsed_time_iterative_planning,
            "routing_time_seconds": elapsed_time_iterative_routing,
            "total_length_meters": iterative_tour_info.get('total_subtour_length_meters', 0.0),
            "total_duration_seconds": iterative_tour_info.get('total_duration_seconds', 0.0),
            "full_route_geojson": iterative_tour_info.get('full_route_geojson'),
            "message": iterative_tour_info.get('message'),
            "haversine_total_length_meters": iterative_tour_info.get('haversine_total_length_meters', 0.0),
            "haversine_subtour_lengths_meters": iterative_tour_info.get('haversine_subtour_lengths_meters', {}),
            "haversine_total_subtour_length_meters": iterative_tour_info.get('haversine_total_subtour_length_meters', 0.0)
        }

        results["selected_plan_type"] = "aware" # Default selection, can be changed based on criteria

        return results

    def plan_all(self, sights, city_center, mode, weather_forecast):
        """
        Original 'plan_old' method, renamed to 'plan_all' as requested.
        This method is kept for compatibility with its original return structure.
        """
        # --- Option 1: create_weather_aware_tour ---
        print("\n--- Measuring create_weather_aware_tour ---")
        start_time_aware = time.time()
        tour_plan_aware = create_weather_aware_tour(sights, weather_forecast, city_center, mode=mode)
        end_time_aware = time.time()
        elapsed_time_aware = end_time_aware - start_time_aware
        print(f"Time taken for plan_citytour_iterative - new : {elapsed_time_aware:.4f} seconds")
        print(f"Tour Plan (Weather-Aware): {tour_plan_aware}")

        # --- Option 2: plan_citytour_iterative ---
        print("\n--- Measuring plan_citytour_iterative ---")
        start_time_iterative = time.time()
        tour_plan_iterative = plan_citytour_iterative(
            sights=sights,
            city_center=city_center,
            weather_forecast=weather_forecast
        )
        end_time_iterative = time.time()
        elapsed_time_iterative = end_time_iterative - start_time_iterative
        print(f"Time taken for plan_citytour_iterative: {elapsed_time_iterative:.4f} seconds")
        print(f"Tour Plan (Iterative): {tour_plan_iterative}")

        flat_plan = [s for slot_sights in tour_plan_iterative.values() for s in slot_sights]
        # Assuming generate_postcard is available
        # postcards = [generate_postcard(s, weather_forecast) for s in flat_plan]

        def get_main_weather(forecast):
            values = forecast.values()
            if all(v == "sunny" for v in values):
                return "sunny"
            elif any(v == "rainy" for v in values):
                return "rainy"
            elif all(v == "mixed" for v in values):
                return "any"
            else:
                return "any"

        main_weather = get_main_weather(weather_forecast)

        # Note: The original 'plan_old' returned flat_plan, main_weather, postcards, tour_plan_iterative.
        # If 'postcards' generation is still needed, ensure 'generate_postcard' is available.
        return flat_plan, main_weather, None, tour_plan_iterative # Returning None for postcards for now

# Later, add:
# class WeekPlanner(Planner):
#     def plan(self, sights, city_center, mode):
#         pass



def plan_day_weather(sights, city_coords):
    from datetime import datetime
    weather = get_weather_condition(city_coords[0], city_coords[1], datetime.now())
    plan = [s for s in sights if weather in s.weather_suitability]
    postcards = [generate_postcard(s, weather) for s in plan]
    return plan, weather, postcards

def plan_day(sights, city_coords):
    weather = "unknown"  # or get_current_weather()
    # Instead of filtering by weather, return all sights for testing
    plan = sights
    postcards = ["Have a great day!"] * len(plan)
    return plan, weather, postcards

def create_weather_aware_tour_old(sights, weather_forecast, city_center):
    """
    Create a tour divided by time slots, only including sights suitable for the weather.
    Returns dict: { time_slot: [ordered sights] }
    """
    # debug log
    print("🗓️ Using forecast:", weather_forecast)
    time_slots = split_day_into_slots()
    tour_plan = {}

    for slot in time_slots.keys():
        weather = weather_forecast.get(slot, "unknown")
        suitable_sights = [s for s in sights if is_weather_suitable(s, weather)]
        ordered_sights = optimize_route(city_center, suitable_sights)
        tour_plan[slot] = ordered_sights

    return tour_plan
def create_weather_aware_tour_old2(sights, weather_forecast, city_center, mode="walking"):
    """
    Assign all sights to time slots based on weather suitability and availability.
    Returns dict: { time_slot: [ordered sights] }
    """
    # debug log
    print("🗓️ Using forecast:", weather_forecast)
    time_slots = split_day_into_slots()  # e.g. {'morning': ..., 'afternoon': ..., 'evening': ...}
    slots = list(time_slots.keys())
    tour_plan = {slot: [] for slot in slots}

    # Weather priority order for fallback
    weather_priority = ["sunny", "cloudy", "rainy", "any"]

    # Helper to get best priority of a sight
    def best_priority(sight):
        for p, w in enumerate(weather_priority):
            if w in sight.weather_suitability:
                return p
        return len(weather_priority)

    # Sort sights by restrictiveness (lower index = more restrictive)
    sights_sorted = sorted(sights, key=best_priority)

    assigned = set()

    # First pass: assign sights to slots where weather matches their suitability best
    for slot in slots:
        slot_weather = weather_forecast.get(slot, "unknown")
        for sight in sights_sorted:
            if sight in assigned:
                continue
            # If sight prefers this weather, assign here
            if slot_weather in sight.weather_suitability or "any" in sight.weather_suitability:
                tour_plan[slot].append(sight)
                assigned.add(sight)

    # Second pass: assign unassigned sights to any slot (fallback)
    for sight in sights_sorted:
        if sight not in assigned:
            for slot in slots:
                tour_plan[slot].append(sight)
                assigned.add(sight)
                break

    # Optimize order per slot
    for slot in slots:
        tour_plan[slot] = optimize_route(city_center, tour_plan[slot], mode=mode)

    return tour_plan

def create_weather_aware_tour3(sights, weather_forecast, city_center, mode="walking"):
    """
    Assign all sights to time slots based on weather suitability and availability.
    Returns dict: { time_slot: [ordered sights] }
    """
    # debug log
    print("🗓️ Using forecast:", weather_forecast)
    time_slots = split_day_into_slots()  # e.g. {'morning': ..., 'afternoon': ..., 'evening': ...}
    slots = list(time_slots.keys())
    tour_plan = {slot: [] for slot in slots}

    # Weather priority order for fallback
    weather_priority = ["sunny", "cloudy", "rainy", "any"]

    # Helper to get best priority of a sight
    def best_priority(sight):
        for p, w in enumerate(weather_priority):
            if w in sight.weather_suitability:
                return p
        return len(weather_priority)

    # Sort sights by restrictiveness (lower index = more restrictive)
    sights_sorted = sorted(sights, key=best_priority)

    assigned = set()

    # First pass: assign sights to slots where weather matches their suitability best
    for sight in sights_sorted:
        matching_slots = [slot for slot in slots if
                          weather_forecast.get(slot) in sight.weather_suitability or "any" in sight.weather_suitability]
        if matching_slots:
            # pick the slot that best suits your logic, e.g., earliest slot:
            assigned_slot = matching_slots[0]
            # or latest slot:
            # assigned_slot = matching_slots[-1]
            # or randomly:
            # assigned_slot = random.choice(matching_slots)
        else:
            assigned_slot = slots[0]  # fallback
        tour_plan[assigned_slot].append(sight)
        print(f"Assigning sight '{sight.name}' with suitability {sight.weather_suitability}")
        print(f"  Matching slots: {matching_slots}")
        print(f"  Assigned to slot: {assigned_slot}")

    # Optimize order per slot
    for slot in slots:
        tour_plan[slot] = optimize_route(city_center, tour_plan[slot], mode=mode)

    return tour_plan

def create_weather_aware_tour4(sights, weather_forecast, city_center, mode="walking"):
    print("🗓️ Using forecast:", weather_forecast)
    time_slots = split_day_into_slots()
    slots = list(time_slots.keys())
    tour_plan = {slot: [] for slot in slots}

    weather_priority = ["sunny", "cloudy", "rainy", "any"]

    def best_priority(sight):
        for p, w in enumerate(weather_priority):
            if w in sight.weather_suitability:
                return p
        return len(weather_priority)

    sights_sorted = sorted(sights, key=best_priority)

    # Group sights by their main weather suitability tag
    weather_grouped_sights = defaultdict(list)
    for sight in sights_sorted:
        main_weather = sight.weather_suitability[0] if sight.weather_suitability else "any"
        weather_grouped_sights[main_weather].append(sight)

    # Optimize each weather group’s sights first
    optimized_groups = {}
    for weather_cat, group_sights in weather_grouped_sights.items():
        optimized_groups[weather_cat] = optimize_route(city_center, group_sights, mode=mode)

    # Map weather -> slots with that weather in forecast
    weather_to_slots = defaultdict(list)
    for slot in slots:
        w = weather_forecast.get(slot)
        if w:
            weather_to_slots[w].append(slot)

    # Now split each optimized group evenly across matching slots
    for weather_cat, ordered_sights in optimized_groups.items():
        matching_slots = weather_to_slots.get(weather_cat, [])
        if not matching_slots:
            matching_slots = slots  # fallback to all slots
        print(f"Weather category '{weather_cat}' matched slots: {matching_slots}")

        n = len(ordered_sights)
        k = len(matching_slots)
        chunk_size = math.ceil(n / k)

        for i, slot in enumerate(matching_slots):
            start = i * chunk_size
            end = start + chunk_size
            tour_plan[slot].extend(ordered_sights[start:end])
            print(f"Assigning {len(ordered_sights[start:end])} sights with weather '{weather_cat}' to slot '{slot}'")

    return tour_plan

def create_weather_aware_tour(sights, weather_forecast, city_center, mode="walking"):
    print("🗓️ Using forecast:", weather_forecast)
    time_slots = split_day_into_slots()
    slots = list(time_slots.keys())
    tour_plan = {slot: [] for slot in slots}

    weather_priority = ["sunny", "cloudy", "rainy", "any"]

    def best_priority(sight):
        for p, w in enumerate(weather_priority):
            if w in sight.weather_suitability:
                return p
        return len(weather_priority)

    sights_sorted = sorted(sights, key=best_priority)

    # Group sights by their main weather suitability tag
    weather_grouped_sights = defaultdict(list)
    for sight in sights_sorted:
        main_weather = sight.weather_suitability[0] if sight.weather_suitability else "any"
        weather_grouped_sights[main_weather].append(sight)

    # Map weather -> slots with that weather in forecast
    weather_to_slots = defaultdict(list)
    for slot in slots:
        w = weather_forecast.get(slot)
        if w:
            weather_to_slots[w].append(slot)

    # Optimize routes per weather category (excluding 'any' for now)
    optimized_groups = {}
    for weather_cat, group_sights in weather_grouped_sights.items():
        if weather_cat != "any":
            optimized_groups[weather_cat] = optimize_route(city_center, group_sights, mode=mode)

    # Count slots per weather category to distribute 'any' proportionally
    slot_counts = {w: len(weather_to_slots.get(w, [])) for w in weather_priority if w != "any"}
    total_slots = sum(slot_counts.values()) or 1  # avoid zero division

    any_sights = weather_grouped_sights.get("any", [])
    any_count = len(any_sights)

    # Calculate how many 'any' sights go to each weather category proportionally to slot counts
    allocations = {w: int(any_count * (slot_counts.get(w, 0) / total_slots)) for w in slot_counts}

    # Fix leftover due to int truncation
    leftover = any_count - sum(allocations.values())
    if leftover > 0:
        max_w = max(slot_counts, key=slot_counts.get)
        allocations[max_w] += leftover

    # Append allocated 'any' sights to corresponding optimized groups
    idx = 0
    for w, alloc in allocations.items():
        optimized_groups.setdefault(w, [])
        optimized_groups[w].extend(any_sights[idx: idx + alloc])
        idx += alloc

    # Step: Rebalance underpopulated categories
    # Count how many sights each group has
    group_sizes = {w: len(optimized_groups.get(w, [])) for w in weather_priority if w != "any"}

    # Identify empty and largest groups
    empty_groups = [w for w, size in group_sizes.items() if size == 0]
    largest_group = max(group_sizes, key=group_sizes.get)

    for underfilled in empty_groups:
        print(f"⚖️ Rebalancing: '{underfilled}' has no sights, stealing from '{largest_group}'")
        donor_group = optimized_groups[largest_group]

        # Try to steal 1–2 suitable sights
        stolen = []
        for s in donor_group:
            if underfilled in s.weather_suitability:
                stolen.append(s)
            if len(stolen) >= 2:
                break

        # Remove from donor, add to receiver
        for s in stolen:
            donor_group.remove(s)
            optimized_groups.setdefault(underfilled, []).append(s)

        print(f"  ➜ Stolen {len(stolen)} sight(s) for category '{underfilled}'")

    # Now split each optimized group evenly across matching slots
    for weather_cat, ordered_sights in optimized_groups.items():
        matching_slots = weather_to_slots.get(weather_cat, [])
        if not matching_slots:
            matching_slots = slots  # fallback to all slots
        print(f"Weather category '{weather_cat}' matched slots: {matching_slots}")

        '''n = len(ordered_sights)
        k = len(matching_slots)
        chunk_size = math.ceil(n / k)

        for i, slot in enumerate(matching_slots):
            start = i * chunk_size
            end = start + chunk_size
            chunk = ordered_sights[start:end]
            tour_plan[slot].extend(chunk)
            print(f"Assigning {len(chunk)} sights with weather '{weather_cat}' to slot '{slot}'")'''
        for i, sight in enumerate(ordered_sights):
            slot = matching_slots[i % len(matching_slots)]
            tour_plan[slot].append(sight)

    return tour_plan
def plan_tour_notNecessary(sights, weather_forecast, slots=["morning", "afternoon", "evening"]):
    # Map from slot to assigned sights
    schedule = {slot: [] for slot in slots}

    # Group sights by weather priority: sunny > cloudy > rainy > any
    weather_priority = {"sunny": 1, "cloudy": 2, "rainy": 3, "any": 4}

    # Sort sights by their most "restrictive" weather suitability (lowest priority number)
    def min_weather_priority(sight):
        return min(weather_priority.get(cond, 10) for cond in sight.weather_suitability)

    sights = sorted(sights, key=min_weather_priority)

    # Track which sights are assigned
    assigned = set()

    # First pass: assign sights to best matching slot
    for slot in slots:
        slot_weather = weather_forecast.get(slot, "unknown")
        for sight in sights:
            if sight in assigned:
                continue
            # If sight can be visited in this weather
            if slot_weather in sight.weather_suitability or "any" in sight.weather_suitability:
                schedule[slot].append(sight)
                assigned.add(sight)

    # Second pass: assign unassigned sights to any slot with room
    for sight in sights:
        if sight not in assigned:
            for slot in slots:
                schedule[slot].append(sight)
                assigned.add(sight)
                break

    return schedule
