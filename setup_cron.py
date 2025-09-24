"""
Setup script to configure cron job for daily data refresh at 10am PST
"""
import os
import subprocess
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_cron_job():
    """Setup cron job for daily refresh at 10am PST"""
    
    # Convert 10am PST to UTC (PST is UTC-8, PDT is UTC-7)
    # For simplicity, we'll use 18:00 UTC (10am PST during standard time)
    # You may need to adjust this for daylight saving time
    cron_time_utc = "0 18"  # 6:00 PM UTC = 10:00 AM PST
    
    # Get the current directory
    current_dir = os.path.abspath(os.path.dirname(__file__))
    python_path = subprocess.check_output(['which', 'python3']).decode().strip()
    
    # Create the cron command
    cron_command = f"{cron_time_utc} * * * {python_path} {current_dir}/scheduler.py --once"
    
    logger.info(f"Setting up cron job: {cron_command}")
    
    try:
        # Get current crontab
        try:
            current_cron = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            current_cron = ""
        
        # Check if our job already exists
        job_marker = "# Redash query refresh job"
        if job_marker in current_cron:
            logger.info("Cron job already exists. Updating...")
            # Remove existing job
            lines = current_cron.split('\n')
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if job_marker in line:
                    skip_next = True
                    continue
                if skip_next and line.strip() and not line.startswith('#'):
                    skip_next = False
                    continue
                if not skip_next:
                    filtered_lines.append(line)
            
            current_cron = '\n'.join(filtered_lines)
        
        # Add our job
        new_cron = current_cron.rstrip() + f"\n{job_marker}\n{cron_command}\n"
        
        # Install the new crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
        process.communicate(input=new_cron.encode())
        
        if process.returncode == 0:
            logger.info("Cron job installed successfully!")
            logger.info("The data will be refreshed daily at 10:00 AM PST (18:00 UTC)")
            return True
        else:
            logger.error("Failed to install cron job")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up cron job: {e}")
        return False

def create_systemd_service():
    """Create systemd service file for the web application"""
    
    current_dir = os.path.abspath(os.path.dirname(__file__))
    python_path = subprocess.check_output(['which', 'python3']).decode().strip()
    
    service_content = f"""[Unit]
Description=Redash Query Results Website
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={current_dir}
Environment=PATH={os.path.dirname(python_path)}
ExecStart={python_path} {current_dir}/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/redash-website.service"
    
    try:
        # Write service file (requires sudo)
        with open('redash-website.service', 'w') as f:
            f.write(service_content)
        
        logger.info("Systemd service file created: redash-website.service")
        logger.info("To install the service, run:")
        logger.info("sudo cp redash-website.service /etc/systemd/system/")
        logger.info("sudo systemctl daemon-reload")
        logger.info("sudo systemctl enable redash-website")
        logger.info("sudo systemctl start redash-website")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating systemd service: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Setting up Redash to Website automation...")
    
    # Validate configuration
    if not Config.validate():
        logger.error("Invalid configuration. Please check your settings in config.py")
        return False
    
    # Setup cron job
    logger.info("Setting up cron job for daily data refresh...")
    if setup_cron_job():
        logger.info("✓ Cron job setup completed")
    else:
        logger.error("✗ Cron job setup failed")
        return False
    
    # Create systemd service
    logger.info("Creating systemd service file...")
    if create_systemd_service():
        logger.info("✓ Systemd service file created")
    else:
        logger.error("✗ Systemd service creation failed")
    
    logger.info("\nSetup completed! Your Redash query results will be:")
    logger.info("1. Refreshed automatically every day at 10:00 AM PST")
    logger.info("2. Displayed on a beautiful web interface")
    logger.info(f"3. Accessible at http://localhost:{Config.WEB_PORT}")
    
    logger.info("\nNext steps:")
    logger.info("1. Update your Redash URL and Query ID in config.py if needed")
    logger.info("2. Install the systemd service (see instructions above)")
    logger.info("3. Start the web application: python3 app.py")
    
    return True

if __name__ == "__main__":
    main()