ct_hex = "627256553f185719edfad8daaaa9b18d33677d51700a2123c9afd7"
pt = ""
for i in range(len(ct_hex) // 2):
    cipher = int(ct_hex[i*2:i*2 + 2], 16)
    i = i % 16
    pt += chr(cipher ^ (i + (i << 4)))
    print(pt)
print(pt)
