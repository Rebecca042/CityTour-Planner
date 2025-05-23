# planner/display.py
from __future__ import annotations
from typing import Dict, List, Sequence, Any

# ---------- CLI rendering ---------- #
def cli_tour_header(overall_weather: str, forecast: dict[str, str]) -> None:
    print(f"\nToday's overall weather: {overall_weather}")
    print("Forecast per slot:")
    for slot, w in forecast.items():
        print(f"  {slot.title():<9}: {w}")

def cli_render_slot(slot: str, sights: Sequence[Any], postcard: str | None) -> None:
    print(f"\n{slot.title()}:")
    for i, s in enumerate(sights, 1):
        print(f"  {i}. {s.name} ({s.category})")
    if postcard:
        print(f"  📝 Postcard → {postcard}")

def show_cli_plan(tour_plan: Dict[str, List[Any]],
                  forecast: Dict[str, str],
                  postcards: Dict[str, str]) -> None:
    cli_tour_header(_derive_overall(forecast), forecast)
    for slot, sights in tour_plan.items():
        cli_render_slot(slot, sights, postcards.get(slot))


# ---------- Streamlit rendering ---------- #
def st_render_plan(st,                           # pass the `streamlit` module
                   tour_plan: Dict[str, List[Any]],
                   forecast: Dict[str, str],
                   postcards: Dict[str, str],
                   fmap=None) -> None:
    st.info(f"Forecasted overall weather: **{_derive_overall(forecast)}**")
    st.write("Forecast per slot:", forecast)

    if fmap is not None:
        from streamlit_folium import st_folium
        st_folium(fmap, width=700, height=500)

    for slot, sights in tour_plan.items():
        st.markdown(f"### {slot.capitalize()} ({forecast.get(slot, 'n/a')})")
        for s in sights:
            st.markdown(f"- **{s.name}** ({s.category})")
        if msg := postcards.get(slot):
            st.markdown(f"> 📝 _Postcard_: {msg}")


# ---------- helpers ---------- #
def _derive_overall(forecast: Dict[str, str]) -> str:
    # crude heuristic: majority vote
    from collections import Counter
    counts = Counter(forecast.values())
    return counts.most_common(1)[0][0] if counts else "unknown"
