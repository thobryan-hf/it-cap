# TODO: Consider all projects - function is done
# TODO: Ignore 0 hours logged
""" Generate a report in CSV or in screen using prettytable with the information required by IT-Cap process.
Please, change generate your token in Jira and change the variables below """

import os
from jira import JIRA  # https://buildmedia.readthedocs.org/media/pdf/jira/latest/jira.pdf
from prettytable import PrettyTable
from workalendar.europe import Germany
from datetime import datetime
import csv
import logging
import sqlite3

token = os.environ.get('jira_token')
email = "thomas.bryan@hellofresh.com"
server = "https://hellofresh.atlassian.net"
logging.basicConfig(level=logging.INFO, format='%(message)s')

# projects = [] # Leave empty for all projects
# projects = ["PX", "REF", "PO"]
projects = ["MCPRO"]

start_date = "2022-08-01"  # First day of previous month
end_date = "2022-09-01"    # Last day of previous month + 1 -> otherwise Jira won't consider tasks resolved in the last day

output = "csv"  # csv or screen

#  Jira Authentication
jira = JIRA(
    basic_auth=(email, token),
    server=server
)

db_file_name = "itcap.db"
if os.path.exists(db_file_name):
    os.remove(db_file_name)

# SQLITE
con = sqlite3.connect(db_file_name)
cur = con.cursor()
# select epic,  task_assignee , sum(task_time) from itcap group by epic, task_assignee order by epic

cur.execute("CREATE TABLE itcap(epic, task, epic_summary, task_summary, task_assignee, task_time, task_resolutiondate, pairee)")


def get_projects():
    projects_acceptable = []

    projects = jira.projects()
    for project in projects:
        if hasattr(project, "projectCategory") and "HelloFresh - Test Projects" not in project.projectCategory.name:
            projects_acceptable.append(project.key)

    return projects_acceptable


def period_working_days(start_date, end_date):
    """
    Return the number of working days in a specific period of time
    :param start_date:
    :param end_date:
    :return:
    """
    cal = Germany()
    working_days = cal.get_working_days_delta(datetime.strptime(start_date, '%Y-%m-%d'),
                                                     datetime.strptime(end_date, '%Y-%m-%d'))
    return working_days


def get_project_lead(key):
    """
    Get project lead
    :param key:
    :return:
    """
    project = jira.project(key)
    return project.lead.displayName


def get_task_info_pairee(issue_task):
    # customfield_12162 -> Pairee field
    try:
        pair = issue_task.fields.customfield_12162.displayName
        logging.warning(f"Paired: {issue_task.fields.customfield_12162.displayName} {issue_task.key}")
        return pair
    except:
        return False


def get_task_info(issue_task):
    """
    Get information relative for a specific task
    :param task_dict:
    :param issue_task:
    :return:
    """

    task_dict = {issue_task: {"task_issuetype": issue_task.fields.issuetype.name,
                              "task_summary": issue_task.fields.summary,
                              "task_time": issue_task.fields.aggregatetimespent,
                              "task_update": issue_task.fields.updated[:10],
                              "task_assignee": issue_task.fields.assignee,
                              "task_resolutiondate": issue_task.fields.resolutiondate,
                              }
                }

    return task_dict


def time_calculation_person_pairee(pair, task_person_dict, issue_task):
    """
    Add or update a specific number of time spent for a pair in a project
    :param task_person_dict:
    :param issue_task:
    :return:
    """
    task_assignee = pair
    task_time = issue_task.fields.aggregatetimespent

    try:
        task_person_dict[task_assignee] = task_person_dict[task_assignee] + issue_task.fields.aggregatetimespent
    except:
        task_person_dict[task_assignee] = task_time

    return task_person_dict


def time_calculation_person(task_person_dict, issue_task):
    """
    Add or update a specific number of time spent for a person in a project
    :param task_person_dict:
    :param issue_task:
    :return:
    """
    task_assignee = str(issue_task.fields.assignee)
    task_time = issue_task.fields.aggregatetimespent

    try:
        task_person_dict[task_assignee] = task_person_dict[task_assignee] + issue_task.fields.aggregatetimespent
    except:
        task_person_dict[task_assignee] = task_time

    return task_person_dict


def get_epic_information(epic_dict, issue_epic, project_dict):
    """
    Get relevant information from the epic and return it
    :param epic_dict:
    :param issue_epic:
    :param project_dict:
    :return:
    """
    key = issue_epic.key
    issue_type = issue_epic.fields.issuetype.name
    summary = issue_epic.fields.summary
    reporter = issue_epic.fields.reporter.displayName
    status = issue_epic.fields.status.name
    created = issue_epic.fields.created[:10]
    updated = issue_epic.fields.updated[:10]
    category = issue_epic.fields.project.projectCategory.description  # name or description

    if project_dict["project_lead"] is None:
        project_dict["project_lead"] = get_project_lead(issue_epic.fields.project.key)

    # analyse resolved field
    try:
        resolved = issue_epic.fields.resolutiondate[:10]
    except:
        resolved = 'None'
    project_name = issue_epic.fields.project.name

    # Prepare benefit string adding "commas" between benefits
    benefit = ''
    try:
        # Field: customfield_12221 -> Future Economic Benefit
        for idx, b in enumerate(issue_epic.fields.customfield_12221):
            benefit += b.value
            if idx < len(issue_epic.fields.customfield_12221) - 1:
                benefit += ", "
    except:
        benefit = "None"

    epic_dict[key] = {'issue_type': issue_type, 'key': key, 'summary': summary, 'reporter': reporter,
                      'status': status, 'created': created, 'updated': updated, 'resolved': resolved,
                      'benefit': benefit, 'project_name': project_name, 'project_lead': project_dict["project_lead"],
                      'category': category}
    return epic_dict


def add_row_report(epic_dict, output):
    """
    Add row in the CSV file or in the "screen" (prettytable)
    :param epic_dict:
    :param output:
    """
    for k in epic_dict:
        row_epic = [epic_dict[k]['issue_type'], epic_dict[k]['key'], epic_dict[k]['summary'],
                    epic_dict[k]['reporter'], epic_dict[k]['status'], epic_dict[k]['created'],
                    epic_dict[k]['updated'], epic_dict[k]['resolved'], epic_dict[k]['benefit'],
                    epic_dict[k]['project_name'], epic_dict[k]['project_lead'], epic_dict[k]['category'],
                    epic_dict[k]['person_1'], epic_dict[k]['person_2'],
                    epic_dict[k]['person_3'], epic_dict[k]['person_4'], epic_dict[k]['person_5'],
                    epic_dict[k]['person_6'], epic_dict[k]['person_7'], epic_dict[k]['total_days']]
        if output == "csv":
            writer.writerow(row_epic)
        elif output == "screen":
            epic_table.add_row(row_epic)


# Working hours validation
def validate_working_days(board, start_date, end_date, report_dict):
    """
    Validate if the total working days logged make sense according to the month working days and number of people that
    worked in this project.
    :param board:
    :param start_date:
    :param end_date:
    :param report_dict:
    """
    period_days = period_working_days(start_date, end_date)
    maximum_days_allowed = len(report_dict['persons']) * period_days
    if report_dict['total_working_report'] > maximum_days_allowed:
        print(
            f'WARNING: BOARD {board} - During the period {start_date} to {end_date} has {period_days} working days and it was logged '
            f'{report_dict["total_working_report"]} ({report_dict["total_working_report"] / len(report_dict["persons"])}'
            f' per person in average). The maximum allowed should be {maximum_days_allowed} days')


def generate_report(projects):

    if not projects:
        projects = get_projects()

    projects_analyzed = 0

    audit_table = PrettyTable()

    for board in projects:
        projects_analyzed += 1

        logging.info(
            f'\nAnalysing Project: {board} {projects_analyzed}/{len(projects)}')

        epic_dict = {}
        report_dict = {'total_working_report': 0, 'persons': []}

        project_dict = {'project_lead': None}

        # Only epics that are capitalizable
        for issue_epic in jira.search_issues(
                f'PROJECT IN ("{board}") AND ISSUETYPE = "Epic" AND "Is Capitalizable?" = "Yes"'):
            task_person_dict = {}

            epic_dict = get_epic_information(epic_dict, issue_epic, project_dict)
            key = issue_epic.key
            epics_changed_in_period = []

            # Only Tasks that were "resolved" in the specific period of time
            logging.info(f'\nTasks that belongs to the EPIC "{issue_epic.key}" that was resolved between {start_date} and {end_date}')
            for issue_task in jira.search_issues(
                    f'PROJECT IN ("{board}") AND ("EPIC LINK" = "{issue_epic.key}" OR parentEpic = "{issue_epic.key}") AND '
                    f'resolved >= "{start_date}" '
                    f'AND resolved <= "{end_date}"'):

                task_info = get_task_info(issue_task)
                pairee = get_task_info_pairee(issue_task)

                # Epic, story and bug must be ignored in this analyze
                if task_info[issue_task]["task_issuetype"] not in ["Epic", "Story", "Bug"] and \
                        task_info[issue_task]['task_time'] != None:
                    task_person_dict = time_calculation_person(task_person_dict, issue_task)
                    epics_changed_in_period.append(issue_epic.key)
                    # try:
                    #     audit_table.add_row([key, issue_task, task_info[issue_task]["task_assignee"], task_info[issue_task]["task_time"]/28800, task_info[issue_task]["task_resolutiondate"]])
                    # except Exception as e:
                    #     logging.info(e)
                    #     logging.info("Error:")
                    #     logging.info(f"Task: {issue_task}")
                    #     logging.info(f"Task Time: {task_info[issue_task]['task_time']}")

                    if pairee:
                        # task_person_dict = time_calculation_person_pairee(pairee, task_person_dict, issue_task)
                        # audit_table.add_row([key, issue_task, pairee,
                        #                      task_info[issue_task]["task_time"] / 28800, task_info[issue_task]["task_resolutiondate"]])
                        cur.execute(
                            "INSERT INTO itcap (epic, task, epic_summary, task_summary, task_assignee, task_time, task_resolutiondate, pairee) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                str(issue_epic.key),
                                str(issue_task),
                                str(issue_epic.fields.summary),
                                str(task_info[issue_task]["task_summary"]),
                                str(pairee),
                                str(task_info[issue_task]["task_time"] / 28800),
                                str(task_info[issue_task]["task_resolutiondate"]),
                                1
                            )
                            )

                    logging.info(f'{issue_task} - Assigned: {task_info[issue_task]["task_assignee"]} - '
                                 f'Time: {task_info[issue_task]["task_time"]}s ({task_info[issue_task]["task_time"]/28800} days) - '
                                 f'Resolution: {task_info[issue_task]["task_resolutiondate"]} - '
                                 f'IssueType: {task_info[issue_task]["task_issuetype"]}')

                    cur.execute("INSERT INTO itcap (epic, task, epic_summary, task_summary, task_assignee, task_time, task_resolutiondate, pairee) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                str(issue_epic.key),
                                str(issue_task),
                                str(issue_epic.fields.summary),
                                str(task_info[issue_task]["task_summary"]),
                                str(task_info[issue_task]["task_assignee"]),
                                str(task_info[issue_task]["task_time"]/28800),
                                str(task_info[issue_task]["task_resolutiondate"]),
                                0
                            )
                        )
                    con.commit()

            total_working_days = 0

            # Prepare report - people that worked in the epic and calculate the total working days spent
            # for i, person in enumerate(task_person_dict):
            #     seconds = task_person_dict[person]
            #     if seconds and seconds != 0 and isinstance(seconds, int):
            #         working_days = seconds / 28800  # 8 hours = 1 working day
            #     else:
            #         if not isinstance(seconds, int):
            #             logging.info(f"[WARNING] {person} {seconds}")
            #             logging.info("[WARNING] Seconds is not an integer")
            #         working_days = 0
            #     total_working_days += working_days
            #
            #     epic_dict[key].update({"person_{}".format(i + 1): person})
            #
            #     report_dict['total_working_report'] += working_days
            #     if person not in report_dict['persons']:
            #         report_dict['persons'].append(person)

            # Fill empty spots in the report (person column)
            # if len(task_person_dict) < 7:
            #     for i in range(len(task_person_dict), 7):
            #         epic_dict[key].update({"person_{}".format(i + 1): "-"})

            # Add total working days in the dictionary or delete epic from the report
            # epic_dict[key].update({"total_days": total_working_days}) # REMOVER
            # Delete epic that was not changed in that specific period of time
            if key not in epics_changed_in_period:
                epic_dict.pop(key)

        # add_row_report(epic_dict, output)

        # validate_working_days(board, start_date, end_date, report_dict)

        # Audit
        # audit_table.field_names = ["Epic", "Issue", "Assigned", "Days", "Resolved"]
        # print(f"\n{audit_table}")


if __name__ == '__main__':

    # header = ["Issue Type", "Key", "Summary", "Reporter", "Status", "Created", "Updated", "Resolved",
    #           'Future Economic Benefit', "Project Name", "Project Lead", "Category", "Team Member 1", "Team Member 2",
    #           "Team Member 3", "Team Member 4", "Team Member 5", "Team Member 6", "Team Member 7", "Total Days"]

    # if output == "csv":
    #     csv_file = 'it-cap.csv'
    #     f = open(csv_file, 'w')
    #     writer = csv.writer(f, dialect='excel')
    #     writer.writerow(header)
    #
    # elif output == "screen":
    #     epic_table = PrettyTable()
    #     epic_table.field_names = header

    generate_report(projects)

    # if output == "csv":
    #     print(f"\nFile {csv_file} was created")
    #     f.close()
    # elif output == "screen":
    #     print(f"\n{epic_table}")

