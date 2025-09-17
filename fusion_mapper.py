class FusionMapper:
    """
    Generates a graph visualization of the connection between
    neural features and logical terms.
    """

    def __init__(self, fusion_data):
        """
        Initializes the mapper with fusion data.

        Args:
            fusion_data (dict): A dictionary describing the connections.
                Example:
                {
                    "logical_terms": {
                        "is_dog": { "source_engine": "engine_resnet", "feature_indices": [10, 15, 22] },
                        "is_cat": { "source_engine": "engine_resnet", "feature_indices": [8, 12, 30] }
                    },
                    "neural_engines": {
                        "engine_resnet": { "model": "ResNet-50", "total_features": 2048 }
                    }
                }
        """
        self.fusion_data = fusion_data

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
    # This data is a placeholder representing how logical terms might be
    # derived from the outputs of different neural network engines.
    mock_fusion_data = {
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
    }

    mapper = FusionMapper(mock_fusion_data)
    dot_string = mapper.generate_dot_graph()

    print("--- Generated DOT Graph ---")
    print(dot_string)
    print("\n--------------------------")

    # Save the DOT string to a file
    output_dot_file = "fusion_map.dot"
    with open(output_dot_file, 'w') as f:
        f.write(dot_string)
    
    print(f"Graph saved to {output_dot_file}")
    print("To render this graph, you can use a tool like Graphviz.")
    print(f"Example command: dot -Tpng {output_dot_file} -o fusion_map.png")
