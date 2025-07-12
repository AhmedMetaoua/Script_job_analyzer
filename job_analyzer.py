#!/usr/bin/env python3
"""
Job Performance Analyzer - Command Line Interface
Generates PDF reports with job performance graphs and sends them via email.

Usage:
    python job_analyzer.py --email recipient@example.com [options]

Example:
    python job_analyzer.py --email admin@company.com --host localhost --user root --password mypass --database scheduler_test --start-date 2025-05-01 --end-date 2025-05-31
"""

import argparse
import sys
import pandas as pd
from datetime import datetime, timedelta
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import tempfile
import os
from collections import defaultdict
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "ahmedmtawahg@gmail.com"
EMAIL_PASSWORD = "wdiervjootstklaq"  # App password

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Job Performance Analyzer - Generate and send PDF reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --email admin@company.com
  %(prog)s --email admin@company.com --host 192.168.1.100 --user admin --password secret
  %(prog)s --email admin@company.com --start-date 2025-01-01 --end-date 2025-01-31
        """
    )
    
    # Required arguments
    parser.add_argument('--email', '-e', required=True, 
                       help='Email address to send the report to')
    
    # Database connection arguments
    parser.add_argument('--host', default='localhost', 
                       help='MySQL host (default: localhost)')
    parser.add_argument('--user', '-u', default='root', 
                       help='MySQL username (default: root)')
    parser.add_argument('--password', '-p', default='azerty', 
                       help='MySQL password (default: azerty)')
    parser.add_argument('--database', '-d', default='scheduler_test', 
                       help='MySQL database name (default: scheduler_test)')
    parser.add_argument('--port', type=int, default=3306, 
                       help='MySQL port (default: 3306)')
    
    # Date range arguments
    parser.add_argument('--start-date', default='2025-05-01', 
                       help='Start date for analysis (YYYY-MM-DD, default: 2025-05-01)')
    parser.add_argument('--end-date', default='2025-05-31', 
                       help='End date for analysis (YYYY-MM-DD, default: 2025-05-31)')
    
    # Email arguments
    parser.add_argument('--subject', default='Job Performance Analysis Report', 
                       help='Email subject (default: Job Performance Analysis Report)')
    parser.add_argument('--message', default='', 
                       help='Custom email message')
    
    # Output arguments
    parser.add_argument('--save-pdf', metavar='PATH', 
                       help='Save PDF to local file instead of/in addition to sending email')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    
    return parser.parse_args()

def log_message(message, verbose=True):
    """Print message with timestamp if verbose mode is enabled"""
    if verbose:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

def connect_to_database(args):
    """Connect to MySQL database and fetch job data using SQLAlchemy"""
    # Create connection string for SQLAlchemy
    connection_string = f"mysql+pymysql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"
    
    log_message(f"Connecting to MySQL: {args.host}:{args.port}/{args.database}", args.verbose)
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(connection_string)
        
        query = """
        SELECT JOB_NAME, START_TIME, END_TIME
        FROM stg_scheduler_history
        WHERE START_TIME IS NOT NULL AND END_TIME IS NOT NULL
        """
        
        log_message("Executing SQL query...", args.verbose)
        
        # Use SQLAlchemy engine with pandas
        with engine.connect() as connection:
            df = pd.read_sql(text(query), connection)
        
        log_message(f"Retrieved {len(df)} records from database", args.verbose)
        return df
        
    except SQLAlchemyError as e:
        log_message(f"Database Error: {e}", True)
        sys.exit(1)
    except Exception as e:
        log_message(f"Database connection error: {e}", True)
        sys.exit(1)

def process_job_data(df, start_date, end_date, verbose=True):
    """Process and filter job data"""
    log_message("Processing job data...", verbose)
    
    # Clean and calculate durations
    df["START_TIME"] = pd.to_datetime(df["START_TIME"], errors='coerce')
    df["END_TIME"] = pd.to_datetime(df["END_TIME"], errors='coerce')
    df["DURATION"] = (df["END_TIME"] - df["START_TIME"]).dt.total_seconds() / 60
    df["DURATION"] = df["DURATION"].fillna(0)
    df["DATE"] = df["START_TIME"].dt.date
    
    # Filter date range
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()
    df_filtered = df[(df["DATE"] >= start_date_obj) & (df["DATE"] <= end_date_obj)]
    
    log_message(f"Filtered data: {len(df_filtered)} records for period {start_date} to {end_date}", verbose)
    
    # Convert to list of dictionaries
    job_data = []
    for _, row in df_filtered.iterrows():
        if pd.notna(row['JOB_NAME']) and pd.notna(row['START_TIME']) and pd.notna(row['END_TIME']):
            job_data.append({
                'jobName': row['JOB_NAME'],
                'startTime': row['START_TIME'],
                'endTime': row['END_TIME'],
                'duration': float(row['DURATION']),
                'date': row['DATE']
            })
    
    return job_data

def generate_pdf_report(job_data, filename, start_date, end_date, verbose=True):
    """Generate PDF report with job performance analysis"""
    log_message(f"Generating PDF report: {filename}", verbose)
    
    plt.style.use('seaborn-v0_8')
    
    # Group jobs by name
    jobs_grouped = defaultdict(list)
    for job in job_data:
        jobs_grouped[job['jobName']].append(job)
    
    with PdfPages(filename) as pdf:
        # Summary page
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        total_jobs = len(jobs_grouped)
        total_executions = len(job_data)
        
        summary_text = f"""
Job Performance Analysis Report
{'='*60}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {start_date} to {end_date}

Summary:
• Total unique jobs: {total_jobs}
• Total job executions: {total_executions}
• Average executions per job: {total_executions/total_jobs:.1f}

Job Details:
"""
        
        # Calculate statistics for each job
        job_stats = []
        for job_name, job_list in jobs_grouped.items():
            durations = [job['duration'] for job in job_list]
            stats = {
                'name': job_name,
                'executions': len(job_list),
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations),
                'total_duration': sum(durations)
            }
            job_stats.append(stats)
        
        # Sort by average duration (descending)
        job_stats.sort(key=lambda x: x['avg_duration'], reverse=True)
        
        for stats in job_stats:
            summary_text += f"""
• {stats['name']}:
  - Executions: {stats['executions']}
  - Average duration: {stats['avg_duration']:.1f} min
  - Duration range: {stats['min_duration']:.1f} - {stats['max_duration']:.1f} min
  - Total time: {stats['total_duration']:.1f} min
"""
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Generate charts for each job
        log_message(f"Generating charts for {total_jobs} jobs...", verbose)
        
        for job_name, job_list in jobs_grouped.items():
            # Aggregate by date
            daily_data = defaultdict(float)
            for job in job_list:
                daily_data[job['date']] += job['duration']
            
            dates = sorted(daily_data.keys())
            durations = [daily_data[date] for date in dates]
            
            if not durations:
                continue
            
            # Calculate statistics
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot data
            ax.plot(dates, durations, marker='o', linewidth=2, markersize=4, 
                    color='#3498db', label='Daily Duration')
            
            # Add reference lines
            ax.axhline(y=avg_duration, color='orange', linestyle='--', alpha=0.7, 
                       label=f'Average: {avg_duration:.1f} min')
            ax.axhline(y=max_duration, color='red', linestyle='--', alpha=0.5, 
                       label=f'Maximum: {max_duration:.1f} min')
            ax.axhline(y=min_duration, color='green', linestyle='--', alpha=0.5, 
                       label=f'Minimum: {min_duration:.1f} min')
            
            # Formatting
            ax.set_title(f'Performance Analysis: {job_name}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Duration (minutes)', fontsize=10)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # Format dates on x-axis
            if len(dates) > 10:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//8)))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
    
    log_message(f"PDF report generated successfully: {filename}", verbose)

def send_email_with_pdf(recipient_email, subject, message, pdf_path, verbose=True):
    """Send email with PDF attachment"""
    log_message(f"Sending email to: {recipient_email}", verbose)
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Email body
        if not message:
            message = """
Please find attached the Job Performance Analysis Report.

This report contains:
- Summary of all job executions
- Performance charts for each job
- Statistical analysis of execution times

The report was generated automatically by the Job Performance Analyzer.

Best regards,
Job Performance Analyzer System
"""
        
        body_text = f"""
{message}

Report Details:
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- File: {os.path.basename(pdf_path)}
- Size: {os.path.getsize(pdf_path) / 1024:.1f} KB

Best regards,
Job Performance Analyzer System
"""
        
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
        
        # Attach PDF
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(pdf_path)}',
        )
        
        msg.attach(part)
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        log_message("Email sent successfully!", verbose)
        
    except Exception as e:
        log_message(f"Email sending failed: {e}", True)
        sys.exit(1)

def validate_arguments(args):
    """Validate command line arguments"""
    # Validate email address
    import re
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, args.email):
        log_message(f"Invalid email address: {args.email}", True)
        sys.exit(1)
    
    # Validate dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        
        if start_date >= end_date:
            log_message("Start date must be before end date", True)
            sys.exit(1)
            
    except ValueError:
        log_message("Invalid date format. Use YYYY-MM-DD", True)
        sys.exit(1)

def main():
    """Main function"""
    args = parse_arguments()
    
    # Validate arguments
    validate_arguments(args)
    
    log_message("Job Performance Analyzer - Starting analysis", args.verbose)
    
    # Connect to database and fetch data
    df = connect_to_database(args)
    
    # Process job data
    job_data = process_job_data(df, args.start_date, args.end_date, args.verbose)
    
    if not job_data:
        log_message("No job data found for the specified date range", True)
        sys.exit(1)
    
    # Generate PDF
    if args.save_pdf:
        pdf_filename = args.save_pdf
    else:
        # Create temporary file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', 
                                               prefix='job_analysis_')
        pdf_filename = temp_pdf.name
        temp_pdf.close()
    
    generate_pdf_report(job_data, pdf_filename, args.start_date, args.end_date, args.verbose)
    
    # Send email
    send_email_with_pdf(args.email, args.subject, args.message, pdf_filename, args.verbose)
    
    # Clean up temporary file if not saving locally
    if not args.save_pdf:
        try:
            os.unlink(pdf_filename)
            log_message("Temporary file cleaned up", args.verbose)
        except:
            pass
    else:
        log_message(f"PDF saved locally: {pdf_filename}", args.verbose)
    
    log_message("Job Performance Analysis completed successfully!", args.verbose)

if __name__ == "__main__":
    main()