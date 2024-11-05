import csv
from datetime import datetime, timedelta
import sys

def parse_time_str(time_str):
    """Convert time string like '1m 8s' or '9m ' to seconds"""
    if not time_str or time_str == '-' or time_str is None:
        return 0
    
    total_seconds = 0
    parts = time_str.strip().split()
    
    for part in parts:
        if part.endswith('m'):
            total_seconds += int(part[:-1]) * 60
        elif part.endswith('s'):
            total_seconds += int(part[:-1])
            
    return total_seconds

def format_duration(seconds):
    """Convert seconds to human readable duration with hours if needed"""
    if seconds == 0:
        return "0m 0s"
    
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    final_seconds = remaining_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if final_seconds > 0:
        parts.append(f"{final_seconds}s")
        
    return " ".join(parts)

def parse_date(date_str):
    """Convert date string to datetime object"""
    return datetime.strptime(date_str, "%b %d, %Y")

def parse_money(money_str):
    """Convert money string to float"""
    if not money_str or money_str == '-':
        return 0.0
    return float(money_str.replace('$', ''))

def analyze_earnings_file(csv_file):
    # Dictionary to store daily totals
    daily_totals = {}
    grand_totals = {
        'total_seconds': 0,
        'prepay_seconds': 0,
        'overtime_seconds': 0,
        'total_earnings': 0.0,
        'prepay_earnings': 0.0,
        'overtime_earnings': 0.0,
        'mission_earnings': 0.0
    }
    
    # Read CSV data
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            date = row['workDate']
            duration = row.get('duration', '')
            pay_type = row['payType']
            payout = parse_money(row['payout'])
            
            # Initialize daily totals if not exists
            if date not in daily_totals:
                daily_totals[date] = {
                    'total_seconds': 0,
                    'prepay_seconds': 0,
                    'overtime_seconds': 0,
                    'total_earnings': 0.0,
                    'prepay_earnings': 0.0,
                    'overtime_earnings': 0.0,
                    'mission_earnings': 0.0
                }
            
            # Update earnings for all types
            daily_totals[date]['total_earnings'] += payout
            grand_totals['total_earnings'] += payout
            
            if pay_type == 'missionReward':
                daily_totals[date]['mission_earnings'] += payout
                grand_totals['mission_earnings'] += payout
                continue
            
            try:
                # Convert duration to seconds for non-mission entries
                seconds = parse_time_str(duration)
                
                # Update daily totals
                daily_totals[date]['total_seconds'] += seconds
                if pay_type == 'prepay':
                    daily_totals[date]['prepay_seconds'] += seconds
                    daily_totals[date]['prepay_earnings'] += payout
                    grand_totals['prepay_earnings'] += payout
                elif pay_type == 'overtimePay':
                    daily_totals[date]['overtime_seconds'] += seconds
                    daily_totals[date]['overtime_earnings'] += payout
                    grand_totals['overtime_earnings'] += payout
                    
                # Update grand time totals
                grand_totals['total_seconds'] += seconds
                if pay_type == 'prepay':
                    grand_totals['prepay_seconds'] += seconds
                elif pay_type == 'overtimePay':
                    grand_totals['overtime_seconds'] += seconds
                    
            except Exception as e:
                print(f"Error processing row with date {date}, duration {duration}: {str(e)}")
    
    # Sort dates properly using datetime objects
    sorted_dates = sorted(daily_totals.keys(), 
                         key=lambda x: parse_date(x), 
                         reverse=True)
    
    # Print results
    print("Daily Totals:")
    print("-" * 65)
    for date in sorted_dates:
        totals = daily_totals[date]
        print(f"\n{date}:")
        print(f"  Total time:     {format_duration(totals['total_seconds']):15} Total earnings:    ${totals['total_earnings']:.2f}")
        print(f"  Prepay time:    {format_duration(totals['prepay_seconds']):15} Prepay earnings:   ${totals['prepay_earnings']:.2f}")
        print(f"  Overtime time:  {format_duration(totals['overtime_seconds']):15} Overtime earnings: ${totals['overtime_earnings']:.2f}")
        if totals['mission_earnings'] > 0:
            print(f"  Mission rewards: ${totals['mission_earnings']:.2f}")
    
    print("\nGrand Totals:")
    print("-" * 65)
    print(f"Total time:     {format_duration(grand_totals['total_seconds']):15} Total earnings:    ${grand_totals['total_earnings']:.2f}")
    print(f"Prepay time:    {format_duration(grand_totals['prepay_seconds']):15} Prepay earnings:   ${grand_totals['prepay_earnings']:.2f}")
    print(f"Overtime time:  {format_duration(grand_totals['overtime_seconds']):15} Overtime earnings: ${grand_totals['overtime_earnings']:.2f}")
    if grand_totals['mission_earnings'] > 0:
        print(f"Mission rewards: ${grand_totals['mission_earnings']:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python earnings_analysis.py <csv_file_path>")
        sys.exit(1)

    csv_file = sys.argv[1]
    analyze_earnings_file(csv_file)
