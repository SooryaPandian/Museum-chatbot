import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def download_images(url, download_folder):
    """Downloads images from a webpage and stores them in the specified folder."""
    try:
        # Initialize Chrome options with headless mode (optional)
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Uncomment for headless mode

        # Initialize the ChromeDriver
        driver = webdriver.Chrome(options=options)

        # Open the target URL
        driver.get(url)

        # Wait for images to load (adjust timeout as needed)
        wait = WebDriverWait(driver, 15)  # Increase timeout if needed
        images = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))

        # Create download folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Download images with improved handling
        for i, image in enumerate(images):
            image_url = image.get_attribute('src')
            if image_url:
                filename = f"image_{i+1}_{int(time.time())}.jpg"  # Include timestamp for unique filenames
                image_path = os.path.join(download_folder, filename)

                try:
                    response = requests.get(image_url, stream=True, timeout=10)
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    with open(image_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"Downloaded {image_path}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image {i+1}: {e}")

        print(f"Downloaded {len(images)} images to {download_folder}")

    except TimeoutException:
        print("Error: Image loading timed out.")
    except NoSuchElementException:
        print("Error: No images found on the page.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()  # Always close the browser

# Example usage
url = "https://nationalmuseumindia.gov.in/en"  # Replace with the actual website URL
download_folder = "downloaded_images"  # Replace with your desired folder name
download_images(url, download_folder)