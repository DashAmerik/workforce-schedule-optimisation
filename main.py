#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import pulp to solve linear programs
import pulp

#import tabulate to build timetable easier
from tabulate import tabulate

#import matplotlib to visualist timetable as graph
import matplotlib.pyplot as plt

#set up initial lists of data, operators and working days
operators = ['Khan', 'Chen', 'Taylor', 'Zidane', 'Perez', 'Santos']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

#dictionary for wage rates of each operator
wage_rates = {
    'Khan': 25,
    'Chen': 26,
    'Taylor': 24,
    'Zidane': 23,
    'Perez': 28,
    'Santos': 30}


#dictionary for availability of each operator
availability = {
    'Khan': {'Monday': 6, 'Tuesday': 0, 'Wednesday': 6, 'Thursday': 0, 'Friday': 6},
    'Chen': {'Monday': 0, 'Tuesday': 6, 'Wednesday': 0, 'Thursday': 6, 'Friday': 0},
    'Taylor': {'Monday': 4, 'Tuesday': 8, 'Wednesday': 4, 'Thursday': 0, 'Friday': 4},
    'Zidane': {'Monday': 5, 'Tuesday': 5, 'Wednesday': 5, 'Thursday': 0, 'Friday': 5},
    'Perez': {'Monday': 14, 'Tuesday': 14, 'Wednesday': 14, 'Thursday': 14, 'Friday': 14},
    'Santos': {'Monday': 14, 'Tuesday': 14, 'Wednesday': 14, 'Thursday': 14, 'Friday': 14}
    }


#dictionary for the minimum hours each operator should work
min_hours = {
    'Khan': 8, 'Chen': 8, 'Taylor': 8, 'Zidane': 8,
    'Perez': 7, 'Santos': 7
    } #8 for bachelor students, 7 for masters students

#dictionary for individual skills of each student
skills = {
    'Programming': ['Khan', 'Chen', 'Perez', 'Santos'],
    'Troubleshooting': ['Taylor', 'Zidane', 'Santos']
}




#function for visualising timetable as bar chart
def visualize_hours(schedule, operators, title):
    names = [row[0] for row in schedule]
    totals = [row[-1] for row in schedule]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, totals)
    
    #label axes and title
    plt.title(f'Total Hour Distribution Per Week: {title}')
    plt.xlabel('Operators')
    plt.ylabel('Total Hours Assigned')
    plt.xticks(rotation=45)
    
    #show value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,f'{height:.1f}',ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()
    print(f"\nBar chart for {title} shown")





def analysis_1(): #function for solving analysis 1
    
    #initialising LpProblem object that reimpliments given Lp model
    prob = pulp.LpProblem("Analysis_1",pulp.LpMinimize) 
    
    #defining decision variables using dicts method
    x = pulp.LpVariable.dicts("x", [(o,d) for o in operators for d in days], lowBound = 0)
    
    #adding objective function with lpSum 
    prob += pulp.lpSum([wage_rates[o] * x[(o, d)] for o in operators for d in days])
    
    #adding constraint (2), not exceeding operator availability
    for o in operators:
        for d in days:
            prob += x[(o, d)] <= availability[o][d]
            
    #adding contraint (3), total 14 hours of work every day by operators
    for d in days:
        prob += pulp.lpSum([x[(o, d)] for o in operators]) == 14
        
    #adding contraint (4) and (5), minimum hours for o in operators:
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) >= min_hours[o]
    
    #adding constraints (6), negative work hours are not permitted
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) >= 0
        
    prob.solve()
    
    
    #display results if solved, else display no optimal solution found
    if pulp.LpStatus[prob.status] == 'Optimal':
        print("Optimal timetable for Analysis 1:")
        total_hours = 0
        total_cost = 0
        #build timetable
        timetable = []
        for o in operators:
            row = [o]
            total = 0
            for d in days:
                hours = x[(o, d)].varValue
                row.append(round(hours,2))
                total += hours
                total_hours += hours
                total_cost += hours * wage_rates[o]
            row.append(round(total, 2))
            timetable.append(row)
        
        headers = ['Operator'] + days + ['Total']
        print(tabulate(timetable, headers=headers,floatfmt=".2f"))
        
        #print total cost
        print(f"Total cost: £{total_cost:.2f}")
        
        
        #visualize the distribution as bar chart
        visualize_hours(timetable, operators, "Analysis 1")
        
        #print total hours
        print(f"Total hours: {total_hours}, total aligns with expected value of "+str(5*14))
        
    
    else:
        print("No optimal solution found.")


def analysis_2(): #function for solving analysis 2
    
    #set maximum additional cost
    max_cost = 1755 * 1.018  # 1.8% increase
    
    prob = pulp.LpProblem("Analysis_2",pulp.LpMinimize) 
    
    #defining decision variables using dicts method
    x = pulp.LpVariable.dicts("x", [(o,d) for o in operators for d in days], 0)
    
    #adding objective to minimise the maximum hours worked
    max_hours = pulp.LpVariable("max_hours", lowBound=0)
    prob += max_hours
    
    #adding constraint (2), not exceeding operator availability
    for o in operators:
        for d in days:
            prob += x[(o, d)] <= availability[o][d]
            
    #adding contraint (3), total 14 hours of work every day by operators
    for d in days:
        prob += pulp.lpSum([x[(o, d)] for o in operators]) == 14
        
    #adding contraint (4) and (5), minimum hoursfor o in operators:
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) >= min_hours[o]
    
    #adding constraints (6), negative work hours are not permitted
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) >= 0
        
    #adding new fairness constraints
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) <= max_hours
    
    # adding new constraint of not increasing cost past the max cost
    prob += pulp.lpSum([wage_rates[o] * x[(o, d)] for o in operators for d in days]) <= max_cost
        
    prob.solve()
    
    
    #display results if solved, else display no optimal solution found
    if pulp.LpStatus[prob.status] == 'Optimal':
        print("Optimal timetable for Analysis 2:")
        total_hours = 0
        total_cost = 0
        #build timetable
        timetable = []
        for o in operators:
            row = [o]
            total = 0
            for d in days:
                hours = x[(o, d)].varValue
                row.append(round(hours,2))
                total += hours
                total_hours += hours
                total_cost += hours * wage_rates[o]
            row.append(round(total, 2))
            timetable.append(row)
        
        headers = ['Operator'] + days + ['Total']
        print(tabulate(timetable, headers=headers,floatfmt=".2f"))
        
        #print total cost
        print(f"Total cost: £{total_cost:.2f}")
        
        #check max value
        print(f"Total cost should not exceed: £{max_cost:.2f}")
        
        #visualize the distribution as bar chart
        visualize_hours(timetable, operators, "Analysis 2")
        
        #print total hours
        print(f"Total hours: {total_hours}, total aligns with expected value of "+str(5*14))
        
        #print maximum hours
        print(f"Maximum hours assigned to any operator: {max_hours.varValue:.2f}")
        
    else:
        print("No optimal solution found.")
    
    

def analysis_3(): #function for solving analysis 3

    
    prob = pulp.LpProblem("Analysis_3", pulp.LpMinimize)
    
    #defining decision variables using dicts method
    x = pulp.LpVariable.dicts("x", [(o, d) for o in operators for d in days], 0)
    
    #adding objective to minimise the maximum hours worked
    max_hours = pulp.LpVariable("max_hours", lowBound=0)
    prob += max_hours
    
    #adding objective function with lpSum 
    prob += pulp.lpSum([wage_rates[o] * x[(o, d)] for o in operators for d in days])
    
    #adding constraint (2), not exceeding operator availability
    for o in operators:
        for d in days:
            prob += x[(o, d)] <= availability[o][d]
            
    #adding contraint (3), total 14 hours of work every day by operators
    for d in days:
        prob += pulp.lpSum([x[(o, d)] for o in operators]) == 14
        
    #adding contraint (4) and (5), minimum hoursfor o in operators:
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) >= min_hours[o]
    
    #adding constraints (6), negative work hours are not permitted
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) >= 0
    
    #new skill constrains, 6 hours per skill per day
    for d in days:
        prob += pulp.lpSum([x[(o, d)] for o in skills['Programming']]) >= 6
        prob += pulp.lpSum([x[(o, d)] for o in skills['Troubleshooting']]) >= 6
        
    #adding fairness constraints
    for o in operators:
        prob += pulp.lpSum([x[(o, d)] for d in days]) <= max_hours
    
        
        
    prob.solve()
    
    
    #display results if solved, else display no optimal solution found
    if pulp.LpStatus[prob.status] == 'Optimal':
        print("Optimal timetable for Analysis 3:")
        total_hours = 0
        total_cost = 0
        #build timetable
        timetable = []
        for o in operators:
            row = [o]
            total = 0
            for d in days:
                hours = x[(o, d)].varValue
                row.append(round(hours,2))
                total += hours
                total_hours += hours
                total_cost += hours * wage_rates[o]
            row.append(round(total, 2))
            timetable.append(row)
        
        headers = ['Operator'] + days + ['Total']
        print(tabulate(timetable, headers=headers,floatfmt=".2f"))
        
        #print total cost
        print(f"Total cost: £{total_cost:.2f}")
        
        
        #visualize the distribution as bar chart
        visualize_hours(timetable, operators, "Analysis 3")
        
        #print total hours
        print(f"\nTotal hours: {total_hours}, total aligns with expected value of "+str(5*14))
        
        #print maximum hours
        print(f"Maximum hours assigned to any operator: {max_hours.varValue:.2f}")
    else:
        print("No optimal solution found.")
    
#building initial user interface
while True:
    print("\nChoose an option:")
    print("1. Analysis 1: Basic scheduling problem")
    print("2. Analysis 2: Scheduling with fairness constraints")
    print("3. Analysis 3: Scheduling with fairness and skill constraints")
    print("4. Exit.")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        print("Generating timetable for Analysis 1...")
        analysis_1()
    elif choice == "2":
        print("Generating timetable for Analysis 2...")
        analysis_2()
    elif choice == "3":
        print("Generating timetable for Analysis 3...")
        analysis_3()
    elif choice == "4":
        print("Program exited.")
        break
    else:
        print("/nInvalid choice. Please try again.")
    

