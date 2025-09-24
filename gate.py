# main.py
from config import *


chrome_path = r"C:\\Program Files\Google\Chrome\Application\chrome.exe"
login_url = "https://goaps.iisc.ac.in/login"
credentials_file = "credentials_gate.txt"

# Read all credentials from file
with open(credentials_file, "r") as f:
    credentials = [line.strip().split(",") for line in f if line.strip()]

# Set up Selenium to use Brave
service = Service(CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()
options.binary_location = chrome_path
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")

# Start browser once
driver = webdriver.Chrome(service=service, options=options)

for username, password in credentials:
    print(f"\n🔐 Trying login with: {username}")
    try:
        # Refresh only once at the start of each attempt
        driver.get(login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        # Fill in login details
        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "username").send_keys(username)
        
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(password)

        # CAPTCHA handling - only + and - operations with single digits
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'captcha')]"))
        )
        captcha_img.screenshot("captcha.png")

        # CAPTCHA processing
        img_cv = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)
        _, thresh = cv2.threshold(img_cv, 200, 255, cv2.THRESH_BINARY)
        
        # Remove lines
        lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, 30, minLineLength=30, maxLineGap=5)
        line_mask = np.zeros_like(img_cv)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(line_mask, (x1, y1), (x2, y2), 255, 2)
            img_cv_clean = cv2.inpaint(img_cv, line_mask, 3, cv2.INPAINT_TELEA)
        else:
            img_cv_clean = img_cv

        # Image processing
        img = Image.fromarray(img_cv_clean)
        img = img.filter(ImageFilter.MedianFilter())
        img = img.point(lambda x: 0 if x < 145 else 255)
        img = img.resize((img.width * 3, img.height * 3))
        img = img.filter(ImageFilter.SHARPEN)
        img.save("final_preprocessed_captcha.png")

        # OCR with limited character set
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789+-'
        raw_text = pytesseract.image_to_string(img, config=custom_config).strip()
        print(f"OCR Output: {raw_text}")

        # Clean and validate CAPTCHA (only single-digit +- operations)
        clean_text = re.sub(r'[^\d+-]', '', raw_text)
        if len(clean_text) < 3:  # Minimum format like "1+1"
            clean_text = "1+1"  # Fallback simple CAPTCHA
        
        # Ensure single-digit operations only
        parts = re.split(r'([+-])', clean_text)
        if len(parts) >= 3:
            # Rebuild with only single digits
            num1 = parts[0][-1] if parts[0] else '1'
            op = parts[1] if parts[1] in '+-' else '+'
            num2 = parts[2][0] if parts[2] else '1'
            safe_text = f"{num1}{op}{num2}"
        else:
            safe_text = "1+1"
        
        print(f"Validated CAPTCHA: {safe_text}")

        try:
            captcha_answer = str(eval(safe_text))
        except:
            captcha_answer = "2"  # Fallback answer
            print("⚠️ CAPTCHA eval failed, using fallback")

        # Submit CAPTCHA and login
        driver.find_element(By.ID, "captcha").clear()
        driver.find_element(By.ID, "captcha").send_keys(captcha_answer)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(., 'Login')]").click()

        # Check login result
        time.sleep(2)
        if "login" not in driver.current_url.lower():
            print("✅ Login successful!")
            break  # Stop after successful login
        else:
            print("❌ Login failed for:", username)

    except Exception as e:
        print("❗ Error:", e)
        driver.save_screenshot(f"error_{username}.png")

# Done
print("\n⏳ Script complete. Closing browser...")
driver.quit()