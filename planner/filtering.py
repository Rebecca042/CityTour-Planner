# planner/filtering.py

import math
from typing import List, Set
from .sights import Sight #p

def is_valid_category(cat: str) -> bool:
    """
    Check if a category string is valid (not None, unknown, NaN).
    """
    if cat is None:
        return False
    cat_str = str(cat).strip().lower()
    if cat_str in ["unknown", "nan"]:
        return False
    if isinstance(cat, float) and math.isnan(cat):
        return False
    return True

def get_available_categories(sights: List[Sight]) -> List[str]:
    """
    Return sorted list of unique, valid categories from sights.
    """
    '''categories: Set[str] = set()
    for s in sights:
        if is_valid_category(s.category):
            categories.add(str(s.category).strip())'''
    categories = sorted(set(
        str(s.category).strip()
        for s in sights
        if s.category is not None
        and str(s.category).strip().lower() not in ["unknown", "nan"]
        and not (isinstance(s.category, float) and math.isnan(s.category))
    ))
    return sorted(categories)

def filter_sights_by_category(sights: List[Sight], selected_categories: List[str]) -> List[Sight]:
    """
    Filter the list of sights by the given categories.
    """

    filtered_sights = [
        s for s in sights
        if s.category is not None
        and str(s.category).strip().lower() not in ["unknown", "nan"]
        and not (isinstance(s.category, float) and math.isnan(s.category))
        and s.category in selected_categories
    ]
    '''filtered = [
        s for s in sights
        if is_valid_category(s.category)
        and str(s.category).strip() in selected_categories
    ]'''
    return filtered_sights
