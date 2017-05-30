import traceback
from multiprocessing import Process


class save_to_file(Process):
    def __init__(self, name, data, path):
        super().__init__()
        self.name = name
        self.data = data
        self.path = path

    def save_to_file(self, name, data):
        print('len of {name} '.format(name=name) + str(len(data)))
        total = len(data)
        with open(self.path + name + '.txt', 'a', encoding='utf-8') as f:
            for each in data:
                try:
                    f.write(str(each) + '\n')
                except:
                    continue
        return total

    def run(self):
        try:
            total = self.save_to_file(self.name, data=self.data)
            return total
        except:
            print(traceback.format_exc())
