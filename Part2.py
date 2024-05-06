import os
from time import sleep, time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from ascon import ascon_hash


def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key, private_key.public_key()


def sign_data(data, private_key):
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


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


def take_snapshot(directory_path, previous_hash, private_key):
    snapshot_hash = generating_merkle_hash(directory_path)
    timestamp = int(time())
    signature = sign_data(snapshot_hash + timestamp.to_bytes(8, byteorder='big'), private_key)
    combined_hash = ascon_hash(previous_hash + snapshot_hash, variant="Ascon-Hash", hashlength=32)
    return snapshot_hash, timestamp, signature, combined_hash


def simulate_with_delay(directory_path, delay_seconds):
    private_key, public_key = generate_rsa_key_pair()
    previous_hash = b'\x00' * 32
    with open("signature_output.txt", "w") as file:
        day_count = 1
        for item_name in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item_name)
            if os.path.isdir(item_path):
                snapshot_hash, timestamp, signature, combined_hash = take_snapshot(item_path, previous_hash,private_key)
                previous_hash = combined_hash
                file.write(f"Day {day_count}, Timestamp: {timestamp}, Signature: {signature.hex()}\n")
                sleep(delay_seconds)
                day_count += 1


target_directory = "spldirectory"
simulate_with_delay(target_directory, 5)
