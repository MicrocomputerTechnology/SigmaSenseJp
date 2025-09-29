# Handles specialized vocabularies like mathematics (SymPy) and physics (SciPy).
import sympy
from scipy import constants as sp_constants
from astropy import constants as ap_constants
from .database_handler import DatabaseHandler

class SpecializedVocabularyService:
    """Provides access to specialized vocabularies from scientific libraries and custom databases."""

    def __init__(self, 
                 python_db_path: str = "data/python_vocabulary.sqlite3",
                 philosophy_db_path: str = "data/philosophy_vocabulary.sqlite3"):
        """Initializes all specialized vocabulary services."""
        self.python_vocab_handler = DatabaseHandler(python_db_path)
        self.philosophy_vocab_handler = DatabaseHandler(philosophy_db_path)

    def get_math_definition(self, symbol_string: str):
        """
        Uses SymPy to get information about a mathematical symbol or expression.
        """
        try:
            expr = sympy.sympify(symbol_string, locals=sympy.__dict__)
            eval_expr = expr.evalf()
            return {
                "symbol": str(expr),
                "value": str(eval_expr),
                "is_constant": expr.is_constant(),
                "is_number": expr.is_number,
            }
        except (sympy.SympifyError, AttributeError) as e:
            return {"error": f"Could not process symbol '{symbol_string}': {e}"}

    def get_physics_constant(self, constant_name: str):
        """
        Looks up a physical constant using SciPy or Astropy.
        """
        if constant_name in sp_constants.physical_constants:
            val, unit, uncertainty = sp_constants.physical_constants[constant_name]
            return {
                "name": constant_name,
                "value": val,
                "unit": unit,
                "uncertainty": uncertainty,
                "source": "SciPy"
            }
        
        if hasattr(ap_constants, constant_name):
            const = getattr(ap_constants, constant_name)
            return {
                "name": const.name,
                "value": const.value,
                "unit": str(const.unit),
                "uncertainty": const.uncertainty,
                "source": "Astropy"
            }

        return {"error": f"Constant '{constant_name}' not found in SciPy or Astropy."}

    def lookup_python_term(self, term: str) -> list[tuple]:
        """Looks up a Python vocabulary term in its database."""
        return self.python_vocab_handler.lookup_word(term, table_name="terms", key_column="term", value_column="description")

    def lookup_philosophy_term(self, term: str) -> list[tuple]:
        """Looks up a philosophy vocabulary term in its database."""
        return self.philosophy_vocab_handler.lookup_word(term, table_name="terms", key_column="term", value_column="description")

    def close(self):
        """Closes all database connections."""
        self.python_vocab_handler.close()
        self.philosophy_vocab_handler.close()

# Example usage:
if __name__ == '__main__':
    service = SpecializedVocabularyService()

    print("--- SymPy Mathematics ---")
    pi_def = service.get_math_definition("pi")
    print(f"Definition of 'pi': {pi_def}")

    print("\n--- SciPy/Astropy Physics Constants ---")
    c_def = service.get_physics_constant("speed of light in vacuum")
    print(f"Definition of 'speed of light in vacuum': {c_def}")

    print("\n--- Python Vocabulary DB ---")
    py_term = "list comprehension"
    py_def = service.lookup_python_term(py_term)
    print(f"Lookup of '{py_term}': {py_def}")

    print("\n--- Philosophy Vocabulary DB ---")
    ph_term = "epistemology"
    ph_def = service.lookup_philosophy_term(ph_term)
    print(f"Lookup of '{ph_term}': {ph_def}")

    service.close()
