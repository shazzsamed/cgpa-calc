from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from credits import credits2019

GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "RA": 0
}
CGPA = 0
TOTAL_CREDITS = 0

def get_semester_data(driver):
    """Extracts course data from the current semester page."""
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#subjects tr"))
    )

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    table = soup.find("tbody", {"id": "subjects"})
    courses = {} 
    gpa = 0
    sem_credits = 0

    for row in table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) >= 12:
            #Extract course code and grade
            course_code = columns[1].text.strip()
            grade = columns[11].text.strip()
            if not grade:
                continue

            #GPA Calculation
            credits = credits2019[course_code]
            sem_credits += credits
            gpa += GRADE_POINTS[grade] * credits

            #Add to courses
            print(course_code, grade)
            if grade in GRADE_POINTS:
                courses[course_code] = (credits2019[course_code],grade)

    gpa = round(gpa / sem_credits, 2) if sem_credits > 0 else 0
    print(f"🎯 GPA: {gpa}\n")

    return courses

def calculate_cgpa(all_courses):
    """Calculates the CGPA."""
    total_credits = sum(credit for credit, _ in all_courses.values())
    weighted_sum = sum(GRADE_POINTS[grade] * credit for credit, grade in all_courses.values())

    return round(weighted_sum / total_credits, 2) if total_credits > 0 else 0

def main():
    driver = webdriver.Chrome()
    driver.get("https://acoe.annauniv.edu/sems/login/student")

    print("✅ Please log in manually, then press Enter to continue...")
    input()

    all_courses = {}
    select_element = Select(driver.find_element(By.ID, "sessions"))
    options = select_element.options

    for option in options:
        session_value = option.get_attribute("value")
        print(f"🔄 Fetching Semester: {option.text}")
        select_element.select_by_value(session_value)
        
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#subjects tr"))
        )

        semester_courses = get_semester_data(driver)
        if semester_courses:
            print(f"🔄 Updating Semester: {option.text}")
            all_courses.update(semester_courses)

    driver.quit()
    final_cgpa = calculate_cgpa(all_courses)
    print(f"\n🎯 Final CGPA: {final_cgpa}")

if __name__ == "__main__":
    main()
