from pwn import *

#initialize things
context.binary = "patched-nine-solves"
context.log_level = "error"
ans = ""

for l in range(6): #byte-by-byte
    #reset
    guess = ""
    test = False
    for i in range(256): #possible byte values
        guess = ans + chr(i)
        
        #access process
        r = process()
        r.readuntil(b"access code: ")
        r.sendline(guess.encode())
        try:
            out = r.readline()
        except:
            out = b""
        ret_val = r.poll(block=True)
        r.close()
        
        #
        if b"test" in out or ret_val == (l + 3):
            ans += chr(i)
            test = True
            print(f"code: {ans}")
            break
    
    if not test:
        print("ERROR")
        break
