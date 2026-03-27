import os
import argparse
import json
from getpass import getpass
from .modules.naukri import NaukriBot
from .modules.model import ChatbotBuild

def main():
    parser = argparse.ArgumentParser(description="Apply using NaukriBot")
    parser.add_argument("--apply",action="store_true",help="To start applying")
    parser.add_argument("--train",action="store_true",help="To train the model")
    parser.add_argument("--email",required=True,help="email address associated with naukri account")
    parser.add_argument("--filters", action="store_true", help="boolean weather to apply filters or not")
    parser.add_argument("--jobs", type=int, help="number of jobs to apply (default 10)")
    parser.add_argument("--search", help="job search keyword for filtered apply")
    parser.add_argument("--experience", type=int, help="years of experience for filtered apply")
    parser.add_argument("--location", nargs="?", const="", default=None, help="job location for filtered apply")
    parser.add_argument("--job-age", type=int, help="age of job posting in days for filtered apply (default 3)")
    parser.add_argument("--tab", help="tab to use for non-filter mode: profile/apply/preference/similar_jobs")
    parser.add_argument("--password", help="password for non-interactive apply (or set JAB_PASSWORD env var)")
    args = parser.parse_args()
    email = args.email
    username = args.email
    if args.apply:
        filt = args.filters
        print("filters",filt)
        password = args.password or os.getenv("JAB_PASSWORD") or getpass("Password: ")
        number = args.jobs if args.jobs is not None else int(input("Number of jobs to apply (default=10): ") or 10)
        nb = NaukriBot(email,password,username,number)
        if filt:
            if all(v is None for v in [args.search, args.experience, args.location, args.job_age]):
                print("Choose your filters to apply::::")
            search = args.search if args.search is not None else input("Job search criteria or keyword to search for (required if applying filters): ")
            if not search:
                print("Search keyword required when using --filters")
                return
            experience = args.experience if args.experience is not None else input("Years of experience (optional, leave blank if none): ")
            location = args.location if args.location is not None else input("Job location (optional, leave blank if none): ")
            location = location.strip() if isinstance(location, str) else location
            location = location if location else None
            jobAge = args.job_age if args.job_age is not None else input("Age of job posting in days (default set to 1 day): ")
            experience = int(experience) if experience not in [None, ""] else None
            jobAge = int(jobAge) if jobAge not in [None, ""] else 1
            nb.filter_apply(search,experience,location,jobAge)
        else:
            tab = args.tab if args.tab else input(f"Choose from these options to start: {nb.tabs} : ")
            if tab not in nb.tabs:
                print(f"Invalid tab '{tab}'. Allowed: {nb.tabs}")
                return
            nb.start_apply(tab)
    elif args.train:
        chb = ChatbotBuild(email)
        chb.train_model()
        training_data = chb.training_data
        with open(f"./jab/data/{username}/training_data.json","w+") as f:
            f.write(json.dumps(training_data,indent=4))
    else:
        print("Use --apply to start applying or --train to train the model")

if __name__ == "__main__":
    main()
