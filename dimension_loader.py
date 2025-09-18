import json
import os
import yaml
from collections import OrderedDict

class DimensionLoader:
    def __init__(self, paths=None):
        """
        Initializes the DimensionLoader by loading dimensions from a list of file paths.
        """
        if paths is None:
            # If no paths are provided, use a default list of known dimension files.
            self.paths = [
                "vector_dimensions_custom_ai.json",
                "vector_dimensions_custom_ai_lyra.json",
                "vector_dimensions_custom_ai_terrier.json",
                "vector_dimensions_mobile.yaml",
                "vector_dimensions_mobile_optimized.yaml",
            ]
        else:
            self.paths = paths

        self.load_dimensions()

    def load_dimensions(self):
        """Loads or reloads dimensions from the specified file paths."""
        self._dimensions = []
        for path in self.paths:
            if not os.path.exists(path):
                print(f"Warning: Dimension file not found: {path}")
                continue
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    if path.endswith('.json'):
                        dims = json.load(f, object_pairs_hook=OrderedDict)
                    elif path.endswith(('.yaml', '.yml')):
                        dims = yaml.safe_load(f)
                    else:
                        print(f"Warning: Skipping unsupported file type: {path}")
                        continue
                
                if not isinstance(dims, list):
                    print(f"Warning: Dimension file {path} does not contain a list of dimensions. Skipping.")
                    continue

                # For backward compatibility, add 'layer' to lyra dimensions
                if 'lyra' in os.path.basename(path):
                    for dim in dims:
                        if 'layer' not in dim:
                            dim['layer'] = 'lyra'

                self._dimensions.extend(dims)
            except (IOError, json.JSONDecodeError, yaml.YAMLError) as e:
                print(f"Warning: Could not load or parse dimensions from {path}. Error: {e}")

        self._id_map = OrderedDict((dim['id'], i) for i, dim in enumerate(self._dimensions))
        self._layer_map = self._create_layer_map()
        
        self._axis_to_layer_map = {
            '形': 'shape', '彩': 'color', '数': 'grouping',
            '座': 'spatial', '感': 'lyra'
        }

    def get_dimensions(self):
        return self._dimensions

    def get_dimension_by_id(self, dim_id):
        index = self._id_map.get(dim_id)
        if index is not None:
            return self._dimensions[index]
        return None

    def get_index(self, dim_id):
        return self._id_map.get(dim_id)

    def get_id(self, index):
        if 0 <= index < len(self._dimensions):
            return self._dimensions[index]['id']
        return None

    @property
    def vector_size(self):
        return len(self._dimensions)

    def get_layer_indices(self, layer_name):
        return self._layer_map.get(layer_name, [])

    def get_indices_for_axis(self, axis_id):
        layer_name = self._axis_to_layer_map.get(axis_id)
        if layer_name:
            if axis_id == '座':
                return self.get_layer_indices(layer_name) + self.get_layer_indices('context')
            return self.get_layer_indices(layer_name)
        return []

    def _create_layer_map(self):
        layer_map = OrderedDict()
        for i, dim in enumerate(self._dimensions):
            layer = dim.get('layer')
            if layer:
                if layer not in layer_map:
                    layer_map[layer] = []
                layer_map[layer].append(i)
        return layer_map