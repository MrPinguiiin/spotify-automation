#!/usr/bin/env python3
"""
SCRIPT EDUKASI - JANGAN DIGUNAKAN UNTUK TUJUAN KOMERSIAL!

Script ini dibuat untuk keperluan edukasi dan penelitian saja.
Penggunaan script ini untuk membuat akun Spotify secara massal atau
bypass sistem pembayaran MELANGGAR Terms of Service dan dapat berakibat:
- Pemblokiran akun
- Masalah hukum
- Pelanggaran kebijakan platform

GUNAKAN DENGAN RISIKO SENDIRI!
"""

import time
import random
import csv
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from colorama import init, Fore, Style
import os
import logging
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import re

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotify_automation.log'),
        logging.StreamHandler()
    ]
)

# Tambahkan fungsi untuk generate username random
def generate_random_username(length=8):
    """Generate random username"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class SpotifyAutomation:
    def __init__(self, proxy=None, vpn_country='AU'):
        """Initialize the automation class with optional proxy and VPN country"""
        self.driver = None
        self.wait = None
        self.proxy = proxy
        
        # Normalisasi kode negara
        vpn_country = vpn_country.upper()
        
        # Daftar negara yang didukung
        supported_countries = ['ID', 'AU', 'US', 'GB', 'SG']
        
        # Validasi negara
        if vpn_country not in supported_countries:
            print(f"{Fore.YELLOW}⚠ Negara {vpn_country} tidak didukung!")
            print(f"{Fore.YELLOW}Menggunakan default: AU")
            vpn_country = 'AU'
        
        self.vpn_country = vpn_country
        self.vcc_data = []
        if not self.load_vcc_data():
            print(f"{Fore.YELLOW}⚠ Tidak ada data kartu kredit yang valid!")
            # Tambahkan data dummy jika diperlukan
            self.vcc_data.append({
                'number': '4111111111111111',
                'month': '12',
                'year': '2025',
                'cvv': '123',
                'name': 'Spotify Trial'
            })
        
    def load_vcc_data(self):
        """Load VCC data from file"""
        try:
            with open('vcc_data.txt', 'r') as file:
                for line in file:
                    # Hapus whitespace dan baris kosong
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Split dengan delimiter '|'
                    parts = line.split('|')
                    
                    # Validasi jumlah bagian
                    if len(parts) >= 4:
                        vcc_info = {
                            'number': parts[0].replace(' ', ''),  # Hapus spasi
                            'month': parts[1].zfill(2),  # Pastikan 2 digit
                            'year': parts[2],
                            'cvv': parts[3],
                            # Tambahkan nama default jika tidak ada
                            'name': 'Spotify Trial' if len(parts) < 5 else parts[4]
                        }
                        self.vcc_data.append(vcc_info)
            
            # Cetak detail untuk debugging
            print(f"{Fore.GREEN}✓ Berhasil memuat {len(self.vcc_data)} data kartu kredit")
            
            # Cetak detail kartu untuk konfirmasi
            for idx, card in enumerate(self.vcc_data, 1):
                print(f"{Fore.CYAN}Kartu {idx}:")
                print(f"  Nomor: {card['number']}")
                print(f"  Kadaluarsa: {card['month']}/{card['year']}")
                print(f"  CVV: {card['cvv']}")
            
            return len(self.vcc_data) > 0
        
        except FileNotFoundError:
            print(f"{Fore.RED}❌ File vcc_data.txt tidak ditemukan!")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan saat memuat data kartu kredit: {e}")
            return False
    
    def setup_proxy(self, options):
        """Setup proxy for the webdriver"""
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        return options
    
    def verify_vpn_connection(self):
        """
        Verifikasi koneksi VPN dengan deteksi IP dan redirect dinamis
        
        :return: Boolean
        """
        # Daftar layanan IP untuk fallback
        ip_services = [
            'https://ipapi.co/json/',
            'https://api.country.is/ip',
            'https://ip-api.com/json',
            'https://ipinfo.io/json'
        ]
        
        for service_url in ip_services:
            try:
                # Gunakan session untuk koneksi yang lebih stabil
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                # Timeout yang lebih panjang dan fleksibel
                response = session.get(service_url, timeout=15)
                
                # Pastikan response berhasil
                response.raise_for_status()
                
                # Parsing JSON dengan error handling
                try:
                    country_data = response.json()
                except ValueError:
                    print(f"{Fore.YELLOW}⚠ Gagal parsing JSON dari {service_url}")
                    continue
                
                # Ekstrak informasi IP dengan fallback
                current_country = country_data.get('country_code') or \
                                  country_data.get('countryCode') or \
                                  country_data.get('country') or \
                                  'Unknown'
                
                current_country = current_country.upper()
                
                # Informasi tambahan
                current_country_name = country_data.get('country_name', 
                                        country_data.get('countryName', 
                                        country_data.get('regionName', 'Tidak Diketahui')))
                current_ip = country_data.get('ip', 
                                              country_data.get('query', 
                                              country_data.get('ipAddress', 'Tidak Diketahui')))
                
                # Logging informasi IP
                print(f"{Fore.CYAN}Informasi IP:")
                print(f"  Layanan: {service_url}")
                print(f"  IP: {current_ip}")
                print(f"  Negara: {current_country_name} ({current_country})")
                
                # Daftar URL signup Spotify untuk berbagai negara
                spotify_signup_urls = {
                    'ID': 'https://www.spotify.com/id/signup',
                    'AU': 'https://www.spotify.com/au/signup',
                    'US': 'https://www.spotify.com/us/signup',
                    'GB': 'https://www.spotify.com/gb/signup',
                    'SG': 'https://www.spotify.com/sg/signup'
                }
                
                # Tentukan URL signup berdasarkan negara
                target_url = spotify_signup_urls.get(self.vpn_country, 
                                                     spotify_signup_urls.get('AU', 'https://www.spotify.com/signup'))
                
                # Validasi koneksi VPN
                if current_country != self.vpn_country:
                    print(f"{Fore.YELLOW}⚠ Koneksi VPN tidak sesuai target!")
                    print(f"{Fore.YELLOW}  Target: {self.vpn_country}")
                    print(f"{Fore.YELLOW}  Aktual: {current_country}")
                    
                    # Opsi: Lanjutkan dengan peringatan atau redirect
                    confirmation = input(f"{Fore.YELLOW}Lanjutkan dengan negara saat ini? (yes/no): ").lower()
                    
                    if confirmation != 'yes':
                        print(f"{Fore.RED}Proses dihentikan karena negara tidak sesuai.")
                        return False
                
                # Navigasi ke URL signup yang sesuai
                try:
                    print(f"{Fore.CYAN}Navigasi ke halaman signup: {target_url}")
                    self.driver.get(target_url)
                    
                    # Tunggu halaman dimuat dengan WebDriverWait
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    
                    # Tambahan: Verifikasi halaman dimuat dengan benar
                    current_page_title = self.driver.title
                    if not current_page_title or 'Signup' not in current_page_title:
                        print(f"{Fore.YELLOW}⚠ Halaman signup mungkin tidak dimuat dengan benar!")
                    
                    return True
                
                except Exception as nav_error:
                    print(f"{Fore.RED}Gagal navigasi ke halaman signup: {nav_error}")
                    continue
            
            except (requests.exceptions.RequestException, 
                    requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout) as req_error:
                print(f"{Fore.YELLOW}⚠ Kesalahan koneksi dengan {service_url}: {req_error}")
                continue
            
            except Exception as e:
                print(f"{Fore.RED}Kesalahan tidak terduga: {e}")
                continue
        
        # Jika semua layanan gagal
        print(f"{Fore.RED}❌ Gagal mendapatkan informasi IP dari semua layanan!")
        
        # Fallback terakhir: Tanya pengguna
        print(f"{Fore.YELLOW}Pilih negara manual:")
        for country_code in ['ID', 'AU', 'US', 'GB', 'SG']:
            print(f"  {country_code}")
        
        manual_country = input(f"{Fore.CYAN}Masukkan kode negara (default AU): ").upper() or 'AU'
        
        # Update vpn_country
        self.vpn_country = manual_country
        
        return False
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def type_like_human(self, element, text):
        """Type text with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def generate_fake_user_data(self):
        """Generate fake user data for account creation"""
        username = generate_random_username()
        name = f"{username.capitalize()} User"
        email = f"{username}@badcode.biz.id"
        password = f"SpotifyTrial{random.randint(1000, 9999)}!"
        
        return {
            'name': name,
            'email': email,
            'password': password,
            'birth_year': random.randint(1990, 2005),
            'birth_month': random.randint(1, 12),
            'birth_day': random.randint(1, 28)
        }
    
    def navigate_to_signup(self):
        """Navigate to Spotify signup page"""
        try:
            print(f"{Fore.CYAN}Navigating to Spotify signup page...")
            self.driver.get("https://www.spotify.com/au/signup")
            self.random_delay(2, 4)
            print(f"{Fore.GREEN}✓ Loaded signup page")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error navigating to signup: {str(e)}")
            return False
    
    def safe_send_keys(self, element, text):
        """Metode aman untuk mengisi input dengan berbagai fallback"""
        try:
            # Metode 1: Clear dan isi langsung
            element.clear()
            element.send_keys(text)
            time.sleep(0.5)
            
            # Metode 2: JavaScript input
            self.driver.execute_script(
                f"arguments[0].value = '{text}';", 
                element
            )
            time.sleep(0.5)
            
            # Trigger events
            self.driver.execute_script("""
                var event = new Event('input', { bubbles: true });
                arguments[0].dispatchEvent(event);
                var event = new Event('change', { bubbles: true });
                arguments[0].dispatchEvent(event);
            """, element)
            
            # Verifikasi isi
            current_value = element.get_attribute('value')
            if current_value != text:
                print(f"{Fore.YELLOW}⚠ Nilai input tidak sesuai. Coba metode manual")
                # Metode manual
                for char in text:
                    element.send_keys(char)
                    time.sleep(0.1)
            
            time.sleep(1)  # Delay akhir
        except Exception as e:
            print(f"{Fore.RED}Gagal mengisi input: {e}")
            # Tangkap screenshot untuk debugging
            try:
                self.driver.save_screenshot(f"input_error_{text}.png")
            except:
                pass

    def fill_signup_form(self, user_data):
        """Fill the signup form with user data"""
        try:
            print(f"{Fore.CYAN}Filling signup form...")
            
            # Email field
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            self.type_like_human(email_field, user_data['email'])
            self.random_delay()
            
            # Password field
            password_field = self.driver.find_element(By.ID, "password")
            self.type_like_human(password_field, user_data['password'])
            self.random_delay()
            
            # Display name
            name_field = self.driver.find_element(By.ID, "displayname")
            self.type_like_human(name_field, user_data['name'])
            self.random_delay()
            
            # Birth date
            day_field = self.driver.find_element(By.ID, "day")
            self.type_like_human(day_field, str(user_data['birth_day']))
            
            month_select = self.driver.find_element(By.ID, "month")
            month_select.click()
            self.random_delay(0.5, 1)
            month_option = self.driver.find_element(By.XPATH, f"//option[@value='{user_data['birth_month']:02d}']")
            month_option.click()
            
            year_field = self.driver.find_element(By.ID, "year")
            self.type_like_human(year_field, str(user_data['birth_year']))
            
            # Gender (random selection)
            gender_options = self.driver.find_elements(By.NAME, "gender")
            if gender_options:
                random.choice(gender_options).click()
            
            self.random_delay()
            
            # Terms and conditions
            terms_checkbox = self.driver.find_element(By.ID, "terms-conditions-checkbox")
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
            
            self.random_delay()
            
            print(f"{Fore.GREEN}✓ Form filled successfully")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error filling form: {str(e)}")
            return False
    
    def submit_signup(self):
        """Submit the signup form"""
        try:
            print(f"{Fore.CYAN}Submitting signup form...")
            
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for potential captcha or verification
            self.random_delay(3, 5)
            
            print(f"{Fore.GREEN}✓ Signup submitted")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error submitting signup: {str(e)}")
            return False
    
    def handle_verification(self):
        """Handle email verification if required"""
        try:
            print(f"{Fore.YELLOW}Checking for verification requirements...")
            
            # Check if verification page is shown
            if "verify" in self.driver.current_url.lower():
                print(f"{Fore.YELLOW}⚠ Email verification required")
                print(f"{Fore.YELLOW}Manual intervention needed for email verification")
                return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error handling verification: {str(e)}")
            return False
    
    def navigate_to_premium(self):
        """Navigate to premium subscription page"""
        try:
            print(f"{Fore.CYAN}Navigating to premium page...")
            
            # Try to find premium link
            premium_links = [
                "//a[contains(text(), 'Premium')]",
                "//a[contains(@href, 'premium')]",
                "//button[contains(text(), 'Premium')]"
            ]
            
            for xpath in premium_links:
                try:
                    premium_link = self.driver.find_element(By.XPATH, xpath)
                    premium_link.click()
                    self.random_delay(2, 3)
                    break
                except NoSuchElementException:
                    continue
            
            print(f"{Fore.GREEN}✓ Navigated to premium page")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error navigating to premium: {str(e)}")
            return False
    
    def select_premium_plan(self):
        """Select a premium plan"""
        try:
            print(f"{Fore.CYAN}Selecting premium plan...")
            
            # Look for premium plan buttons
            plan_buttons = [
                "//button[contains(text(), 'Individual')]",
                "//button[contains(text(), 'Get Premium')]",
                "//a[contains(text(), 'Individual')]"
            ]
            
            for xpath in plan_buttons:
                try:
                    plan_button = self.driver.find_element(By.XPATH, xpath)
                    plan_button.click()
                    self.random_delay(2, 3)
                    break
                except NoSuchElementException:
                    continue
            
            print(f"{Fore.GREEN}✓ Premium plan selected")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error selecting plan: {str(e)}")
            return False
    
    def fill_payment_form(self, vcc_info):
        """Fill payment form with VCC data"""
        try:
            print(f"{Fore.CYAN}Filling payment form...")
            print(f"{Fore.RED}⚠ WARNING: This is for educational purposes only!")
            
            # Card number
            card_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "cardnumber"))
            )
            self.type_like_human(card_field, vcc_info['number'])
            self.random_delay()
            
            # Expiry month
            month_field = self.driver.find_element(By.NAME, "exp-month")
            self.type_like_human(month_field, vcc_info['month'])
            
            # Expiry year
            year_field = self.driver.find_element(By.NAME, "exp-year")
            self.type_like_human(year_field, vcc_info['year'])
            
            # CVV
            cvv_field = self.driver.find_element(By.NAME, "cvc")
            self.type_like_human(cvv_field, vcc_info['cvv'])
            
            # Cardholder name
            name_field = self.driver.find_element(By.NAME, "cardholdername")
            self.type_like_human(name_field, vcc_info['name'])
            
            self.random_delay()
            
            print(f"{Fore.GREEN}✓ Payment form filled")
            print(f"{Fore.RED}⚠ NOT SUBMITTING - Educational purpose only!")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error filling payment form: {str(e)}")
            return False
    
    def save_account_info(self, user_data, success=False):
        """Save account information to file"""
        try:
            with open('created_accounts.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                
                # Write header if file is empty
                if file.tell() == 0:
                    writer.writerow(['Email', 'Password', 'Name', 'Status', 'Timestamp'])
                
                status = 'Success' if success else 'Failed'
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                
                writer.writerow([
                    user_data['email'],
                    user_data['password'],
                    user_data['name'],
                    status,
                    timestamp
                ])
            
            print(f"{Fore.GREEN}✓ Account info saved to file")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error saving account info: {str(e)}")
    
    def click_button(self, button):
        """Metode klik tombol dengan multiple fallback"""
        try:
            # Metode 1: Selenium click standar
            try:
                button.click()
                time.sleep(1)
                return True
            except:
                pass
            
            # Metode 2: JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                return True
            except:
                pass
            
            # Metode 3: JavaScript trigger mouse event
            try:
                self.driver.execute_script("""
                    var evt = document.createEvent('MouseEvents');
                    evt.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                    arguments[0].dispatchEvent(evt);
                """, button)
                time.sleep(1)
                return True
            except:
                pass
            
            # Metode 4: Koordinat click
            try:
                actions = webdriver.ActionChains(self.driver)
                actions.move_to_element(button).click().perform()
                time.sleep(1)
                return True
            except:
                pass
            
            print(f"{Fore.RED}❌ Gagal mengklik tombol!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}Kesalahan saat mengklik tombol: {e}")
            return False

    def find_element_robust(self, strategies):
        """
        Metode pencarian elemen dengan multiple fallback strategies
        
        :param strategies: List of tuples (search_method, locator)
        :return: WebElement atau None
        """
        for method, locator in strategies:
            try:
                # Coba berbagai metode pencarian
                if method == 'xpath':
                    element = self.driver.find_element(By.XPATH, locator)
                elif method == 'css':
                    element = self.driver.find_element(By.CSS_SELECTOR, locator)
                elif method == 'id':
                    element = self.driver.find_element(By.ID, locator)
                elif method == 'name':
                    element = self.driver.find_element(By.NAME, locator)
                elif method == 'class':
                    element = self.driver.find_element(By.CLASS_NAME, locator)
                elif method == 'tag':
                    element = self.driver.find_element(By.TAG_NAME, locator)
                else:
                    continue
                
                # Tambahan validasi
                if element and element.is_displayed() and element.is_enabled():
                    return element
            except:
                continue
        
        return None

    def click_element_expert(self, element):
        """
        Metode klik elemen dengan multiple fallback
        
        :param element: WebElement untuk diklik
        :return: Boolean
        """
        click_strategies = [
            # Metode 1: Selenium click standar
            lambda: element.click(),
            
            # Metode 2: JavaScript click
            lambda: self.driver.execute_script("arguments[0].click();", element),
            
            # Metode 3: ActionChains click
            lambda: webdriver.ActionChains(self.driver).move_to_element(element).click().perform(),
            
            # Metode 4: JavaScript trigger mouse event
            lambda: self.driver.execute_script("""
                var evt = document.createEvent('MouseEvents');
                evt.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                arguments[0].dispatchEvent(evt);
            """, element)
        ]
        
        for strategy in click_strategies:
            try:
                strategy()
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"{Fore.YELLOW}Metode klik gagal: {e}")
                continue
        
        print(f"{Fore.RED}❌ Semua metode klik gagal!")
        return False

    def send_keys_expert(self, element, text):
        """
        Metode input teks dengan multiple fallback
        
        :param element: WebElement untuk diisi
        :param text: Teks yang akan dimasukkan
        :return: Boolean
        """
        input_strategies = [
            # Metode 1: Selenium send_keys
            lambda: element.clear() or element.send_keys(text),
            
            # Metode 2: JavaScript set value
            lambda: self.driver.execute_script(f"arguments[0].value = '{text}';", element),
            
            # Metode 3: Karakter per karakter
            lambda: [element.send_keys(char) or time.sleep(0.1) for char in text]
        ]
        
        for strategy in input_strategies:
            try:
                strategy()
                
                # Validasi isi
                current_value = element.get_attribute('value')
                if current_value == text:
                    # Trigger events
                    self.driver.execute_script("""
                        var event = new Event('input', { bubbles: true });
                        arguments[0].dispatchEvent(event);
                        var changeEvent = new Event('change', { bubbles: true });
                        arguments[0].dispatchEvent(changeEvent);
                    """, element)
                    
                    time.sleep(0.5)
                    return True
            except Exception as e:
                print(f"{Fore.YELLOW}Metode input gagal: {e}")
                continue
        
        print(f"{Fore.RED}❌ Semua metode input gagal!")
        return False

    def wait_for_page_change(self, initial_url, timeout=10, check_interval=1):
        """
        Tunggu perubahan halaman dengan mekanisme deteksi canggih
        
        :param initial_url: URL awal sebelum navigasi
        :param timeout: Waktu maksimal tunggu perubahan
        :param check_interval: Interval pengecekan
        :return: Boolean
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Cek perubahan URL
                current_url = self.driver.current_url
                if current_url != initial_url:
                    print(f"{Fore.GREEN}✓ Halaman berhasil berubah!")
                    return True
                
                # Cek keberadaan elemen baru
                new_page_indicators = [
                    # Selector untuk field password
                    ('id', 'password'),
                    ('xpath', "//input[@type='password']"),
                    
                    # Selector untuk field nama
                    ('id', 'displayname'),
                    ('xpath', "//input[@placeholder='Enter a profile name']"),
                    
                    # Selector umum untuk halaman berikutnya
                    ('xpath', "//button[contains(text(), 'Next')]"),
                    ('xpath', "//button[@type='submit']")
                ]
                
                for method, locator in new_page_indicators:
                    try:
                        if method == 'id':
                            element = self.driver.find_element(By.ID, locator)
                        elif method == 'xpath':
                            element = self.driver.find_element(By.XPATH, locator)
                        
                        # Jika elemen ditemukan dan dapat diinteraksi
                        if element and element.is_displayed() and element.is_enabled():
                            print(f"{Fore.GREEN}✓ Elemen baru ditemukan: {locator}")
                            return True
                    except:
                        continue
                
                # Tambahan: Cek perubahan DOM
                page_height = self.driver.execute_script("return document.body.scrollHeight")
                page_width = self.driver.execute_script("return document.body.scrollWidth")
                
                # Tunggu sebentar
                time.sleep(check_interval)
                
                # Bandingkan perubahan DOM
                new_page_height = self.driver.execute_script("return document.body.scrollHeight")
                new_page_width = self.driver.execute_script("return document.body.scrollWidth")
                
                if (new_page_height != page_height or new_page_width != page_width):
                    print(f"{Fore.GREEN}✓ Struktur halaman berubah!")
                    return True
                
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Kesalahan saat memeriksa halaman: {e}")
            
            # Tunggu sebentar sebelum cek ulang
            time.sleep(check_interval)
        
        print(f"{Fore.RED}❌ Tidak ada perubahan halaman setelah {timeout} detik")
        return False

    def click_next_robust(self, strategies, max_attempts=3):
        """
        Metode klik tombol Next dengan multiple attempts dan deteksi halaman
        
        :param strategies: Daftar strategi pencarian tombol
        :param max_attempts: Jumlah maksimal percobaan klik
        :return: Boolean
        """
        for attempt in range(max_attempts):
            try:
                # Simpan URL awal
                initial_url = self.driver.current_url
                
                # Cari tombol
                next_button = self.find_element_robust(strategies)
                
                if not next_button:
                    print(f"{Fore.YELLOW}⚠ Tombol Next tidak ditemukan (Percobaan {attempt + 1})")
                    time.sleep(1)  # Tunggu sebentar
                    continue
                
                # Scroll ke tombol jika perlu
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(0.5)
                except:
                    pass
                
                # Klik tombol dengan metode expert
                if not self.click_element_expert(next_button):
                    print(f"{Fore.YELLOW}⚠ Gagal mengklik tombol (Percobaan {attempt + 1})")
                    time.sleep(1)
                    continue
                
                # Tunggu perubahan halaman
                if self.wait_for_page_change(initial_url):
                    print(f"{Fore.GREEN}✓ Berhasil navigasi (Percobaan {attempt + 1})")
                    return True
                
                # Jika tidak berubah, coba metode alternatif
                try:
                    # Coba trigger JavaScript navigation
                    self.driver.execute_script("""
                        var buttons = document.querySelectorAll('button[type="submit"], button[data-testid="submit"]');
                        if (buttons.length > 0) {
                            buttons[0].click();
                        }
                    """)
                    
                    # Tunggu perubahan
                    if self.wait_for_page_change(initial_url):
                        print(f"{Fore.GREEN}✓ Berhasil navigasi dengan JavaScript (Percobaan {attempt + 1})")
                        return True
                except:
                    pass
                
                # Tunggu sebentar sebelum percobaan berikutnya
                time.sleep(1)
            
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Kesalahan saat navigasi: {e}")
                time.sleep(1)
        
        print(f"{Fore.RED}❌ Gagal navigasi setelah {max_attempts} percobaan")
        return False

    def handle_username_input(self, user_data):
        """
        Metode komprehensif untuk menangani input username dengan strategi canggih
        
        :param user_data: Dictionary berisi data pengguna
        :return: Boolean
        """
        try:
            # Simpan URL awal
            initial_url = self.driver.current_url
            
            # Strategi pencarian field email/username
            username_strategies = [
                ('id', 'username'),
                ('id', 'email'),
                ('xpath', "//input[@type='email']"),
                ('xpath', "//input[contains(@placeholder, 'email')]"),
                ('css', "input[type='email']"),
                ('name', 'email')
            ]
            
            # Cari field username
            username_field = self.find_element_robust(username_strategies)
            if not username_field:
                print(f"{Fore.RED}❌ Tidak dapat menemukan field username!")
                return False
            
            # Input username dengan metode expert
            if not self.send_keys_expert(username_field, user_data['email']):
                print(f"{Fore.RED}❌ Gagal mengisi username!")
                return False
            
            # Strategi tombol Next
            next_button_strategies = [
                ('xpath', "//button[@data-testid='submit']"),
                ('xpath', "//button[contains(@class, 'Button-sc-')]"),
                ('xpath', "//button[@type='submit']"),
                ('xpath', "//button[contains(text(), 'Next')]"),
                ('css', "button[type='submit']")
            ]
            
            # Multiple strategi klik tombol
            click_strategies = [
                # Strategi 1: Klik langsung
                lambda: self.click_next_robust(next_button_strategies),
                
                # Strategi 2: Trigger keyboard Enter
                lambda: self.trigger_enter_key(username_field),
                
                # Strategi 3: JavaScript click pada tombol terdekat
                lambda: self.click_nearest_button(username_field)
            ]
            
            # Coba setiap strategi
            for strategy in click_strategies:
                try:
                    # Reset halaman jika perlu
                    self.driver.refresh()
                    time.sleep(1)
                    
                    # Isi ulang field
                    username_field = self.find_element_robust(username_strategies)
                    if username_field:
                        self.send_keys_expert(username_field, user_data['email'])
                    
                    # Coba strategi navigasi
                    if strategy():
                        # Tunggu perubahan halaman
                        if self.wait_for_page_change(initial_url):
                            print(f"{Fore.GREEN}✓ Berhasil navigasi setelah input username!")
                            return True
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠ Strategi navigasi gagal: {e}")
                    continue
            
            print(f"{Fore.RED}❌ Semua strategi navigasi gagal!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan saat menangani input username: {str(e)}")
            return False
    
    def trigger_enter_key(self, element):
        """
        Trigger tombol Enter pada elemen
        
        :param element: WebElement untuk trigger Enter
        :return: Boolean
        """
        try:
            # Metode 1: Selenium send_keys
            element.send_keys(Keys.RETURN)
            time.sleep(1)
            return True
        except:
            try:
                # Metode 2: JavaScript trigger
                self.driver.execute_script("""
                    var evt = new KeyboardEvent('keydown', {
                        'key': 'Enter',
                        'keyCode': 13,
                        'which': 13,
                        'bubbles': true,
                        'cancelable': true
                    });
                    arguments[0].dispatchEvent(evt);
                """, element)
                time.sleep(1)
                return True
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Gagal trigger Enter: {e}")
                return False
    
    def click_nearest_button(self, element):
        """
        Cari dan klik tombol terdekat dengan elemen
        
        :param element: WebElement referensi
        :return: 
        """
        try:
            # Cari tombol terdekat dengan berbagai strategi
            button_strategies = [
                # Cari tombol submit terdekat
                lambda: element.find_element(By.XPATH, "./following::button[@type='submit']"),
                
                # Cari tombol di parent
                lambda: element.find_element(By.XPATH, ".//ancestor::form//button[@type='submit']"),
                
                # Cari tombol di sekitar elemen
                lambda: element.find_element(By.XPATH, ".//ancestor::div//button[contains(@class, 'submit')]"),
                
                # JavaScript query selector
                lambda: self.driver.execute_script("""
                    var element = arguments[0];
                    var buttons = element.closest('form').querySelectorAll('button[type="submit"]');
                    return buttons.length > 0 ? buttons[0] : null;
                """, element)
            ]
            
            # Coba setiap strategi
            for strategy in button_strategies:
                try:
                    button = strategy()
                    if button:
                        # Scroll ke tombol
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # Klik tombol
                        if self.click_element_expert(button):
                            return True
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠ Strategi pencarian tombol gagal: {e}")
                    continue
            
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan saat mencari tombol terdekat: {str(e)}")
            return False

    def prevent_page_regression(self, initial_url, max_attempts=3):
        """
        Cegah regresi halaman dengan berbagai strategi
        
        :param initial_url: URL awal sebelum navigasi
        :param max_attempts: Jumlah maksimal percobaan
        :return: Boolean
        """
        for attempt in range(max_attempts):
            try:
                current_url = self.driver.current_url
                
                # Cek apakah halaman kembali ke semula
                if current_url == initial_url:
                    print(f"{Fore.YELLOW}⚠ Deteksi regresi halaman (Percobaan {attempt + 1})")
                    
                    # Strategi 1: Refresh halaman
                    self.driver.refresh()
                    time.sleep(2)
                    
                    # Strategi 2: Hapus cache dan cookies untuk halaman tersebut
                    self.driver.execute_script("localStorage.clear(); sessionStorage.clear();")
                    self.driver.delete_all_cookies()
                    
                    # Strategi 3: Trigger JavaScript navigation
                    self.driver.execute_script("""
                        // Coba navigasi mundur
                        if (window.history.length > 1) {
                            window.history.forward();
                        }
                        
                        // Trigger event navigasi
                        var event = new Event('popstate');
                        window.dispatchEvent(event);
                    """)
                    
                    time.sleep(2)
                    
                    # Cek ulang URL
                    if self.driver.current_url == initial_url:
                        # Strategi terakhir: Reload dari server
                        self.driver.execute_script("location.reload(true);")
                        time.sleep(2)
                
                # Cek keberadaan elemen lanjutan
                advanced_page_indicators = [
                    ('xpath', "//input[@type='password']"),
                    ('id', 'password'),
                    ('xpath', "//button[contains(text(), 'Next')]"),
                    ('xpath', "//button[@type='submit']")
                ]
                
                # Cari indikator halaman lanjutan
                for method, locator in advanced_page_indicators:
                    try:
                        if method == 'xpath':
                            element = self.driver.find_element(By.XPATH, locator)
                        elif method == 'id':
                            element = self.driver.find_element(By.ID, locator)
                        
                        # Jika elemen ditemukan dan dapat diinteraksi
                        if element and element.is_displayed() and element.is_enabled():
                            print(f"{Fore.GREEN}✓ Berhasil mencapai halaman lanjutan!")
                            return True
                    except:
                        continue
                
                # Jika tidak ada indikasi maju
                print(f"{Fore.YELLOW}⚠ Tidak ada kemajuan halaman")
                time.sleep(1)
            
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Kesalahan saat mencegah regresi: {e}")
                time.sleep(1)
        
        print(f"{Fore.RED}❌ Gagal mencegah regresi halaman")
        return False

    def select_gender(self):
        """
        Metode komprehensif dan robust untuk memilih gender
        
        :return: Boolean
        """
        try:
            # Daftar strategi pencarian elemen gender dengan prioritas tinggi
            gender_strategies = [
                # Strategi 1: Selector spesifik dengan ID dan value yang tepat
                lambda: self.driver.find_element(By.ID, "gender_option_male"),
                lambda: self.driver.find_element(By.XPATH, "//input[@id='gender_option_male']"),
                
                # Strategi 2: Selector dengan atribut name dan value
                lambda: self.driver.find_element(By.XPATH, "//input[@name='gender' and @value='male']"),
                
                # Strategi 3: Pencarian luas dengan berbagai selector
                lambda: self.driver.find_element(By.XPATH, "//input[@name='gender' and @id='gender_option_male']"),
                lambda: self.driver.find_element(By.XPATH, "//div[contains(@class, 'gender-options')]//input[@value='male']"),
            ]
            
            # Variabel untuk menyimpan elemen gender yang valid
            gender_element = None
            
            # Coba setiap strategi pencarian
            for strategy in gender_strategies:
                try:
                    potential_element = strategy()
                    
                    # Validasi elemen
                    if (potential_element and 
                        potential_element.is_displayed() and 
                        potential_element.is_enabled()):
                        gender_element = potential_element
                        break
                except Exception as strategy_error:
                    print(f"{Fore.YELLOW}⚠ Strategi pencarian gender gagal: {strategy_error}")
                    continue
            
            # Jika tidak ditemukan elemen
            if not gender_element:
                print(f"{Fore.RED}❌ Tidak dapat menemukan elemen gender!")
                
                # Debugging: Cetak semua input radio
                try:
                    radio_inputs = self.driver.find_elements(By.XPATH, "//input[@type='radio' and @name='gender']")
                    print(f"{Fore.YELLOW}Input radio yang tersedia:")
                    for input_el in radio_inputs:
                        print(f"  - ID: {input_el.get_attribute('id')}")
                        print(f"  - Name: {input_el.get_attribute('name')}")
                        print(f"  - Value: {input_el.get_attribute('value')}")
                        print(f"  - Displayed: {input_el.is_displayed()}")
                        print(f"  - Enabled: {input_el.is_enabled()}")
                        print("---")
                except Exception as debug_error:
                    print(f"{Fore.YELLOW}Gagal mendapatkan informasi debug: {debug_error}")
                
                return False
            
            # Scroll ke elemen dengan JavaScript
            self.driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'nearest'
                });
            """, gender_element)
            time.sleep(0.5)
            
            # Multiple click strategies
            click_strategies = [
                # Metode 1: Selenium click standar
                lambda: gender_element.click(),
                
                # Metode 2: JavaScript click
                lambda: self.driver.execute_script("arguments[0].click();", gender_element),
                
                # Metode 3: Trigger click events
                lambda: self.driver.execute_script("""
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    arguments[0].dispatchEvent(event);
                """, gender_element)
            ]
            
            # Coba setiap strategi klik
            for strategy in click_strategies:
                try:
                    strategy()
                    
                    # Verifikasi pilihan
                    time.sleep(0.5)
                    if gender_element.is_selected():
                        print(f"{Fore.GREEN}✓ Berhasil memilih gender!")
                        return True
                except Exception as click_error:
                    print(f"{Fore.YELLOW}⚠ Metode klik gender gagal: {click_error}")
            
            print(f"{Fore.RED}❌ Gagal memilih gender!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan fatal saat memilih gender: {e}")
            return False

    def fill_profile_form(self, user_data):
        """
        Metode komprehensif untuk mengisi form profil Spotify dengan strategi canggih
        
        :param user_data: Dictionary berisi data pengguna
        :return: Boolean
        """
        try:
            # Strategi pencarian field nama dengan selector baru
            name_strategies = [
                ('id', 'displayName'),
                ('xpath', "//input[@name='displayName']"),
                ('xpath', "//input[contains(@aria-errormessage, 'displayname-error-message')]"),
                ('xpath', "//input[contains(@data-encore-id, 'formInput')]")
            ]
            
            # Cari field nama dengan strategi robust
            name_field = self.find_element_robust(name_strategies)
            if not name_field:
                print(f"{Fore.RED}❌ Tidak dapat menemukan field nama!")
                return False
            
            # Input nama dengan metode expert
            if not self.send_keys_expert(name_field, user_data['name']):
                print(f"{Fore.RED}❌ Gagal mengisi nama!")
                return False
            
            # Strategi input tanggal lahir
            day_strategies = [
                ('id', 'day'),
                ('xpath', "//input[@data-encore-id='formInput' and @name='day']"),
                ('xpath', "//input[@placeholder='DD']")
            ]
            
            month_strategies = [
                ('xpath', "//div[@data-encore-id='formSelect']//select[@name='month']"),
                ('id', 'month'),
                ('xpath', "//select[contains(@aria-label, 'Month')]")
            ]
            
            year_strategies = [
                ('id', 'year'),
                ('xpath', "//input[@data-encore-id='formInput' and @name='year']"),
                ('xpath', "//input[@placeholder='YYYY']")
            ]
            
            # Cari dan isi field hari
            day_field = self.find_element_robust(day_strategies)
            if not day_field:
                print(f"{Fore.RED}❌ Tidak dapat menemukan field hari!")
                return False
            
            # Input hari
            if not self.send_keys_expert(day_field, str(user_data['birth_day']).zfill(2)):
                print(f"{Fore.RED}❌ Gagal mengisi hari!")
                return False
            
            # Cari dan pilih bulan dengan strategi canggih
            month_field = self.find_element_robust(month_strategies)
            if not month_field:
                print(f"{Fore.RED}❌ Tidak dapat menemukan field bulan!")
                return False
            
            # Metode pilih bulan yang lebih robust
            try:
                # Konversi nama bulan jika perlu
                month_mapping = {
                    1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                    5: 'May', 6: 'June', 7: 'July', 8: 'August', 
                    9: 'September', 10: 'October', 11: 'November', 12: 'December'
                }
                month_name = month_mapping.get(user_data['birth_month'], str(user_data['birth_month']))
                
                # Coba berbagai metode select
                select_methods = [
                    # Metode 1: Select by value
                    lambda: Select(month_field).select_by_value(f"{user_data['birth_month']:02d}"),
                    
                    # Metode 2: Select by visible text
                    lambda: Select(month_field).select_by_visible_text(month_name),
                    
                    # Metode 3: JavaScript select
                    lambda: self.driver.execute_script(f"""
                        var select = arguments[0];
                        for (var i = 0; i < select.options.length; i++) {{
                            if (select.options[i].value == '{user_data['birth_month']:02d}' || 
                                select.options[i].text.includes('{month_name}')) {{
                                select.selectedIndex = i;
                                select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                return true;
                            }}
                        }}
                        return false;
                    """, month_field)
                ]
                
                # Coba setiap metode
                for method in select_methods:
                    try:
                        method()
                        break
                    except Exception as select_error:
                        print(f"{Fore.YELLOW}⚠ Metode select bulan gagal: {select_error}")
                else:
                    print(f"{Fore.RED}❌ Gagal memilih bulan!")
                    return False
            
            except Exception as month_error:
                print(f"{Fore.RED}❌ Kesalahan saat memilih bulan: {month_error}")
                return False
            
            # Cari dan isi field tahun
            year_field = self.find_element_robust(year_strategies)
            if not year_field:
                print(f"{Fore.RED}❌ Tidak dapat menemukan field tahun!")
                return False
            
            # Input tahun
            if not self.send_keys_expert(year_field, str(user_data['birth_year'])):
                print(f"{Fore.RED}❌ Gagal mengisi tahun!")
                return False
            
            # Pilih gender menggunakan metode baru
            if not self.select_gender():
                print(f"{Fore.YELLOW}⚠ Gagal memilih gender!")
                # Lanjutkan meskipun gagal memilih gender
            
            # Strategi tombol Next
            next_button_strategies = [
                ('xpath', "//button[@data-encore-id='buttonPrimary']"),
                ('xpath', "//button[contains(@class, 'Button-sc-')]"),
                ('xpath', "//button[@type='submit' and contains(@class, 'Button-sc-')]"),
                ('xpath', "//button[contains(text(), 'Next')]")
            ]
            
            # Cari dan klik tombol Next
            next_button = self.find_element_robust(next_button_strategies)
            if not next_button:
                print(f"{Fore.RED}❌ Tidak dapat menemukan tombol Next!")
                return False
            
            # Klik tombol Next
            if not self.click_element_expert(next_button):
                print(f"{Fore.RED}❌ Gagal mengklik tombol Next!")
                return False
            
            print(f"{Fore.GREEN}✓ Berhasil mengisi form profil!")
            return True
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan saat mengisi form profil: {str(e)}")
            return False

    def complete_final_signup_step(self):
        """
        Metode komprehensif untuk menyelesaikan langkah terakhir signup Spotify
        
        :return: Boolean
        """
        try:
            # Strategi pencarian tombol submit final
            final_submit_strategies = [
                # Selector spesifik dari gambar
                ('xpath', "//button[@data-testid='submit']"),
                ('xpath', "//button[@data-encore-id='buttonPrimary']"),
                
                # Selector umum untuk tombol submit
                ('xpath', "//button[@type='submit' and contains(@class, 'Button-sc-')]"),
                ('xpath', "//button[contains(text(), 'Sign up')]"),
                ('xpath', "//button[contains(@class, 'signup-button')]"),
                
                # Selector dengan teks spesifik
                ('xpath', "//button[contains(text(), 'Create account')]"),
                ('xpath', "//button[contains(text(), 'Continue')]"),
                
                # Selector dengan data attributes
                ('xpath', "//button[@data-encore-id='text' and contains(text(), 'Sign up')]")
            ]
            
            # Cari tombol submit
            submit_button = None
            for strategy in final_submit_strategies:
                try:
                    potential_button = self.driver.find_element(By.XPATH, strategy[1])
                    
                    # Validasi tambahan
                    if (potential_button.is_displayed() and 
                        potential_button.is_enabled()):
                        submit_button = potential_button
                        break
                except:
                    continue
            
            # Jika tombol tidak ditemukan
            if not submit_button:
                print(f"{Fore.RED}❌ Tidak dapat menemukan tombol submit akhir!")
                
                # Tangkap screenshot untuk debugging
                try:
                    self.driver.save_screenshot("final_signup_error.png")
                    print(f"{Fore.YELLOW}Screenshot disimpan sebagai final_signup_error.png")
                except:
                    pass
                
                return False
            
            # Scroll ke tombol
            self.driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'nearest'
                });
            """, submit_button)
            time.sleep(0.5)
            
            # Multiple click strategies
            click_strategies = [
                # Metode 1: Selenium click
                lambda: submit_button.click(),
                
                # Metode 2: JavaScript click
                lambda: self.driver.execute_script("arguments[0].click();", submit_button),
                
                # Metode 3: Trigger click events
                lambda: self.driver.execute_script("""
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    arguments[0].dispatchEvent(event);
                """, submit_button)
            ]
            
            # Coba setiap strategi klik
            for strategy in click_strategies:
                try:
                    strategy()
                    
                    # Tunggu perubahan halaman
                    WebDriverWait(self.driver, 10).until(
                        EC.url_changes(self.driver.current_url)
                    )
                    
                    print(f"{Fore.GREEN}✓ Berhasil submit langkah terakhir!")
                    return True
                
                except Exception as click_error:
                    print(f"{Fore.YELLOW}⚠ Metode klik submit gagal: {click_error}")
            
            print(f"{Fore.RED}❌ Gagal submit langkah terakhir!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan fatal saat submit akhir: {e}")
            
            # Tangkap screenshot untuk debugging
            try:
                self.driver.save_screenshot("final_signup_fatal_error.png")
                print(f"{Fore.YELLOW}Screenshot fatal error disimpan sebagai final_signup_fatal_error.png")
            except:
                pass
            
            return False

    def bypass_recaptcha(self):
        """
        Metode bypass reCAPTCHA Spotify dengan navigasi keyboard murni
        
        :return: Boolean
        """
        try:
            print(f"{Fore.CYAN}Memulai proses bypass reCAPTCHA...")
            
            # Simpan URL saat ini
            current_url = self.driver.current_url
            
            # Daftar URL free trial/pembayaran Spotify
            free_trial_urls = [
                'https://www.spotify.com/au/purchase/offer/default-intro?country=AU'
            ]
            
            # Tunggu sebentar untuk memastikan halaman dimuat
            time.sleep(2)
            
            # Klik 1 kali di halaman kosong
            try:
                # Klik di tengah halaman
                self.driver.execute_script("""
                    var body = document.body;
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: body.clientWidth / 2,
                        clientY: body.clientHeight / 2
                    });
                    body.dispatchEvent(event);
                """)
                
                print(f"{Fore.GREEN}✓ Berhasil klik halaman kosong!")
                
                # Tunggu sebentar setelah klik
                time.sleep(1)
            
            except Exception as click_error:
                print(f"{Fore.YELLOW}⚠ Gagal klik halaman kosong: {click_error}")
            
            # Navigasi keyboard
            try:
                # Persiapan ActionChains
                actions = webdriver.ActionChains(self.driver)
                
                # Tekan Tab beberapa kali untuk mencapai checkbox
                for _ in range(2):  # 4 kali
                    actions.send_keys(Keys.TAB).pause(1)  # Delay 1 detik
                
                # Eksekusi navigasi
                actions.perform()
                
                # Tunggu sebentar
                time.sleep(1)
                
                # Tekan Enter
                actions.send_keys(Keys.ENTER).pause(0.5).perform()
                
                print(f"{Fore.GREEN}✓ Berhasil navigasi keyboard!")
                
                # Tunggu sebentar untuk proses verifikasi
                time.sleep(2)
            
            except Exception as keyboard_error:
                print(f"{Fore.YELLOW}⚠ Gagal navigasi keyboard: {keyboard_error}")
                return False
            
            # Cari tombol Continue
            continue_buttons = [
                "//button[contains(text(), 'Continue')]",
                "//button[@data-testid='submit']",
                "//button[contains(@class, 'ReCaptchaChallenge__StyledButtonPrimary')]",
                "//button[contains(@class, 'Button-sc-')]",
                "//button[contains(@class, 'g-recaptcha')]"
            ]
            
            continue_button = None
            for button_xpath in continue_buttons:
                try:
                    potential_button = self.driver.find_element(By.XPATH, button_xpath)
                    
                    # Validasi tombol
                    if potential_button.is_displayed() and potential_button.is_enabled():
                        continue_button = potential_button
                        break
                except:
                    continue
            
            # Jika tombol Continue ditemukan, klik perlahan
            if continue_button:
                try:
                    # Tunggu sebentar
                    time.sleep(1)
                    
                    # Scroll ke tombol
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView({
                            behavior: 'smooth', 
                            block: 'center'
                        });
                    """, continue_button)
                    
                    # Tunggu sebentar setelah scroll
                    time.sleep(1)
                    
                    # Klik tombol Continue
                    actions = webdriver.ActionChains(self.driver)
                    actions.move_to_element(continue_button).pause(0.5).click().perform()
                    
                    # Tunggu navigasi
                    time.sleep(3)
                    
                    # Cek URL setelah klik Continue
                    new_url = self.driver.current_url
                    
                    # Pola URL pembayaran Spotify
                    payment_url_pattern = r'https://payments\.spotify\.com/checkout/[a-f0-9-]+/\?country=\w+&market=\w+&product=default-intro'
                    
                    # Validasi URL pembayaran
                    if re.match(payment_url_pattern, new_url):
                        print(f"{Fore.GREEN}✓ Berhasil redirect ke halaman pembayaran!")
                        print(f"{Fore.CYAN}URL Pembayaran: {new_url}")
                        
                        # Log URL pembayaran ke file
                        try:
                            with open('payment_urls.txt', 'a') as f:
                                f.write(f"{new_url}\n")
                            print(f"{Fore.GREEN}✓ URL pembayaran disimpan di payment_urls.txt")
                        except Exception as log_error:
                            print(f"{Fore.YELLOW}⚠ Gagal menyimpan URL: {log_error}")
                        
                        # Navigasi keyboard
                        try:
                            # Persiapan ActionChains
                            actions = webdriver.ActionChains(self.driver)
                            
                            # Tekan Tab sebanyak 8 kali
                            for _ in range(8):
                                actions.send_keys(Keys.TAB).pause(0.1)
                            
                            # Eksekusi navigasi Tab
                            actions.perform()
                            
                            # Tunggu sebentar
                            time.sleep(0.7)
                            
                            # Tekan Enter
                            actions.send_keys(Keys.ENTER).perform()
                            
                            print(f"{Fore.GREEN}✓ Berhasil navigasi keyboard!")
                        
                        except Exception as keyboard_error:
                            print(f"{Fore.YELLOW}⚠ Gagal navigasi keyboard: {keyboard_error}")
                        
                        return True
                    
                    # Jika URL tidak sesuai, coba redirect manual
                    for url in free_trial_urls:
                        try:
                            print(f"{Fore.CYAN}Mencoba redirect manual ke: {url}")
                            
                            # Tambahkan delay 3-5 detik sebelum redirect
                            delay = random.uniform(3, 5)
                            print(f"{Fore.YELLOW}Menunggu {delay:.2f} detik sebelum redirect...")
                            time.sleep(delay)
                            
                            self.driver.get(url)
                            
                            # Tunggu halaman dimuat
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, 'body'))
                            )
                            
                            # Validasi halaman
                            current_url = self.driver.current_url
                            if 'payments.spotify.com/checkout' in current_url:
                                print(f"{Fore.GREEN}✓ Berhasil redirect ke halaman pembayaran!")
                                print(f"{Fore.CYAN}URL Pembayaran: {current_url}")
                                
                                # Log URL pembayaran
                                try:
                                    with open('payment_urls.txt', 'a') as f:
                                        f.write(f"{current_url}\n")
                                    print(f"{Fore.GREEN}✓ URL pembayaran disimpan di payment_urls.txt")
                                except Exception as log_error:
                                    print(f"{Fore.YELLOW}⚠ Gagal menyimpan URL: {log_error}")
                                
                                # Navigasi keyboard
                                try:
                                    # Persiapan ActionChains
                                    actions = webdriver.ActionChains(self.driver)
                                    
                                    # Tekan Tab sebanyak 8 kali
                                    for _ in range(8):
                                        actions.send_keys(Keys.TAB).pause(0.1)
                                    
                                    # Eksekusi navigasi Tab
                                    actions.perform()
                                    
                                    # Tunggu sebentar
                                    time.sleep(0.7)
                                    
                                    # Tekan Enter
                                    actions.send_keys(Keys.ENTER).perform()
                                    
                                    print(f"{Fore.GREEN}✓ Berhasil navigasi keyboard!")
                                
                                except Exception as keyboard_error:
                                    print(f"{Fore.YELLOW}⚠ Gagal navigasi keyboard: {keyboard_error}")
                                
                                return True
                        except Exception as redirect_error:
                            print(f"{Fore.YELLOW}⚠ Gagal redirect: {redirect_error}")
                    
                    print(f"{Fore.YELLOW}⚠ URL tidak sesuai pola pembayaran: {new_url}")
                    return False
                
                except Exception as continue_error:
                    print(f"{Fore.YELLOW}⚠ Gagal klik tombol Continue: {continue_error}")
            
            print(f"{Fore.RED}❌ Gagal bypass reCAPTCHA!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan fatal saat bypass reCAPTCHA: {e}")
            
            # Tangkap screenshot untuk debugging
            try:
                self.driver.save_screenshot("recaptcha_fatal_error.png")
                print(f"{Fore.YELLOW}Screenshot error disimpan sebagai recaptcha_fatal_error.png")
            except:
                pass
            
            return False
    
    def generate_random_checkout_id(self, length=36):
        """
        Generate random checkout ID untuk URL Spotify
        
        :param length: Panjang ID checkout
        :return: String checkout ID
        """
        import uuid
        return str(uuid.uuid4())

    def redirect_to_payment_page(self):
        """
        Metode untuk redirect ke halaman pembayaran/free trial Spotify
        
        :return: Boolean
        """
        try:
            # Daftar URL potensial untuk free trial/pembayaran
            payment_urls = [
                'https://www.spotify.com/au/purchase/offer/default-intro?country=AU'
            ]
            
            # Metode redirect dengan berbagai strategi
            redirect_strategies = [
                # Strategi 1: Direct navigation
                lambda url: self.driver.get(url),
                
                # Strategi 2: JavaScript navigation
                lambda url: self.driver.execute_script(f"window.location.href = '{url}'"),
                
                # Strategi 3: Advanced navigation dengan manipulasi history
                lambda url: self.driver.execute_script(f"""
                    history.pushState(null, null, '{url}');
                    window.dispatchEvent(new PopStateEvent('popstate'));
                """)
            ]
            
            # Coba setiap URL dengan setiap strategi
            for url in payment_urls:
                for strategy in redirect_strategies:
                    try:
                        print(f"{Fore.CYAN}Mencoba redirect ke: {url}")
                        
                        # Jalankan strategi redirect
                        strategy(url)
                        
                        # Tunggu halaman dimuat
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'body'))
                        )
                        
                        # Validasi halaman
                        current_url = self.driver.current_url
                        
                        # Pola URL pembayaran Spotify
                        payment_url_patterns = [
                            r'https://www\.spotify\.com/\w+/purchase/offer/default-intro\?country=\w+',
                            r'https://payments\.spotify\.com/checkout/[a-f0-9-]+/\?country=\w+&market=\w+&product=default-intro'
                        ]
                        
                        # Cek apakah URL cocok dengan pola
                        url_match = any(re.search(pattern, current_url) for pattern in payment_url_patterns)
                        
                        if url_match:
                            print(f"{Fore.GREEN}✓ Berhasil redirect ke halaman pembayaran!")
                            print(f"{Fore.CYAN}URL Pembayaran: {current_url}")
                            
                            # Log URL pembayaran
                            try:
                                with open('payment_urls.txt', 'a') as f:
                                    f.write(f"{current_url}\n")
                                print(f"{Fore.GREEN}✓ URL pembayaran disimpan di payment_urls.txt")
                            except Exception as log_error:
                                print(f"{Fore.YELLOW}⚠ Gagal menyimpan URL: {log_error}")
                            
                            # Tambahkan delay 2 detik
                            time.sleep(2)
                            
                            # Navigasi keyboard
                            try:
                                # Persiapan ActionChains
                                actions = webdriver.ActionChains(self.driver)
                                
                                # Tekan Tab sebanyak 8 kali dengan delay 1 detik per klik
                                for _ in range(8):
                                    actions.send_keys(Keys.TAB)
                                    actions.pause(1)
                                
                                # Eksekusi navigasi Tab
                                actions.perform()
                                
                                # Tekan Enter
                                actions.send_keys(Keys.ENTER).perform()
                                
                                print(f"{Fore.GREEN}✓ Berhasil navigasi keyboard!")
                            
                            except Exception as keyboard_error:
                                print(f"{Fore.YELLOW}⚠ Gagal navigasi keyboard: {keyboard_error}")
                            
                            return True
                    
                    except Exception as redirect_error:
                        print(f"{Fore.YELLOW}⚠ Gagal redirect: {redirect_error}")
            
            print(f"{Fore.RED}❌ Gagal redirect ke halaman pembayaran!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan fatal saat redirect: {e}")
            return False

    def select_payment_method(self):
        """
        Metode untuk memilih metode pembayaran kartu kredit/debit secara otomatis
        
        :return: Boolean
        """
        try:
            print(f"{Fore.CYAN}Memilih metode pembayaran kartu kredit/debit...")
            
            # Strategi pencarian elemen radio button
            payment_method_strategies = [
                # Strategi 1: Pencarian dengan ID spesifik
                lambda: self.driver.find_element(By.ID, "option-cards"),
                
                # Strategi 2: Pencarian dengan XPath
                lambda: self.driver.find_element(By.XPATH, "//input[@type='radio' and @id='option-cards']"),
                
                # Strategi 3: Pencarian dengan atribut data-encore-id
                lambda: self.driver.find_element(By.XPATH, "//input[@data-encore-id='visuallyHidden' and @id='option-cards']"),
                
                # Strategi 4: Pencarian dengan label terkait
                lambda: self.driver.find_element(By.XPATH, "//label[contains(text(), 'Credit or debit card')]//preceding-sibling::input[@type='radio']")
            ]
            
            # Variabel untuk menyimpan elemen radio button
            radio_button = None
            
            # Coba setiap strategi pencarian
            for strategy in payment_method_strategies:
                try:
                    potential_element = strategy()
                    
                    # Validasi elemen
                    if (potential_element and 
                        potential_element.is_displayed() or 
                        potential_element.get_attribute('class').find('visually-hidden') != -1):
                        radio_button = potential_element
                        break
                except Exception as strategy_error:
                    print(f"{Fore.YELLOW}⚠ Strategi pencarian gagal: {strategy_error}")
                    continue
            
            # Jika tidak ditemukan elemen
            if not radio_button:
                print(f"{Fore.RED}❌ Tidak dapat menemukan radio button metode pembayaran!")
                
                # Debugging: Cetak semua input radio
                try:
                    radio_inputs = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
                    print(f"{Fore.YELLOW}Input radio yang tersedia:")
                    for input_el in radio_inputs:
                        print(f"  - ID: {input_el.get_attribute('id')}")
                        print(f"  - Name: {input_el.get_attribute('name')}")
                        print(f"  - Value: {input_el.get_attribute('value')}")
                        print(f"  - Displayed: {input_el.is_displayed()}")
                        print(f"  - Enabled: {input_el.is_enabled()}")
                        print("---")
                except Exception as debug_error:
                    print(f"{Fore.YELLOW}Gagal mendapatkan informasi debug: {debug_error}")
                
                return False
            
            # Scroll ke elemen dengan JavaScript
            self.driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'nearest'
                });
            """, radio_button)
            time.sleep(0.5)
            
            # Multiple click strategies
            click_strategies = [
                # Metode 1: Selenium click standar
                lambda: radio_button.click(),
                
                # Metode 2: JavaScript click
                lambda: self.driver.execute_script("arguments[0].click();", radio_button),
                
                # Metode 3: Trigger click events
                lambda: self.driver.execute_script("""
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    arguments[0].dispatchEvent(event);
                """, radio_button)
            ]
            
            # Coba setiap strategi klik
            for strategy in click_strategies:
                try:
                    strategy()
                    
                    # Verifikasi pilihan
                    time.sleep(0.5)
                    if radio_button.is_selected():
                        print(f"{Fore.GREEN}✓ Berhasil memilih metode pembayaran kartu kredit/debit!")
                        return True
                except Exception as click_error:
                    print(f"{Fore.YELLOW}⚠ Metode klik gagal: {click_error}")
            
            print(f"{Fore.RED}❌ Gagal memilih metode pembayaran!")
            return False
        
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan fatal saat memilih metode pembayaran: {e}")
            return False

    def create_account(self):
        """Main method to create a single Spotify account"""
        try:
            # Verify VPN connection
            if not self.verify_vpn_connection():
                print(f"{Fore.RED}❌ Koneksi VPN tidak valid!")
                return False
            
            # Generate user data
            user_data = self.generate_fake_user_data()
            user_data['password'] = "Mautauaja28@"  # Default password
            
            print(f"{Fore.CYAN}Detail Akun:")
            print(f"  Email: {user_data['email']}")
            print(f"  Name: {user_data['name']}")
            
            # Definisi strategi tombol Next (global untuk metode ini)
            next_button_strategies = [
                ('xpath', "//button[@data-testid='submit']"),
                ('xpath', "//button[contains(@class, 'Button-sc-')]"),
                ('xpath', "//button[@type='submit']"),
                ('xpath', "//button[contains(text(), 'Next')]"),
                ('css', "button[type='submit']")
            ]
            
            # Navigate to Spotify signup
            self.driver.get("https://www.spotify.com/au/signup")
            
            # Tunggu halaman dimuat
            time.sleep(2)
            
            # Simpan URL awal
            initial_signup_url = self.driver.current_url
            
            # === TAHAP 1: INPUT USERNAME ===
            # Tangani input username
            if not self.handle_username_input(user_data):
                print(f"{Fore.RED}❌ Gagal navigasi setelah input username!")
                return False
            
            # Simpan URL setelah input username
            username_url = self.driver.current_url
            
            # === TAHAP 2: INPUT PASSWORD ===
            # Password input
            password_strategies = [
                ('id', 'password'),
                ('xpath', "//input[@type='password']")
            ]
            
            password_field = self.find_element_robust(password_strategies)
            if not password_field:
                # Coba cegah regresi halaman
                if not self.prevent_page_regression(initial_signup_url):
                    print(f"{Fore.RED}❌ Tidak dapat menemukan field password!")
                    return False
                
                # Cari ulang field password
                password_field = self.find_element_robust(password_strategies)
                if not password_field:
                    print(f"{Fore.RED}❌ Tidak dapat menemukan field password!")
                    return False
            
            if not self.send_keys_expert(password_field, user_data['password']):
                print(f"{Fore.RED}❌ Gagal mengisi password!")
                return False
            
            # Multiple strategi navigasi untuk halaman password
            password_navigation_strategies = [
                # Strategi 1: Klik tombol Next standar
                lambda: self.click_next_robust(next_button_strategies),
                
                # Strategi 2: Trigger Enter pada field password
                lambda: self.trigger_enter_key(password_field),
                
                # Strategi 3: JavaScript click pada tombol terdekat
                lambda: self.click_nearest_button(password_field),
                
                # Strategi 4: JavaScript click pada tombol submit
                lambda: self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button[type="submit"], button[data-testid="submit"]');
                    if (buttons.length > 0) {
                        buttons[0].click();
                        return true;
                    }
                    return false;
                """)
            ]
            
            # === TAHAP 3: NAVIGASI PASSWORD ===
            # Coba setiap strategi navigasi
            navigation_success = False
            for strategy in password_navigation_strategies:
                try:
                    # Coba strategi navigasi
                    if strategy():
                        # Tunggu perubahan halaman
                        if self.wait_for_page_change(username_url):
                            print(f"{Fore.GREEN}✓ Berhasil navigasi setelah input password!")
                            navigation_success = True
                            break
                        
                        # Jika tidak berubah, coba cegah regresi
                        if self.prevent_page_regression(username_url):
                            navigation_success = True
                            break
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠ Strategi navigasi password gagal: {e}")
                    continue
            
            # Periksa keberhasilan navigasi
            if not navigation_success:
                print(f"{Fore.RED}❌ Gagal navigasi setelah input password!")
                return False
            
            # Tunggu halaman profil
            time.sleep(2)
            
            # === TAHAP 4: INPUT DATA PROFIL ===
            # Gunakan metode baru untuk mengisi form profil
            if not self.fill_profile_form(user_data):
                print(f"{Fore.RED}❌ Gagal mengisi form profil!")
                return False
            
            # === TAHAP 5: SUBMIT AKHIR ===
            # Gunakan metode baru untuk submit langkah terakhir
            if not self.complete_final_signup_step():
                print(f"{Fore.RED}❌ Gagal submit langkah terakhir!")
                return False
            
            # === TAHAP 6: BYPASS RECAPTCHA ===
            # Tambahkan metode bypass reCAPTCHA
            if not self.bypass_recaptcha():
                print(f"{Fore.RED}❌ Gagal bypass reCAPTCHA!")
                return False
            
            # === TAHAP 7: REDIRECT KE HALAMAN PEMBAYARAN ===
            # Redirect ke halaman pembayaran/free trial
            if not self.redirect_to_payment_page():
                print(f"{Fore.RED}❌ Gagal redirect ke halaman pembayaran!")
                return False
            
            # === TAHAP 8: PILIH METODE PEMBAYARAN ===
            # Pilih metode pembayaran kartu kredit
            if not self.select_payment_method():
                print(f"{Fore.RED}❌ Gagal memilih metode pembayaran!")
                return False
            
            # === TAHAP 9: ISI FORM PEMBAYARAN ===
            # Isi form pembayaran secara manual
            if not self.fill_payment_form_manual():
                print(f"{Fore.RED}❌ Gagal mengisi form pembayaran!")
                return False
            
            print(f"{Fore.GREEN}✓ Proses signup dimulai untuk {user_data['email']}")
            return user_data
            
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan pembuatan akun: {str(e)}")
            try:
                self.driver.save_screenshot("signup_error.png")
                print(f"{Fore.YELLOW}Screenshot error disimpan sebagai signup_error.png")
            except:
                pass
            return False
    
    def run_automation(self):
        """Run Spotify account creation automation"""
        try:
            # Setup driver dengan opsi stealth dan incognito
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--incognito')  # Tambahkan mode incognito
            
            # Setup proxy jika ada
            options = self.setup_proxy(options)
            
            # Inisiasi driver dengan penanganan kesalahan
            try:
                # Coba dengan path ChromeDriver manual
                chromedriver_path = os.path.expanduser('~/.local/bin/chromedriver-linux64/chromedriver')
                
                # Metode 1: Undetected ChromeDriver
                self.driver = uc.Chrome(
                    driver_executable_path=chromedriver_path, 
                    options=options
                )
            except Exception as driver_error:
                print(f"{Fore.RED}❌ Kesalahan inisiasi driver: {driver_error}")
                print(f"{Fore.YELLOW}Mencoba metode alternatif...")
                
                # Metode alternatif: Gunakan ChromeDriverManager
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            # Jalankan proses pembuatan akun
            account_data = self.create_account()
            
            if account_data:
                print(f"{Fore.GREEN}🎉 Akun berhasil dibuat!")
                print(f"{Fore.YELLOW}Silakan lanjutkan proses verifikasi secara manual.")
            
            # Tunggu input manual untuk melanjutkan proses
            input(f"{Fore.CYAN}Tekan Enter untuk menutup browser...")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Automation error: {str(e)}")
            # Tambahkan detail error untuk debugging
            import traceback
            traceback.print_exc()
        
        finally:
            if hasattr(self, 'driver'):
                try:
                    self.driver.quit()
                except:
                    pass

    def fill_payment_form_manual(self):
        """
        Metode untuk mengisi form pembayaran kartu kredit secara manual
        menggunakan data dari vcc_data.txt dan JavaScript untuk iframe
        
        :return: Boolean
        """
        try:
            print(f"{Fore.CYAN}Mengisi form pembayaran kartu kredit...")
            print(f"{Fore.RED}⚠ PERINGATAN: Hanya untuk tujuan edukasi!")
            
            # Tunggu iframe muncul
            try:
                iframe = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Card form']"))
                )
                print(f"{Fore.GREEN}✓ Iframe form pembayaran ditemukan!")
            except Exception as e:
                print(f"{Fore.RED}❌ Iframe form pembayaran tidak ditemukan: {e}")
                return False

            # Switch ke iframe
            self.driver.switch_to.frame(iframe)
            
            # Pastikan vcc_data tersedia
            if not hasattr(self, 'vcc_data') or not self.vcc_data:
                self.vcc_data = [{
                    'number': '4596930078139128',
                    'month': '05',
                    'year': '2030',
                    'cvv': '594'
                }]
            
            card_data = self.vcc_data[0]
            
            # Tunggu form dalam iframe dimuat
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "cardnumber"))
                )
            except:
                print(f"{Fore.RED}❌ Form dalam iframe tidak dimuat!")
                return False

            # Script JavaScript untuk mengisi form
            fill_form_script = f"""
                // Fungsi untuk trigger event
                function triggerEvent(element, eventType) {{
                    const event = new Event(eventType, {{ bubbles: true }});
                    element.dispatchEvent(event);
                }}

                // Fungsi untuk mengisi input dengan delay
                async function fillInput(element, value) {{
                    element.value = '';
                    for (let char of value) {{
                        element.value += char;
                        triggerEvent(element, 'input');
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }}
                    triggerEvent(element, 'change');
                }}

                // Fungsi utama pengisian form
                async function fillForm() {{
                    const cardNumber = document.getElementById('cardnumber');
                    const expiryDate = document.getElementById('expiry-date');
                    const securityCode = document.getElementById('security-code');

                    if (cardNumber && expiryDate && securityCode) {{
                        await fillInput(cardNumber, '{card_data["number"]}');
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        const expiry = '{card_data["month"]}/{card_data["year"][-2:]}';
                        await fillInput(expiryDate, expiry);
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        await fillInput(securityCode, '{card_data["cvv"]}');
                        return true;
                    }}
                    return false;
                }}

                return fillForm();
            """

            # Eksekusi script
            success = self.driver.execute_script(fill_form_script)
            
            if success:
                print(f"{Fore.GREEN}✓ Berhasil mengisi form pembayaran!")
            else:
                print(f"{Fore.RED}❌ Gagal mengisi form pembayaran!")
                return False

            # Kembali ke frame utama
            self.driver.switch_to.default_content()
            
            # Tunggu 1 detik
            time.sleep(1)
            
            # Klik tombol Complete purchase
            try:
                # Coba berbagai selector untuk tombol
                purchase_button_selectors = [
                    (By.ID, "checkout_submit"),
                    (By.CSS_SELECTOR, "button[data-encore-id='buttonPrimary']"),
                    (By.XPATH, "//button[contains(@class, 'e-9916-button-primary')]"),
                    (By.XPATH, "//button[contains(text(), 'Complete purchase')]")
                ]
                
                purchase_button = None
                for selector_type, selector in purchase_button_selectors:
                    try:
                        purchase_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((selector_type, selector))
                        )
                        break
                    except:
                        continue
                
                if purchase_button:
                    # Scroll ke tombol
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", purchase_button)
                    time.sleep(0.5)
                    
                    # Klik tombol dengan JavaScript
                    self.driver.execute_script("arguments[0].click();", purchase_button)
                    print(f"{Fore.GREEN}✓ Berhasil mengklik tombol Complete purchase!")
                else:
                    print(f"{Fore.RED}❌ Tombol Complete purchase tidak ditemukan!")
                    return False
                
            except Exception as e:
                print(f"{Fore.RED}❌ Gagal mengklik tombol Complete purchase: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Kesalahan saat mengisi form pembayaran: {e}")
            
            # Pastikan kembali ke frame utama
            try:
                self.driver.switch_to.default_content()
            except:
                pass
                
            return False

def main():
    print(f"{Fore.RED}{'='*60}")
    print(f"{Fore.RED}DISCLAIMER PENTING:")
    print(f"{Fore.RED}Script ini HANYA untuk TUJUAN EDUKASI!")
    print(f"{Fore.RED}Menggunakan script ini untuk bypass layanan")
    print(f"{Fore.RED}melanggar Terms of Service Spotify.")
    print(f"{Fore.RED}Risiko sepenuhnya ada pada pengguna!")
    print(f"{Fore.RED}{'='*60}\n")
    
    response = input(f"{Fore.YELLOW}Apakah Anda memahami risiko penggunaan? (yes/no): ")
    
    if response.lower() != 'yes':
        print(f"{Fore.RED}Proses dihentikan.")
        return
    
    # Minta input proxy opsional
    proxy_input = input(f"{Fore.CYAN}Masukkan proxy (opsional, format: ip:port): ").strip()
    proxy = proxy_input if proxy_input else None
    
    # Inisiasi automation
    automation = SpotifyAutomation(
        proxy=proxy, 
        vpn_country='AU'  
    )
    
    automation.run_automation()

if __name__ == "__main__":
    main()