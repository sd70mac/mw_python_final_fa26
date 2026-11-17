# Main Program goes here.

import os
import sys
import pie_in_the_sky


# I hope I'm doing this right.
# I know I need to call the functions in main() so that they actually run!
def main():
    """
    Main function to run the Pie in the Sky order process.
    No parameters are passed to this function, and it does not return any values."""
    clear_screen()
    customer_info = get_customer_info()
    print(f"Welcome To Pie In The Sky, {customer_info['name']}!")
    past_orders = get_past_orders(customer_info=customer_info)
    show_past_orders(past_orders=past_orders)
    order = (
        select_past_order(past_orders=past_orders) or get_order()
    )  # adding the 'or get_order()' fixed order.extend(selected_items) [Currently line 109]

    for category in CATEGORIES:
        available_items = get_available_items(category=category)
        selected_items = get_items_for_category(
            category=category, available_items=available_items
        )
        order.extend(selected_items)  # I have read about combining lists before.
        # Handy link: https://www.w3schools.com/python/ref_list_extend.asp

    total = calculate_bill(order=order)
    print_bill(order=order, total=total)


## Run the main function when the file is executed
main()
