from datetime import datetime
from pprint import pprint
import tkinter as tk
import statistics
import time
import csv
import os


# Stats variables.
target_timer = 1
timer_stat_flag = False
last_toggle_time = 0
elapsed_time_b_total = 0
elapsed_time_a_total = 0
timer_stats = []


def update_timer_stats(unflip_timer=True):
    global last_toggle_time
    global target_timer
    global timer_stats

    new_toggle_time = time.time()
    elapsed_time = new_toggle_time - last_toggle_time
    if unflip_timer:
        timer_stats.append((int(not target_timer),
                            elapsed_time))
    else:
        timer_stats.append((target_timer,
                            elapsed_time))

    last_toggle_time = new_toggle_time


def handle_clock_tick():
    global elapsed_time_b_total
    global elapsed_time_a_total
    global timer_stat_flag
    global target_timer

    # Increment the appropriate timer.
    if target_timer == 1:
        elapsed_time_b_total = elapsed_time_b_total + 1
    else:
        elapsed_time_a_total = elapsed_time_a_total + 1

    # Update timer statistics.
    if timer_stat_flag:
        timer_stat_flag = False  # Lower the timer stat flag.
        update_timer_stats()


def stat_log():
    global elapsed_time_a_total
    global elapsed_time_b_total
    global timer_stats

    print("Left Clock Total Time: {}".format(elapsed_time_a_total))
    print("Right Clock Total Time: {}".format(elapsed_time_b_total))
    if elapsed_time_b_total > 0:
        print("Left-Right Ratio: {}".format(elapsed_time_a_total /
              elapsed_time_b_total))

    # Get last timer info before close.
    update_timer_stats(unflip_timer=False)

    # Sanity check on target timer IDs.
    for x in range(0, len(timer_stats)):
        if timer_stats[x][0] != 0 and timer_stats[x][0] != 1:
            print("[ warning ] Invalid target timer for element: {}. Target timer: {}.".format(
                x, timer_stats[x][0]))

    # Statistics tasks.
    left_clock_time_intervals = [element[1]
                                 for element in timer_stats if element[0] == 0]
    right_clock_time_intervals = [element[1]
                                  for element in timer_stats if element[0] == 1]

    print("\nLeft Clock Descriptive Statistics:")
    lc_count = len(left_clock_time_intervals)
    lc_mean = statistics.mean(left_clock_time_intervals) if len(
        left_clock_time_intervals) >= 1 else 0
    lc_stdev = statistics.stdev(left_clock_time_intervals) if len(
        left_clock_time_intervals) >= 2 else 0
    print("LC Count: {}\nLC Mean: {}\nLC STDEV: {}".format(
        lc_count, lc_mean, lc_stdev))

    print("\nRight Clock Descriptive Statistics:")
    rc_count = len(right_clock_time_intervals)
    rc_mean = statistics.mean(right_clock_time_intervals) if len(
        right_clock_time_intervals) >= 1 else 0
    rc_stdev = statistics.stdev(right_clock_time_intervals) if len(
        right_clock_time_intervals) >= 2 else 0
    print("RC Count: {}\nRC Mean: {}\nRC STDEV: {}".format(
        rc_count, rc_mean, rc_stdev))

    # CSV tasks.
    csv_data = [["Left Clock Data", "Right Clock Data"]]
    csv_data.extend(
        list(zip(left_clock_time_intervals, right_clock_time_intervals)))
    pprint(csv_data)

    current_date = datetime.now()
    s_year = "{:04d}".format(current_date.year)
    s_month = "{:02d}".format(current_date.month)
    s_day = "{:02d}".format(current_date.day)

    # Directory structure: CWD / ####y / ##m
    cd = os.getcwd()
    output_file_path = os.path.join(cd, s_year,
                                    s_month)

    # File name format: ####y-##m-##d.csv
    output_file_name = s_year + '-' + s_month + '-' + s_day + '.csv'

    # Complete output file path, name, and type.
    output_file = os.path.join(output_file_path, output_file_name)

    # Ensure the file path exists.
    os.makedirs(output_file_path, exist_ok=True)

    append_mode = False
    if os.path.exists(str(output_file)):
        append_mode = True

    # Write the raw data.
    write_mode = 'w' if not append_mode else 'a'
    with open(str(output_file), write_mode) as f:
        writer = csv.writer(f)

        if append_mode:
            # If the file alrady exists, we don't need to re-write the headers.
            for row in csv_data[1:]:
                writer.writerow(row)
        else:
            writer.writerows(csv_data)


class App:
    def __init__(self, root):
        # Initialization.
        self.root = root
        self.root.title("Flip Clock")
        self.root.geometry("450x300")
        self.update_initialized = False

        # Font configuration.
        typeface = "Andale Mono"
        typeface_size = 24

        # First row: Time labels.
        self.elapsed_time_a_label = tk.StringVar()
        self.elapsed_time_a_label.set("00:00:00")
        self.time_a_label = tk.Label(root, textvariable=self.elapsed_time_a_label, font=(
            typeface, typeface_size), fg="black", bg="white")
        self.time_a_label.grid(row=0, column=0, columnspan=1, sticky="nsew")

        self.elapsed_time_b_label = tk.StringVar()
        self.elapsed_time_b_label.set("00:00:00")
        self.time_b_label = tk.Label(root, textvariable=self.elapsed_time_b_label, font=(
            typeface, typeface_size), fg="black", bg="white")
        self.time_b_label.grid(row=0, column=1, columnspan=1, sticky="nsew")

        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=2)

        # Next row: Ratio stat view.
        self.ratio_stat_label = tk.StringVar()
        self.ratio_stat_label.set("Left-Right Ratio: 0000.0000")
        self.ratio_stat = tk.Label(
            root, textvariable=self.ratio_stat_label, font=(typeface, typeface_size))
        self.ratio_stat.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.rowconfigure(1, weight=1)

        # Next row: Timer toggle button.
        self.toggle_timer_text = tk.StringVar()
        self.toggle_timer_text.set("Start Left Clock")
        self.toggle_time_button = tk.Button(
            root, textvariable=self.toggle_timer_text, command=self.toggle_timer_fn, font=(typeface, typeface_size))
        self.toggle_time_button.grid(
            row=2, column=0, columnspan=2, sticky="nsew")

        self.root.rowconfigure(2, weight=2)

    def toggle_timer_fn(self):
        global last_toggle_time
        global timer_stat_flag
        global target_timer

        # Raise the timer stat flag.
        if self.update_initialized:
            timer_stat_flag = True

        if target_timer == 1:
            # Toggle the target timer.
            target_timer = 0

            # Update label and button presentation.
            self.time_a_label.configure(bg="#cddc39")  # green
            self.time_b_label.configure(bg="#f44336")  # red
        else:
            # Toggle the target timer
            target_timer = 1

            # Update the label and button presentation.
            self.time_b_label.configure(bg="#cddc39")  # green
            self.time_a_label.configure(bg="#f44336")  # red

        # Post-timer initialization.
        if self.update_initialized == False:
            self.update_initialized = True
            self.toggle_timer_text.set("Toggle Clocks")
            last_toggle_time = time.time()
            self.update()  # This function reschedules itself.

    def update(self):
        handle_clock_tick()
        global elapsed_time_a_total
        global elapsed_time_b_total

        # Update labels.
        self.elapsed_time_b_label.set(time.strftime(
            "%H:%M:%S", time.gmtime(elapsed_time_b_total)))
        self.elapsed_time_a_label.set(time.strftime(
            "%H:%M:%S", time.gmtime(elapsed_time_a_total)))

        # Cannot calculate ratio without both timers initialized.
        if 0 != elapsed_time_b_total:
            self.ratio_stat_label.set("Left-Right Ratio: {:0009.4f}".format(
                (elapsed_time_a_total / elapsed_time_b_total)))
        else:
            self.ratio_stat_label.set("Left-Right Ratio: 0000.0000")

        # Reschedule this update.
        self.root.after(1000, self.update)


# Create the main window
root = tk.Tk()

# Instantiate the App class.
app = App(root)

# Run the application.
root.mainloop()

# Run stat analysis and logging afterwards.
stat_log()
