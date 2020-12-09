from stitch import *

for i in range(1, 10):
    print(i)
    directory_input = 'input/' + str(i) + '/'
    directory_output = 'output/' + str(i) + '/'
    s = Stitch(directory_input, directory_output)
    s.run_stitch()
