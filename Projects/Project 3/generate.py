import sys

from crossword import *
import copy 

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        # Make a copy of the domains
        domain_copy = copy.deepcopy(self.domains)
        # Iterate through variables in the domain
        for variable in domain_copy:
            # Get the length of the variable
            length = variable.length
            # Iterate through words in the domain 
            for word in domain_copy[variable]:
                # If the length of the word is not equal to the length of the variable, remove the word from the domain
                if len(word) != length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
            
        # Initializing revision
        revision = False
        # If the variables overlap, check if the letters are the same
        if self.crossword.overlaps[x, y]:
        # Iterate through letters in x and y domains. If the letters are not the same, remove the word from the domain
            for word_x in self.domains[x]:
                for word_y in self.domains[y]:
                    if word_x[self.crossword.overlaps[x, y][0]] != word_y[self.crossword.overlaps[x, y][1]]:
                        self.domains[x].remove(word_x)
                        revision = True
            return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initializing arcs
        if arcs == None:
            arcs = []
            for variable1 in self.domains:
                for variable2 in self.crossword.neighbors(variable1):
                    if self.crossword.overlaps[variable1, variable2] is not None:
                        arcs.append((variable1, variable2))
        # Iterating over all arcs
        for arc in arcs:
            x,y = arcs.pop(0)
            # If the domain is empty, return False
            if len(self.domains[x]) == 0:
                return False
            # If the domain is not empty, iterate over all neighbors of the variable
            for neighbour in self.crossword.neighbors(x):
                # If the neighbor is not y, append the neighbor to the arcs
                if neighbour != y:
                    arcs.append((neighbour, x))
        return True
    

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Iterate over all variables
        for variable in self.domains:
            # If the variable is not in the assignment, return False
            if variable not in assignment:
                return False
            # If the variable is in the assignment, but the assignment is empty, return False
            if assignment[variable] not in self.domains[variable]:
                    return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all values are distinct
        words = [*assignment.values()]
        if len(words) != len(set(words)):
            return False
        # Iterate over variables
        for variable in assignment:
            # Check if the length of the word is correct
            if variable.length != len(assignment[variable]):
                return False
        # Check if there are any conflicts between neighbouring variables
        for variable in assignment:
            for neighbour in self.crossword.neighbors(variable):
                if neighbour in assignment:
                    x, y = self.crossword.overlaps[variable, neighbour]
                    if assignment[variable][x] != assignment[neighbour][y]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Initializing dictionary
        values = {}
        # Iterate over all words in the domain of the variable
        for word in self.domains[var]:
            # Initializing counter
            counter = 0
            # Iterate over all neighbors of the variable
            for neighbor in self.crossword.neighbors(var):
                # If the neighbor is not assigned, check if the word is in the domain of the neighbor
                if neighbor not in assignment:
                    if word in self.domains[neighbor]:
                        counter += 1
            # Add the word and the counter to the dictionary
            values[word] = counter
        # Sort the dictionary by the counter
        sorted_values = sorted(values.items(), key=lambda x: x[1])
        # Return the sorted list of words
        return [word[0] for word in sorted_values]


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Initializing dictionary
        values = {}
        # Iterate over all variables
        for variable in self.domains:
            # If the variable is not assigned, add it to the dictionary
            if variable not in assignment:
                values[variable] = len(self.domains[variable])
        # Sort the dictionary by the number of remaining values in its domain
        sorted_values = sorted(values.items(), key=lambda x: x[1])
        # Return the variable with the minimum number of remaining values in its domain
        return sorted_values[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
            
        # If the assignment is complete, return the assignment
        if self.assignment_complete(assignment):
            return assignment
        # Select an unassigned variable
        variable = self.select_unassigned_variable(assignment)
        # Iterate over all words in the domain of the variable
        for word in self.domains[variable]:
            # Add the word to the assignment
            assignment[variable] = word
            # If the assignment is consistent, continue
            if self.consistent(assignment):
                    # Recursive call to backtrack
                    result = self.backtrack(assignment)
                    # If the result is not None, return the result
                    if result is not None:
                        return result
                # Remove the word from the assignment
            assignment.pop(variable)
            # Return None
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()