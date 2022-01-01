import json
import os
import requests
import csv
from tabulate import tabulate

APP_DETAILS_URL = 'http://store.steampowered.com/api/appdetails/'
LOWEST_PRICE_URL = 'https://api.isthereanydeal.com/v01/game/lowest/'
KEY = '7be447da09c12bc36d535acf3741ae46360f34c2'

dir_path = os.path.dirname(os.path.realpath(__file__))
email_file = os.path.join(dir_path, 'email.txt')
data_file = os.path.join(dir_path, 'data.json')
list_file = os.path.join(dir_path, 'list.csv')

def search_items(search_query):
    with open(data_file, 'r') as f:
        items = json.load(f)
        return [x for x in items if search_query in x['name']]
        
def get_prices(items):
    app_ids = ','.join(str(x['appid']) for x in items)
    plains = ','.join(x['plain'] for x in items)

    params = {
        'filters': 'price_overview',
        'appids': app_ids
    }
    response = requests.get(APP_DETAILS_URL, params=params)
    data = response.json()

    params = {
        'key': KEY,
        'plains': plains,
        'region': 'us',
        'country': 'US',
        'shops': 'steam'
    }
    response = requests.get(LOWEST_PRICE_URL, params=params)
    historical_lows = response.json()
    
    prices = {}

    for item in items:
        item_details = data[str(item['appid'])]
        historical_low = historical_lows['data'][item['plain']]
       
        if item_details['success']:
            if item_details['data'] == []:
                prices[item['appid']] = {'is_free': True }
            else:
                price_overview = item_details['data']['price_overview']
                price = {
                    'is_free': False,
                    'final_formatted': price_overview['final_formatted'],
                    'discount_percent': '{}%'.format(price_overview['discount_percent']),
                }
                if 'price' in historical_low and 'cut' in historical_low:
                    price['historical_low'] = historical_low['price']
                    price['historical_low_discount_percent'] = '{}%'.format(historical_low['cut'])
                else:
                    price['historical_low'] = price_overview['final_formatted']
                    price['historical_low_discount_percent'] = '{}%'.format(price_overview['discount_percent'])

                if (price_overview['initial'] == price_overview['final']):
                    price['initial_formatted'] = price_overview['final_formatted']
                else:
                    price['initial_formatted'] = price_overview['initial_formatted']
                prices[item['appid']] = price
        else:
            prices[item['appid']] = {}
        
    return prices

def add_item(item, desired_price):
    with open(list_file, 'r') as f:
        reader = csv.reader(f)
        existing = [row[0] for row in reader]
    with open(list_file, 'a') as f:
        writer = csv.writer(f)
        if item['name'] not in existing:
            writer.writerow([item['name'], item['appid'], item['plain'], desired_price])
            print("\n{} successfuly added to list\n".format(item['name']))
        else:
            print("\n{} already added\n".format(item['name']))
    print_list()

def remove_item(item):
    with open(list_file, 'r') as f:
        reader = csv.reader(f)
        items = [row for row in reader if row[1] != item[1]]
    
    with open(list_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(items)
        print("\n{} successfully removed from list\n".format(item[0]))

def edit_item(item, desired_price):
    items = []
    with open(list_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] == item[1]:
                row[3] = desired_price
            items.append(row)

    with open(list_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(items)
        print("\n{} successfully edited\n".format(item[0]))

def print_list():
    list = []
    output = []
    with open(list_file, 'r') as f:
        reader = csv.reader(f)
        if reader:
            print("LIST")
            for i,row in enumerate(reader):
                list.append(row)
                output.append([row[0], row[3]])
            print(tabulate(output, headers=['Name', 'Desired Price'], showindex="always", tablefmt="simple"))
            print()
        else:
            print('List currently empty\n')
    return list

def menu_option_a():
    while True:
        print("Press enter to return to main menu")
        search_query = input("Enter the item's name: ")

        if search_query == "":
            print()
            break

        results = search_items(search_query)
        prices = get_prices(results)
        results = [x for x in results if prices[x['appid']]]
        result_count = len(results)
       
        output = []
        if results:
            for i, item in enumerate(results):
                price = prices[item['appid']]
                if price == {}:
                    continue
                if price['is_free']:
                    output.append([item['name'], 'F2P'])
                    # print("({}) {}".format(i+1, item['name']))
                else:
                    output.append([item['name'], price['initial_formatted'], 
                        price['final_formatted'], price['discount_percent'],
                        price['historical_low'], price['historical_low_discount_percent']])
                    # print("({}) {:<{}} {} {} {} {} {}".format(i+1, item['name'], max_len+5, price['initial_formatted'], 
                    #     price['final_formatted'], price['discount_percent'],
                    #     price['historical_low'], price['historical_low_discount_percent']))

            while True:
                print(tabulate(output, headers=['Name', 'Original Price', 'Curr Price', 'Curr Discount', 'Lowest $', 'Lowest Discount'], showindex="always", tablefmt="simple"))
                print("\nPress enter to return to search")
                user_input = input("Enter the number corresponding to the item you wish to add to your list: ")

                if user_input == '':
                    print()
                    break
                if user_input.isdigit():
                    user_input = int(user_input)
                    if user_input >= 0 and user_input < result_count:
                        item = results[user_input]
                        if (prices[item['appid']]['is_free']):
                            print("\nItem is free")
                            continue
                        desired_price = input("Enter the desired price: ")
                        try:
                            val = float(desired_price)
                            if val > 0:  
                                add_item(results[user_input], desired_price)
                                input("Press anything to continue: ")
                            else:
                                print("\nInvalid price\n")
                        except ValueError:
                            print("\nThat's not a number!\n")  
                    else:
                        print("\nInvalid number. Enter a number in the following range [0-{})\n".format(result_count))
                else:
                    print("\nInvalid input. Enter a number in the follwing range [0-{})\n".format(result_count))
        else:
            print("\nNo results matching the query were found\n")
            break

def menu_option_b():
    while True:
        list = print_list()
        list_count = len(list)
        print("Press enter to return to main menu")
        user_input = input("Enter the number corresponding to the item you wish to remove from your list: ")

        if user_input == '':
            print()
            break
        if user_input.isdigit():
                user_input = int(user_input)
                if user_input >= 0 and user_input < list_count:
                    remove_item(list[user_input])
                else:
                    print("\nInvalid number. Enter a number in the following range [0-{})\n".format(list_count))
        else:
            print("\nInvalid input. Enter a number in the follwing range [0-{})\n".format(list_count))

def menu_option_c():
     while True:
        list = print_list()
        list_count = len(list)
        print("Press enter to return to main menu")
        user_input = input("Enter the number corresponding to the item you wish to edit: ")

        if user_input == '':
            print()
            break
        if user_input.isdigit():
                user_input = int(user_input)
                if user_input >= 0 and user_input < list_count:
                    # remove_item(list[user_input][0])
                    desired_price = input("Enter the desired price: ")
                    try:
                        val = float(desired_price)
                        if val > 0:  
                            edit_item(list[user_input], desired_price)
                        else:
                            print("\nInvalid price\n")
                    except ValueError:
                        print("\nThat's not a number!\n")  
                else:
                    print("\nInvalid number. Enter a number in the following range [0-{})\n".format(list_count))
        else:
            print("\nInvalid input. Enter a number in the follwing range [0-{})\n".format(list_count))

def menu_option_e():
    while True:
        print("Press enter to return to main menu")
        with open('email.txt', 'r') as f:
            content = f.read()
            print("Current email address is {}".format(content))
        user_input = input("Enter new gmail address: ")

        if user_input == '':
            print()
            break
        else:
            with open('account.txt', 'w') as f:
                f.write(user_input)
            print('\nEmail is now {}\n'.format(user_input))

def main():
    # If file doesn't exist or if file exists and size is 0
    while True:
        if os.path.exists(email_file) == False or os.path.getsize(email_file) == 0:
            while True:
                print("Enter email: ", end='')
                email = input()
                if email == '':
                    print("\nEmail cannot be empty\n")
                else:
                    with open('email.txt', 'w') as f:
                        f.write(email)
                    print('Email successfully registered\n')
                    break
        else:
            break
        
    while True:
        # Print Main Menu Options
        print("(A) - Add item to list")
        print("(B) - Remove item from list")
        print("(C) - Edit item price")
        print("(D) - Print list")
        print("(E) - Change Email")
        print("(Q) - Exit program")
        print("Enter an option: ", end='')
        user_input = input().lower()
        print()

        if user_input == "a":
            menu_option_a()
        elif user_input == "b":
            menu_option_b()
        elif user_input == "c":
            menu_option_c()
        elif user_input == "d":
            print_list()
        elif user_input == "e":
            menu_option_e()
        elif user_input == "q":
            break
        else:
            print("Invalid menu option\n")

if __name__ == "__main__":
    main()