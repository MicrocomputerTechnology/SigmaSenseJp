import json
import os
from collections import OrderedDict

class DimensionLoader:
    def __init__(self, selia_path=None, lyra_path=None):
        """
        Initializes the DimensionLoader.
        Paths must be provided for the loader to have dimensions.
        """
        default_selia_path = "vector_dimensions_custom_ai.json"
        default_lyra_path = "vector_dimensions_custom_ai_lyra.json"

        self.selia_path = selia_path if selia_path is not None else default_selia_path
        self.lyra_path = lyra_path if lyra_path is not None else default_lyra_path

        self.load_dimensions()

    def load_dimensions(self):
        """Loads or reloads dimensions from the specified file paths."""
        self._selia_dims = []
        self._lyra_dims = []
        try:
            if self.selia_path and os.path.exists(self.selia_path):
                 with open(self.selia_path, 'r', encoding='utf-8') as f:
                    self._selia_dims = json.load(f, object_pairs_hook=OrderedDict)
            else:
                 print(f"Warning: Selia dimension file not found: {self.selia_path}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load or parse Selia dimensions from {self.selia_path}. Error: {e}")

        try:
            if self.lyra_path and os.path.exists(self.lyra_path):
                with open(self.lyra_path, 'r', encoding='utf-8') as f:
                    self._lyra_dims = json.load(f, object_pairs_hook=OrderedDict)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load or parse Lyra dimensions from {self.lyra_path}. Error: {e}")
        
        for dim in self._lyra_dims:
            dim['layer'] = 'lyra'

        self._dimensions = self._selia_dims + self._lyra_dims
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
