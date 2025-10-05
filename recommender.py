from career_data import CAREER_PATHS

def generate_career_path(user):
    interest = user.get("interest", "").lower()

    if "code" in interest or "software" in interest:
        return CAREER_PATHS["Software Engineer"]
    elif "data" in interest or "math" in interest:
        return CAREER_PATHS["Data Scientist"]
    elif "design" in interest or "art" in interest:
        return CAREER_PATHS["Graphic Designer"]
    elif "construction" in interest or "civil" in interest:
        return CAREER_PATHS["Civil Engineer"]
    else:
        return ["Explore different fields", "Take online courses", "Talk to mentors", "Find your passion"]
