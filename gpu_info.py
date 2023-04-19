import re
import subprocess
import os
import psutil

__all__ = ['get_user', 'gpu_usage', 'check_empty', 'get_info', 'run_command']

def run_command(command: str):
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    return process.stdout.splitlines()

def get_user(pid):
    try:
        process = psutil.Process(pid)
        return process.username()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def get_info():
    gpu_used = set()
    pid_current = set()
    percent = []
    memory = []
    pid_list = {}
    lines_ns = run_command('nvidia-smi')

    for line in lines_ns:
        if '%' in line:
            percent.append(int(line.split('%')[-2][-3:]))
            memory.append(int(line.split('MiB')[0][-5:]))
        elif 'MiB' in line:
            arrs = re.split('[ ]+', line)
            gpu_id = int(arrs[1])
            pid = arrs[2]
            mem = int(arrs[-2][:-3])

            gpu_used.add(gpu_id)
            pid_current.add(pid)

            pid_list.setdefault(pid, []).append(gpu_id)

    return pid_list, percent, memory, list(gpu_used)

def gpu_usage():
    _, percent, memory, _ = get_info()
    return percent, memory

def check_empty():
    _, _, _, gpu_used = get_info()
    gpu_unused = [i for i in range(max(gpu_used) + 1) if i not in gpu_used]

    if not gpu_unused:
        return None
    else:
        return gpu_unused

def get_users(gpu_id: int):
    lines_ns = run_command('nvidia-smi')
    users_dict = {}

    for line in lines_ns:
        if 'MiB' in line:
            arrs = re.split('[ ]+', line)
            g_id = int(arrs[1])

            if g_id != gpu_id:
                continue

            pid = arrs[2]
            mem = int(line.split('MiB')[0][-5:])
            user = get_user(pid)

            users_dict[user] = users_dict.get(user, 0) + mem

    return users_dict

if __name__ == "__main__":
    print(get_info())
