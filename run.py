import sys
import os
import subprocess

_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jbvnv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable) != os.path.abspath(_venv_python):
    sys.exit(subprocess.call([_venv_python] + sys.argv))

from jab.modules.naukri import NaukriBot

EMAIL    = "niteshsingh5375@gmail.com"
PASSWORD = "nitesh5375"
SEARCH   = "java developer"
JOB_AGE  = "3"
MAX_PAGES = 10

EXPERIENCE_PHASES = [3, 4]

# Sections to apply from on the Recommended Jobs page, in order.
# Available sections: "Profile", "Applies", "Top Candidate", "You might like"
RECOMMENDED_SECTIONS = ["Applies", "Profile",  "Top Candidate", "You might like"]

total_applied = 0

for exp in EXPERIENCE_PHASES:
    print(f"\n{'='*55}")
    print(f"Search : '{SEARCH}'  |  Experience : {exp} yrs  |  Pages : 1–{MAX_PAGES}")
    print(f"{'='*55}")

    bot = NaukriBot(EMAIL, PASSWORD, EMAIL, number=10000)
    try:
        result = bot.filter_apply(SEARCH, exp, "", JOB_AGE, max_pages=MAX_PAGES, recommended_sections=RECOMMENDED_SECTIONS)
        phase_applied = result.get("applied", 0)
        total_applied += phase_applied
        print(f"Phase done — applied this phase: {phase_applied}  |  total so far: {total_applied}")
    except Exception as e:
        print(f"Error during {exp}-year phase: {e}")

print(f"\n{'='*55}")
print(f"Automation complete. Total jobs applied: {total_applied}")
print(f"{'='*55}")
