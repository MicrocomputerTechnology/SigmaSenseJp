import json

class DimensionEditor:
    """
    A class to load, edit, and save semantic dimension definition files.
    """

    def __init__(self, file_path):
        """
        Initializes the editor by loading a dimension definition file.

        Args:
            file_path (str): The path to the JSON dimension file.
        """
        self.file_path = file_path
        self.dimensions = []
        self.dimensions_map = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.dimensions = json.load(f)
            self._build_map()
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load or parse {file_path}. Starting with an empty dimension list. Error: {e}")

    def _build_map(self):
        """Builds a dictionary for quick access to dimensions by ID."""
        self.dimensions_map = {dim['id']: dim for dim in self.dimensions}

    def get_dimension(self, dim_id):
        """
        Retrieves a dimension by its ID.

        Args:
            dim_id (str): The ID of the dimension to retrieve.

        Returns:
            dict: The dimension object, or None if not found.
        """
        return self.dimensions_map.get(dim_id)

    def add_dimension(self, new_dim):
        """
        Adds a new dimension.

        Args:
            new_dim (dict): The new dimension object to add. It must contain an 'id'.

        Returns:
            bool: True if addition was successful, False otherwise (e.g., duplicate ID).
        """
        if 'id' not in new_dim:
            print("Error: New dimension must have an 'id'.")
            return False
        if new_dim['id'] in self.dimensions_map:
            print(f"Error: Dimension with id '{new_dim['id']}' already exists.")
            return False
        
        self.dimensions.append(new_dim)
        self.dimensions_map[new_dim['id']] = new_dim
        return True

    def update_dimension(self, dim_id, updated_fields):
        """
        Updates an existing dimension with new fields.

        Args:
            dim_id (str): The ID of the dimension to update.
            updated_fields (dict): A dictionary of fields to add or update.
                                   This can include a 'logical_rule'.

        Returns:
            bool: True if update was successful, False if the dimension was not found.
        """
        dimension = self.get_dimension(dim_id)
        if not dimension:
            print(f"Error: Dimension with id '{dim_id}' not found.")
            return False
        
        dimension.update(updated_fields)
        return True

    def remove_dimension(self, dim_id):
        """
        Removes a dimension by its ID.

        Args:
            dim_id (str): The ID of the dimension to remove.

        Returns:
            bool: True if removal was successful, False if the dimension was not found.
        """
        if dim_id not in self.dimensions_map:
            print(f"Error: Dimension with id '{dim_id}' not found.")
            return False
            
        self.dimensions = [dim for dim in self.dimensions if dim['id'] != dim_id]
        del self.dimensions_map[dim_id]
        return True

    def save(self, new_file_path=None):
        """
        Saves the current dimensions to a file.

        Args:
            new_file_path (str, optional): If provided, saves to a new file. 
                                           Otherwise, overwrites the original file.
        """
        save_path = new_file_path if new_file_path else self.file_path
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.dimensions, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved dimensions to {save_path}")
        except IOError as e:
            print(f"Error: Could not save file to {save_path}. Error: {e}")

if __name__ == '__main__':
    # Example usage:
    # This assumes 'vector_dimensions_custom_ai.json' exists and is readable.
    try:
        editor = DimensionEditor('vector_dimensions_custom_ai.json')

        # 1. Get a dimension
        dim_id = 'main_color_saturation'
        dim = editor.get_dimension(dim_id)
        if dim:
            print(f"--- Got Dimension: {dim_id} ---")
            print(dim)

        # 2. Update a dimension to add a logical rule
        print(f"\n--- Updating Dimension: {dim_id} ---")
        update_success = editor.update_dimension(dim_id, {
            "logical_rule": "(is_colorful AND NOT is_monochrome)",
            "author": "DimensionEditor"
        })
        if update_success:
            print("Update successful.")
            print(editor.get_dimension(dim_id))

        # 3. Add a new dimension
        print("\n--- Adding New Dimension ---")
        new_dim_obj = {
            "id": "is_face",
            "name_ja": "顔である",
            "description": "画像に顔が含まれているか。",
            "algorithm_idea": "Haar CascadeやDNNベースの顔検出器を使用する。",
            "layer": "semantic",
            "logical_rule": "(has_eyes AND has_nose AND has_mouth)"
        }
        add_success = editor.add_dimension(new_dim_obj)
        if add_success:
            print("New dimension added successfully.")
            print(editor.get_dimension("is_face"))

        # 4. Remove a dimension
        print("\n--- Removing Dimension ---")
        remove_id = 'global_luminosity'
        remove_success = editor.remove_dimension(remove_id)
        if remove_success:
            print(f"Dimension '{remove_id}' removed successfully.")
            print(f"Trying to get '{remove_id}' again: {editor.get_dimension(remove_id)}")


        # 5. Save the changes to a new file
        print("\n--- Saving Changes ---")
        editor.save('vector_dimensions_edited.json')
    except FileNotFoundError:
        print("\nSkipping example usage because vector_dimensions_custom_ai.json was not found.")
