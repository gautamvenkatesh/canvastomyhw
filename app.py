import requests
import json
from lxml import html
import mysql.connector
import datetime
from bs4 import BeautifulSoup as bf

def startup():
    canvas_req = requests.session()
    #Create canvas API key and replalce the hashes
    header = {'Authorization' : 'Bearer ##################'}
    #Add your nickname for a class before the colon, and the name of the class on canvas after. Example below
    class_dict = {'EECS16a': "EECS 16A and EECS47D",
                  'CS61a': "COMPSCI 61A - LEC 001",
                  'INTEGBI35AC': "INTEGBI 35AC",
                  'SASIAN140' : "SASIAN 140 - LEC 001"}
    what_class = input('Please input the class: ')
    if what_class in class_dict:
        search_class = class_dict[what_class]
    else:
        print('Not valid class')
        exit()
    #Replace beginning of url (before 'api') with your canvas url for your school for each url
    courses = json.loads(canvas_req.get('https://bcourses.berkeley.edu/api/v1/courses/', headers = header).text)
    course_id = ''
    for course in courses:
        if course['course_code'] == search_class:
            course_id = course['id']
    url = f'https://bcourses.berkeley.edu/api/v1/courses/{course_id}/assignments/'
    result = canvas_req.get(url, headers = header)
    return json.loads(result.text), what_class

def date_time_title(assignments, the_class):
    date_list = []
    time_list = []
    title_list = []
    for i,val in enumerate(assignments):
        x = val['due_at']
        date = datetime.today()
        date = date.strftime("%m/%d/%y")
        time = '11:59'
        c = 0
        if x:
            date = ''
            time = ''
            for i in x:
                if i == 'T': c = 1
                if c == 0: date+=i
                elif c == 1: time+=i
            time = time[1:len(time)-1]
            date = date.replace('-', '/')
            date = date[5:] + '/' + date[:4]
        date_list.append(date)
        time_list.append(time)
        if 'name' in val:
            title_list.append(val['name'])
        elif 'title' in val:
            title_list.append(val['title'])
        else:
            title_list.append('No Title')
    return {'title' : title_list, 'times' : time_list, 'dates' : date_list, 'class': [the_class] * len(title_list)}

def add_hw(title, due, time, the_class):
    session = requests.session()
    url = 'https://myhomeworkapp.com/login'
    #Add user and pass for myHomework app
    data = {
        'username' : '##########',
        'password' : '##########'
    }
    hw_login = session.get(url)
    tree = html.fromstring(hw_login.text)
    data['csrfmiddlewaretoken'] = list(set(tree.xpath("//input[@name = 'csrfmiddlewaretoken']/@value")))[0]
    hw_login_response = session.post(url, data = data, headers = dict(referer = url))
    hw_add = session.get('https://myhomeworkapp.com/homework/add')
    soup = bf(hw_add.text, 'html.parser')
    req_class = ''
    for i in soup.find_all('option'):
        if i.text == the_class:
            req_class = i['value']
    hw_data = {
        'title' : title,
        'cls' : req_class,
        'type' : 1,
        'due_date' : due,
        'due_time' : time,
        'repeats' : 0,
        'save' : 'Save'
    }
    tree2 = html.fromstring(hw_add.text)
    hw_data['csrfmiddlewaretoken'] = list(set(tree2.xpath("//input[@name = 'csrfmiddlewaretoken']/@value")))[0]
    submit_url = 'https://myhomeworkapp.com/homework/add'
    hw_submit = session.post(submit_url, data = hw_data, headers = dict(referer = submit_url))
    print(hw_submit)
    return 0

def check_new_hw(assignments, the_class):
    print(assignments)
    if not assignments:
        print('No assignments in this class')
        exit()
    #replace with mysql server login details
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="########",
        )
    cursor = mydb.cursor(buffered = True)
    cursor.execute('use  homework')
    cursor.execute('select homework from hmwrk')
    previous = dict()
    new = []
    for i in cursor.fetchmany(30):
        previous[i[0]] = True
    for hw in assignments:
        if str(hw['id']) not in previous:
            new.append(hw)
            cursor.execute(f"insert into hmwrk values ('{hw['id']}')")
    mydb.commit()
    cursor.close()
    return new, the_class
