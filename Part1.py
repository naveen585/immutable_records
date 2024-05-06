import os
from time import sleep
from ascon import ascon_hash


def generating_merkle_hash(directory_path):
    if not os.path.isdir(directory_path):
        return b""
    file_hashes = []
    for item_name in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item_name)
        if os.path.isdir(item_path):
            generating_merkle_hash(item_path)
        elif os.path.isfile(item_path):
            with open(item_path, "rb") as file:
                message = file.read()
                file_hash = ascon_hash(message, variant="Ascon-Hash", hashlength=32)
                file_hashes.append(file_hash)
    sorted_file_hashes = sorted(file_hashes)
    directory_hash = ascon_hash(b"".join(sorted_file_hashes), variant="Ascon-Hash", hashlength=32)
    return directory_hash


def take_snapshot(directory_path, previous_hash):
    snapshot_hash = generating_merkle_hash(directory_path)
    combined_hash = ascon_hash(previous_hash + snapshot_hash, variant="Ascon-Hash", hashlength=32)
    return snapshot_hash, combined_hash


def simulate(directory_path,delay_seconds):
    previous_hash = b'\x00' * 32
    with open("hash_output_1.txt", "w") as file:
        day_count = 1
        for item_name in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item_name)
            if os.path.isdir(item_path):
                snapshot_hash, combined_hash = take_snapshot(item_path, previous_hash)
                previous_hash = combined_hash
                file.write(f"Day {day_count}, Combined Hash: {combined_hash.hex()}\n")
                sleep(delay_seconds)
                day_count += 1


target_directory = "spldirectory"
simulate(target_directory,5)
