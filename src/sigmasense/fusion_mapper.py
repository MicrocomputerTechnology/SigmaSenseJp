import os
from src.sigmasense.config_loader import ConfigLoader

from typing import Optional

class FusionMapper:
    """
    Maps the relationship between logical terms and meaning vectors.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initializes the mapper with fusion data loaded from a config object.

        Args:
            config (dict): A dictionary containing the configuration.
        """
        if config is None:
            config = {}

        self.fusion_data = config.get("fusion_data", {
            "logical_terms": {
                "is_dog": {
                    "source_engine": "engine_resnet",
                    "feature_indices": [100, 150, 201]
                },
                "is_cat": {
                    "source_engine": "engine_resnet",
                    "feature_indices": [102, 152, 203]
                },
                "has_wheels": {
                    "source_engine": "engine_mobilenet",
                    "feature_indices": [50, 55]
                },
                "is_vehicle": {
                    "source_engine": "engine_mobilenet",
                    "feature_indices": [48, 50, 55, 60]
                }
            },
            "neural_engines": {
                "engine_resnet": {
                    "model": "ResNet-50",
                    "total_features": 2048
                },
                "engine_mobilenet": {
                    "model": "MobileNetV1",
                    "total_features": 1024
                }
            }
        })

    def generate_dot_graph(self):
        """
        Generates a DOT language string for graph visualization.

        Returns:
            str: A string in DOT format.
        """
        dot_lines = ["digraph FusionMap {", "    rankdir=LR;"]
        
        # Define nodes for neural engines
        dot_lines.append("    subgraph cluster_engines {")
        dot_lines.append("        label=\"Neural Engines\";")
        dot_lines.append("        node [shape=box, style=filled, color=lightblue];")
        for engine_id, engine_info in self.fusion_data.get("neural_engines", {}).items():
            dot_lines.append(f"        {engine_id} [label=\"{engine_info.get('model', engine_id)}\"];")
        dot_lines.append("    }")

        # Define nodes for logical terms
        dot_lines.append("    subgraph cluster_logical {")
        dot_lines.append("        label=\"Logical Terms\";")
        dot_lines.append("        node [shape=ellipse, style=filled, color=lightgreen];")
        for term_id in self.fusion_data.get("logical_terms", {}).keys():
            dot_lines.append(f"        {term_id};")
        dot_lines.append("    }")

        # Define edges (connections)
        for term_id, term_info in self.fusion_data.get("logical_terms", {}).items():
            engine_id = term_info.get("source_engine")
            if engine_id:
                feature_indices = term_info.get("feature_indices", [])
                label = f"features {str(feature_indices)}"
                dot_lines.append(f"    {engine_id} -> {term_id} [label=\"{label}\"];")

        dot_lines.append("}")
        return "\n".join(dot_lines)

if __name__ == '__main__':
    # Example Usage:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    config_loader = ConfigLoader(config_dir)
    fusion_config = config_loader.get_config("fusion_mapper_profile")

    mapper = FusionMapper(config=fusion_config)
    dot_string = mapper.generate_dot_graph()

    print("--- Generated DOT Graph ---")
    print(dot_string)
    print("--------------------------")

    # Save the DOT string to a file
    output_dot_file = "fusion_map.dot"
    with open(output_dot_file, 'w') as f:
        f.write(dot_string)
    
    print(f"Graph saved to {output_dot_file}")
    print("To render this graph, you can use a tool like Graphviz.")
    print(f"Example command: dot -Tpng {output_dot_file} -o fusion_map.png")
