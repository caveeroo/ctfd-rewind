import os
import json
import zipfile
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def parse_args():
    parser = argparse.ArgumentParser(
        description="Visualization of CTFd Rewind")
    parser.add_argument('--format', choices=['svg', 'png', 'pdf', 'all'],
                        required=True, help="Output format for the graphs")
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


def save_plot(filename, export_format, pdf=None):
    if export_format in ['svg', 'all']:
        plt.savefig(f'{filename}.svg', bbox_inches='tight')
    if export_format in ['png', 'all']:
        plt.savefig(f'{filename}.png', bbox_inches='tight')

    if export_format in ['pdf', 'all'] and pdf is not None:
        plt.tight_layout(pad=3.0)
        pdf.savefig()

    plt.close()


def create_zip_and_cleanup(filenames, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in filenames:
            zipf.write(file)
            os.remove(file)


def plot_submissions_per_category(df, export_format, pdf=None):
    plt.figure(figsize=(10, 6), tight_layout=True)
    ax = sns.barplot(x='Submissions', y='Category', data=df,
                     palette='muted', hue='Category', legend=False)
    ax.set(title='Submissions Per Category',
           xlabel='Number of Submissions', ylabel='Category')
    save_plot('submissions_per_category', export_format, pdf)


def plot_solves_per_category(df, export_format, pdf=None):
    plt.figure(figsize=(10, 6), tight_layout=True)
    ax = sns.barplot(x='Solves', y='Category', data=df,
                     palette='muted', hue='Category', legend=False)
    ax.set(title='Solves Per Category',
           xlabel='Number of Solves', ylabel='Category')
    save_plot('solves_per_category', export_format, pdf)


def plot_challenge_statistics(df, export_format, pdf=None):
    plt.figure(figsize=(8, 4), tight_layout=True)

    # Creating a bar plot
    ax = sns.barplot(x='Number of Challenges', y='Status', data=df,
                     palette='muted', hue='Number of Challenges', legend=False)
    for i in ax.containers:
        ax.bar_label(i,)

    plt.title('Challenge solves')
    plt.xlabel('')
    plt.ylabel('')
    save_plot('challenge_statistics', export_format, pdf)


def plot_first_bloods(df, export_format, pdf=None):
    fig_height = max(4, len(df) * 0.3)
    fig, ax = plt.subplots(figsize=(6, fig_height))
    ax.axis('off')  # Hide the axes

    table_data = [["Challenge", "First Blood"]] + df.values.tolist()
    table = ax.table(cellText=table_data, cellLoc='center',
                     loc='center', colWidths=[0.5]*len(df.columns))
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    plt.title("First Bloods per Challenge", fontsize=14)
    save_plot('first_bloods', export_format, pdf)


def plot_top_users_failed_submissions(df, export_format, pdf=None):
    plt.figure(figsize=(10, 6), tight_layout=True)
    ax = sns.barplot(x='Failed Submissions', y='User', data=df,
                     palette='muted', hue='User', legend=False)
    ax.set(title='Top Users by Failed Submissions Count',
           xlabel='Failed Submissions', ylabel='User')
    save_plot('top_users_failed_submissions', export_format, pdf)


def plot_top_failed_submissions_by_challenge(df, export_format, pdf=None):
    plt.figure(figsize=(10, 6), tight_layout=True)
    ax = sns.barplot(x='Failed Submissions', y='Challenge',
                     data=df, palette='muted', hue='Challenge', legend=False)
    ax.set(title='Top Failed Submissions by Challenge',
           xlabel='Failed Submissions', ylabel='Challenge')

    for index, row in df.iterrows():
        solve_rate = row['Solve Rate']
        ax.text(row['Failed Submissions'] + 0.02, index, f'{solve_rate}%',
                color='black', ha="center", va="center")

    save_plot('top_failed_submissions_by_challenge', export_format, pdf)


if __name__ == "__main__":
    args = parse_args()
    export_format = args.format

    results_data = load_json_data("results.json")

    sns.set_style('darkgrid')
    plt.rc('axes', titlesize=18)
    plt.rc('axes', labelsize=14)
    plt.rc('xtick', labelsize=13)
    plt.rc('ytick', labelsize=13)
    plt.rc('legend', fontsize=13)
    plt.rc('font', size=13)

    submissions_per_category_df = pd.DataFrame(
        results_data['submissions_per_category'], columns=['Category', 'Submissions'])
    solves_per_category_df = pd.DataFrame(
        results_data['solves_per_category'], columns=['Category', 'Solves'])
    challenge_stats_dict = results_data['challenge_statistics']
    labels_map = {'solved_challenges': 'Solved',
                  'unsolved_challenges': 'Unsolved'}
    challenges_statistics = pd.DataFrame({'Status': [labels_map[key] for key in challenge_stats_dict.keys()],
                                          'Number of Challenges': list(challenge_stats_dict.values())})

    first_bloods = pd.DataFrame(
        results_data['first_bloods'], columns=['Challenge', 'User'])

    top_users_failed_submissions_count_df = pd.DataFrame(
        results_data['top_users_failed_submissions_count'], columns=['User', 'Failed Submissions'])
    top_failed_submissions_by_challenge_df = pd.DataFrame(results_data['top_failed_submissions_by_challenge'], columns=[
                                                          'Challenge', 'Failed Submissions', 'Correct Submissions', 'Solve Rate'])

    pdf = None
    if export_format in ['pdf', 'all']:
        pdf = PdfPages('results.pdf')

    plot_submissions_per_category(
        submissions_per_category_df, export_format, pdf)
    plot_solves_per_category(solves_per_category_df, export_format, pdf)
    plot_challenge_statistics(challenges_statistics, export_format, pdf)
    plot_first_bloods(first_bloods, export_format, pdf)
    plot_top_users_failed_submissions(
        top_users_failed_submissions_count_df, export_format, pdf)
    plot_top_failed_submissions_by_challenge(
        top_failed_submissions_by_challenge_df, export_format, pdf)

    if pdf:
        pdf.close()
        if export_format == 'pdf':
            print(f"Pdf saved to results.pdf")

    if export_format in ['svg', 'png', 'all']:
        file_extensions = [
            'svg', 'png'] if export_format == 'all' else [export_format]
        all_files = []
        for ext in file_extensions:
            all_files.extend([
                f'submissions_per_category.{ext}',
                f'solves_per_category.{ext}',
                f'challenge_statistics.{ext}',
                f'first_bloods.{ext}',
                f'top_users_failed_submissions.{ext}',
                f'top_failed_submissions_by_challenge.{ext}'
            ])
        if export_format == 'all':
            all_files.append('results.pdf')
        create_zip_and_cleanup(all_files, f'results_{export_format}.zip')
        print(f"results_{export_format}.zip created successfully")
