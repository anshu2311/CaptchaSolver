# main.py
from config import *


chrome_binary_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
credentials_file = "credentials_recaptcha.txt"
login_url = "https://leetcode.com/accounts/login/"

def human_type(element, text):
    """Simulate human typing with random delays"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def load_credentials():
    """Load credentials from file"""
    try:
        with open(credentials_file, "r") as f:
            return [line.strip().split(",") for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"Error reading credentials: {e}")
        return []

def setup_driver():
    """Configure undetectable browser"""
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    
    # Anti-detection settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def handle_recaptcha(driver):
    """Click verify button and wait for manual solving"""
    print("\n🛡️ reCAPTCHA verification required")
    
    # Switch to reCAPTCHA iframe
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']")))
    
    # Click verify checkbox
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
    checkbox.click()
    
    # Switch back to main content
    driver.switch_to.default_content()
    
    # Wait for manual solving
    print("1. Please solve any image challenges")
    print("2. Wait for verification to complete")
    print("3. The script will continue automatically once verified...")
    
    # Wait for verification to complete
    try:
        WebDriverWait(driver, 120).until(
            lambda d: d.find_element(By.XPATH, "//div[contains(@class, 'recaptcha-success')]"))
        print("✅ Verification complete!")
        return True
    except:
        print("❌ Verification failed or timed out")
        return False

def leetcode_login(driver, username, password):
    """Complete login flow with reCAPTCHA handling"""
    try:
        # Load login page
        driver.get(login_url)
        time.sleep(random.uniform(1, 2))
        
        # Fill credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_login")))
        human_type(username_field, username)
        
        password_field = driver.find_element(By.ID, "id_password")
        human_type(password_field, password)
        time.sleep(1)
        
        # Handle reCAPTCHA before login
        if handle_recaptcha(driver):
            # Click login after verification
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "signin_btn")))
            login_button.click()
            
            # Verify login success
            WebDriverWait(driver, 15).until(
                lambda d: "leetcode.com" in d.current_url and "accounts/login" not in d.current_url)
            print("🎉 Login successful!")
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        driver.save_screenshot("login_error.png")
        return False

def main():
    credentials = load_credentials()
    if not credentials:
        print("No valid credentials found")
        return
    
    driver = setup_driver()
    try:
        for username, password in credentials:
            if leetcode_login(driver, username, password):
                print(f"Logged in as {username}")
                break
            print(f"Failed for {username} - trying next...")
        
        # Keep browser open
        print("Keeping browser open for 60 seconds...")
        time.sleep(60)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
