# Category: Reverse Engineering

## Challenge: nine-solves

This challenge gives us a binary (nine-solves), which is linked in the repo, as well as a nc connection.

### Rev?
Running the binary and opening it in binja (my favorite decompiler <3), we see this is a classic rev challenge, where we must figure out the access code and send it to the server to get the flag.

<img src="images/binja.png">

Looking closer at the disassembly, it appears to check character by character for a string of length 6. If a character is valid, it increments the count (rsi) by one until it equals 6. If we believed in reverse engineering, we may try to understand the code and predict each of the characters. However, we can just patch the binary (using my favorite decompiler binja <3) to print out the number of correct characters at the end, allowing us to brute force byte-by-byte. Alternatively, you can use debugger scripting, which I will discuss at the end.

## Brute Force > Rev
There are lots of way to patch the binary, but as described above, we will print/send some information about the number of correct characters. We do this by editing the return value to equal the count variable when the input fails.

Original code:

<img src="images/original_code.png">

<img src="images/original_disassembly.png">

Patched Code:

<img src="images/patch.png">

With the program patched, we create a simple brute force script that goes byte-by-byte, checking for an increment in the return value. We also account for the final character, which will not fail, by checking for the flag output. In my case, I created a test "flag.txt" containing "test".

### Script:

```
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
```

### Win
We run the script, getting the code, and then send the code to the server!

flag: lactf{the_only_valid_solution_is_BigyaP}

### Debugger Scripting
During the competition, I did not use this method, but I thought it would be fun to code up and add to my writeup. The goal is to detect when a byte is valid using a debugger instead of patching the binary. We can use Binja's debugger or GDB to do this. Unfortunately, I do not have a Binja license (yet), so I will use GDB scripting. Please give Binja license. GDB scripting hurts my soul ;(

This method is decently simple. We put a breakpoint on the count increment and have our script start guessing the next byte when it detects an increase in the counter at this breakpoint. We also set a breakpoint at the "ACCESS DENIED" print out in order to increment our guess after each failed attempt. Once all six bytes are found, we print out the access code and win! We also have to do some weird logging configurations to send a GDB variable into the program's input. The script is seen below:

```
set $ans = (char[6]) {0}
set $guess = 0
set $count = 0

set confirm off
set logging overwrite on

#successful byte
b *main + 138
commands
  if $rsi == $count
    set $guess = 0
    set $count += 1
    r < gdb.txt
  end
  c
end

#failed input
b *main + 184
commands
  set $guess += 1
  set $ans[$count] = $guess
  set logging enabled on
  printf "%s\n", $ans
  set logging enabled off
  r < gdb.txt
end

#win call
b *main + 163
commands
  p $ans
end

#run
set logging enabled on
printf "wrong\n"
set logging enabled off
r < gdb.txt
```

We run the script using `gdb -x script.gdb ./nine-solves` and win!
