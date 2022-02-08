import json
def load() -> dict[int,dict]: # loads member data
    with open(f"bb.json", "r") as f: r=json.loads(f.read())
    new={int(i):r[i] for i in r if i.isdigit()}
    for i in r:
        if not i.isdigit(): new[i]=r[i]
    return new

Data=load()

for member in Data:
    if type(Data[member])==dict and type(member)==int:
        if "bithday" not in Data[member]:
            Data[member]["birthday"]=""

def save(dictionary): # saves member data in dictionary to hard storage
    with open(f"bb.json", "w") as f: json.dump(dictionary, f)

save(Data)
