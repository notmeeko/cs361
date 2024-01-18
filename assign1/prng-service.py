import time
import random

while True:
    with open("prng-service.txt", "r") as file:
        lineread = file.readline().strip()

    if lineread == "run":
        print("Successfully running...")

        random_number = random.randint(1, 5)
        print(f"Generated random number: {random_number}")

        with open("prng-service.txt", "w") as file:
            file.write((f"{random_number}"))

        break
    else:
        print("Scanning...")

    time.sleep(3)