import time

q = input("Type 'run' to run the program: ")
if q == 'run':  
    print("Running...")
    with open("prng-service.txt", "w") as file:
        file.write("run")

    while True:
        with open("prng-service.txt", "r") as file:
            lineread = file.readline().strip()

        if lineread.isdigit() and 1 <= int(lineread) <= 5:
            print("Successfully found an integer...")

            with open("image-service.txt", "w") as file:
                file.write(f"{lineread}")

            break
        else:
            print("Scanning for an integer...")

        time.sleep(3)


else:
    print("System down. See you later!")