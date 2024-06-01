"""
hashing.py
This file will contain the implementation and help for sim-hashing.
"""

from hashlib import sha256


def hash_feature(feature):
    """Hashes a single feature using SHA-256."""
    return int(sha256(feature.encode('utf-8')).hexdigest(), 16)


class Simhash:
    def __init__(self, num_features=256):
        """Initializes the Simhash with a given number of features, features meaning bits"""
        self.num_features = num_features
        self.hash_values = [0] * num_features

    def add_feature(self, feature):
        """Adds a feature to the Simhash by applying bitwise operations."""
        feature_hash = hash_feature(feature)
        for i in range(self.num_features):
            if (feature_hash >> i) & 1:  # Check if bit is set
                self.hash_values[i] += 1  # Increment count for that bit
            else:
                self.hash_values[i] -= 1  # Decrement count for that bit

    def value(self):
        """Returns the final Simhash value as a bit string."""
        simhash_value = 0
        for i in range(self.num_features):
            if self.hash_values[i] > 0:  # Check if count is positive
                simhash_value |= (1 << i)  # Set the corresponding bit
        return simhash_value

    def distance(self, other):
        """Calculates the Hamming distance between two Simhash values."""
        return bin(self.value() ^ other.value()).count('1')

    def similarity(self, other):
        """Calculates the similarity between two Simhash values based on Hamming distance."""
        distance = self.distance(other)
        return 1 - (distance / self.num_features)


def create_shingles(document: list, shingle_size: int = 3) -> list:
    """
    This function will take in a document and return a list of shingles.
    :param document: list
    :param shingle_size: int
    :return: list
    """
    # Create a list to store the shingles
    shingles = []

    # Create shingles
    for i in range(len(document) - shingle_size + 1):
        shingle = " ".join(document[i:i + shingle_size])
        shingles.append(shingle)

    # Return the list of shingles
    return shingles


def sim_hash(text: list) -> Simhash:
    """
    This function will take in a list of words and return the sim-hash of the document list.
    :param text: list
    :return: Simhash
    """
    # Create a Simhash object
    simhash = Simhash()
    # Create shingles
    shingles = create_shingles(text, 3)

    # Add shingles to the Simhash
    for shingle in shingles:
        simhash.add_feature(shingle)

    # Return the Simhash value
    return simhash
