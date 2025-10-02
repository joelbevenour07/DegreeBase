
from datetime import datetime

def parse_time(time_str):
    # Assuming the time is in the format "HH:MM AM/PM"
    return datetime.strptime(time_str, "%I:%M %p").time()


def convert_days_to_numbers(day_string):
    day_map = {'M': 1, 'T': 2, 'W': 3, 'R': 4, 'F': 5}
    days = []
    i = 0
    while i < len(day_string):
        # if day_string[i:i+2] == 'TR':
        #     days.append(day_map['TR'])
        #     i += 2
        days.append(day_map[day_string[i]])
        i += 1
    return days

def days_overlap(days1, days2):
    set1 = set(convert_days_to_numbers(days1))
    set2 = set(convert_days_to_numbers(days2))
    return not set1.isdisjoint(set2)

def times_overlap(start1, end1, start2, end2):
    start1 = parse_time(start1)
    end1 = parse_time(end1)
    start2 = parse_time(start2)
    end2 = parse_time(end2)
    return start1 < end2 and start2 < end1


def can_enroll(new_enroll, existing_classes, new_class):
    new_days = new_class.days
    new_start = new_class.start_time
    new_end = new_class.end_time
    
    for existing_class in existing_classes:
        existing_days = existing_class.days
        existing_start = existing_class.start_time
        existing_end = existing_class.end_time
        
        if days_overlap(new_days, existing_days) and times_overlap(new_start, new_end, existing_start, existing_end):
            return False  # Overlap found, cannot enroll
    return True  # No overlaps, can enroll