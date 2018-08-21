import curses 
import string                          # 一个图形界面的库
from random import randrange, choice
from collections import defaultdict     # 内建集合模块


letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']      # ord()把字符变成键值 然后把这个字典给 letter_codes
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions * 2))     
# zip函数：接受任意多个（包括0个和1个）序列作为参数，返回一个tuple列表。
# dict() 函数 合并两个字典
# action * 2 就是 ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit', 'Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']


def get_user_action(keyboard): 
	char = 'N'
	while char not in actions_dict:
		char = keyboard.getch()     # 获得一个输入的字符
	return actions_dict[char]         # 返回这个字符代表的那个动作


def transpose(field):     # 矩阵转置
	return [list(row) for row in zip(*field)]

# 传入一个压缩矩阵，zip(*field)把它解压变成原矩阵，再用list把每一行(  )变成[ ]


def invert(field):         # 矩阵逆转   field是传进来的一个矩阵
	return [row[::-1] for row in field]  # [::-1]就是全部倒过来

class GameField(object):
	def __init__(self, height = 4, width = 4, win = 2048):
		self.height = height         # 高
		self.width = width           # 宽
		self.win_value = win         # 过关分数
		self.score = 0               # 当前分数
		self.highscore = 0           # 最高分
		self.reset()                 # 棋盘重置

	def reset(self):
		if self.score > self.highscore:
			self.highscore = self.score     # 重置最高分
		self.score = 0 
		self.field = [[0 for i in range(self.width)] for j in range(self.height)]
		# a for i in range(b)  把a当作i搞出b个
		self.spawn()
		self.spawn() 

	def move(self, direction):             # 定义移动
		def move_row_left(row):
			def tighten(row):   # tighten 缩紧的意思    # 判断出应该是数字型的[] 比如[1，2，3]
				new_row = [i for i in row if i != 0]   # 假如不是零则保留
				new_row += [0 for i in range(len(row) - len(new_row))]   # 加上被去除掉的0的数量
				return new_row                         # 返回新的row

			def merge(row):     # merge 融合的意思
				pair = False
				new_row = []
				for i in range(len(row)):    # 开始循环[]里的每一个值
					if pair:
						new_row.append(2 * row[i])  # 要是一样则新row添加两倍的i
						self.score += 2 * row[i]
						pair = False
					else:
						if i + 1 < len(row) and row[i] == row[i + 1]: # 如果i和i+1相等
							pair = True
							new_row.append(0)       # 那么就在new_row末尾加一个0
						else:
							new_row.append(row[i])  # 要是不一样就添加一个i
				assert len(new_row) == len(row)     # 一个断言 新旧长度必定一样，否则肯定出错了
				return new_row                      # 返回新row

			return tighten(merge(tighten(row)))    


		moves = {}
		moves['Left'] = lambda field: [move_row_left(row) for row in field]
			# 对每一行都执行向左划的操作
			# 输入的是一个field 然后输出 [move_row_left(row) for row in field]
		moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
			# 左右倒过来向左划再倒回去
		moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))

		moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))

		if direction in moves:
			if self.move_is_possible(direction):    # 假如可以移动
				self.field = moves[direction](self.field) # 那就move
				self.spawn()
				return True
			else:
				return False

	def is_win(self):
		return any(any(i >= self.win_value for i in row) for row in self.field)
		# 把i >= self.win_value出现的0/1当作i放到row里


	def is_gameover(self):
		return not any(self.move_is_possible(move) for move in actions)

	def draw(self, screen):          # 画图形界面的函数
		help_string1 = '(W)Up (S)Down (A)Left (D)Right '
		help_string2 = '      (R)Restart  (Q)Exit      '
		gameover_string = '        Game over       ' 
		win_string = '         You win                 ' 

		def cast(string):
			screen.addstr(string + '\n')


		def draw_hor_separator():                              # separator：分隔器  画杠杠用的
			line = '+' + ( '+-------' *self.width + '+')[1:]    # 画分割线
			separator = defaultdict(lambda: line)              # 
			if not hasattr(draw_hor_separator, "counter"):     
			# 判断draw_hor_separator()函数有没有"counter"属性
				draw_hor_separator.counter = 0                 # 没有就给它添加一个
			cast(separator[draw_hor_separator.counter])
			draw_hor_separator.counter += 1

		def draw_row(row):                                     # 画分割线中间的数字
			cast(''.join('|{: ^7}'.format(num) if num > 0 else '|       ' for num in row) + '|' )


		screen.clear()                                         # 清屏
		cast('SCORE:' + str(self.score))
		if 0 != self.highscore:
			cast('HIGHSCORE:' + str(self.highscore))

		for row in self.field:           # 画界面
			draw_hor_separator()
			draw_row(row)

		draw_hor_separator()

		if self.is_win():
			cast(win_string)
		else: 
			if self.is_gameover():
				cast(gameover_string)
			else:
				cast(help_string1)
		cast(help_string2)


	def spawn(self):     # 随机出现2 
		new_element = 4 if randrange(100) > 89 else 2     # 控制概率
		(i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0]) 
		# 随机找一个该二维数组的我为之
		self.field[i][j] = new_element  # 2 or 4 赋值给这个幸运的位置



	def move_is_possible(self, direction):           # 是否可以移动(不能就gg了)
		def row_is_left_movable(row):                # 是否可以左移
			def change(i):
				if row[i] == 0 and row[i + 1] != 0:  # 左边有空位的情况
					return True
				if row[i] != 0 and row[i + 1] == row[i]:  # 左边没空位但是有两个一样的
					return True
				return False
			return any(change(i) for i in range(len(row) - 1))

		check = {}
		check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)
		check['Right'] = lambda field: check['Left'](invert(field))
		check['Up'] = lambda field: check['Left'](invert(field))
		check['Down'] = lambda field: check['Right'](invert(field))

		if direction in check:
			return check[direction](self.field)
		else:
			return False


def main(stdscr):   # stdscr 标准屏幕
	def init():
		game_field.reset()
		return 'Game'

	def not_game(state):
		game_field.draw(stdscr)
		action = get_user_action(stdscr)
		responses = defaultdict(lambda: state)       # lambda  匿名函数   假如没有键值则抛出state	
		responses['Restart'], responses['Exit'] = 'Init', 'Exit'
		return responses[action]

	def game():
		game_field.draw(stdscr)
		action = get_user_action(stdscr)

		if action == 'Restart':
			return 'Init'
		if action == 'Exit':
			return 'Exit'
		if game_field.move(action):
			if game_field.is_win():
			 	return 'Init'
			if game_field.is_gameover():
			 	return 'Init'
		return 'Game'

	state_actions = {
			'Init': init,
			'Win': lambda: not_game('Win'),
			'Gameover': lambda:not_game('Gameover'),
			'Game' : game
		}

	game_field = GameField(win = 32)
	state = 'Init'
	while state != 'Exit':
		state = state_actions[state]()

curses.wrapper(main)

# Q是有效的
# 其他的有问题

# 主逻辑就是     主循环 判断state 然后转到合并函数 无限递归


