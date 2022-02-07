
from profanity_filter import ProfanityFilter
from timeit import default_timer as dt

profanity_filter=ProfanityFilter()
whole=dt()
st=whole
with open('bb.py','r') as f:
    lines=f.read()
print(f"Read took {dt()-st}s")
st=dt()
filtered=profanity_filter.censor(lines)
print(f"Filter took {dt()-st}s")
st=dt()
with open("bb.py",'w') as f:
    print(filtered,file=f)
print(f"Write took {dt()-st}s")
print(f"Whole took {dt()-whole}s")
