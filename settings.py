__author__ = 'Hk4Fun'
__date__ = '2018/9/18 0:12'

MODE = 'priority'  # priority is the only available choice
CPU_PROCESS_TIME = 0.5  # Waiting time for clearer show
SUB_TIME = 500  # How much time would each tern sub
PRIORITY_ADD_EACH_TERN = 0.5  # Add priority each tern
PRIORITY_MAX = 10  # Limit job's max priority to avoid too big priority
AGING_TABLE = [0.1, 0.1, 0.2, 0.4, 0.4, 0.5, 1.0, 1.0, 1.5, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
COLOR_MEMORY = (12, 249, 20)
COLOR_USED_MEMORY = (255, 106, 106)
MEM_OS_TAKE = 20  # How much memory would operating system take
TOTAL_MEM = 26  # must higher than MEM_OS_TAKE
LOGGING_LEVEL = 'info'
SAVE_LOG_TO_FILE = True
LOG_FILE_PATH = './log.txt' # valid only if SAVE_LOG_TO_FILE is True