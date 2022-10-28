class zgwfcss:
    def __init__(self):
        self.left = ''
        self.right = []

    def print(self):
        print(self.left, end=' ')
        print("->", end=' ')
        for index, r in enumerate(self.right):
            for char in r:
                print(char, end=' ')
            if index != len(self.right) - 1:
                print('|', end=' ')
        print()

    def print_to_file(self, f):
        print(self.left, end=' ', file=f)
        print("->", end=' ', file=f)
        for index, r in enumerate(self.right):
            for char in r:
                print(char, end=' ', file=f)
            if index != len(self.right) - 1:
                print('|', end=' ', file=f)
        print(file=f)

    def create_from_str(self, line):
        self.left, rs = line.split('->')
        for r in rs.split('|'):
            self.right.append(r.split(' '))
        return self


class NPDA_move_right:
    def __init__(self, to_status, into_stack):
        self.to_status = to_status
        self.into_stack = into_stack


class NPDA_move:
    def __init__(self, current_status, in_put, top_of_stack):
        self.current_status = current_status  # 控制器当前状态
        self.in_put = in_put  # 输入
        self.top_of_stack = top_of_stack  # 当前栈顶
        self.right = []

    def add_to_right(self, to_status, item):
        new_right = NPDA_move_right(to_status, item)
        self.right.append(new_right)

    def print(self):
        print('𝛿(', end='')
        print(self.current_status + ',', end='')
        print(self.in_put + ',', end='')
        print(self.top_of_stack + ')={', end='')
        for index, r in enumerate(self.right):
            print('(' + r.to_status + ',', end='')
            for index2, char in enumerate(r.into_stack):
                print(char, end='')
                if index2 != len(r.into_stack) - 1:
                    print(' ', end='')
                else:
                    print(')', end='')
            if index != len(self.right) - 1:
                print(',', end='')
            else:
                print('}')

    def print_to_file(self, f):
        print('𝛿(', end='', file=f)
        print(self.current_status + ',', end='', file=f)
        print(self.in_put + ',', end='', file=f)
        print(self.top_of_stack + ')={', end='', file=f)
        for index, r in enumerate(self.right):
            print('(' + r.to_status + ',', end='', file=f)
            for index2, char in enumerate(r.into_stack):
                print(char, end='', file=f)
                if index2 != len(r.into_stack) - 1:
                    print(' ', end='', file=f)
                else:
                    print(')', end='', file=f)
            if index != len(self.right) - 1:
                print(',', end='', file=f)
            else:
                print('}', file=f)


if __name__ == '__main__':
    new_move = NPDA_move('q1', 'a', 'S')
    new_move.add_to_right('q1', ['S', 'A', 'A'])
    new_move.add_to_right('q1', ['ε'])
    new_move.print()
