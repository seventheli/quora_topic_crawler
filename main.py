from concurrent.futures import ProcessPoolExecutor

from create_topic_thread import topic_thread
from setting import text, max_topic_in_single_total


def main():
    total = create_list()
    max_workers = int(input('how many process run in total(integer): \n'))
    pool = ProcessPoolExecutor(max_workers=max_workers)
    for each in total:
        print(each)
        pool.submit(run_a_process, each)


def run_a_process(name):
    process = topic_thread(name, max_topic_in_single_total)
    process.run()


def create_list():
    total = text.split('\n')
    return total


if __name__ == "__main__":
    main()
