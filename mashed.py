#!/usr/bin/env python3
'''''''''''''''''''''''''''''
COPYRIGHT FETCH DEVELOPMENT,
2020-2022

'''''''''''''''''''''''''''''

from __future__ import print_function
import requests
import os
import sys
import re

HEADERS = {
	"Content-Type": "application/json",
	"Accept": "application/json;charset=UTF-8",
	"Accept-Language": "ru",
	#"Accept-Encoding": "gzip, deflate, br",
	"Host": "uchebnik.mos.ru",
	"Cache-Control": "no-cache",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
	"Connection": "keep-alive",
	"Referer": "https://uchebnik.mos.ru/exam/test/test_by_binding/9027558/homework/117518999/variant/18878473/num/1?generation_context_type=homework&registration=2a86e7e2-edff-28db-12c4-ba2e99a924cb",
	"Cookie": "", #Your cookies go here
	}

VARIANT = 19992612 #Your variant number goes here

RED = "\033[31m"
GRN = "\033[32m"
ORG = "\033[33m"
YEL = "\033[93m"
BLD = "\033[1m"
RES = "\033[0m"

def report_error(code):
	print(f'{RED + BLD}ERROR:{RES} Got {code} response code.')
	exit(-1)

tasks_count = 0
tasks = []
print(f'{ORG + BLD}SERVING{RES} headers... ', end="")
r = requests.get(f"https://uchebnik.mos.ru/exam/rest/secure/testplayer/variant/{VARIANT}", headers = HEADERS)
if r.status_code != 200:
	report_error(r.status_code)
else:
	resp_json = r.json()
	print(f'{GRN + BLD}SUCCESS{RES}')
	tasks_count = resp_json['tasks_count']
	print(f'{GRN + BLD}FOUND {RES}test with {BLD + str(tasks_count) + RES} questions')

print(f'{ORG + BLD}RETRIEVING{RES} task instances...')
for i in range(0, tasks_count):
	g = requests.get(f"https://uchebnik.mos.ru/exam/rest/secure/api/test_task/{VARIANT}/{i + 1}", headers = HEADERS)
	if g.status_code != 200:
		report_error(g.status_code)
	else:
		task_json = g.json()
		#tasks.append({"name": task_json['question_elements'][0]['text'], "id": task_json['id']})
		tasks.append(task_json)
		print(f'{GRN + BLD}RETRIEVED {RES + BLD + str(i + 1)}/{str(tasks_count) + RES}')

print(f'{ORG + BLD}RETRIEVING{RES} answers... ', end="")
r = requests.get(f"https://uchebnik.mos.ru/exam/rest/secure/api/answer/variant/{VARIANT}", headers = HEADERS)
if r.status_code != 200:
	report_error(r.status_code)
else:
	resp_json = r.json()
	print(f'{GRN + BLD}SUCCESS{RES}')
	print(f'{ORG + BLD}COMPARING{RES} data... ')
	found_answers = []
	for i in resp_json:
		if len(found_answers) == tasks_count:
			break
		#https://uchebnik.mos.ru/exam/rest/secure/api/test_task/18878473/1
		g = requests.get(f"https://uchebnik.mos.ru/exam/rest/secure/api/test_task/{VARIANT}/{i}", headers = HEADERS)
		tid = i['task_id']
		if i['answer_status'] == "correct" and tid not in found_answers:
			for j in tasks:
				if j['id'] == tid:
					match i['given_answer']['@answer_type']:
						case "answer/single":
							for k in j['answer']['options']:
								if k['id'] == i['given_answer']['id']:
									answer = k['content'][0]['content'] if k['content'] else k['text']
						case "answer/multiple":
							answer = ""
							for k in j['answer']['options']:
								if k['id'] in i['given_answer']['ids']:
									answer += (k['content'][0]['content'] if k['content'] else k['text'] + "; ")
						case "answer/number":
							answer = str(i['given_answer']['number'])
						case "answer/string":
							answer = str(i['given_answer']['string'])
						case "answer/groups":
							answer = ""
							for i_group in i['given_answer']['groups']:
								for k in j['answer']['options']:
										if k['id'] == i_group['group_id']:
											answer += ('GROUP "' + k['content'][0]['content'] if k['content'] else k['text'] + '": ')
								for i_opt in i_group['options_ids']:
									for k in j['answer']['options']:
										if k['id'] == i_opt:
											answer += (k['content'][0]['content'] if k['content'] else k['text'] + "; ")
						case "answer/match":
							answer = ""
							for k in j['answer']['options']:
								if k['id'] in i['given_answer']['match']:
									answer += k['text'] + " => "
									for i_match in j['answer']['options']:
										for m in i['given_answer']['match'][k['id']]:
											if i_match['id'] == m:
												answer += (i_match['content'][0]['content'] if i_match['content'] else i_match['text']) + "; "
						case _:
							answer = f"<TYPE {i['given_answer']['@answer_type']} NOT SUPPORTED>"
					print(f"{GRN + BLD}Found {RES}correct answer:")
					print(f"     {BLD}Q:{RES} '" + j['question_elements'][0]['text'].replace("\u00AD", '').replace("\n", "\n     ") + "'")
					print(f'     {BLD}A:{RES} ' + answer.replace("\u00AD", '').replace("\n", "\n     ") + RES)
					break
			found_answers.append(tid)
	print(f'{BLD}{len(found_answers)}/{tasks_count}{RES} answers found')
	print(f"This is the last time 'mashed.py' is being run. \nIt's been fun two years.\nSo long.")
	print("========================================================")
