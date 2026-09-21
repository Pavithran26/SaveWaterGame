# Scratch block logic reference

## Stage

```text
when green flag clicked
set [Score v] to (0)
set [Lives v] to (5)
broadcast [Start Game v]
```

## Tank

```text
when green flag clicked
go to x: (0) y: (-140)

when [left arrow v] key pressed
change x by (-10)

when [right arrow v] key pressed
change x by (10)
```

## Water Drop spawner

```text
when green flag clicked
hide
forever
  create clone of [myself v]
  wait (1) seconds
```

## Water Drop clone

```text
when I start as a clone
go to x: (pick random (-220) to (220)) y: (170)
show
repeat (70)
  change y by (-5)
  if <touching [Tank v]?> then
    change [Score v] by (1)
    delete this clone
  end
end
change [Lives v] by (-1)
delete this clone
```

## Extension path

Add a `broadcast [Milestone v]` check after every score change. Use a `Milestone` variable to ensure each celebration fires once. Add `broadcast [Game Over v]` when `Lives = 0`, then switch the Stage to a game-over backdrop and stop all scripts.
