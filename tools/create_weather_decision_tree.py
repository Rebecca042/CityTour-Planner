from graphviz import Digraph

def create_weather_decision_tree_viz(output_path="../visualizations/weather_decision_tree"):
    dot = Digraph(comment="Weather Decision Tree")

    # Root node: check precipitation sum
    dot.node('A', 'Precipitation sum > 1.0?')

    # Left branch: Yes (rainy)
    dot.node('B', 'Rainy')
    dot.edge('A', 'B', label='Yes')

    # Right branch: No -> check avg temperature
    dot.node('C', 'Avg Temp > 20°C?')
    dot.edge('A', 'C', label='No')

    # If avg temp > 20
    dot.node('D', 'Sunny')
    dot.edge('C', 'D', label='Yes')

    # Else avg temp <= 20
    dot.node('E', 'Cloudy')
    dot.edge('C', 'E', label='No')

    dot.render(output_path, format='png')
    print(f"Decision tree graph saved to {output_path}.png")

if __name__ == "__main__":
    create_weather_decision_tree_viz()