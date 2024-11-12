from hashlib import sha256

def get_file_hash(file_path: str, hash_function, block_size=65536) -> str:
    with open(file_path, "rb", buffering=0) as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            hash_function.update(chunk)
    return hash_function.hexdigest()

def sha256sum(file_path: str) -> str:
    return get_file_hash(file_path, sha256())