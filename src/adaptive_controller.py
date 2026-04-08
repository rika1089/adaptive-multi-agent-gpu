# adaptive_controller.py

import time
from allocator import compute_allocation
from scheduler import update_weights

if __name__ == "__main__":

    prev_alloc = None

    while True:

        weights = compute_allocation()

        print("\n📊 New Allocation:", weights)

        # update scheduler instead of restarting containers
        update_weights(weights)

        prev_alloc = weights

        time.sleep(5)