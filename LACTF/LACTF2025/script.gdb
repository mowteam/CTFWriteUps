set $ans = (char[6]) {0}
set $guess = 0
set $count = 0

set confirm off
set logging overwrite on

#successful byte
b *main + 138
commands
  silent
  #set $ans[$count] = $guess
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
  silent
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
