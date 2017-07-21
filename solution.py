assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_multiples(values, multiples):
    """Eliminate values using the naked multiples strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked multiples eliminated from peers.
    """
    for unit in unit_list:
        multiple_digits = [values[box] for box in unit if len(values[box]) == multiples]
        multiple_digits = set([digit for digit in multiple_digits if multiple_digits.count(digit) == multiples])
        for multiple_digit in multiple_digits:
            for box in unit:
                if values[box] != multiple_digit:
                    for digit in multiple_digit:
                        values = assign_value(values, box, values[box].replace(digit, ''))
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    return naked_multiples(values, 2)

def naked_triplets(values):
    """Eliminate values using the naked triplets strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked triplets eliminated from peers.
    """
    return naked_multiples(values, 3)

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

def merge(A, B):
    "Join elements of zipping elements of A with elements of B."
    return [a + b for (a, b) in zip(A, B)]

def chunk(A, n):
    "Split of elements in A into chunks of size n"
    return [A[i : i + n] for i in range(0, len(A), n)]

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_triples = chunk(rows, 3)
col_triples = chunk(cols, 3)

row_units = [cross(row, cols) for row in rows]
col_units = [cross(rows, col) for col in cols]
square_units = [cross(row_triple, col_triple) for row_triple in row_triples for col_triple in col_triples]
diag_units = [merge(rows, cols), merge(rows, cols[::-1])]

unit_list = row_units + col_units + square_units + diag_units

units = dict((box, [unit for unit in unit_list if box in unit]) for box in boxes)
peers = dict((box, set(sum(units[box], [])) - set([box])) for box in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict([(box, '123456789' if char == '.' else char)
            for (box, char) in zip(boxes, grid)])

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if values is False:
        print('We could not display your board. Solution was not found.')
        return
    width = 1 + max(len(values[box]) for box in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in rows:
        print(''.join(values[row + col].center(width) +
                ('|' if col in '36' else '') for col in cols))
        if row in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for box in solved_boxes(values):
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(values[box], ''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unit_list:
        for digit in '123456789':
            box = [box for box in unit if digit in values[box]]
            if len(box) == 1:
                values = assign_value(values, box[0], digit)
    return values

def invalid_boxes(values):
    "Boxes with invalid digit values(size 0)."
    return [box for (box, digit) in values.items() if len(digit) == 0]

def solved_boxes(values):
    "Boxes which are already solved(size 1)"
    return [box for (box, digit) in values.items() if len(digit) == 1]

def unsolved_boxes(values):
    "Boxes which are not yet solved(size greater than 1)."
    return [box for (box, digit) in values.items() if len(digit) > 1]

def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice(), naked_twins() and naked_triplets(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    unsolved_before = unsolved_boxes(values)
    values = eliminate(values)
    values = only_choice(values)
    values = naked_twins(values)
    values = naked_triplets(values)
    unsolved_after = unsolved_boxes(values)
    if len(invalid_boxes(values)) != 0:
        return False
    if len(unsolved_before) == len(unsolved_after):
        return values
    return reduce_puzzle(values)

def search(values):
    "Using depth-first search and propagation, try all possible values."
    values = reduce_puzzle(values)
    if values is False:
        return False
    unsolved = unsolved_boxes(values)
    if len(unsolved) == 0:
        return values
    unsolved = sorted(unsolved, key = lambda box: len(values[box]))
    box = unsolved[0]
    for digit in values[box]:
        guessed_values = assign_value(values.copy(), box, digit)
        found_values = search(guessed_values)
        if found_values is not False:
            return found_values
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
