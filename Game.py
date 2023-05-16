def game(m1, m2):
    if m1[0] == 'R' and m2[0] == 'S': # if player1 send Rock and player2 send Scissors
        return True                   # the function return True
    elif m1 == 'R' and m2 == 'P':
        return False
    if m1 == 'P' and m2 == 'R':
        return True
    if m1 == 'P' and m2 == 'S':
        return False
    if m1 == 'S' and m2 == 'R':
        return False
    if m1 == 'S' and m2 == 'P':
        return True
    else:                              # if both players enters the same move
        return None


