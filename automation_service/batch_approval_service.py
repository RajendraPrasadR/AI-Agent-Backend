"""
Automation Service - Batch Approval Service
Selenium-based automation for Naipunyam portal batch approval.
"""

import os
import sys
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException
)
from webdriver_manager.chrome import ChromeDriverManager

from config import ESC_USERNAME, ESC_PASSWORD, HEADLESS, DOWNLOAD_PATH
from logging_config import setup_logging
from utils import ensure_dir, timestamped_filename, Timer

# Get Selenium timeout from environment
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", "30"))

# Setup logging
setup_logging("automation_service")
logger = logging.getLogger(__name__)

class NaipunyamBatchApprovalService:
    """
    Service for automating batch approval in Naipunyam portal.
    """
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://naipunyam.gov.in"  # Replace with actual URL
        self.login_url = f"{self.base_url}/login"
        self.batches_url = f"{self.base_url}/esc/pending-batches"
        
        # Create directories
        self.screenshot_dir = ensure_dir(Path(__file__).parent.parent / "logs" / "screenshots")
        self.results_dir = ensure_dir(Path(__file__).parent.parent / "results")
        self.download_dir = ensure_dir(DOWNLOAD_PATH)
        
        # Initialize logs list for structured logging
        self.execution_logs = []
        
    def _setup_driver(self) -> webdriver.Chrome:
        """
        Setup Chrome WebDriver with appropriate options.
        
        Returns:
            Configured Chrome WebDriver instance
        """
        logger.info("Setting up Chrome WebDriver")
        
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Headless mode
        if HEADLESS:
            chrome_options.add_argument("--headless")
            logger.info("Running in headless mode")
        
        # Download preferences
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Additional stability options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Setup Chrome service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts using environment variable
            driver.implicitly_wait(SELENIUM_TIMEOUT)
            driver.set_page_load_timeout(SELENIUM_TIMEOUT)
            
            logger.info("Chrome WebDriver setup completed")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            raise
    
    def _add_log(self, message: str, level: str = "info"):
        """
        Add a log entry to the execution logs.
        
        Args:
            message: Log message
            level: Log level (info, warning, error)
        """
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        self.execution_logs.append(log_entry)
        
        # Also log to the standard logger
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def _take_screenshot(self, filename_prefix: str = "screenshot", save_to_results: bool = False) -> Optional[str]:
        """
        Take a screenshot and save it to screenshots or results directory.
        
        Args:
            filename_prefix: Prefix for the screenshot filename
            save_to_results: If True, save to results directory for frontend access
            
        Returns:
            Path to the saved screenshot or None if failed
        """
        if not self.driver:
            self._add_log("No WebDriver available for screenshot", "warning")
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{timestamp}.png"
            
            # Choose directory based on save_to_results flag
            target_dir = self.results_dir if save_to_results else self.screenshot_dir
            screenshot_path = target_dir / filename
            
            self.driver.save_screenshot(str(screenshot_path))
            self._add_log(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self._add_log(f"Failed to take screenshot: {e}", "error")
            return None
    
    def _login(self) -> bool:
        """
        Login to Naipunyam portal.
        
        Returns:
            True if login successful, False otherwise
        """
        logger.info("Attempting to login to Naipunyam portal")
        
        try:
            # Navigate to login page
            self.driver.get(self.login_url)
            logger.info(f"Navigated to login page: {self.login_url}")
            
            # Wait for login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys(ESC_USERNAME)
            
            password_field.clear()
            password_field.send_keys(ESC_PASSWORD)
            
            # Take screenshot before login
            self._take_screenshot("before_login")
            
            # Click login button
            login_button.click()
            
            # Wait for successful login (check for dashboard or profile element)
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "dashboard")),
                    EC.presence_of_element_located((By.CLASS_NAME, "user-profile")),
                    EC.url_contains("dashboard")
                )
            )
            
            logger.info("Login successful")
            self._take_screenshot("after_login")
            return True
            
        except TimeoutException:
            logger.error("Login timeout - credentials may be incorrect or page structure changed")
            self._take_screenshot("login_timeout_error")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self._take_screenshot("login_error")
            return False
    
    def _navigate_to_pending_batches(self) -> bool:
        """
        Navigate to pending ESC batches page.
        
        Returns:
            True if navigation successful, False otherwise
        """
        logger.info("Navigating to pending batches page")
        
        try:
            # Navigate to batches page
            self.driver.get(self.batches_url)
            
            # Wait for batches table to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "batches-table"))
            )
            
            logger.info("Successfully navigated to pending batches page")
            self._take_screenshot("pending_batches_page")
            return True
            
        except TimeoutException:
            logger.error("Timeout waiting for pending batches page to load")
            self._take_screenshot("navigation_timeout_error")
            return False
        except Exception as e:
            logger.error(f"Failed to navigate to pending batches: {e}")
            self._take_screenshot("navigation_error")
            return False
    
    def _get_pending_batches(self) -> List[Dict[str, Any]]:
        """
        Get list of pending batches from the page.
        
        Returns:
            List of batch information dictionaries
        """
        logger.info("Retrieving pending batches")
        
        try:
            # Find all batch rows
            batch_rows = self.driver.find_elements(By.XPATH, "//table[@class='batches-table']//tr[position()>1]")
            
            batches = []
            for i, row in enumerate(batch_rows):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 6:  # Adjust based on actual table structure
                        batch_info = {
                            'row_index': i,
                            'batch_id': cells[0].text.strip(),
                            'district': cells[1].text.strip(),
                            'course': cells[2].text.strip(),
                            'college': cells[3].text.strip(),
                            'trainer': cells[4].text.strip(),
                            'status': cells[5].text.strip(),
                            'element': row
                        }
                        batches.append(batch_info)
                        logger.debug(f"Found batch: {batch_info['batch_id']} - {batch_info['district']}")
                        
                except Exception as e:
                    logger.warning(f"Failed to parse batch row {i}: {e}")
                    continue
            
            logger.info(f"Found {len(batches)} pending batches")
            return batches
            
        except Exception as e:
            logger.error(f"Failed to retrieve pending batches: {e}")
            self._take_screenshot("get_batches_error")
            return []
    
    def _approve_batch(self, batch_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Approve a single batch.
        
        Args:
            batch_info: Batch information dictionary
            
        Returns:
            Approval result dictionary
        """
        batch_id = batch_info['batch_id']
        logger.info(f"Attempting to approve batch: {batch_id}")
        
        try:
            # Find approve button in the batch row
            approve_button = batch_info['element'].find_element(
                By.XPATH, ".//button[contains(@class, 'approve-btn') or contains(text(), 'Approve')]"
            )
            
            # Scroll to button if needed
            self.driver.execute_script("arguments[0].scrollIntoView(true);", approve_button)
            time.sleep(1)
            
            # Click approve button
            approve_button.click()
            
            # Wait for confirmation dialog if present
            try:
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes')]"))
                )
                confirm_button.click()
                logger.info(f"Confirmed approval for batch: {batch_id}")
            except TimeoutException:
                logger.info(f"No confirmation dialog for batch: {batch_id}")
            
            # Wait for success message or page update
            try:
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "success-message")),
                        EC.presence_of_element_located((By.CLASS_NAME, "alert-success")),
                        EC.text_to_be_present_in_element((By.CLASS_NAME, "status"), "Approved")
                    )
                )
            except TimeoutException:
                logger.warning(f"No success confirmation visible for batch: {batch_id}")
            
            approval_time = datetime.utcnow().isoformat()
            
            result = {
                'batch_id': batch_id,
                'district': batch_info['district'],
                'course': batch_info['course'],
                'college': batch_info['college'],
                'trainer': batch_info['trainer'],
                'status': 'approved',
                'approved_at': approval_time,
                'success': True
            }
            
            logger.info(f"Successfully approved batch: {batch_id}")
            return result
            
        except ElementClickInterceptedException:
            logger.error(f"Approve button for batch {batch_id} is not clickable")
            return {
                'batch_id': batch_id,
                'status': 'failed',
                'error': 'Button not clickable',
                'success': False
            }
        except Exception as e:
            logger.error(f"Failed to approve batch {batch_id}: {e}")
            self._take_screenshot(f"approve_error_{batch_id}")
            return {
                'batch_id': batch_id,
                'status': 'failed',
                'error': str(e),
                'success': False
            }
    
    def approve_batches(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main function to approve batches in Naipunyam portal.
        
        Args:
            params: Parameters including batch_ids (optional), max_batches (optional)
            
        Returns:
            Approval results dictionary
        """
        logger.info("Starting batch approval process")
        start_time = datetime.utcnow()
        
        # Initialize result structure
        result = {
            'status': 'running',
            'approved_count': 0,
            'failed_count': 0,
            'details': [],
            'summary': '',
            'started_at': start_time.isoformat(),
            'logs': [],
            'screenshot_path': None,
            'download_files': []
        }
        
        # Initialize execution logs
        self.execution_logs = []
        self._add_log(f"Starting batch approval process with params: {params}")
        
        try:
            with Timer("Batch Approval Process") as timer:
                # Setup WebDriver
                self.driver = self._setup_driver()
                self.wait = WebDriverWait(self.driver, SELENIUM_TIMEOUT)
                
                # Login
                self._add_log("Attempting to login to Naipunyam portal")
                if not self._login():
                    raise Exception("Failed to login to Naipunyam portal")
                self._add_log("Successfully logged in to Naipunyam portal")
                
                # Navigate to pending batches
                self._add_log("Navigating to pending batches page")
                if not self._navigate_to_pending_batches():
                    raise Exception("Failed to navigate to pending batches page")
                self._add_log("Successfully navigated to pending batches page")
                
                # Get pending batches
                self._add_log("Fetching pending batches")
                pending_batches = self._get_pending_batches()
                if not pending_batches:
                    self._add_log("No pending batches found")
                    result['summary'] = "No pending batches found"
                    result['completed_at'] = datetime.utcnow().isoformat()
                    result['logs'] = self.execution_logs
                    return result
                
                self._add_log(f"Found {len(pending_batches)} pending batches")
                
                # Filter batches if specific batch_ids provided
                target_batch_ids = params.get('batch_ids', [])
                if target_batch_ids:
                    pending_batches = [
                        batch for batch in pending_batches 
                        if batch['batch_id'] in target_batch_ids
                    ]
                    self._add_log(f"Filtered to {len(pending_batches)} target batches")
                
                # Limit number of batches to process
                max_batches = params.get('max_batches', len(pending_batches))
                batches_to_process = pending_batches[:max_batches]
                
                self._add_log(f"Processing {len(batches_to_process)} batches")
                
                # Process each batch
                for i, batch_info in enumerate(batches_to_process, 1):
                    self._add_log(f"Processing batch {i}/{len(batches_to_process)}: {batch_info.get('batch_id', 'Unknown')}")
                    approval_result = self._approve_batch(batch_info)
                    result['details'].append(approval_result)
                    
                    if approval_result['success']:
                        result['approved_count'] += 1
                        self._add_log(f"Successfully approved batch: {batch_info.get('batch_id', 'Unknown')}")
                    else:
                        result['failed_count'] += 1
                        self._add_log(f"Failed to approve batch: {batch_info.get('batch_id', 'Unknown')} - {approval_result.get('error', 'Unknown error')}", "error")
                    
                    # Add delay between approvals
                    time.sleep(2)
                
                # Update summary
                result['summary'] = f"Processed {len(batches_to_process)} batches: {result['approved_count']} approved, {result['failed_count']} failed"
                result['completed_at'] = datetime.utcnow().isoformat()
                result['execution_time'] = timer.duration
                result['logs'] = self.execution_logs
                
                self._add_log(f"Batch approval process completed: {result['summary']}")
                
                # Take a success screenshot and save to results directory
                success_screenshot = self._take_screenshot("batch_approval_success", save_to_results=True)
                if success_screenshot:
                    result['screenshot_path'] = success_screenshot
                
        except Exception as e:
            error_msg = str(e)
            self._add_log(f"Batch approval process failed: {error_msg}", "error")
            
            # Take error screenshot and save to results directory for frontend access
            error_screenshot = None
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                error_screenshot = self._take_screenshot(f"batch_approval_error_{timestamp}", save_to_results=True)
                if error_screenshot:
                    self._add_log(f"Error screenshot saved: {error_screenshot}")
            except Exception as screenshot_error:
                self._add_log(f"Failed to capture error screenshot: {screenshot_error}", "warning")
            
            result.update({
                'status': 'failed',
                'error': error_msg,
                'failed_at': datetime.utcnow().isoformat(),
                'screenshot_path': error_screenshot,
                'selenium_timeout': SELENIUM_TIMEOUT,
                'logs': self.execution_logs
            })
            
        finally:
            # Cleanup WebDriver
            if self.driver:
                try:
                    self.driver.quit()
                    self._add_log("WebDriver closed successfully")
                except Exception as e:
                    self._add_log(f"Failed to close WebDriver: {e}", "warning")
            
            # Ensure logs are always included in the result
            if 'logs' not in result:
                result['logs'] = self.execution_logs
        
        return result

# Global function for task mapping
def approve_batches(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Global function for batch approval (used by worker service).
    
    Args:
        params: Task parameters
        
    Returns:
        Batch approval results
    """
    service = NaipunyamBatchApprovalService()
    return service.approve_batches(params)
