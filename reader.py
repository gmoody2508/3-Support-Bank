import csv
import json
import sys
import logging
import datetime
import xml.etree.ElementTree as ET
from transaction import Transaction
from transaction import TransactionSum

logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

#filename=input('Which file would you like to open? ')
filename='Transactions2014.csv'
logging.info("User chose to open "+ str(filename))
filetype=filename.split(".")[-1]
option=input("Select '1' to list value in credit/debit for each employee. Select '2' to list all transactions for a given name. Select 3 to exit")
output_option=input("Provide filename to write results to (press RETURN to print to terminal)")
#Function checks if date format is d/m/y, returns true or false
def datetype1(date):
    try:
        datetime.datetime.strptime(date, "%d/%m/%Y")
        return True
    except ValueError as error:
        logging.info(error)
        return False

#Function checks if date format is y-m-d, returns true or false
def datetype2(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError as error:
        logging.info(error)
        return False

#Functions converts xml date format to y-m-d format
def xmldate(date):
    temp=datetime.date(1900,1,1)
    delta=datetime.timedelta(days=date)
    date=temp+delta
    return date

#Function rounds number to 2 d.p
def rounder(number):
    number=round(number,2)
    number=str(number)
    number_split = number.split('.')
    if len(number_split[1]) != 2:
        number = number + '0'
    return number

#Function calculates net balance for each employee
def sum_all(input,to_index,from_index,val_index):
    names = {}
    i=1
    for line in input:
        debtor = line[from_index]
        creditor = line[to_index]
        try:
            val = float(line[val_index])
        except ValueError:
            logging.info(line[val_index]+" is not a valid price. Please check datafile")
            print("ERROR on line "+str(i+1)+" of '"+filename+"'. Check the logfile for more details!")
            continue
        if debtor in names.keys():
            names[debtor] = names[debtor] - val
        else:
            names[debtor] = -val
        if creditor in names.keys():
            names[creditor] = names[creditor] + val
        else:
            names[creditor] = val
        i=i+1
    for name in names:
        final_val=names[name]
        final_val=rounder(final_val)
        person_sum = TransactionSum(name, final_val)
        if output_option:
            with open(output_option,'a') as outfile:
                person_sum=str(person_sum)
                outfile.write(person_sum+"\n")
        else:
            print(person_sum)

#Intially determines filetype csv, json or xml
with open(filename) as input:
    if filetype == 'json':
        logging.info("Opening JSON file "+ str(input))
        input = json.load(input)
        header=[]
        for key in input[0]:
            header.append(key.lower())
    elif filetype == 'csv':
        logging.info("Opening CSV file " + str(input))
        input=csv.reader(input,delimiter=',')
        top_row=next(input)
        header=[]
        for word in top_row:
            header.append(word.lower())
    elif filetype == 'xml':
        logging.info("Opening XML file " + str(input))
        input=[]
        header=['date', 'from', 'to', 'narrative', 'amount']
        input.append(header)
        tree=ET.parse(filename)
        root=tree.getroot()
        for entry in root:
            line=[]
            date=list(entry.attrib.items())
            date=date[0][1]
            date=int(date)
            date=xmldate(date)
            date=str(date)
            line.append(date)
            for cell in entry:
                if cell.tag == 'Parties':
                    for person in cell:
                        if person.tag == 'From':
                            line.append(person.text)
                        elif person.tag == 'To':
                            line.append(person.text)
            for cell in entry:
                if cell.tag == 'Description':
                    line.append(cell.text)
            for cell in entry:
                if cell.tag == 'Value':
                    line.append(cell.text)
            input.append(line)
        #file=outfile
    i=0
    for word in header:
        if 'date' in word:
            date_index=i
        elif 'to' in word:
            to_index=i
        elif 'from' in word:
            from_index=i
        elif 'narrative' in word:
            note_index=i
        elif 'amount' in word:
            val_index=i
        i=i+1
    if filetype == 'json':
        outfile=[]
        for line in input:
            newline=[]
            line=line.items()
            for x in line:
                newline.append(x[1])
            outfile.append(newline)
        input=outfile
    if option == '1':
        logging.info("User selected View All")
        sum_all(input,to_index,from_index,val_index)

    elif option == '2':
        logging.info("User selected List[Name]")
        i=1
        name = input("Please give name of account holder")
        logging.info("User inputted account name "+ name)
        account = False
        for line in input:
            debtor = line[from_index]
            creditor = line[to_index]
            if name == debtor or name == creditor:
                account = True
                number=line[val_index]
                number=float(number)
                number=rounder(number)
                Account=Transaction(line[date_index],debtor,creditor,line[note_index],number)
                if datetype1(line[date_index]):
                    pass
                elif datetype2(line[date_index]):
                    temp=datetime.datetime.strptime(line[date_index], "%Y-%m-%d")
                    temp=temp.strftime('%d/%m/%Y')
                    line[date_index]=str(temp)
                else:
                    print("DATE ON LINE " + str(i) + " IS NOT A VALID DATE FORMAT!!")
                    logging.info(line[date_index] + "on line " + str(i) + " is not a valid date format.")
                if output_option:
                    with open(output_option, 'a') as outfile:
                        Account = str(Account)
                        outfile.write(Account + "\n")
                else:
                    print(Account)
                print(Account)
            i=i+1
        if not account:
            print("Account does not exist!")
            logging.info("User Entered: "+name+". This is not a valid account name!")
    elif option == '3':
        sys.exit()
    else:
        print("Bad Input!")
        logging.info("User Entered: "+option+". This is not a valid input!")