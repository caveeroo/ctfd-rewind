import os
import json
import logging
import argparse
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tool to analyze ctf competitions data")
    parser.add_argument(
        '--output', choices=['txt', 'json'], required=True, help="Output format")
    parser.add_argument('--dir', default='.',
                        help="Directory containing CTFd export")
    return parser.parse_args()


def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except IOError as e:
        logging.error(f"IO Error loading JSON data from {file_path}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error in {file_path}: {e}")
    return None


def output_txt(data):
    with open('results.txt', 'w') as file:
        for key, value in data.items():
            file.write(f"{key}:\n")
            if isinstance(value, (list, set)):
                for item in value:
                    file.write(f"  {item}\n")
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    file.write(f"  {subkey}: {subvalue}\n")
            else:
                file.write(f"  {value}\n")
            file.write("\n")
    print("saved to results.txt")


def output_json(data):
    with open('results.json', 'w') as file:
        json.dump(data, file, indent=4)
    print("saved to results.json")


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


def submissions_per_category(submissions_data, hidden_and_admin_user_ids, challenge_category_mapping):
    """Returns the number of submissions per category."""
    submits_by_category = Counter()

    for submission in submissions_data['results']:
        if submission['user_id'] not in hidden_and_admin_user_ids:
            category = challenge_category_mapping.get(
                submission['challenge_id'])
            submits_by_category[category] += 1

    return sorted(submits_by_category.items(), key=lambda item: item[1], reverse=True)


def solves_per_category(submissions_data, hidden_and_admin_user_ids, challenge_category_mapping):
    """Returns the number of solves per category."""
    solves_by_category = Counter()
    for submission in submissions_data['results']:
        if submission['type'] == 'correct' and submission['user_id'] not in hidden_and_admin_user_ids:
            category = challenge_category_mapping.get(
                submission['challenge_id'])
            solves_by_category[category] += 1

    return sorted(solves_by_category.items(), key=lambda item: item[1], reverse=True)


def top_users_failed_submissions_count(submissions_data, id_to_username, n):
    """Returns the top N users with the highest number of failed submissions."""
    username_failed_submissions = Counter()
    for submission in submissions_data["results"]:
        if submission["type"] == "incorrect":
            username = id_to_username.get(submission["user_id"], "Unknown")
            username_failed_submissions[username] += 1

    return username_failed_submissions.most_common(n)


def first_bloods(submissions_data, hidden_and_admin_user_ids, id_to_username, challenge_name_mapping):
    """Returns the first solver of each challenge."""
    first_solvers = {}

    for submission in submissions_data['results']:
        if submission['type'] == 'correct' and submission['user_id'] not in hidden_and_admin_user_ids:
            first_solvers.setdefault(
                submission['challenge_id'], submission['user_id'])

    return [(challenge_name_mapping.get(challenge_id, 'Unknown'), id_to_username.get(user_id, 'Unknown'))
            for challenge_id, user_id in sorted(first_solvers.items(), key=lambda x: challenge_name_mapping.get(x[0], ''))]


def challenge_stats(submissions_data, challenges_data):
    """Returns statistics about solved and unsolved challenges."""
    solved_challenge_ids = {submission['challenge_id']
                            for submission in submissions_data['results'] if submission['type'] == 'correct'}
    all_challenge_ids = {challenge['id']
                         for challenge in challenges_data['results']}

    return {
        "solved_challenges": len(solved_challenge_ids),
        "unsolved_challenges": len(all_challenge_ids - solved_challenge_ids)
    }


def most_popular_category(submissions_data, challenge_category_mapping):
    """Returns the most popular category based on solves."""
    solves_by_category = Counter()
    for submission in submissions_data['results']:
        if submission['type'] == 'correct':
            category = challenge_category_mapping.get(
                submission['challenge_id'])
            solves_by_category[category] += 1

    most_popular = max(solves_by_category.items(), key=lambda x: x[1])
    return most_popular


def longest_submission(submissions_data, id_to_username):
    """Returns details of the longest submission."""
    longest_submission = max(
        submissions_data['results'], key=lambda x: len(x['provided']), default=None)
    if longest_submission:
        submission_user = id_to_username.get(
            longest_submission['user_id'], 'Unknown')
        return {
            "id": longest_submission['id'],
            "user": submission_user,
            "length": len(longest_submission['provided']),
            "content": longest_submission['provided']
        }
    else:
        return {"message": "No submissions found."}


def top_failed_submissions_by_challenge(submissions_data: dict, hidden_and_admin_user_ids, challenge_name_mapping):
    """Returns challenges with the highest number of failed submissions."""
    failed_submissions = Counter()
    correct_submissions = Counter()

    for submission in submissions_data['results']:
        if submission['user_id'] not in hidden_and_admin_user_ids:
            challenge_id = submission['challenge_id']
            if submission['type'] == 'incorrect':
                failed_submissions[challenge_id] += 1
            elif submission['type'] == 'correct':
                correct_submissions[challenge_id] += 1

    top_challenges = []
    for challenge_id, num_failures in failed_submissions.most_common(3):
        challenge_name = challenge_name_mapping.get(challenge_id, 'Unknown')
        challenge_solves = correct_submissions[challenge_id]
        solve_rate = round((challenge_solves / num_failures)
                           * 100, 2) if num_failures else 0
        top_challenges.append(
            (challenge_name, num_failures, challenge_solves, solve_rate))

    return top_challenges


def rewind(data_dir, output_format):
    submissions_data = load_json_data(
        os.path.join(data_dir, 'db/submissions.json'))
    users_data = load_json_data(os.path.join(data_dir, 'db/users.json'))
    challenges_data = load_json_data(
        os.path.join(data_dir, 'db/challenges.json'))

    if not all([submissions_data, users_data, challenges_data]):
        logging.error("Failed to load data. Exiting.")
        return

    # mappings
    id_to_username = {user["id"]: user["name"]
                      for user in users_data.get("results", [])}
    hidden_user_ids, admin_user_ids = get_hidden_and_admin_user_ids(users_data)
    hidden_and_admin_user_ids = hidden_user_ids | admin_user_ids
    challenge_category_mapping = get_challenge_category_mapping(
        challenges_data)
    challenge_name_mapping = get_challenge_name_mapping(challenges_data)

    # analysis
    most_popular_data = most_popular_category(
        submissions_data, challenge_category_mapping)

    submissions_per_category_data = submissions_per_category(
        submissions_data, hidden_and_admin_user_ids, challenge_category_mapping)

    solves_data = solves_per_category(
        submissions_data, hidden_and_admin_user_ids, challenge_category_mapping)

    challenge_stats_data = challenge_stats(submissions_data, challenges_data)

    first_bloods_data = first_bloods(
        submissions_data, hidden_and_admin_user_ids, id_to_username, challenge_name_mapping)

    top_users_failed_data = top_users_failed_submissions_count(
        submissions_data, id_to_username, 10)

    longest_submission_data = longest_submission(
        submissions_data, id_to_username)

    top_failed_submissions_data = top_failed_submissions_by_challenge(
        submissions_data, hidden_and_admin_user_ids, challenge_name_mapping)

    # output
    combined_data = {
        "most_popular_category": most_popular_data,
        "submissions_per_category": submissions_per_category_data,
        "solves_per_category": solves_data,
        "challenge_statistics": challenge_stats_data,
        "first_bloods": first_bloods_data,
        "top_users_failed_submissions_count": top_users_failed_data,
        "longest_submissions": longest_submission_data,
        "top_failed_submissions_by_challenge": top_failed_submissions_data
    }

    output_functions = {
        'txt': output_txt,
        'json': output_json
    }

    output_func = output_functions.get(output_format)
    if output_func:
        output_func(combined_data)
    else:
        logging.error(f"Invalid output format: {output_format}")


if __name__ == "__main__":
    args = parse_args()
    rewind(args.dir, args.output)
