import sys


had_error = False

buffer = []

current_line_num = 0

symbols = {
    'SCREEN': 16384,
    'KBD': 24576,
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4
}

for i in range(16):
    symbols['R' + str(i)] = i

requests = []


def main(infile, outfile):
    global current_line_num
    global buffer

    with open(infile) as fin:
        for line in fin.readlines():
            current_line_num += 1
            res = translate_line(line)
            if res is not None:
                buffer.append(res)

    if had_error:
        return

    fill_requests()

    with open(outfile, 'w') as fout:
        for short in buffer:
            fout.write('{0:016b}\n'.format(short))


def fill_requests():
    global requests
    global buffer
    
    var_requests = {}

    for request in requests:
        offset = request[0]
        sym = request[1]
        if sym in symbols:
            buffer[offset] = symbols[sym]
        else:
            if sym in var_requests:
                var_requests[sym].append(offset)
            else:
                var_requests[sym] = [offset]

    requests = []

    for i, (name, offsets) in enumerate(var_requests.items()):
        for offset in offsets:
            # No check if too many vars.
            buffer[offset] = i + 16


def translate_line(line):
    line = remove_whitespace(line)
    if not line:
        return None
    elif line[0] == '@':
        return a_command(line)
    elif line[0] == '(':
        add_label(line[1:-1])
        return None
    else:
        return c_command(line)


def add_label(name):
    symbols[name] = len(buffer)


def a_command(line):
    num_or_sym = line[1:]

    if not num_or_sym:
        error("no number provided")

    if num_or_sym[0].isalpha():
        try:
            val = symbols[num_or_sym]
            return val
        except KeyError:
            requests.append((len(buffer), num_or_sym))
            return 0

    num = int(num_or_sym)

    if not is_valid_a_num(num):
        error("number is out of range")

    return num & 0b0111111111111111


def is_valid_a_num(num):
    # return num <= (2**14 - 1) and num >= (-2**14)
    return num >= 0 and num <= 2**15


def c_command(line):
    cmd = split_c_command(line)

    dest = find_dest(cmd[0])
    comp = find_comp(cmd[1])
    jmp = find_jmp(cmd[2])

    dest <<= 3
    comp <<= 6

    ones = 0b111 << 13

    return ones + comp + dest + jmp


def split_c_command(line):
    dest = None
    comp = None
    jmp = None

    line_semicolon = line.split(';')
    if len(line_semicolon) == 1:
        jmp = ''
    else:
        jmp = line_semicolon[1].strip()

    line_equal = line_semicolon[0].split('=')
    if len(line_equal) == 1:
        dest = ''
        comp = line_equal[0].strip()
    else:
        dest = line_equal[0].strip()
        comp = line_equal[1].strip()

    return [dest, comp, jmp]


def find_dest(part):
    res = 0
    if 'M' in part:
        res += 1
    if 'D' in part:
        res += 2
    if 'A' in part:
        res += 4
    return res


def find_jmp(part):
    jmp_map = {
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111',
    }

    if part in jmp_map:
        return part_to_int(jmp_map[part])

    return 0


def part_to_int(part):
    return int(part, 2)


def find_comp(part):
    a_zero = {
        '0': '101010',
        '1': '111111',
        '-1': '111010',
        'D': '001100',
        'A': '110000',
        '!D': '001101',
        '!A': '110001',
        '-D': '001111',
        '-A': '110011',
        'D+1': '011111',
        'A+1': '110111',
        'D-1': '001110',
        'A-1': '110010',
        'D+A': '000010',
        'D-A': '010011',
        'A-D': '000111',
        'D&A': '000000',
        'D|A': '010101',
    }

    a_one = {
        'M': '110000',
        '!M': '110001',
        '-M': '110011',
        'M+1': '110111',
        'M-1': '110010',
        'D+M': '000010',
        'D-M': '010011',
        'M-D': '000111',
        'D&M': '000000',
        'D|M': '010101',
    }

    a = 2**6

    if part in a_zero:
        return part_to_int(a_zero[part])
    elif part in a_one:
        return part_to_int(a_one[part]) + a
    else:
        error("unknown computation")


def remove_whitespace(line):
    comment_begin = line.find('//')
    if comment_begin != -1:
        line = line[0:comment_begin]
    line = line.strip()
    return line


def error(msg):
    print(f'{current_line_num}: {msg}')
    had_error = True
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Error: wrong arguments count")
        print("Usage: hack_assembler.py infile outfile")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
