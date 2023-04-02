import random
from datetime import datetime
import time


def random_id():
    return "".join([chr(random.randint(65, 90)) for _ in range(5)])

def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def random_location():
    return (random.uniform(-90, 90), random.uniform(-180, 180))

def random_name():
    first_names = ["Sophia", "Jackson", "Olivia", "Liam", "Emma", "Noah", "Ava", "Aiden", "Isabella", "Caden"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Miller", "Wilson", "Moore", "Anderson", "Thomas", "Jackson"]

    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_data():
    location = random_location()

    return {
        "name": random_name(),
        "id": random_id(),
        "ip": random_ip(),
        "latitude": str(location[0]),
        "longiitude": str(location[1]),
        "value": random.uniform(1, 10),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


if __name__ == "__main__":
    print("Generate Data for Training")
    while True:
        with open("/tmp/data.log", mode="a") as file:
            data = generate_data()
            file.write(f"{data}\n")
            file.close()
            print(f"success to generate data...{data.get('id')}")

        time.sleep(1)
