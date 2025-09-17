
import yaml
import json
import os
from difflib import SequenceMatcher

def print_header(title):
    bar = "="*60
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

class DimensionComparator:
    """
    Compares dimensions discovered by Vetra (offline) with those designed by
    Orien (online/Gemini) and recommends integration actions.
    """

    def __init__(self, vetra_config_path, orien_config_path):
        print_header("Initializing Dimension Comparator")
        self.vetra_dims = self._load_yaml(vetra_config_path)
        self.orien_dims = self._load_json(orien_config_path)
        print("Vetra's and Orien's dimension models have been loaded.")

    def _load_yaml(self, path):
        if not os.path.exists(path):
            print(f"Warning: Vetra's config '{path}' not found. Returning empty dict.")
            return {}
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _load_json(self, path):
        if not os.path.exists(path):
            print(f"Warning: Orien's config '{path}' not found. Returning empty list.")
            return []
        with open(path, 'r') as f:
            # Orien's config is a list of dicts, convert to a dict keyed by id
            return {item['id']: item for item in json.load(f)}

    def _calculate_similarity(self, str1, str2):
        """Calculates a similarity score between two strings."""
        return SequenceMatcher(None, str1, str2).ratio()

    def _calculate_semantic_overlap(self, desc1, desc2):
        """Simulates semantic overlap by checking for common keywords."""
        words1 = set(desc1.lower().replace('.','').split())
        words2 = set(desc2.lower().replace('.','').split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0

    def compare_dimensions(self):
        """
        Compares each of Vetra's dimensions against all of Orien's.
        """
        print_header("Comparing Vetra's discoveries to Orien's master plan")
        report = []

        for vetra_id, vetra_data in self.vetra_dims.items():
            best_match = {"orien_id": None, "score": 0.0}
            
            for orien_id, orien_data in self.orien_dims.items():
                name_similarity = self._calculate_similarity(vetra_id, orien_id)
                desc_similarity = self._calculate_semantic_overlap(
                    vetra_data.get('description', ''), orien_data.get('description', '')
                )
                # Combine scores, giving more weight to description
                combined_score = (name_similarity * 0.4) + (desc_similarity * 0.6)

                if combined_score > best_match["score"]:
                    best_match = {"orien_id": orien_id, "score": combined_score}

            # Generate recommendation based on the best match score
            rec = self._generate_recommendation(vetra_id, best_match)
            report.append(rec)
            print(f"- Compared Vetra's '{vetra_id}'. Best match in Orien's plan: '{rec['best_match_orien']}' (Score: {rec['match_score']:.2f}). Action: {rec['recommended_action']}")

        return report

    def _generate_recommendation(self, vetra_id, match_info):
        """Generates a recommendation based on the similarity score."""
        score = match_info['score']
        action = ""
        if score > 0.6:
            action = "merge_and_rename"
        elif score > 0.3:
            action = "flag_for_review"
        else:
            action = "keep_as_new_discovery"
        
        return {
            "vetra_dimension": vetra_id,
            "best_match_orien": match_info['orien_id'],
            "match_score": score,
            "recommended_action": action
        }

    def integrate(self, report):
        """
        Integrates the dimensions based on the comparison report and saves
        the new master configuration.
        """
        print_header("Integrating Dimensions")
        final_dims = self.orien_dims.copy()

        for item in report:
            action = item['recommended_action']
            vetra_id = item['vetra_dimension']

            if action == "keep_as_new_discovery":
                print(f"  -> Integrating '{vetra_id}' as a new dimension.")
                new_dim_data = self.vetra_dims[vetra_id]
                final_dims[f"vetra_{vetra_id}"] = {
                    'id': f"vetra_{vetra_id}",
                    'name_ja': f"[Vetra発見] {vetra_id}",
                    'description': new_dim_data.get('description', 'N/A'),
                    'algorithm_idea': new_dim_data.get('method', 'N/A'),
                    'layer': 'vetra_discovered'
                }
            elif action == "merge_and_rename":
                 print(f"  -> Merging '{vetra_id}' into Orien's '{item['best_match_orien']}'. No new dimension added.")
            else: # flag_for_review
                print(f"  -> Flagging '{vetra_id}' for manual review. Not integrated automatically.")

        # Convert back to list for JSON format
        final_dims_list = list(final_dims.values())
        output_path = "vector_dimensions_custom_ai_integrated.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_dims_list, f, ensure_ascii=False, indent=2)
        
        print(f"\nIntegration complete. Final model saved to '{output_path}'.")
        return final_dims_list

if __name__ == '__main__':
    VETRA_PATH = "vector_dimensions_mobile_optimized.yaml"
    ORIEN_PATH = "vector_dimensions_custom_ai.json"

    if not os.path.exists(VETRA_PATH):
        print(f"ERROR: Vetra's optimized config '{VETRA_PATH}' not found.")
        print("Please run the offline evolution cycle first.")
    else:
        comparator = DimensionComparator(VETRA_PATH, ORIEN_PATH)
        comparison_report = comparator.compare_dimensions()
        final_model = comparator.integrate(comparison_report)
        print(f"\nFinal integrated model contains {len(final_model)} dimensions.")
