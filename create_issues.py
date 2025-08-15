import csv
import requests

# Replace with your repo and token
GITHUB_TOKEN = "YOUR_PERSONAL_ACCESS_TOKEN"
REPO = "yourusername/yourrepo"  # e.g. "myuser/tailor-backend"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def create_issue(title, body, labels):
    url = f"https://api.github.com/repos/{REPO}/issues"
    payload = {
        "title": title,
        "body": body,
        "labels": labels.split(",") if labels else []
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 201:
        print(f"Issue '{title}' created successfully.")
    else:
        print(f"Failed to create issue '{title}': {response.status_code} {response.text}")

def main():
    with open("user_stories.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create_issue(row["title"], row["body"], row["labels"])

if __name__ == "__main__":
    main()
