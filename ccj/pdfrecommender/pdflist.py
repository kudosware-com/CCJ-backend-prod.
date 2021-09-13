'''
tables: 
    1. word --> id,word,pdf_id,count
    2. pdf  --> id,filename,description

example files:
    p1 = "django is python framework"
    p2 = "python have django framework"
    p3 = "python have many framework including django framework also we can use python for data processing"

'''
import time
import pymssql
import re
from ccj import settings
from datetime import datetime

def getTime():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

def make_connection():
    '''
    Making connection with database
    '''
    global cnx
    global cursor

    cnx = pymssql.connect(server="infabrandsdb.database.windows.net",user="infabrandsdb",password="dbpassword@123",database="infabrandsdb")
    cursor = cnx.cursor()


def break_connection():
    '''
    Close connection
    '''
    cnx.close()


def recommend_pdf(exp):
    '''
    Return list of all the file which match the expression in some order
    in Descending order with score
    '''
    parts, keys = get_parts_of_expression(exp)
    keys = normalize(keys)
    get_word_dict(keys)
    files, files_keys_bool = get_relevant_files(keys)
    for file in files:
        # If files satisfies the expression its score is worth more than partial match so +10000
        if does_file_satisfies_expression(file, files_keys_bool, parts.copy(), keys):
            files[file] += 10000

    files_and_score = list(files.items())
    files_and_score.sort(reverse=True, key=comp)
    filename_and_score = list()

    print("score: ",files_and_score)
    for i in range(len(files_and_score)):
        query = "SELECT filename,local_url FROM pdf WHERE id={part};".format(part=files_and_score[i][0])
        cursor.execute(query)
        res = cursor.fetchall()
        filename_and_score.append([res[0][0],res[0][1])

    return filename_and_score,keys

def get_parts_of_expression(exp):
    '''
    parsing expression to get operators and operands
    keys = operands and parts = operators
    '''
    exp = exp.lower()
    parts = list()
    keys = list()
    number = 0
    letter = ""

    for char in exp :
        if char in ('(', ')', '|', '&'):
            letter = letter.strip()
            if letter != "" and letter != " " :
                number += 1
                # Get all the operator's index
                parts.append(number - 1)
                # Get all the individual phrases
                keys.append(letter)
                letter = ""
            parts.append(char)
        else:
            letter += char

    return parts, keys

def get_word_dict(keys):
    '''
    to associate each word with pdf with furthur maps to list of position where word occurs
    '''
    global words
    words = dict()

    keys_seperated = []
    for i in range(len(keys)):
        tp = keys[i].strip(" ")
        tp = tp.strip(",")
        keys_seperated.append(tp.strip(","))

    if len(keys_seperated) > 0:
        query_part = "word='{word}'".format(word=keys_seperated[0])

        for i in range(1, len(keys_seperated)):
            key = keys_seperated[i]
            query_part = query_part + " or word='{word}'".format(word=key)
        future_qp = query_part
        # get id,pdf_id and word for every word
        query = "SELECT id,pdf_id,word,count FROM word WHERE {part};".format(part=query_part)
        cursor.execute(query)
        res = cursor.fetchall()
        
        if len(res) > 0:
            for i in range(len(res)):
                current_pdf = res[i][1]
                current_word = res[i][2]
                current_count = res[i][3]

                if(current_word in words):
                    words[current_word][current_pdf] = current_count
                else:
                    words[current_word] = dict()
                    words[current_word][current_pdf] = current_count



        # if len(res) > 0:
        #     # get index of all words
        #     query = "SELECT word, count,pdf_id FROM word WHERE {part};".format(part=future_qp)
        #     cursor.execute(query)   
        #     res = cursor.fetchall()
        #     # storing position of each word in file
        #     for i in range(len(res)):
        #         current_word = res[i][0]
        #         current_pdf_id = res[i][2]
        #         if current_word in words:    
        #             if current_pdf_id in words[current_word]:
        #                 positions = list()
        #                 position_string = res[i][1]
        #                 position_string = position_string[1:-1]
        #                 positions = position_string.split(',')
        #                 for i in range(len(positions)):
        #                     positions[i] = int(positions[i].strip())
        #                 for pos in positions:
        #                     words[current_word][current_pdf_id].append(pos)
        #             else:
        #                 words[current_word][current_pdf_id] = list()
        #                 positions = list()
        #                 position_string = res[i][1]
        #                 position_string = position_string[1:-1]
        #                 positions = position_string.split(',')
        #                 for i in range(len(positions)):
        #                     positions[i] = int(positions[i].strip())
        #                 for pos in positions:
        #                     words[current_word][current_pdf_id].append(pos)
        #         else:
        #             words[current_word] = {current_pdf_id:[]}
        #             position_string = res[i][1]
        #             position_string = position_string[1:-1]
        #             positions = position_string.split(',')
        #             for i in range(len(positions)):
        #                 positions[i] = int(positions[i].strip())
        #             for pos in positions:
        #                 words[current_word][current_pdf_id].append(pos)
    return

def get_relevant_files(keys):
    '''
    Returns files and also dictionary whether key is present in specific pdf or not
    '''
    files_list = dict()
    files_listBool = dict()
    for key in keys:
        # for checking consecutive sequence of word
        # also firstWordSet is prefix list 
        firstWordSet = dict()
        if key in words:
            firstWordSet = words[key]        
        # Add base score to each file (no. of matches)
        for pdf in firstWordSet:
            if pdf in files_list:
                files_list[pdf] += firstWordSet[pdf]
            else:
                files_list[pdf] = firstWordSet[pdf]

            if pdf in files_listBool:
                files_listBool[pdf][key] = True
            else:
                files_listBool[pdf] = dict()
                files_listBool[pdf][key] = True

    return files_list, files_listBool

def normalize(keyparts):
    '''
    Remove empty keys and trim every keyparts
    '''
    res = list()
    for i in keyparts:
        if(i == ''):
            continue
        else:
            res.append(i.strip())
    return res

def intersection_of_two_list(arr1, arr2):
    '''
    check whether next word is consecutive to previous prefix words
    '''
    i, j = 0, 0
    m = len(arr1)
    n = len(arr2)
    result = list()

    while i < m and j < n:
        if arr1[i] < arr2[j]:
            if arr2[j] - arr1[i] == 1:
                result.append(arr2[j])
                j += 1
            i += 1
        elif arr2[j] < arr1[i]:
            j += 1

    return result

def does_file_satisfies_expression(filename, keys_bool, parts, keys):
    '''
    returns 1 if whole expression is satisfied
    '''
    for i in range(len(parts)):
        if parts[i] not in ('(', ')', '|', '&'):
            word = keys[parts[i]]
            if word in keys_bool[filename]:
                parts[i] = 1
            else:
                parts[i] = 0

    stack = list()

    for i in range(len(parts)):
        if parts[i] != ')':
            stack.append(parts[i])
        else:
            while stack[-1] != '(':
                if stack[-2] in ('|', '&'):
                    a = stack[-1]
                    b = stack[-3]
                    op = {True: 'or', False: 'and'}[stack[-2] == '|']
                    c = {True: a or b, False: a and b}[op == 'or']
                    stack.pop()
                    stack.pop()
                    stack.pop()
                    stack.append(c)
                else:
                    c = stack[-1]
                    stack.pop()
                    stack.pop()
                    stack.append(c)
                    break
    return stack[0]
def comp(e):
    return e[1]

#Prequisites
def preq():
    print("preq start")
    make_connection()
    print("preq done")
