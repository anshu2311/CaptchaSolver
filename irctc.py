# main.py
from config import *


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

IRCTC_URL = "https://www.irctc.co.in/nget/redirect?pnr=2108873329&service=PRS_MEAL_BOOKING"


def process_captcha(img_path):
    """Clean and prepare CAPTCHA image for OCR"""
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((2,2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return Image.fromarray(processed)

def solve_captcha(driver):
    """Try solving CAPTCHA until a valid one is read and entered"""
    attempts = 0
    while attempts < 5:
        try:
            print(f"\n🔄 Attempting to solve CAPTCHA (Try {attempts + 1})")
            
            # Wait for the CAPTCHA image and save it
            captcha_img = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="login_header_disable"]/div/div/div[2]/div[2]/div/div[2]/div/div[2]/form/div[5]/div/app-captcha/div/div/div[2]/span[1]/img')))
            captcha_img.screenshot('captcha.png')

            # Process image and extract text
            img = process_captcha('captcha.png')
            captcha_text = pytesseract.image_to_string(img, config='--psm 8').strip()
            #captcha_text = ''.join([c for c in captcha_text if c.isalnum()])[:6]
            captcha_text = captcha_text[:6]


            print(f"🔍 Solved CAPTCHA: {captcha_text}")
            
            # If we have a non-empty alphanumeric CAPTCHA
            if len(captcha_text) >= 4:
                captcha_field = driver.find_element(By.XPATH, '//*[@id="captcha"]')
                captcha_field.clear()
                captcha_field.send_keys(captcha_text)
                time.sleep(2)  # Wait 2 seconds after entering CAPTCHA
                return True
            
            attempts += 1
            time.sleep(1)

        except Exception as e:
            print(f"❌ CAPTCHA error: {e}")
            attempts += 1
            time.sleep(2)
    return False

def main():
    # Setup Chrome browser
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_PATH
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Step 1: Open IRCTC
        driver.get(IRCTC_URL)
        time.sleep(2)

        # Step 2: Click on hamburger menu
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-home/div[1]/app-header/div[1]/div[2]/a/i"))
        ).click()
        time.sleep(1)

        # Step 3: Click on login button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='slide-menu']/p-sidebar/div/nav/div/label/button"))
        ).click()
        time.sleep(2)

        # Step 4: Solve CAPTCHA
        if solve_captcha(driver):
            print("✅ CAPTCHA successfully entered!")

        # Hold browser open
        print("⏳ Browser will remain open for 30 seconds...")
        time.sleep(30)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
