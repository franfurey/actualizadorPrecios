import os
from dotenv import load_dotenv

load_dotenv('db.env')

print(os.getenv('DATABASE_URL'))
print(os.getenv('DATABASE_URI'))
print(os.getenv('HOST'))
print(os.getenv('USERNAME'))
print(os.getenv('PASSWORD'))
print(os.getenv('DATABASE'))
