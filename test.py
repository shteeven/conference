
A = True
B = True
C = True


print((not A and not B and C) == ((not A and not B) and not C))


# def input_validator(msg, val_type, negatives=True):
#     valid = False
#     parsing = {
#         'float': float,
#         'int': int,
#         'bool': bool
#     }
#     while not valid:
#         print(msg)
#         value = parsing[val_type](input())
#         if negatives or value >= 0:
#             valid = True
#         else:
#             print('Please enter a positive value')
#     return value
#
#
# miles = input_validator("Input miles to convert:", 'float', False)
# gallons = input_validator("Input gallons to convert:", 'float', False)
# fahrenheit = input_validator("Input fahrenheit to convert:", 'float')
#


#
# try:
#     int_a = int(a)
# except ValueError:
#     print("The values you entered was not an integer")
#     exit(1)
# print(a)