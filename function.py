from data_struct import zgwfcss, NPDA_move

V = []
T = []
P = []
S = ''


# 读取正规文法产生式
def read_zgwfcss(filename):
    f = open(filename, "r", encoding='utf-8')
    content = f.readlines()
    for num, line in enumerate(content):
        if num == 0:
            Vmembers = line.strip().split(' ')
            for Vmember in Vmembers:
                V.append(Vmember)
        elif num == 1:
            Tmembers = line.strip().split(' ')
            for Tmember in Tmembers:
                T.append(Tmember)
        elif num == 2:
            global S
            S = line.strip()
        else:
            P.append(zgwfcss().create_from_str(line.strip()))
    f.close()


# 打印G=(V,T,P,S)
def print_G():
    for v in V:
        print(v, end=' ')
    print()
    for t in T:
        print(t, end=' ')
    print()
    for p in P:
        p.print()
    print(S)
    print()


# 输出到文件
def print_G_to_file(filename):
    f = open(filename, mode="w", encoding='utf-8')
    for v in V:
        print(v, end=' ', file=f)
    print(file=f)
    for t in T:
        print(t, end=' ', file=f)
    print(file=f)
    for p in P:
        p.print_to_file(f)
    print(S, file=f)
    print(file=f)
    f.close()


"""
1.消除ε规则
2.消除单一产生式
3.消除无用符号
4.消除左递归
"""
index_A = 1
index_B = 1
index_T = 1
index_C = 1


# 消除空产生式
def delete_epsilon():
    V0 = []  # 可空符号集
    V1 = []  # 不可空符号集

    # 对于所有产生式A->ε，A是一个可致空符号
    for p in P:  # 对每个符号
        css_num = len(p.right)
        have_T = 0
        for item in p.right:  # 对每个符号的每个产生式
            if len(item) == 1 and 'ε' in item and p.left not in V0:
                V0.append(p.left)
                break
            else:
                for char in item:
                    if char in T:
                        have_T += 1
                        break
        if have_T == css_num and p.left not in V0 and p.left not in V1:  # 判断所有的产生式都含有终结符
            V1.append(p.left)

    # 如果有产生式B->C1C2...Ck，其中每一个Ci∈V0是可致空符号，则B是一个可致空符号
    def can_be_epsilon(v):  # 判断一个非终结符是否能推出空
        flag1 = 0  # 当前符号是否可空，1为可空
        if v in V0:
            return True
        elif v in V1:
            return False
        else:
            for p in P:
                if p.left == v:  # 找到符号对应的产生式
                    flag2 = 0
                    flag3 = 0
                    for item in p.right:  # 对每个产生式
                        for char in item:  # 对产生式右边的每个符号
                            if char in T or char in V1:  # 如果包含终结符或不可空的非终结符，处理下一个产生式
                                flag2 = 1
                                break
                        if flag2 == 1:
                            flag2 = 0
                            continue
                        for char in item:  # 产生式中全是非终结符，且有的能推出空，有的不知道是否能推出空
                            if not can_be_epsilon(char):
                                flag3 = 1
                                break
                        if flag3 == 0:
                            flag1 = 1
                            break
                        else:
                            flag3 = 0
                    if flag1 == 1 and p.left not in V0:
                        V0.append(p.left)
                        return True
                    elif flag1 == 0 and p.left not in V1:
                        V1.append(p.left)
                        return False

    # 先推出可空符号集
    for v in V:
        can_be_epsilon(v)

    # print(V0)
    # print(V1)

    # 替换可空符号
    for p in P:
        index = []  # 可空符号的下标
        for item in p.right:
            for i, char in enumerate(item):
                if char in V0:
                    index.append(i)
            if len(index) != 0:
                for i in index:
                    copy = item.copy()
                    del copy[i]
                    if copy not in p.right:
                        p.right.append(copy)
            index.clear()

    # 删除ε产生式
    for p in P:
        copy_right = p.right.copy()
        for item in copy_right:
            if len(item) == 0 or len(item) == 1 and 'ε' in item:
                p.right.remove(item)
    if 'ε' in T:
        del T[T.index('ε')]

    # 删除只能推出空的非终结符
    useless_V = []
    copy_P = P.copy()
    for p in copy_P:
        if len(p.right) == 0:
            useless_V.append(p.left)
            V.remove(p.left)
            P.remove(p)
    for p in P:
        copy_right = p.right.copy()
        for item in copy_right:
            may_replace_item = [i for i in item if i not in useless_V]
            if len(may_replace_item) != len(item):  # 有无用非终结符
                p.right.remove(item)
                if may_replace_item not in p.right and len(may_replace_item) != 0:
                    p.right.append(may_replace_item)

    # 处理S->ε
    global S
    if S in V0:
        oldS = S
        S += '\''
        V.append(S)
        css = S + "->" + 'ε|' + oldS
        newcss = zgwfcss().create_from_str(css.strip())
        P.insert(0, newcss)
        T.append('ε')


# 消除单一产生式
def delete_single():
    queue = []  # 队列
    N = []  # 单元偶对集
    for p in P:
        queue.append(p.left)
        # BFS寻找当前非终结符的单元偶对
        while len(queue) != 0:
            current = queue.pop(0)  # 当前符号
            N.append(current)
            for pp in P:
                if pp.left == current:
                    for item in pp.right:
                        if len(item) == 1 and item[0] in V and item[0] not in N and item[0] not in queue:
                            queue.append(item[0])
        # print("N" + p.left + ":", end="")
        # print(N)
        # 处理单元偶对
        for n in N:
            for ppp in P:
                if ppp.left == n:
                    for item in ppp.right:
                        if (not (len(item) == 1 and item[0] in V)) and item not in p.right:
                            p.right.append(item)
        queue.clear()
        N.clear()
    for p in P:
        copy_right = p.right.copy()
        for item in copy_right:
            if len(item) == 1 and item[0] in V:
                p.right.remove(item)


# 消除无用符号
def delete_useless():
    generate = []  # 生成符号集
    reach = []  # 可达符号集
    queue = []
    should_delete_T = []  # 只有无用符号产生式里有的终结符
    for p in P:
        for item in p.right:
            if len(item) == 1 and item[0] in T:
                generate.append(p.left)
                break
    num_of_generate = len(generate)
    last = 0
    # 寻找生成符号
    while num_of_generate > last or S not in generate:
        last = num_of_generate
        for p in P:
            if p.left not in generate:
                for item in p.right:
                    flag = 1
                    for char in item:
                        if char not in generate and char not in T:
                            flag = 0
                            break
                    if flag == 1:
                        generate.append(p.left)
                        break
        num_of_generate = len(generate)
    # print(generate)
    # 删除非生成符号
    copy_P = P.copy()
    for p in copy_P:
        if p.left not in generate:
            for item in p.right:
                for char in item:
                    if char in T and char not in should_delete_T:
                        should_delete_T.append(char)
            P.remove(p)
        else:
            copy_right = p.right.copy()
            for item in copy_right:
                for char in item:
                    if char in V and char not in generate:
                        p.right.remove(item)
                        break
    copy_V = V.copy()
    for v in copy_V:
        if v not in generate:
            V.remove(v)
    # 寻找可达符号
    queue.append(S)
    while len(queue) != 0:
        current = queue.pop(0)  # 当前符号
        reach.append(current)
        for p in P:
            if p.left == current:
                for item in p.right:
                    for char in item:
                        if char in V and char not in reach and char not in queue:
                            queue.append(char)
    # print(reach)
    # 删除不可达符号
    copy_P = P.copy()
    for p in copy_P:
        if p.left not in reach:
            for item in p.right:
                for char in item:
                    if char in T and char not in should_delete_T:
                        should_delete_T.append(char)
            P.remove(p)
        else:
            copy_right = p.right.copy()
            for item in copy_right:
                for char in item:
                    if char in V and char not in reach:
                        p.right.remove(item)
                        break
    copy_V = V.copy()
    for v in copy_V:
        if v not in reach:
            V.remove(v)
    for p in P:
        for item in p.right:
            for char in item:
                if char in T and char in should_delete_T:
                    del should_delete_T[should_delete_T.index(char)]
    # print(should_delete_T)
    for s in should_delete_T:
        del T[T.index(s)]


# 消除左递归
def delete_left_recursive():
    map = {}  # 产生式和标号的映射
    for index, p in enumerate(P):
        map[p.left] = index
    # print(map)
    global index_A
    alpha = []
    beta = []
    length = len(P)
    for indexp in range(length - 1, -1, -1):  # 倒序遍历每个符号的产生式
        # 消直接左递归
        copy_right = P[indexp].right.copy()
        for item in copy_right:
            if P[indexp].left == item[0]:  # 有直接左递归
                alpha.append(item[1:])  # 添加到α集
                P[indexp].right.remove(item)
            else:
                beta.append(item)  # 添加到β集
        # print(alpha)
        # print(beta)
        if len(alpha) != 0:
            new_V = 'A' + str(index_A)
            index_A += 1
            V.append(new_V)
            for b in beta:
                bb = b.copy()
                bb.append(new_V)
                P[indexp].right.append(bb)
            css = new_V + "->"
            new_p = zgwfcss().create_from_str(css.strip())
            new_p.right.clear()
            for a in alpha:
                add_right = a.copy()
                new_p.right.append(add_right)
            for a in alpha:
                add_right = a.copy()
                add_right.append(new_V)
                new_p.right.append(add_right)
            P.append(new_p)
        alpha.clear()
        beta.clear()

        def can_replace(index):  # 判断右部是否有可以替换的产生式
            for item in P[index].right:
                if item[0] in V and map[item[0]] > index:  # 代入
                    return True
            return False

        # 消间接左递归
        while can_replace(indexp):  # 判断是否可以代入
            copy_right = P[indexp].right.copy()  # 消除了直接左递归后的右部
            for item in copy_right:
                if item[0] in V and map[item[0]] > indexp:  # 代入
                    for item2 in P[map[item[0]]].right:
                        remain = item[1:]
                        add_right = item2 + remain
                        if add_right not in P[indexp].right:
                            P[indexp].right.append(add_right)
                    P[indexp].right.remove(item)
        # 代入完成后，消直接左递归
        copy_right = P[indexp].right.copy()
        for item in copy_right:
            if P[indexp].left == item[0]:  # 有直接左递归
                alpha.append(item[1:])  # 添加到α集
                P[indexp].right.remove(item)
            else:
                beta.append(item)  # 添加到β集
        if len(alpha) != 0:
            new_V = 'A' + str(index_A)
            index_A += 1
            V.append(new_V)
            for b in beta:
                bb = b.copy()
                bb.append(new_V)
                P[indexp].right.append(bb)
            css = new_V + "->"
            new_p = zgwfcss().create_from_str(css.strip())
            new_p.right.clear()
            for a in alpha:
                add_right = a.copy()
                new_p.right.append(add_right)
            for a in alpha:
                add_right = a.copy()
                add_right.append(new_V)
                new_p.right.append(add_right)
            P.append(new_p)
        alpha.clear()
        beta.clear()


# 转化为Chomsky范式
def toCNF():
    delete_epsilon()
    delete_single()
    delete_useless()
    print_G()  # 打印消空、消单、消无用后的文法
    global index_B
    # 构造G1
    for indexp, p in enumerate(P):
        offset = 1
        for item in p.right:
            if len(item) >= 2:
                for indexc, char in enumerate(item):
                    if char in V:
                        continue
                    elif char in T:
                        flag = 0
                        replace_char = ''
                        for pp in P:
                            if len(pp.right) == 1 and len(pp.right[0]) == 1 and char == pp.right[0][0]:
                                replace_char = pp.left
                                flag = 1
                                break
                        if flag == 0:
                            replace_char = 'B' + str(index_B)
                            index_B += 1
                            css = replace_char + "->" + char
                            P.insert(indexp + offset, zgwfcss().create_from_str(css.strip()))
                            offset += 1
                            V.append(replace_char)
                            item[indexc] = replace_char
                        elif flag == 1:
                            item[indexc] = replace_char
    print_G()  # 打印G1
    global index_T
    F = {}
    # 构造GC
    for indexp, p in enumerate(P):
        offset = 1
        for item in p.right:
            if len(item) > 2:
                remain = item.copy()
                flag = 0
                length = len(remain)
                for f in F:
                    if F[f] == remain[1:]:
                        for i in range(1, length):
                            del item[1]
                        item.append(f)
                        flag = 1
                        break
                if flag == 0:
                    add_char = "T" + str(index_T)
                    index_T += 1
                    V.append(add_char)
                    for i in range(1, length):
                        del item[1]
                    item.append(add_char)
                    F[add_char] = remain[1:]
                    del remain[0]
                elif flag == 1:
                    continue
                flag2 = 1
                while len(remain) > 2:
                    flag = 0
                    for f in F:
                        if F[f] == remain[1:]:
                            add_left = "T" + str(index_T - 1)
                            add_right = f
                            css = add_left + "->" + remain[0] + " " + add_right
                            P.insert(indexp + offset, zgwfcss().create_from_str(css.strip()))
                            offset += 1
                            flag = 1
                            break
                    if flag == 1:
                        flag2 = 0
                        break
                    elif flag == 0:
                        add_left = "T" + str(index_T - 1)
                        add_right = "T" + str(index_T)
                        index_T += 1
                        V.append(add_right)
                        css = add_left + "->" + remain[0] + " " + add_right
                        P.insert(indexp + offset, zgwfcss().create_from_str(css.strip()))
                        offset += 1
                        F[add_right] = remain[1:]
                        del remain[0]
                if flag2 == 1:
                    add_left = "T" + str(index_T - 1)
                    css = add_left + "->" + remain[0] + " " + remain[1]
                    P.insert(indexp + offset, zgwfcss().create_from_str(css.strip()))
                    offset += 1


# 转化为Greibach范式
def toGNF():
    delete_epsilon()
    delete_single()
    delete_useless()
    delete_left_recursive()
    delete_single()
    delete_useless()

    map = {}  # 产生式和标号的映射
    for index, p in enumerate(P):
        map[p.left] = index

    # 将所有产生式变成终结符号开头
    def need_replace(p):  # 判断右部是否有非终结符开头的产生式
        for item in p.right:
            if item[0] in V:
                return True
        return False

    for p in P:
        while need_replace(p):  # 判断是否可以代入
            copy_right = p.right.copy()
            for item in copy_right:
                if item[0] in V:  # 代入
                    for item2 in P[map[item[0]]].right:
                        remain = item[1:]
                        add_right = item2 + remain
                        if add_right not in p.right:
                            p.right.append(add_right)
                    p.right.remove(item)
    # 替换中间的终结符
    global index_C
    for indexp, p in enumerate(P):
        offset = 1
        for item in p.right:
            for indexc, char in enumerate(item):
                if indexc == 0 or char in V:
                    continue
                elif char in T:
                    flag = 0
                    replace_char = ''
                    for pp in P:
                        if len(pp.right) == 1 and len(pp.right[0]) == 1 and char == pp.right[0][0]:
                            replace_char = pp.left
                            flag = 1
                            break
                    if flag == 0:
                        replace_char = 'C' + str(index_C)
                        index_C += 1
                        css = replace_char + "->" + char
                        P.insert(indexp + offset, zgwfcss().create_from_str(css.strip()))
                        offset += 1
                        V.append(replace_char)
                        item[indexc] = replace_char
                    elif flag == 1:
                        item[indexc] = replace_char


NPDA = []


# 打印NPDA
def print_NPDA():
    for n in NPDA:
        n.print()
    print()


# 输出NPDA到文件
def print_NPDA_to_file(filename):
    f = open(filename, mode="w", encoding='utf-8')
    for n in NPDA:
        n.print_to_file(f)
    print(file=f)
    f.close()


# 将Greibach范式转换为NPDA
def toNPDA():
    # 加入开始转移和结束转移
    start = NPDA_move('q0', 'ε', 'z')
    start.add_to_right('q1', [S, 'z'])
    NPDA.append(start)
    end = NPDA_move('q1', 'ε', 'z')
    end.add_to_right('qf', ['z'])
    NPDA.append(end)
    for p in P:
        current_status = 'q1'
        top_of_stack = p.left
        to_status = 'q1'
        for item in p.right:
            in_put = item[0]
            flag = 0
            for n in NPDA:
                if n.current_status == current_status and n.in_put == in_put and n.top_of_stack == top_of_stack:
                    if len(item) == 1:
                        n.add_to_right(to_status, ['ε'])
                    else:
                        n.add_to_right(to_status, item[1:])
                    flag = 1
                    break
            if flag == 0:
                new_move = NPDA_move(current_status, in_put, top_of_stack)
                if len(item) == 1:
                    new_move.add_to_right(to_status, ['ε'])
                else:
                    new_move.add_to_right(to_status, item[1:])
                NPDA.append(new_move)


# 使用NPDA判断输入是否符合文法
def NPDA_solver(filename, print_trace=False):
    f = open(filename, "r", encoding='utf-8')
    language = f.readline().strip()
    f.close()
    if len(language) == 0:  # 读空串
        language = 'ε'
    empty = 'ε'
    language = empty + language + empty  # 引入开始和结束的空
    status = 'q0'  # 控制器的当前状态
    p = 0  # 输入指针
    stack = ['z']  # 栈
    trace = []  # 追踪接受
    print_trace = print_trace

    def solver():
        nonlocal status
        nonlocal p
        nonlocal stack
        nonlocal trace
        init_status = status  # 保存初始的状态
        init_p = p  # 保存初始指针
        init_stack = stack.copy()  # 保存初始栈
        index_NPDA = -1  # 对应的NPDA转移函数标号
        # 找到对应的NPDA转移函数
        for index, n in enumerate(NPDA):
            if n.current_status == status and n.in_put == language[p] and n.top_of_stack == stack[-1]:
                index_NPDA = index
                break
        if index_NPDA == -1:
            return 0  # 没有能用的转移函数，此路不通
        for item in NPDA[index_NPDA].right:
            # 回溯时恢复状态、指针、栈到初始状态
            status = init_status
            p = init_p
            stack = init_stack.copy()
            p += 1  # 指针移动
            status = item.to_status  # 状态转移
            stack.pop()  # 出栈
            for i in range(len(item.into_stack) - 1, -1, -1):
                if item.into_stack[i] == 'ε':  # 消除
                    continue
                else:
                    stack.append(item.into_stack[i])  # 入栈
            if status == 'qf':
                t = [status, p, stack[::-1]]
                trace.append(t.copy())
                tt = [init_status, init_p, init_stack[::-1]]
                trace.append(tt)
                return 1  # 已到达终态
            else:
                result = solver()  # 递归
                if result == 0:
                    continue
                elif result == 1:
                    t = [init_status, init_p, init_stack[::-1]]
                    trace.append(t)
                    return 1  # 向上传递已到达终态信号
        return 0  # 所有都用不了，此路不通

    result = solver()
    if result == 0:
        print("NO")
    elif result == 1:
        print("YES")
    if print_trace:
        for i in range(len(trace) - 1, -1, -1):
            for index, item in enumerate(trace[i]):
                if index == 0:
                    print('(' + item + ',', end="")
                if index == 1:
                    print(str(item) + ',', end="")
                elif index == 2:
                    for indexc, char in enumerate(item):
                        if indexc != len(item) - 1:
                            print(char, end=" ")
                        else:
                            print(char + ')')


if __name__ == "__main__":
    read_zgwfcss("test.txt")
    print_G()
    toGNF()
    print_G()
    # print_G_to_file(r"./结果/Greibach范式.txt")
    toNPDA()
    print_NPDA()
    # print_NPDA_to_file(r"./结果/NPDA.txt")
    NPDA_solver("NPDA识别输入.txt", True)
