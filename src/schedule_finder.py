import csv
import glob

def parse_time(time_str):
    """Convert time string 'HH:MM' to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def format_time(minutes):
    """Convert minutes since midnight back to time string 'HH:MM'."""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def read_schedule(filename):
    """Read a CSV file and return a schedule dict with days as keys and busy intervals as values."""
    schedule = {}
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            day = row['Day']
            start_time = parse_time(row['Start Time'])
            end_time = parse_time(row['End Time'])
            if day not in schedule:
                schedule[day] = []
            schedule[day].append((start_time, end_time))
    return schedule

def merge_intervals(intervals):
    """Merge overlapping intervals."""
    if not intervals:
        return []
    intervals.sort()
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:  # Overlapping intervals
            merged[-1] = (prev[0], max(prev[1], current[1]))
        else:
            merged.append(current)
    return merged

def get_free_intervals(busy_intervals, day_start, day_end):
    """Compute free intervals given busy intervals and the day's start and end times."""
    free_intervals = []
    if not busy_intervals:
        free_intervals.append((day_start, day_end))
    else:
        if busy_intervals[0][0] > day_start:
            free_intervals.append((day_start, busy_intervals[0][0]))
        for i in range(len(busy_intervals) - 1):
            free_intervals.append((busy_intervals[i][1], busy_intervals[i + 1][0]))
        if busy_intervals[-1][1] < day_end:
            free_intervals.append((busy_intervals[-1][1], day_end))
    # Discard intervals less than one hour
    filtered_intervals = [
        interval for interval in free_intervals
        if (interval[1] - interval[0]) >= 60
    ]
    return filtered_intervals

def main():
    # Define working hours (08:00 to 22:00)
    day_start = parse_time('08:00')
    day_end = parse_time('22:00')
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # Read schedules from all CSV files in the current directory
    schedules = []
    for filename in glob.glob('../resources/*.csv'):
        schedule = read_schedule(filename)
        schedules.append(schedule)

    # Compute combined busy intervals for each day
    combined_busy = {}
    for day in days_of_week:
        daily_intervals = []
        for schedule in schedules:
            if day in schedule:
                daily_intervals.extend(schedule[day])
        # Merge intervals
        merged_intervals = merge_intervals(daily_intervals)
        combined_busy[day] = merged_intervals

    # Compute free intervals for each day
    combined_free = {}
    for day in days_of_week:
        busy_intervals = combined_busy.get(day, [])
        free_intervals = get_free_intervals(busy_intervals, day_start, day_end)
        combined_free[day] = free_intervals

    # Output the free intervals
    print("Common Available Time Slots (Intervals of at least 1 hour):")
    for day in days_of_week:
        print(f"\n{day}:")
        free_intervals = combined_free[day]
        if not free_intervals:
            print("  No common free time slots available.")
        else:
            for interval in free_intervals:
                start = format_time(interval[0])
                end = format_time(interval[1])
                print(f"  {start} - {end}")

if __name__ == "__main__":
    main()
