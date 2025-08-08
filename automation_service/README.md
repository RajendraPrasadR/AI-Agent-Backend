# Automation Service

## Description
The Automation Service contains Selenium-based automation scripts for various portal interactions. This service is designed to be modular, allowing easy addition of new automation tasks.

## Features
- Modular automation modules
- Selenium WebDriver integration
- Portal automation capabilities
- Extensible architecture for new automation tasks

## Planned Modules
- **Batch Approval**: ESC batch approval automation for Naipunyam portal
- **Certificate Generation**: Automated certificate generation tasks
- **Report Download**: Automated report downloading from various portals

## Running the Service
```bash
cd automation_service
pip install -r requirements.txt
python main.py
```

## Adding New Automation Modules
1. Create a new function for your automation task
2. Add it to the `AutomationService.execute_automation()` method
3. Update the `available_modules` list in `get_status()`

## Configuration
The service will use environment variables for portal credentials and configuration settings.
