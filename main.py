import json
from collections import Counter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except IOError as e:
        logging.error(f"IO Error loading JSON data from {file_path}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error in {file_path}: {e}")
    return None


def get_hidden_and_admin_user_ids(users_data):
    """Returns sets of hidden and admin user IDs."""
    hidden_user_ids = {user['id']
                       for user in users_data['results'] if user['hidden']}
    admin_user_ids = {user['id']
                      for user in users_data['results'] if user['type'] == 'admin'}
    return hidden_user_ids, admin_user_ids


def get_challenge_category_mapping(challenges_data):
    """Returns a mapping of challenge IDs to their categories."""
    return {challenge['id']: challenge['category']
            for challenge in challenges_data['results']}


def get_challenge_name_mapping(challenges_data):
    """Returns a mapping of challenge IDs to their names."""
    return {challenge['id']: challenge['name']
            for challenge in challenges_data['results']}


def submissions_per_category():
    """Prints the number of submissions per category."""
    print("\nSubmissions by category:\n")
    submits_by_category = Counter()

    for submission in submissions_data['results']:
        if submission['user_id'] not in hidden_and_admin_user_ids:
            category = challenge_category_mapping.get(
                submission['challenge_id'])
            submits_by_category[category] += 1

    for category, count in sorted(
            submits_by_category.items(), key=lambda item: item[1], reverse=True):
        print(f"Category {category}: {count} submissions")


def solves_per_category():
    """Prints the number of solves per category."""
    print("\nSolves by category:\n")

    solves_by_category = Counter()
    for submission in submissions_data['results']:
        if submission['type'] == 'correct' and submission['user_id'] not in hidden_and_admin_user_ids:
            category = challenge_category_mapping.get(
                submission['challenge_id'])
            solves_by_category[category] += 1

    for category, count in sorted(solves_by_category.items(),
                                  key=lambda item: item[1], reverse=True):
        print(f"Category {category}: {count} solves")


def top_users_failed_submissions_count():
    """Prints the top 10 users with the highest number of failed submissions."""
    print("\nTop 10 users with the highest number of failed submissions:\n")
    username_failed_submissions = Counter()
    for submission in submissions_data["results"]:
        if submission["type"] == "incorrect":
            username = id_to_username.get(submission["user_id"], "Unknown")
            username_failed_submissions[username] += 1

    for user, count in username_failed_submissions.most_common(10):
        print(f"{user}: {count} failed submissions")


def first_bloods():
    """Prints the first solver of each challenge."""
    print("\nFirst bloods for each solved challenge:\n")
    first_solvers = {}

    for submission in submissions_data['results']:
        if submission['type'] == 'correct' and submission['user_id'] not in hidden_and_admin_user_ids:
            first_solvers.setdefault(
                submission['challenge_id'],
                submission['user_id'])

    for challenge_id, user_id in sorted(first_solvers.items(
    ), key=lambda x: challenge_name_mapping.get(x[0], '')):
        username = id_to_username.get(user_id, 'Unknown')
        challenge_name = challenge_name_mapping.get(challenge_id, 'Unknown')
        print(f"{challenge_name}: {username}")


def challenge_stats():
    """Prints statistics about solved and unsolved challenges."""
    print("\nChallenge statistics:\n")
    solved_challenge_ids = {submission['challenge_id']
                            for submission in submissions_data['results'] if submission['type'] == 'correct'}
    all_challenge_ids = {challenge['id']
                         for challenge in challenges_data['results']}

    num_solved_challenges = len(solved_challenge_ids)
    num_unsolved_challenges = len(all_challenge_ids - solved_challenge_ids)

    print(f"Challenges with at least one solve: {num_solved_challenges}")
    print(f"Challenges with zero solves: {num_unsolved_challenges}")


def most_popular_category():
    """Prints the most popular category based on solves."""
    print("\nMost popular category (highest number of solves):")

    solves_by_category = Counter()
    for submission in submissions_data['results']:
        if submission['type'] == 'correct':
            category = challenge_category_mapping.get(
                submission['challenge_id'])
            solves_by_category[category] += 1

    most_popular = max(solves_by_category.items(), key=lambda x: x[1])
    print(f"\n{most_popular[0]} ({most_popular[1]} solves)")


def longest_submission():
    """Prints details of the longest submission."""
    print("\nLongest submission:\n")
    longest_submission = max(
        submissions_data['results'],
        key=lambda x: len(
            x['provided']),
        default=None)

    if longest_submission:
        submission_user = id_to_username.get(
            longest_submission['user_id'], 'Unknown')
        print(
            f"The submission with ID {longest_submission['id']} made by user {submission_user} is the longest, with {len(longest_submission['provided'])} characters:\n")
        print(longest_submission['provided'])
    else:
        print("No submissions found.")


def top_failed_submissions_by_challenge():
    """Prints challenges with the highest number of failed submissions."""
    print("\nTop challenges with the highest number of failed submissions:\n")

    failed_submissions = Counter()
    correct_submissions = Counter()

    for submission in submissions_data['results']:
        if submission['user_id'] not in hidden_and_admin_user_ids:
            challenge_id = submission['challenge_id']
            if submission['type'] == 'incorrect':
                failed_submissions[challenge_id] += 1
            elif submission['type'] == 'correct':
                correct_submissions[challenge_id] += 1

    for challenge_id, num_failures in failed_submissions.most_common(3):
        challenge_name = challenge_name_mapping.get(challenge_id, 'Unknown')
        challenge_solves = correct_submissions[challenge_id]
        solve_rate = round(
            (challenge_solves / num_failures) * 100, 2) if num_failures else 0
        print(f"{challenge_name}: {num_failures} failed submissions, {challenge_solves} correct submissions, solve rate: {solve_rate}%")


def rewind():

    if not all([submissions_data, users_data, challenges_data]):
        logging.error("Failed to load data. Exiting.")
        return

    most_popular_category()
    submissions_per_category()
    solves_per_category()
    challenge_stats()
    first_bloods()
    top_users_failed_submissions_count()
    longest_submission()
    top_failed_submissions_by_challenge()


if __name__ == "__main__":
    submissions_data = load_json_data('db/submissions.json')
    users_data = load_json_data('db/users.json')
    challenges_data = load_json_data('db/challenges.json')

    id_to_username = {user["id"]: user["name"]
                      for user in users_data.get("results", [])}
    id_to_score = {user["id"]: 0 for user in users_data.get("results", [])}

    hidden_user_ids, admin_user_ids = get_hidden_and_admin_user_ids(users_data)
    hidden_and_admin_user_ids = hidden_user_ids | admin_user_ids
    challenge_category_mapping = get_challenge_category_mapping(challenges_data)
    challenge_name_mapping = get_challenge_name_mapping(challenges_data)

    rewind()
