from function import read_zgwfcss, print_G, toGNF, toNPDA, print_NPDA, NPDA_solver

read_zgwfcss("上下文无关文法.txt")
print_G()
toGNF()
print_G()
# print_G_to_file(r"./结果/Greibach范式.txt")
toNPDA()
print_NPDA()
# print_NPDA_to_file(r"./结果/NPDA.txt")
NPDA_solver("NPDA识别输入.txt", True)
