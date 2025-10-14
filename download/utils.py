import random
import string

def sizeof_fmt(num, suffix="B"):
  for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
    if abs(num) < 1024.0:
      return f"{num:3.1f} {unit}{suffix}"
    num /= 1024.0
  return f"{num:.1f} Y{suffix}"

def get_random_string(length):
  # choose from all lowercase letter
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(length))
    
def clone_exclude(params, keys):
  return {x: params[x] for x in params if x not in keys}