""" Using text files storing historical financial data from 1926 to 2013, the user
can choose an investment strategy that is then simulated with their initial investment,
annual withdrawals, and years in retirement. The program starts on a random point in
the timeline between 1926 - 2013 and simulates the investment with the given number
of retirement years, i.e. starting at 1954 and retired for 30 years will simulate
the investment with data from 1954 to 1984. The user can choose how many 'runs'
the simulation preforms with their input values. The first 3000 runs are graphed."""

import sys
import random
import matplotlib.pyplot as plt


def read_to_list(file_name):
    """Open a file of numbers, convert them from percentages to decimals"""
    with open(file_name) as file_read:
        lines = [float(line.strip()) for line in file_read]
        decimal = [round(line / 100, 5) for line in lines]
        return decimal


# load data files with original data in percent form
print("\nList of investment types:\n")
try:
    bonds = read_to_list('10yr_treasury_bond_1926-2013.txt')
    stocks = read_to_list('SP500_1926_2013.txt')
    blend_40_50_10 = read_to_list('40_50_10_blend_1926-2013.txt')
    blend_50_50 = read_to_list('50_50_blend_1926-2013.txt')
    infl_rate = read_to_list('inflation_rate_1926-2013.txt')
except IOError as e:
    print(f"{e}\nTerminating program.")
    sys.exit(1)


investment_types = {'bonds': bonds, 'stocks': stocks, '50_50_blend': blend_50_50,
                    '40_50_10_blend': blend_40_50_10}


# input legend
print("stocks           =  S&P 500 Index")
print("bonds            =  10-year Treasury Bond")
print("50_50_blend      =  50% S&P 500, 50% Treasury Bond")
print("40_50_10_blend   =  40% S&P 500, 50% Treasury Bond, 10% Cash\n")


invest_type = input("Enter investment type (stocks, bonds, 50_50_blend, "
                    "40_50_10_blend):  ").lower()
while invest_type not in investment_types:
    invest_type = input("Invalid investment. Enter investment type as listed:  ")

start_value = input("How much money will you invest? (enter number):  ")
while not start_value.isdigit():
    start_value = input("Invalid input. Enter integer only:  ")

withdrawal = input("How much will you withdrawal each year?:  ")
while not withdrawal.isdigit():
    withdrawal = input("Invalid input. Enter integer only:  ")

min_years = input("Enter minimum number of years in retirement:  ")
while not min_years.isdigit():
    min_years = input("Invalid input. Enter integer only:  ")

most_likely_years = input("Enter most-likely number of years in retirement:  ")
while not most_likely_years.isdigit():
    most_likely_years = input("Invalid input. Enter integer only:  ")

max_years = input("Enter maximum number of years in retirement:  ")
while not max_years.isdigit():
    max_years = input("Invalid input. Enter integer only:  ")

num_sim = input("Enter number of simulations to run:  ")
while not num_sim.isdigit():
    num_sim = input("Invalid input. Enter integer only:  ")


# check the math on inputs
if not int(min_years) < int(most_likely_years) < int(max_years)\
        or int(max_years) > 99:
    print("\nInput value of retirement years was illogical")
    print("Requirement: minimum < most-likely < maximum < 99")
    sys.exit(1)
if not int(withdrawal) < int(start_value):
    print("\nYou cannot withdrawal more than you started with")
    print("Requirement: withdrawal < starting investment")
    sys.exit(1)


def simulator(returns):
    """Run simulation and return investment value at end-of-plan and bankrupt count"""
    sim_count = 0
    bankrupt_count = 0
    outcome = []

    while sim_count < int(num_sim):
        investments = int(start_value)
        start_year = random.randrange(0, len(returns))
        duration = int(random.triangular(int(min_years), int(max_years),
                                         int(most_likely_years)))
        end_year = start_year + duration
        lifespan = [i for i in range(start_year, end_year)]
        bankrupt = 'no'

        # build temporary lists for each simulation
        lifespan_returns = []
        lifespan_infl = []
        for i in lifespan:
            lifespan_returns.append(returns[i % len(returns)])
            lifespan_infl.append(infl_rate[i % len(infl_rate)])

        # loop through each year of retirement for each simulation run
        for index, i in enumerate(lifespan_returns):
            infl = lifespan_infl[index]

            if index == 0:
                withdrawal_infl = int(withdrawal)
            else:
                withdrawal_infl = int(withdrawal_infl * (1 + infl))

            investments -= withdrawal_infl
            investments = int(investments * (1 + i))

            if investments <= 0:
                bankrupt = 'yes'
                break

        if bankrupt == 'yes':
            outcome.append(0)
            bankrupt_count += 1
        else:
            outcome.append(investments)

        sim_count += 1

    return outcome, bankrupt_count


def bankrupt_prob(outcome, bankrupt_count):
    """Calculate and return chance of running out of money and other stats"""
    total = len(outcome)
    odds = round(100 * bankrupt_count / total, 1)

    print(f"\nInvestment Type:  {invest_type}")
    print(f"Starting Value:  ${int(start_value):,}")
    print(f"Annual Withdrawal:  ${int(withdrawal):,}")
    print(f"Years in Retirement (min-med-max):  {min_years}-{most_likely_years}-{max_years}")
    print(f"Number of runs:  {len(outcome):,}")
    print(f"Odds of Bankruptcy:  {odds}%")
    print(f"Average Outcome:  ${int(sum(outcome) / total):,}")
    print(f"Minimum Outcome:  ${min(i for i in outcome):,}")
    print(f"Maximum Outcome:  ${max(i for i in outcome):,}")

    return odds


def main():
    """Call simulator and bankrupt functions and draw bar chart of results"""
    outcome, bankrupt_count = simulator(investment_types[invest_type])
    odds = bankrupt_prob(outcome, bankrupt_count)

    plot_data = outcome[:3000]

    plt.figure(f'Showing first {len(plot_data)} simulated outcomes',
               figsize=(16, 5))
    index = [i + 1 for i in range(len(plot_data))]
    plt.bar(index, plot_data, color='black')
    plt.xlabel('Individual Outcomes', fontsize=18)
    plt.ylabel('Money Remaining', fontsize=18)
    plt.ticklabel_format(style='plain', axis='y')
    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter
                                       (lambda x, loc: f"{int(x)}"))
    plt.title(f'Odds of Bankruptcy = {odds}%', fontsize=20, color='red')
    plt.show()


if __name__ == '__main__':
    main()