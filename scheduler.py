# Import the needed libraries
import sys
import pandas as pd

class process:
    """
    Class to represent a process in a CPU scheduling system.
    
    We've two sceduler: Round Robin with quantum time and Earlist Deadline First.
    """
    
    def __init__(self, name, arrival_time, burst_time, deadline):
        """
        Initializes a Process object with its attributes.

        Args:
            name: A string representing the name of the process.
            arrival_time: An integer representing the arrival time of the process.
            burst_time: An integer representing the burst time (CPU processing time) of the process.
            deadline: An integer representing the deadline of the process.
        """
        
        # basic attributes
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.deadline = deadline
        
        # additional attributes (initialized with None or default values)
        self.start_time = None
        self.end_time = None
        self.remaining_time = burst_time    # remaining time equal to burst time for process doesn't start.
        self.waiting_time = None
        self.response_time = None
        self.turnaround_time = None
        self.status = None

    def __repr__(self):
        """
        Returns a string representation of the Process object.

        This method allows you to control how objects are represented when printed.
        """
        
        return f"process({self.name}, {self.arrival_time}, {self.burst_time}, {self.deadline})"


def read_processes(input_file):
    """
    Returns a list of processes objects representing the processes in the file.

    Args:
        input_file (str): The path to the text file containing process data.

    Notes:
        - The file format is expected to be a txt with a header line and whitespace-separated values.
        - The header line is skipped.
        - The function assumes the presence of four data elements per line after the header: name, arrival time, burst time, and deadline.
    """
    
    processes = []
    
    # Read the processes file
    with open(input_file, 'r') as file:
        next(file)      # Ignore the header line        
        for line in file.readlines():
            name, arrival, burst, deadline = line.strip().split()
            # It stores a reference (memory address) to the object itself in the list.
            # Any changes made to the object through that variable or list entry will affect the original object in memory.
            processes.append(process(name, int(arrival), int(burst), int(deadline)))
    
    return processes


def rr(processes, quantum):
    """
    This function implements the Round Robin (RR) scheduling algorithm.

    Args:
        processes (list[Process]): The list of processes to be scheduled.
        quantum (int): The time quantum used for scheduling in RR.

    Returns:
        list[Process]: The list of completed processes with their scheduling details updated.
    """
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)
    
    global current_time
    current_time = 0        # Timer to simulate the cpu time
    cpu = []                # List of processes that have been finished
    ready_queue = []        # Processes waiting in the ready queue
    
    while processes or ready_queue:
        update_ready_queue(processes, ready_queue)

        # Handle idle CPU if no processes are ready
        if not ready_queue:
            current_time += 1
            continue
        
        process = ready_queue.pop(0)         # Get the first process from the ready queue   
        if process.response_time is None:
            process.response_time = current_time - process.arrival_time
            process.start_time = current_time

        # Execute the process for the time quantum or its remaining burst time, whichever is less
        
        running_time = min(quantum, process.remaining_time)
        while running_time > 0:
            process.remaining_time -= 1
            current_time += 1
            running_time -=1
            update_ready_queue(processes, ready_queue)
        
        if process.remaining_time == 0:         # Process completed
            process.end_time = current_time
            process.status = 'S' 
            cpu.append(process)
        else:
            update_ready_queue(processes, ready_queue)    
            ready_queue.append(process)         # Put unfinished process back in ready queue 
    
    return sorted(cpu, key=lambda p: p.start_time)


def edf(processes):
    """
    This function implements the Earlist Deadline First (EDF) scheduling algorithm.

    Args:
        processes (list[Process]): The list of processes to be scheduled.
        quantum (int): The time quantum used for scheduling in RR.

    Returns:
        list[Process]: The list of completed processes with their scheduling details updated.
    """
    
    # Sort processes by arrival time
    processes.sort(key=lambda p: p.arrival_time)

    global current_time
    current_time = 0        # Timer to simulate the cpu time
    cpu = []                # List of processes that have been finished
    ready_queue = []        # Processes waiting in the ready queue
    
    while processes or ready_queue:
        update_ready_queue(processes, ready_queue)

        # Handle idle CPU if no processes are ready
        if not ready_queue:
            current_time += 1
            continue
        
        # Get the earliest deadline process by sort the processes by deadline time
        ready_queue.sort(key=lambda p: p.deadline)
        process = ready_queue.pop(0)
        
        if process.response_time is None:
            process.response_time = current_time - process.arrival_time
            process.start_time = current_time
        
        # Execute the process for 1 unit of time (preemptive)
        process.remaining_time -= 1
        current_time += 1
        update_ready_queue(processes, ready_queue)
        
        if process.remaining_time == 0:         # Process completed
            process.end_time = current_time
            check_status(process)
            cpu.append(process)
        else:
            update_ready_queue(processes, ready_queue)    
            ready_queue.append(process)         # Put unfinished process back in ready queue 
    
    return sorted(cpu, key=lambda p: p.start_time)        
        

def calculate_metrics(cpu):
    """
    This function calculates various scheduling metrics for a list of completed processes.

    Args:
        cpu (list[Process]): A list of Process objects representing the completed processes.

    Returns:
        tuple: A tuple containing the calculated metrics (AWT, ART, ATT, Throughput, Utilization, Proportionality).
    """

    total_processes = len(cpu)
    total_time = max(cpu, key=lambda p: p.end_time).end_time    # Last process finish time
    
    for process in cpu:
        process.turnaround_time = process.end_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time

    total_waiting_time = sum([p.waiting_time for p in cpu])
    total_turnaround_time = sum([p.turnaround_time for p in cpu])
    total_response_time = sum([p.response_time for p in cpu])
    total_burst_time = sum([p.burst_time for p in cpu])
    
    # Calculate scheduling metrics        
    awt = round(total_waiting_time / total_processes, 2) if total_processes > 0 else 0
    art = round(total_response_time / total_processes, 2) if total_processes > 0 else 0     # Avoid division by zero
    att = round(total_turnaround_time / total_processes, 2)if total_processes > 0 else 0
    throughput = round(total_processes / total_time, 2)
    utilization = round((total_burst_time / total_time) * 100, 2)
    proportionality = max(round(process.turnaround_time / process.burst_time, 2) for process in cpu)

    return awt, art, att, throughput, utilization, proportionality


def update_ready_queue(processes, ready_queue):
    """
    This function updates the ready queue by adding processes that have arrived by the current time.

    Args:
        processes (list[Process]): The list of all processes.
        ready_queue (list[Process]): The list of processes in the ready queue..
    """
    
    for process in processes:
        if process.arrival_time <= current_time:
            ready_queue.append(process)
            processes.remove(process)


def check_status(process):
    """
    This function checks the status of a process based on its ending time and deadline.

    Args:
        process (Process): The Process object to check the status for.
    """
    
    if process.end_time <= process.deadline:
        process.status = 'S'
    else:
        process.status = 'F'
        

def main(input_file, quantum):
    """
    This function is the main entry point for the program.
    
    It reads process data from a file, executes two scheduling algorithms 
    (Round Robin and EDF) with the provided quantum, calculates performance metrics 
    for each policy, and displays the results in a table and detailed scheduling order.

    Args:
        input_file (str): The path to the text file containing process data (assumed to be a .txt file).
        quantum (int): The time quantum used for scheduling (relevant for Round Robin).
    """
    
    processes1 = read_processes(input_file)
    processes2 = read_processes(input_file)
    
    policies = {
        'RR': rr(processes1, quantum),
        'EDF': edf(processes2)
    }

    # Calculate performance metrics for each policy
    metrics = {policy: calculate_metrics(cpu) for policy, cpu in policies.items()}
    metrics_df = pd.DataFrame(metrics, index=['AWT', 'ART', 'ATT', 'Throughput', 'Utilization', 'Proportionality']).T
    sorted_metrics_df = metrics_df.sort_values(by=['AWT', 'ART', 'ATT', 'Throughput', 'Utilization', 'Proportionality'])

    #print the desired output
    for metric in sorted_metrics_df.columns:
        line = f"{metric} "
        for policy in sorted_metrics_df.index:
            line += f"{policy} ({sorted_metrics_df.loc[policy, metric]}) "
        print(line)
    
    # Print scheduling order for each policy
    for policy, cpu in policies.items():
        print(f"\nPolicy: {policy}")
        for process in cpu:
            print(f"process: {process.name}, Start Time: {process.start_time}, End Time: {process.end_time}, Duration: {process.burst_time}, Status: {process.status}")


if __name__ == "__main__":
    """
    This block ensures the code below only executes when the script 
    is run directly, not when imported as a module.
    """
    
    # Validate the number of arguments provided
    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments provided.")
        print("Usage: python scheduler.py [input-file] [quantum]")
        sys.exit(1)

    # Validate input file argument
    try:
        input_file = sys.argv[1]
        if not input_file.lower().endswith(".txt"):
            print("Error: Input file must be a .txt file.")
            sys.exit(1)
    except IndexError:
        print("Error: Input file path not provided.")
        sys.exit(1)
    
    # Validate quantum argument
    try:
        quantum = int(sys.argv[2])
        if quantum <= 0:
            print("Error: Quantum value must be a positive integer.")
            sys.exit(1)
    except ValueError:
        print("Error: Quantum value must be an integer.")
        sys.exit(1)
    
    # Call the main function with validated arguments
    main(input_file, quantum)
    