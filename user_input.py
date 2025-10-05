def get_user_details():
    print("\nPlease answer a few questions to get career guidance:\n")
    name = input("What is your name? ")
    interest = input("What are your main interests? (e.g., coding, data, design, civil) ")

    return {
        "name": name,
        "interest": interest
    }
