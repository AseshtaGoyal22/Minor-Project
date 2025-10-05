from user_input import get_user_details
from recommender import generate_career_path
from utils import print_banner

def main():
    print_banner("Career Guide Generator")

    # Step 1: Get user details
    user = get_user_details()

    # Step 2: Generate career path recommendation
    path = generate_career_path(user)

    # Step 3: Display result
    print("\n🎯 Recommended Career Path for You:")
    for step in path:
        print(f"- {step}")

if __name__ == "__main__":
    main()
