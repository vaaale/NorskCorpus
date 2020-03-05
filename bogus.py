import sys

vals = list(range(5))

for i in vals:
    print(f'Hello nummer {i}')
    print("<doc id=123>")
    print("</doc>")
try:
    print(vals[4000])
except:
    print("Cannot read that value, idiot!", file=sys.stderr)
