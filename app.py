#!/usr/bin/python

import sys, getopt

from dateutil.parser import parse
import argparse

from jira import JIRA


class JiraMetrics(object):
	WORKFLOW = {
		'Open': 'Idle',
		'Backlog': 'Idle',
		'Reopened': 'Idle',
		'Blocked': 'Idle',
		'Selected for Development': 'Idle',
		'Verified': 'Idle',
		'In Development': 'Development',
		'In Progress': 'Development',
		'In Review': 'Code Review',
		'Awaiting PM Review': 'PM Review',
		'In PM Review': 'PM Review',
		'Closed': 'Done',
		'Resolved': 'Done'
	}

	def __init__(self, username, password, board_id, sprint_id, server='https://issues.liferay.com'):
		self.jira = JIRA(server=server, basic_auth=(username, password))

		self.board_id = board_id
		self.sprint_id = sprint_id

	def sprint_completed_issues(self):
		return self.jira.completed_issues(self.board_id, self.sprint_id)

	def sprint_completed_issues_count(self):
		completed_issues = self.sprint_completed_issues()

		return len(completed_issues)

	def sprint_incompleted_issues(self):
		return self.jira.incompleted_issues(self.board_id, self.sprint_id)

	def sprint_incompleted_issues_count(self):
		incompleted_issues = self.sprint_incompleted_issues()

		return len(incompleted_issues)

	def sprint_progress(self):
		completed_issues_count = self.sprint_completed_issues_count()
		incompleted_issues_count = self.sprint_incompleted_issues_count()

		total_issues_count = completed_issues_count + incompleted_issues_count

		return (completed_issues_count / float(total_issues_count)) * 100

	def get_issue_swimlanes_metrics(self, issue_key):
		issue = self.jira.issue(issue_key, expand='changelog')

		issue_created_date = self.__parse_date(issue.fields.created)
		issue_status_histories = self.__get_issue_status_hitories(issue)

		sorted_issue_status_histories_keys = sorted(issue_status_histories.keys())

		swimlanes_metrics = {
			'Idle': {
				'delta': None,
				'last_execution_date': issue_created_date
			},
			'Development': {
				'delta': None,
				'last_execution_date': None
			},
			'Code Review': {
				'delta': None,
				'last_execution_date': None
			},
			'PM Review': {
				'delta': None,
				'last_execution_date': None
			},
			'Done': {
				'delta': None,
				'last_execution_date': None
			}
		}

		for history_key in sorted_issue_status_histories_keys:
			transition = issue_status_histories[history_key].split('#')

			transition_from = transition[0]
			transition_to = transition[1]
			transition_date = self.__parse_date(transition[2])

			from_swimlanes_key = self.WORKFLOW[transition_from]
			to_swimlanes_key = self.WORKFLOW[transition_to]

			from_swimlane = swimlanes_metrics[from_swimlanes_key]
			to_swimlane = swimlanes_metrics[to_swimlanes_key]

			if from_swimlane['delta'] == None:
				from_swimlane['delta'] = transition_date - from_swimlane['last_execution_date']
			else:
				from_swimlane['delta'] = from_swimlane['delta'] + (transition_date - from_swimlane['last_execution_date'])

			to_swimlane['last_execution_date'] = transition_date

		return swimlanes_metrics

	def __get_issue_status_hitories(self, issue):
		issue_status_histories = {}

		for history in issue.changelog.histories:
			for item in history.items:
				if item.field == 'status':
					issue_status_histories[history.id] = item.fromString + '#' + item.toString + '#' + history.created

		return issue_status_histories

	def get_sprint(self, sprint_id):
		pass

	def __parse_date(self, date_str):
		return parse(date_str)

	def __date_difference_in_seconds(date1, date2):
		delta = date1 - date2
		return delta.seconds

def print_issues_list(jiraMetrics, issues):
	for issue in issues:
		print '\t\thttps://issues.liferay.com/browse/%s' % issue.key

		swimlanes_metrics = jiraMetrics.get_issue_swimlanes_metrics(issue.key)

		print '\t\t\tIdle: %s' % swimlanes_metrics['Idle']['delta']
		print '\t\t\tDevelopment: %s' % swimlanes_metrics['Development']['delta']
		print '\t\t\tCode Review: %s' % swimlanes_metrics['Code Review']['delta']
		print '\t\t\tPM Review: %s' % swimlanes_metrics['PM Review']['delta']

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-u', '--username', required=True, metavar='<JIRA username>')
	parser.add_argument('-p', '--password', required=True, metavar='<JIRA password>')

	args = parser.parse_args()

	jiraMetrics = JiraMetrics(args.username, args.password, 1718, 3946)

	print '---------------------'
	print 'Sprint Metrics Report'
	print '---------------------'
	print '\tSprint Progress: %d' % jiraMetrics.sprint_progress()
	print '\tCompleted Issues:'
	print_issues_list(jiraMetrics, jiraMetrics.sprint_completed_issues())

	print '\tIncompleted Issues:'
	print_issues_list(jiraMetrics, jiraMetrics.sprint_incompleted_issues())