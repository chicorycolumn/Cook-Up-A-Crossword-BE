obj = {"name": "billie"}
objCopy = obj
obj["age"] = 33
objCopy["age"] = 33

obj["age"] += 1

print("obj", obj)
print("objCopy", objCopy)