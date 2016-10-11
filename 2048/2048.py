# _*_ coding: utf-8 _*_

import curses
import os
from random import randrange, choice
from collections import defaultdict
try:
    from cPickle import pickle
except ImportError:
    import pickle

letter_codes = [ord(ch) for ch in 'WSADBRQwsadbrq123']
actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'LAST', 'RESTART', 'EXIT']
actions_dict = dict(zip(letter_codes, actions * 2 + ['EASY', 'NORMAL', 'HARD']))
# zip: return a list of tuple  #


def get_user_action(keyboard):
    char = 'N'
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]


def load_level(screen):
    screen.clear()
    info_string1 = 'Please type the number to choose the difficulty of the game:'
    info_string2 = '1 - EASY(1024)    2 - NORMAL(2048)     3 - HARD(4096)'
    screen.addstr(info_string1 + '\n' + info_string2)
    level = 'N'
    while level not in ('EASY', 'NORMAL', 'HARD'):
        level = get_user_action(screen)
    # screen.clear()
    return choice


def transpose(field):
    return [list(row) for row in zip(*field)]


def invert(field):
    return [row[::-1] for row in field]


class GameField(object):
    filepath = os.path.join(os.path.dirname(__file__), 'highest_score.dat')
    win_scores = {'EASY': 1024, 'NORMAL': 2048, 'HARD': 4096}

    def __init__(self, height=4, width=4, level='MEDIUM'):
        self.height = height
        self.width = width
        self.field = None
        self.last_field = None
        self.level = level
        self.win_value = None
        self.score = None
        self.high_score = {'EASY': 0, 'NORMAL': 0, 'HARD': 0}
        if os.path.exists(self.filepath):
            with open(self.filepath, 'rb') as f:
                # assert isinstance(pickle.load(f), int), 'load the highest score failed'
                self.high_score = pickle.load(f)
        else:
            with open(self.filepath, 'wb') as f:
                pickle.dump(self.high_score, f)
        # self.reset()

    def reset(self, level):
        # if self.score > self.high_score:
        #     self.high_score = self.score
        self.level = level
        self.win_value = self.win_scores[level]
        self.score = 0
        # self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        # self.field = [[0] * self.width] * self.height
        self.field = [[0] * self.width for i in range(self.height)]
        self.spawn()
        self.spawn()

    def do_highest_score(self):
        f = open(self.filepath, 'rb')
        highest = pickle.load(f)
        if self.score > highest[self.level]:
            self.high_score[self.level] = self.score
            f.close()
            with open(self.filepath, 'wb') as f:
                pickle.dump(self.high_score, f)
        # else:
            # self.high_score = highest
            # f.close()

    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def move(self, direction):
        def move_row_left(row2move):
            def tighten(row):
                new_row = [i for i in row if i != 0]
                new_row += [0] * (len(row) - len(new_row))
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    elif i + 1 < len(row) and row[i] == row[i + 1]:
                        pair = True
                        new_row.append(0)
                    else:
                        new_row.append(row[i])
                assert len(new_row) == len(row), 'error in merge a row'
                return new_row

            return tighten(merge(tighten(row2move)))

        moves = {'LEFT': lambda field: [move_row_left(row) for row in field]}
        moves['RIGHT'] = lambda field: invert(moves['LEFT'](invert(field)))
        moves['UP'] = lambda field: transpose(moves['LEFT'](transpose(field)))
        moves['DOWN'] = lambda field: transpose(moves['RIGHT'](transpose(field)))

        if direction in moves:
            if self.move_is_possible(direction):
                self.last_field = self.field
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def draw(self, screen):
        title_string = '         Xiao Zhu Zai\n'
        target_string = 'TARGET: {}'.format(self.win_value)
        help_string1 = 'Up(W) Down(S) Left(A) Right(D)'
        help_string2 = '  Back(B) Restart(R) Exit(Q)'
        gameover_string = '          GAME OVER'
        win_string = '           YOU WIN!'

        def cast(string):
            screen.addstr(string + '\n')

        def draw_hor_separator():
            line = '+------' * self.width + '+'
            cast(line)
            # separator = defaultdict(lambda: line)
            # if not hasattr(draw_hor_separator, 'counter'):
            # 	draw_hor_separator.counter = 0
            # cast(separator[draw_hor_separator.counter])
            # draw_hor_separator.counter += 1

        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row )+ '|')

        screen.clear()
        cast(title_string)
        # cast(target_string)
        cast('SCORE: ' + str(self.score))
        # if 0 != self.high_score:
        cast('HIGHSCORE: ' + str(self.high_score[self.level]))
        cast(target_string)
        # cast('\n')
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        # cast(target_string)
        # cast('\n')
        if self.is_win():
            cast(win_string)
        elif self.is_gameover():
            cast(gameover_string)
        else:
            cast(help_string1)
        cast(help_string2)

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                elif row[i != 0] and row[i + 1] == row[i]:
                    return True
                else:
                    return False

            return any(change(i) for i in range(len(row) - 1))

        check = {'LEFT': lambda field: any(row_is_left_movable(row) for row in field)}
        check['RIGHT'] = lambda field: check['LEFT'](invert(field))
        check['UP'] = lambda field: check['LEFT'](transpose(field))
        check['DOWN'] = lambda field: check['RIGHT'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False


def main(stdscr):
    def init():
        level = load_level(stdscr)
        game_field.reset(level)
        return 'GAME'

    def not_game(state):
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        responses['RESTART'] = 'INIT'
        responses['EXIT'] = 'EXIT'
        return responses[action]

    def game():
        game_field.draw(stdscr)
        action = get_user_action(stdscr)

        if action == 'RESTART':
            game_field.do_highest_score()
            return 'INIT'
        if action == 'EXIT':
            game_field.do_highest_score()
            return 'EXIT'
        if action == "LAST":
            game_field.field = game_field.last_field
        if game_field.move(action):
            if game_field.is_win():
                game_field.do_highest_score()
                return 'WIN'
            if game_field.is_gameover():
                game_field.do_highest_score()
                return 'GAMEOVER'
        return 'GAME'

    state_actions = {
        'INIT': init,
        'WIN': lambda: not_game('WIN'),
        'GAMEOVER': lambda: not_game('GAMEOVER'),
        'GAME': game
    }

    # curses.start_colors()
    # curses.use_default_colors()
    game_field = GameField()

    state = 'INIT'

    while state != 'EXIT':
        state = state_actions[state]()

    # curses.nocbreak()
    # curses.echo()
    # curses.endwin()

scr = curses.initscr()
curses.noecho()
curses.cbreak()
# scr = curses.newwin(60, 60, 1, 23)
scr = curses.newwin(50, 70)
main(scr)
curses.endwin()
# curses.wrapper(main)
