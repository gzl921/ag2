#!/usr/bin/env python3
"""
Name Generation Algorithm
A simple implementation that learns name patterns and generates new names.
"""

from collections import defaultdict
import random

def train_model(names):
    model = defaultdict(list)
    for name in names:
        name = name.lower()
        for i in range(len(name) - 2):
            pair = name[i : i + 2]
            next_letter = name[i + 2]
            model[pair].append(next_letter)
    return model

def generate_name(model, start="em", length=6):
    result = start
    while len(result) < length:
        pair = result[-2:]
        if pair not in model:
            break
        result += random.choice(model[pair])
    return result


def main():
    # Load names from file
    try:
        with open('names.txt', 'r') as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("names.txt not found. Using sample names.")
        names = ["emma", "olivia", "ava", "isabella", "sophia", "charlotte", "mia", "amelia", "harper", "evelyn"]
    
    print(f"Loaded {len(names)} names: {names[:10]}")
    
    # Train the model
    model = train_model(names)
    
    # Generate some names
    print("\nGenerated names:")
    print(f"Starting with 'ph': {generate_name(model, start='ph', length=6)}")
    print(f"Starting with 'xy': {generate_name(model, start='xy', length=6)}")
    print(f"Starting with 'zz': {generate_name(model, start='zz', length=6)}")

if __name__ == "__main__":
    main()
