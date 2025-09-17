class LogicalExpression:
    """Base class for logical expressions."""
    def evaluate(self, context):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def to_logical_form(self):
        """Returns the string representation of the logical formula."""
        return str(self)

    def get_variables(self):
        """Returns a set of variable names used in the expression."""
        raise NotImplementedError

class Variable(LogicalExpression):
    """Represents a variable (semantic axis) in a logical expression."""
    def __init__(self, name):
        self.name = name

    def evaluate(self, context):
        """Evaluates the variable against a context."""
        return context.get(self.name, False)

    def __str__(self):
        return self.name

    def get_variables(self):
        return {self.name}

class And(LogicalExpression):
    """Represents a logical AND operation."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, context):
        """Evaluates the AND expression."""
        return self.left.evaluate(context) and self.right.evaluate(context)

    def __str__(self):
        return f"({self.left} AND {self.right})"

    def get_variables(self):
        return self.left.get_variables().union(self.right.get_variables())

class Or(LogicalExpression):
    """Represents a logical OR operation."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, context):
        """Evaluates the OR expression."""
        return self.left.evaluate(context) or self.right.evaluate(context)

    def __str__(self):
        return f"({self.left} OR {self.right})"

    def get_variables(self):
        return self.left.get_variables().union(self.right.get_variables())

class Not(LogicalExpression):
    """Represents a logical NOT operation."""
    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, context):
        """Evaluates the NOT expression."""
        return not self.operand.evaluate(context)

    def __str__(self):
        return f"NOT({self.operand})"

    def get_variables(self):
        return self.operand.get_variables()

def parse_expression(expression_str):
    """
    Parses a string into a logical expression object.
    (This is a placeholder for a more sophisticated parser)
    """
    # In a real implementation, this would involve a proper parsing library
    # like pyparsing or PLY, or a recursive descent parser.
    # For now, we'll just return a dummy example.
    if "AND" in expression_str:
        parts = expression_str.strip("()" ).split(" AND ", 1)
        return And(parse_expression(parts[0]), parse_expression(parts[1]))
    elif "OR" in expression_str:
        parts = expression_str.strip("()" ).split(" OR ", 1)
        return Or(parse_expression(parts[0]), parse_expression(parts[1]))
    elif expression_str.startswith("NOT"):
        var_str = expression_str[expression_str.find("(")+1:expression_str.rfind(")")]
        return Not(parse_expression(var_str))
    else:
        return Variable(expression_str.strip())

if __name__ == '__main__':
    # Example Usage
    context = {
        "is_animal": True,
        "has_fur": True,
        "is_dog": False,
        "has_wings": False
    }

    # (is_animal AND has_fur)
    expr1 = And(Variable("is_animal"), Variable("has_fur"))
    print(f"Expression: {expr1}")
    print(f"Evaluation: {expr1.evaluate(context)}") # Expected: True
    print(f"Variables: {expr1.get_variables()}")

    # (is_dog OR has_wings)
    expr2 = Or(Variable("is_dog"), Variable("has_wings"))
    print(f"Expression: {expr2}")
    print(f"Evaluation: {expr2.evaluate(context)}") # Expected: False
    print(f"Variables: {expr2.get_variables()}")

    # NOT(is_dog)
    expr3 = Not(Variable("is_dog"))
    print(f"Expression: {expr3}")
    print(f"Evaluation: {expr3.evaluate(context)}") # Expected: True
    print(f"Variables: {expr3.get_variables()}")

    # A more complex expression: ( (is_animal AND has_fur) AND NOT(is_dog) )
    expr4 = And(expr1, expr3)
    print(f"Expression: {expr4}")
    print(f"Evaluation: {expr4.evaluate(context)}") # Expected: True
    print(f"Variables: {expr4.get_variables()}")

    # Placeholder parser example
    parsed_expr = parse_expression("((is_animal AND has_fur) OR NOT(is_dog))")
    # A proper parser is needed for complex nested expressions.
    # The current dummy parser is very limited.
    # For this example, let's manually construct the complex expression.
    manual_expr = Or(And(Variable("is_animal"), Variable("has_fur")), Not(Variable("is_dog")))
    print(f"Complex Expression: {manual_expr}")
    print(f"Complex Eval: {manual_expr.evaluate(context)}")
    print(f"Complex Vars: {manual_expr.get_variables()}")
    assert manual_expr.get_variables() == {"is_animal", "has_fur", "is_dog"}
    print("\nTests passed!")
