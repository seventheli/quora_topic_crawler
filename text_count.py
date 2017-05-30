import os
import traceback

from setting import text, save_path

path = save_path


def count_files():
    total = 0
    remove = []
    for each in os.listdir(path):
        with open(path + each, 'r', encoding='utf8') as f:
            len_file = len(f.read().split('\n'))
            print(each + ' : ' + str(len_file))
            if len_file <= 5000:
                remove.append(each)
            else:
                total += len_file
    for each in remove:
        print('remove: ' + each)
        os.remove(path + each)
    print(total)


def read_files():
    now = text.split('\n')
    for each in os.listdir(path):
        try:
            now.remove(each[:-4])
        except:
            pass
    for each in now:
        print(each)


def decoded():
    for each in os.listdir(path):
        try:
            with open(path + each, 'r', encoding='utf8') as f:
                file_to_write = f.read()
            with open(path + each, 'w', encoding='utf8') as f:
                f.write(file_to_write)
        except:
            print(traceback.format_exc())
            print('error at : ' + each)
