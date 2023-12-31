import traceback

from top_inscriptions import get_all_data
import time

if __name__ == '__main__':
    while True:
        try:
            get_all_data(int(int(time.time()) / 600))
            print("inscriptions cache refreshed")
            time.sleep(600)
        except Exception as e:
            traceback.print_exc()
            print(f"refresh cache error: inscriptions")
            print(e)
            time.sleep(300)
