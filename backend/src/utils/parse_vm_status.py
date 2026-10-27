def parse_vm_status(text):
    lines = text.strip().splitlines()
    data_lines = lines[2:]  # Skip header and separator

    vm_list = []

    for line in data_lines:
        parts = line.strip().split()
        if len(parts) >= 3:
            state = parts[2]
            for i in parts[3:]:
                state += f" {i}"
            vm = {
                "Id": parts[0],
                "Name": parts[1],
                "State": state
            }
            vm_list.append(vm)

    vm_list = sorted(vm_list, key=lambda x: x['Name'])

    return vm_list
