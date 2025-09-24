# Redash Query to Website

This project automatically fetches data from a Redash query and displays it on a beautiful, modern website that refreshes daily at 10:00 AM PST.

## Features

- 🔄 **Automatic Daily Refresh**: Data refreshes every day at 10:00 AM PST
- 🌐 **Beautiful Web Interface**: Modern, responsive design with Bootstrap 5
- 📊 **Data Visualization**: Clean tables with sorting and filtering
- 🔧 **Manual Refresh**: Option to manually refresh data through the UI
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🔌 **API Endpoints**: RESTful API for programmatic access
- 📈 **Real-time Status**: Live status indicators and metrics
- 🔒 **Error Handling**: Robust error handling and logging

## Quick Start

### 1. Prerequisites

- Python 3.7 or higher
- Access to a Redash instance
- Redash API key
- Query ID from your Redash instance

### 2. Installation

```bash
# Clone or download the project files
cd redash-to-website

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data logs
```

### 3. Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the configuration in `config.py` or set environment variables:

```python
# Required settings
REDASH_BASE_URL = "https://your-redash-instance.com"
REDASH_API_KEY = "ofytSWp0O5riMpC3ldRrJy0sCndu2H9jYEqkfLG1"  # Your API key is already set
REDASH_QUERY_ID = 123  # Replace with your actual query ID
```

### 4. Test the Connection

```bash
# Test the Redash connection
python redash_client.py
```

### 5. Setup Automatic Scheduling

```bash
# Setup cron job for daily refresh at 10am PST
python setup_cron.py
```

### 6. Start the Web Application

```bash
# Start the web server
python app.py
```

Visit `http://localhost:8000` to see your website!

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDASH_BASE_URL` | Your Redash instance URL | Required |
| `REDASH_API_KEY` | Your Redash API key | Already set |
| `REDASH_QUERY_ID` | The ID of your query | Required |
| `WEB_PORT` | Port for the web server | 8000 |
| `WEB_HOST` | Host for the web server | 0.0.0.0 |
| `SITE_TITLE` | Title of your website | "Redash Query Results" |
| `SITE_DESCRIPTION` | Description of your website | "Daily updated query results" |

### Finding Your Query ID

1. Open your query in Redash
2. Look at the URL: `https://your-redash.com/queries/123`
3. The number (123) is your Query ID

## Usage

### Web Interface

- **Main Dashboard**: View your query results in a beautiful table format
- **Manual Refresh**: Click the "Refresh Data" button to update immediately
- **Auto-refresh**: Page automatically checks for new data every 5 minutes
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### API Endpoints

- `GET /` - Main dashboard page
- `GET /api/data` - Get current data as JSON
- `POST /api/refresh` - Manually trigger data refresh
- `GET /health` - Health check endpoint

### Manual Operations

```bash
# Run a one-time data refresh
python scheduler.py --once

# Test the Redash connection
python redash_client.py

# Run the scheduler continuously (for testing)
python scheduler.py
```

## Deployment

### Option 1: Simple Background Process

```bash
# Run the web app in the background
nohup python app.py > app.log 2>&1 &
```

### Option 2: Systemd Service (Recommended)

1. Install the service:
```bash
sudo cp redash-website.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable redash-website
sudo systemctl start redash-website
```

2. Check status:
```bash
sudo systemctl status redash-website
```

### Option 3: Docker (if you prefer)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py"]
```

## Scheduling Details

The system uses cron to schedule daily data refreshes at 10:00 AM PST:

- **Cron Expression**: `0 18 * * *` (18:00 UTC = 10:00 AM PST)
- **Timezone Handling**: Automatically converts PST to UTC
- **Error Handling**: Failed refreshes are logged and retried
- **Daylight Saving**: You may need to adjust for DST

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check your Redash URL and API key
   - Ensure your Redash instance is accessible
   - Verify the API key has proper permissions

2. **Query Not Found**
   - Verify the Query ID is correct
   - Ensure the query exists and is published
   - Check if you have access to the query

3. **Data Not Refreshing**
   - Check the cron job: `crontab -l`
   - Review logs: `tail -f logs/app.log`
   - Test manual refresh: `python scheduler.py --once`

4. **Website Not Loading**
   - Check if the port is available: `netstat -tlnp | grep 8000`
   - Review Flask logs for errors
   - Ensure all dependencies are installed

### Logs

- Application logs: `logs/app.log`
- Cron logs: Check system cron logs (`/var/log/cron` or `journalctl -u cron`)
- Service logs: `sudo journalctl -u redash-website`

## Security Considerations

- Keep your API key secure and don't commit it to version control
- Consider using environment variables or a secrets management system
- Restrict access to the web interface if displaying sensitive data
- Use HTTPS in production environments
- Regularly rotate your API keys

## Customization

### Styling

Edit `templates/index.html` to customize the appearance:
- Modify CSS variables in the `<style>` section
- Change colors, fonts, and layout
- Add your own branding

### Data Processing

Edit `app.py` to customize how data is processed:
- Modify the `format_data_for_display()` function
- Add data aggregations or calculations
- Implement custom filters

### Scheduling

Edit `scheduler.py` to change refresh timing:
- Modify the schedule time
- Add multiple refresh times
- Implement different refresh strategies

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure your configuration is correct
4. Test each component individually

## Contributing

Feel free to submit issues and enhancement requests!