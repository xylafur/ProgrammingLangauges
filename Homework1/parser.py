from lexer import Location, Lexer
import sys

ID = 1       # identifier
LPAR = 2     # (
RPAR = 3     # )
NOT = 4      # !
AND = 5      # /\
OR = 6       # \/
IMPLIES = 7  # =>
IFF = 8      # <=>
COMMA = 9    # ,
INTEGER = 10 # 0-9 integers
NEWLINE = 11 # Used to figure out when to increment the row.
EPSILON = 12 # Used to terminate the lines.

# This parser implements the following grammer:
# props->prop->atomic->ID
# props->prop->compound->

# propositions -> proposition | more-proposition

# more-proposition -> , propositions | epsilon

# proposition -> atomic | compound

# atomic -> 0 | 1 | ID

# compound -> atomic connective proposition | LPAR proposition RPAR | NOT proposition

# connective -> AND | OR | IMPLIES | IFF

def more_proposition(token, token_iter, token_list):
    left = None
    #import pdb;pdb.set_trace()
    if token.tag == COMMA:
        token_iter += 1
        left, token_iter = propositions(token_list[token_iter], token_iter, token_list)
        left.append("COMMA")
        left.append("more-proposition")

    if token.tag == EPSILON and not left:
        return (["EPSILON", "more-proposition"], token_iter)
    else:
        if left:
            return (left, token_iter)
        else:
            return (None, token_iter)

def connective(token, token_iter, token_list):
    if token.tag == AND:
        return (["AND", "connective"], token_iter)
    if token.tag == OR:
        return (["OR", "connective"], token_iter)
    if token.tag == IMPLIES:
        return (["IMPLIES", "connective"], token_iter)
    if token.tag == IFF:
        return (["IFF", "connective"], token_iter)
    else:
        return (None, token_iter)

def atomic(token, token_iter, token_list):
    if token.tag == ID:
        return (["ID","atomic"], token_iter)
    if token.tag == INTEGER:
        return (["INTEGER","atomic"], token_iter)
    else:
        return (None, token_iter)

def compound(token, token_iter, token_list):
    # Do the leftmost rule first.
    left = None
    left_len = None
    middle_len = None
    right_len = None
    atomic_list, left_iter = atomic(token, token_iter, token_list)
    left_iter += 1
    connective_list, left_iter = connective(token_list[left_iter], left_iter, token_list) if atomic_list else (None, token_iter)
    left_iter += 1
    proposition_list, left_iter = proposition(token_list[left_iter], left_iter, token_list) if connective_list else (None, token_iter)

    if proposition_list:
        left = []
        left.extend(proposition_list)
        left.extend(connective_list)
        left.extend(atomic_list)
        left.append("compound")
        left_len = len(left)

    middle = None
    if token.tag == LPAR:
        proposition_list, middle_iter = proposition(token_list[token_iter+1], token_iter+1, token_list)
        if proposition_list:
            middle_iter += 1
            if token_list[middle_iter].tag == RPAR:
                middle = []
                middle.append("RPAR")
                middle.extend(proposition_list)
                middle.append("LPAR")
                middle.append("compound")
                
                
                middle_len = len(middle)
    right = None
    if token.tag == NOT:
        proposition_list, right_iter = proposition(token_list[token_iter+1], token_iter+1, token_list)
        if proposition_list:
            right = []
            right.extend(proposition_list)
            right.append("NOT")
            right.append("compound")
            right_len = len(right)

    # If all three are None, this returns none.
    if left_len >= right_len and left_len >= middle_len:
        return (left, left_iter)
    
    elif right_len >= middle_len:
        return (right, right_iter)
    else:
        return (middle, middle_iter)

def proposition(token, token_iter, token_list):
    left, left_iter = atomic(token, token_iter, token_list)
    left_len = None
    if left:
        left.append("proposition")
        left_len = len(left)

    right, right_iter = compound(token, token_iter, token_list)
    right_len = None
    if right:
        right.append("proposition")
        right_len = len(right)

    if left_len >= right_len:
        return (left, left_iter)
    else:
        return (right, right_iter)

def propositions(token, token_iter, token_list):
    orig_iter = token_iter
    left_len = None
    right_len = None
    left, left_iter = proposition(token, token_iter, token_list)
    if left:
        left.append("propositions")
        left_len = len(left)

    right, right_iter = more_proposition(token, token_iter, token_list)
    if right:
        right.append("propositions")
        right_len = len(right)
    # Neither one resolved, so raise an error for this token.
    if not(left or right):
        print "Syntax Error: " + token.symbol + " Row: " + str(token.row) + " Column: " + str(token.column)
        return (None, token_iter)

    if left_len >= right_len:
        return (left, left_iter)
    else:
        return (right, right_iter)

def parse(tokens):
    parse_error = False
    token_iter = 0
    parse_tree = []
    token_list = tokens
    token_count = len(token_list)
    while token_iter < token_count:
        tree, token_iter = propositions(token_list[token_iter], token_iter, token_list)
        if tree:
            tree.reverse()
            parse_tree.extend(tree)
        else:
            parse_error = True
        token_iter += 1

    # Only print the parse tree if there was no syntax error.
    if not parse_error:
        print(parse_tree)
