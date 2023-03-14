from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
from json.decoder import JSONDecodeError
from pathlib import Path
import math

MyFiPlan_Path = Path("./MyFiPlan.json")

Today = datetime.today().date()

MyFiPlan_Path.touch(exist_ok=True)
with open(MyFiPlan_Path) as json_file:
    try:
        MyFiPlan = json.load(json_file)
    except JSONDecodeError:
        currency = input("What is your plan currency? (Use ISO4217 format)")
        current_saving_power = input("What is your monthly saving power? (Include all your loans and current investments)")
        dateOf_birth = input("What is your date birth date? (YYYY-mm-dd format)")
        expected_lifeExp = input("What is your life expectancy age?")
        expectedDateOf_death = datetime.strptime(dateOf_birth, "%Y-%m-%d") + relativedelta(years=int(expected_lifeExp))
        years_left = expectedDateOf_death.year - Today.year
        expectedYearly_inflation = input("What is the average expected yearly inflation for the next " + str(years_left) + " years? (from 0 to 100)")

        MyFiPlan = {
            "info": {
                "currency": currency,
                "current_saving_power": current_saving_power,
                "dateOf_birth": dateOf_birth,
                "expectedYearly_inflation": float(expectedYearly_inflation)/100,
                "expectedDateOf_death": expectedDateOf_death.strftime("%Y-%m-%d"),
                "lastgoal_index": 0,
                "lastenvelop_index": 0
            },
            "data": {
            }
        }


def printFiPlan(myfiplan):
    for goal in myfiplan['data']:
        print("["+goal+"] ("+myfiplan['data'][goal].get('type')+") " + myfiplan['data'][goal].get('name'))
    print("What would you like to do ?")
    resp = input("Type 'A' to add a goal; its index number to modify or delete it ; 'Q' to exit ")
    if resp == "A":
        addFiGoal(myfiplan)
    elif resp == "Q":
        with open(MyFiPlan_Path, 'w') as outfile:
            json.dump(myfiplan, outfile, indent=4)
        exit(0)
    else:
        modFiGoal(resp, myfiplan)
    return 0


def addFiGoal_Loan():
    name = input("Name of this loan? ")
    monthly_reimb = input("Your monthly reimbursement? ")
    lefttoreimb = input("How much left to reimburse? ")
    endOf_date = input("When will be the last reimbursement? (YYYY-mm-dd format) ")
    return {
        "type": "Loan",
        "name": name,
        "endOf_date": endOf_date,
        "envelops": {
            "0": {
                "name": name + " reimb account",
                "current_balance": -float(lefttoreimb),
                "expected_growthYield": 0.0,
                "expected_dividendYield": 0.0,
                "monthly_invest": float(monthly_reimb)
            }
        }
    }


def addFiGoal_Generic():
    name = input("Name of this goal? ")
    goal_amount = input("What is your goal amount? ")
    endOf_date = input("When do you want to achieve this goal? (YYYY-mm-dd format) ")
    return {"type": "Generic", "name": name, "goal": float(goal_amount), "endOf_date": endOf_date, "envelops": {}}


def addFiGoal_Emergency(current_saving_power):
    name = "Emergency goal"
    goal_amount = input("What is your emergency found goal amount? ")
    current_balance = input("How much you have save already? ")
    print("You have " + str(current_saving_power) + " monthly power saving. You should first totaly use it in order to finish your emergency found as soon as possible")
    monthly_saving = input("Your monthly saving for your emergency found? ")
    endOf_date = datetime.today() + relativedelta(months=int(math.ceil((float(goal_amount) - float(current_balance)) / float(monthly_saving))))
    return {
        "type": "Emergency",
        "name": name,
        "goal": float(goal_amount),
        "endOf_date": str(endOf_date.date()),
        "envelops": {
            "0": {
                "name": name + " saving account",
                "current_balance": current_balance,
                "expected_growthYield": 0.0,
                "expected_dividendYield": 0.0,
                "monthly_invest": float(monthly_saving)
            }
        }
    }


def addFiGoal_Retirement(dateofbirth):
    name = input("Name of this retirement goal? ")
    goal_amout = input("What is your goal amount? ")
    retirement_age = input("At what age you planning to retire? (Should be lower than your life expectancy ;)")
    endOf_date = datetime.strptime(dateofbirth, "%Y-%m-%d") + relativedelta(years=int(retirement_age))
    return {"type": "Retirement", "name": name, "goal": float(goal_amout), "endOf_date": str(endOf_date.date()), "envelops": {}}


def addFiGoal(myfiplan):
    fiplan = myfiplan
    print("What type of goal to you want to add?")
    print("[L] Loan")
    print("[E] Emergency founds")
    print("[R] Retirement")
    print("[G] Generic goal")
    res = input("Your choice? ")

    if res == "L":
        fiplan['data'].update(
            {str(fiplan['info'].get('lastgoal_index')+1): addFiGoal_Loan()}
        )
        fiplan['info'].update({"lastgoal_index": fiplan['info'].get('lastgoal_index')+1})
    elif res == "G":
        fiplan['data'].update(
            {str(fiplan['info'].get('lastgoal_index') + 1): addFiGoal_Generic()}
        )
        fiplan['info'].update({"lastgoal_index": fiplan['info'].get('lastgoal_index') + 1})
    elif res == "E":
        fiplan['data'].update(
            {str(fiplan['info'].get('lastgoal_index') + 1): addFiGoal_Emergency(myfiplan)}
        )
        fiplan['info'].update({"lastgoal_index": fiplan['info'].get('lastgoal_index') + 1})
    elif res == "R":
        fiplan['data'].update(
            {str(fiplan['info'].get('lastgoal_index') + 1): addFiGoal_Retirement(fiplan['info'].get('dateOf_birth'))}
        )
        fiplan['info'].update({"lastgoal_index": fiplan['info'].get('lastgoal_index') + 1})
    printFiPlan(myfiplan)
    return fiplan


def modFiGoal(index, myfiplan):
    print("Details for " + myfiplan['data'][index].get('name') + ":")
    for k, v in myfiplan['data'][index].items():
        print(k, v)

    if myfiplan['data'][index].get('type') != "Loan":
        resp = input("'D' to delete, 'M' to modify, 'E' to manage goal envelops, 'A' to add an envelop or 'B' to go back to goal listing ")
    else:
        resp = input("'D' to delete or 'M' to modify ")

    if resp == "D":
        del myfiplan['data'][index]
    elif resp == "M":
        if myfiplan['data'][index].get('type') == "Loan":
            myfiplan['data'].update(
                {index: addFiGoal_Loan()}
            )
        elif myfiplan['data'][index].get('type') == "Emergency":
            myfiplan['data'].update(
                {index: addFiGoal_Emergency(myfiplan['info'].get('current_saving_power'))}
            )
        elif myfiplan['data'][index].get('type') == "Retirement":
            myfiplan['data'].update(
                {index: addFiGoal_Retirement(myfiplan['info'].get('dateOf_birth'))}
            )
        elif myfiplan['data'][index].get('type') == "Generic":
            myfiplan['data'].update(
                {index: addFiGoal_Generic()}
            )
    elif resp == "E":
        modEnvelops(myfiplan, index)
    elif resp == "A":
        addEnvelop(myfiplan, index)
        myfiplan['info'].update({"lastenvelop_index": myfiplan['info'].get('lastenvelop_index') + 1})
    elif resp == "B":
        modFiGoal(index, myfiplan)
    else:
        print("Wrong input")
    printFiPlan(myfiplan)
    return myfiplan


def modEnvelops(myfiplan, myfigoalindex):
    print("Envelops for " + myfiplan['data'][myfigoalindex].get('name') + ":")
    for k, v in myfiplan['data'][myfigoalindex]['envelops'].items():
        print(k, v)
    resp = input("'A' to add an envelop, its index to modify/remove it ")
    if resp == 'A':
        addEnvelop(myfiplan, myfigoalindex)
        myfiplan['info'].update({"lastenvelop_index": myfiplan['info'].get('lastenvelop_index') + 1})
    else:
        if str(resp) in myfiplan['data'][myfigoalindex]['envelops']:
            myfiplan['data'][myfigoalindex]['envelops'].update(
                {
                    str(myfiplan['info'].get('lastenvelop_index') + 1):
                    {
                        genEnvelop()
                    }
                }
            )
        else:
            print("Wrong input")


def genEnvelop():
    name = input('The of this goal envelop? ')
    current_balance = input('Current balance of this envelop? ')
    expected_growthYield = input('Expected yearly growth performance of this envelop? (from 0 to 100) ')
    expected_dividendYield = input('Expected yearly dividend yield of this envelop? (from 0 to 100) ')
    monthly_invest = input('Current monthly invested? ')
    return {
        'name': name,
        'current_balance': float(current_balance),
        'expected_growthYield': float(expected_growthYield)/100,
        'expected_dividendYield': float(expected_dividendYield)/100,
        'monthly_invest': float(monthly_invest)
    }


def addEnvelop(myfiplan, myfigoalindex):

    myfiplan['data'][myfigoalindex]['envelops'].update(
        {
            str(myfiplan['info'].get('lastenvelop_index') + 1):
                {
                genEnvelop()
                }
        }
    )

# def modEnvelop(index, myfigoal):

# TODO mod/remove envelops from goals


printFiPlan(MyFiPlan)
