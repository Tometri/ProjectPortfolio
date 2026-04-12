# Welcome message
welcome = "Bill Split Calculator"
print(welcome)

# Inputs
bill_amount = float(input("Enter bill amount: "))
tip_percentage = float(input("Enter tip percentage: "))
split = int(input("How many people are splitting the bill? "))

# Calculations
tip_amount = (tip_percentage / 100) * bill_amount
total_amount = bill_amount + tip_amount
split_amount = total_amount / split

print(f"Total (including tip): {total_amount:.2f}")
print(f"Each person pays: {split_amount:.2f}")
