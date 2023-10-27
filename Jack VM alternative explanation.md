# Jack VM alternative explanation

## Rationale

Nand2Tetris consits of two parts: hardware-oriented (part I) and software-oriented (part II). In the first part of the course it was natural to learn computer architecture bottom-up. But learning the core software for the computer bottom-up is not the best way IMHO. So there I took little notes about the Jack VM and its implementation.

## VM

To translate programs in Jack language it is easier and more fun (and practical) to firstly compile it to VM code and then compile VM code to Hack machine language.

Jack VM is a stack based virtual machine. The operands and the computation is performed on the stack.

There are 3 different instruction types that the VM support:

- Pushing *something* on to the stack.

- Popping value from the stack to *something*.

- Performing arithmetical and logical operation with the values on the top of the stack.

For example, the code:

```js
15 + 2 * 4
```

Translates into:

```
push 15
push 2
push 4
mul
add
```

Pretty simple. But the thing is, that in the high-level language there are lots of *things* we can push on the stack:

- Local variables of the function

- Arguments passed to the function

- Fields of the instance

- Static fields of the class

- Arrays

So pushing and popping from the stack should be also marked with type of that thing. Jack VM calls them **memory segments**.

There are several memory segments:

- `local`: local variables of the function. The argument of the push/pop command is the index of the local. For example:
  
  ```
  let int a, x, y;
  let a = x + y
  ```
  
  Translates to:
  
  ```
  push local 1
  push local 2
  add
  pop local 0
  ```

- `argument`: this is the argument of the function. For example:
  
  ```
  function add(a, b) {
      return a + b;
  }
  ```
  
  Translates (partially) into:
  
  ```
  push argument 1
  push argument 0
  add
  ```

- `this`: those are fields of the instance. They are indexed the same as locals.

- `that`: *what is this?*

- `constant`: that is the number. It is not really a memory segment, just a notation.

- `static`: this is the storage for static field variables in classes. They global for everyone and indexed similarly as the locals, though the order may be arbitrary.

- `pointer`: another non-memory memory segment. There are only two pointer instructions: `push pointer 0` which pushes `this` variable on the stack and `push pointer 1` which pushes `that` pointer on the stack.

- `temp`: don't know why we need it. It's like an internal local (or actually static) variable.

## Implementation of memory segments, pushing and popping

- `stack`: not a memory segment, but should be noted. The first register `R0` of Hack is used as stack pointer `SP`. The base address for the stack is 256.

- `local`: we use the second register of Hack `R1` as the base address for the locals `LCL`. The location of locals is arbitrary. The `this`, `that` and `arguments` are implemented the same.
  
  To implement this instruction:
  
  ```
  push local i
  ```
  
  We should implement this:
  
  ```
  addr = LCL + i;
  *SP = *addr;
  SP++;
  ```
  
  For `pop` instruction:
  
  ```
  addr = LCL + i
  SP--;
  *addr = *SP;
  ```

- `constant`:
  
  The code:
  
  ```
  push constant x
  ```
  
  Translates to:
  
  ```
  *SP = x;
  SP++;
  ```

- `static`: static variables are mapped to addresses 16-255.

- `temp`: mapped to addresses 5-12.

- `pointer`:![](/home/ruslan/.var/app/com.github.marktext.marktext/config/marktext/images/2023-09-26-12-06-25-image.png)
