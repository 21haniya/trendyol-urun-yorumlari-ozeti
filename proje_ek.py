import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
import os
import time

# --- Trendyol'dan Yorum Çekme Fonksiyonu ---
def fetch_comments_and_image(product_url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 1080)
    driver.get(product_url)
    time.sleep(0.5)

    comment_texts = []
    rating_value = None
    image_path = None

    try:
        rating_element = driver.find_element(By.CSS_SELECTOR, 'div.rating-line-count')
        rating_value = rating_element.text

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.onboarding-button'))
        ).click()

        img_xpath = '//*[@id="product-detail-app"]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/img'
        image_element = driver.find_element(By.XPATH, img_xpath)
        image_src = image_element.get_attribute("src")

        save_path = "downloaded_image.jpg"

        if os.path.exists(save_path):
            os.remove(save_path)

        response = requests.get(image_src)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((300, 300))  # Boyutu küçültüyoruz
        img.save(save_path)
        image_path = save_path

        show_all_reviews_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.navigate-all-reviews-btn'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", show_all_reviews_button)
        driver.execute_script("arguments[0].click();", show_all_reviews_button)

        def scroll_to_bottom(driver):
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        scroll_to_bottom(driver)

        comments = driver.find_elements(By.CSS_SELECTOR, 'div.comment-text p')
        comment_texts = [comment.text for comment in comments]

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

    finally:
        driver.quit()

    return comment_texts, rating_value, image_path

# --- Yorumları Özetleme Fonksiyonu ---
def summarize_comments(comments):
    client = OpenAI(api_key="YOUR_API_KEY")
    combined_comments = "\n".join(comments)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"trendyol yorum özetleme botu olarak metni özetler misin? [{combined_comments}]",
            }
        ],
        model="gpt-4o-mini",
    )
    ozet = chat_completion.choices[0].message.content
    return ozet

# --- Arayüz Kısmı ---
st.markdown(
    """
    <style>
    .main {
        background-color: #ffffff;  /* Sayfa arka plan rengi beyaz */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #333333;  /* Başlık rengi koyu gri */
    }
    .summary-box {
        border: none;  /* Kutu sınırı rengi kaldırıldı */
        border-radius: 5px;  /* Kenar yuvarlama */
        padding: 10px;  /* İç boşluk */
        background-color: #003366;  /* Kutu arka plan rengi koyu gri */
        color: #ffffff;  /* Yazı rengi beyaz */
        margin-top: 10px;  /* Kutu ile üstteki öğe arasındaki boşluk */
        overflow: auto;  /* Taşma durumunda kaydırma çubuğu ekle */
    }
    .rating {
        color: #FFD700;  /* Puan rengi altın sarısı */
        font-size: 24px; /* Puan büyüklüğü */
    }
    .image-box {
        max-width: 200px;  /* Görsel genişliğini daha da küçült */
        height: auto;  /* Oran koruma */
        margin: 10px auto;  /* Görseli ortalama */
    }
    .stSpinner > div > div {
        color: #000000;  /* Spinner içeriği için siyah renk */
    }
    .stAlert p {
        color: #000000;  /* Alert mesajı için siyah renk */
    }
    .stSubheader {
        white-space: nowrap;  /* Alt başlığın tek satırda kalmasını sağlar */
        overflow: hidden;  /* Taşan kısmı gizler */
        text-overflow: ellipsis;  /* Uzun metinlerin sonunda üç nokta ekler */
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Trendyol Ürün Yorumları Özeti")

# Search bar için input alanı
product_url = st.text_input("Trendyol ürün linkini buraya yapıştırın:")


if product_url:
    with st.spinner("Yorumlar çekiliyor..."):
        comments, rating_value, image_path = fetch_comments_and_image(product_url)
        
    if comments:
        col1, col2 = st.columns([2, 1])  
        
        with col1:
            summary = summarize_comments(comments)

            st.subheader("Yorum Özeti")

            if rating_value:
                st.markdown(f"<div class='rating'>{rating_value} ⭐</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
            
            
        
        with col2:
            if image_path:
                st.image(image_path, caption="Ürün Görseli", use_column_width=True)
    else:
        st.markdown('<p style="color:black;">Yorumlar çekilemedi veya özetlenemedi.</p>', unsafe_allow_html=True)
