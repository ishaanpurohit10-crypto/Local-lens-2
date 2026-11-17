import streamlit as st
from google import genai
from PIL import Image
import json
import math
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LocalLens AI | Global & Hyper-Local Discovery",
    page_icon="🌍",
    layout="wide"
)

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
    <style>
    .shop-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        border-left: 6px solid #2e7d32;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        color: #1f1f1f;
    }
    .badge {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 700;
    }
    .new-badge {
        background-color: #fff3e0;
        color: #e65100;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 700;
        margin-left: 8px;
    }
    .whatsapp-btn {
        display: inline-block;
        margin-top: 10px;
        background-color: #25D366;
        color: white !important;
        padding: 7px 15px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# --- WORLD & REGIONAL HUB COORDINATES ---
GLOBAL_HUBS = {
    "Sanganer, Jaipur (India)": (26.8192, 75.7885),
    "Bagru, Jaipur (India)": (26.8155, 75.5458),
    "Amer Road, Jaipur (India)": (26.9535, 75.8412),
    "Bassi, Jaipur (India)": (26.8350, 76.0480),
    "Chomu, Jaipur (India)": (27.1636, 75.7214),
    "Shahpura, Jaipur (India)": (27.3860, 75.9592),
    "Kyoto Artisan Quarter (Japan)": (35.0116, 135.7681),
    "Milan Leather & Design District (Italy)": (45.4642, 9.1900),
    "Istanbul Grand Bazaar Crafts (Turkey)": (41.0107, 28.9681),
    "Oaxaca Folk Pottery Hub (Mexico)": (17.0732, -96.7266),
    "Nairobi Maasai Market Crafts (Kenya)": (-1.2864, 36.8172),
    "Portland Independent Makers (USA)": (45.5152, -122.6784),
    "Custom Lat/Lon Coordinates": (0.0, 0.0)
}

# --- INITIALIZE SESSION STATE DATABASE ---
if "shops_db" not in st.session_state:
    st.session_state.shops_db = [
        {
            "id": 1,
            "shop_name": "Sanganer Heritage Block Prints",
            "category": "Handicrafts & Textiles",
            "area": "Sanganer, Jaipur, India",
            "lat": 26.8192,
            "lon": 75.7885,
            "phone": "919829011111",
            "product": "Hand-Block Printed Indigo Cotton Bedsheet",
            "price": "₹1,250",
            "stock": "8 units in stock",
            "keywords": ["bedsheet", "cotton", "block print", "indigo", "blue", "floral", "textile", "fabric", "cloth"],
            "is_new": False
        },
        {
            "id": 2,
            "shop_name": "Bagru Natural Dye Artisans",
            "category": "Handicrafts & Textiles",
            "area": "Bagru, Jaipur, India",
            "lat": 26.8155,
            "lon": 75.5458,
            "phone": "919829066666",
            "product": "Dabu Mud-Resist Handloom Cotton Saree",
            "price": "₹1,850",
            "stock": "12 units in stock",
            "keywords": ["saree", "dabu", "bagru", "fabric", "handloom", "cotton", "textile", "natural dye", "cloth"],
            "is_new": False
        },
        {
            "id": 3,
            "shop_name": "Jaipur Blue Pottery Art Studio",
            "category": "Artisanal Home Decor",
            "area": "Amer Road, Jaipur, India",
            "lat": 26.9535,
            "lon": 75.8412,
            "phone": "919829022222",
            "product": "Traditional Hand-Painted Blue Pottery Ceramic Vase",
            "price": "₹850",
            "stock": "5 units in stock",
            "keywords": ["pottery", "vase", "ceramic", "blue", "flower pot", "decor", "handicraft", "bowl", "jar"],
            "is_new": False
        },
        {
            "id": 4,
            "shop_name": "Sharma Brass & Plumbing Hardware",
            "category": "Specialized Hardware",
            "area": "Pratap Nagar, Jaipur, India",
            "lat": 26.8045,
            "lon": 75.8091,
            "phone": "919829033333",
            "product": "Heavy-Duty 1/2 Inch Brass Gate Valve & Tap Spindle",
            "price": "₹320",
            "stock": "14 units in stock",
            "keywords": ["valve", "brass", "pipe", "tap", "plumbing", "hardware", "faucet", "leak", "metal", "fitting"],
            "is_new": False
        },
        {
            "id": 5,
            "shop_name": "Bassi Organic Farm Collective",
            "category": "Fresh Farm Produce",
            "area": "Bassi, Jaipur, India",
            "lat": 26.8350,
            "lon": 76.0480,
            "phone": "919829044444",
            "product": "Raw Wildflower Honey & Cold-Pressed Mustard Oil",
            "price": "₹450",
            "stock": "Fresh harvest today",
            "keywords": ["honey", "organic", "mustard oil", "farm", "produce", "food", "natural", "jar", "bottle"],
            "is_new": False
        },
        {
            "id": 6,
            "shop_name": "Kyoto Kiyomizu Ceramic Guild",
            "category": "Artisanal Home Decor",
            "area": "Higashiyama, Kyoto, Japan",
            "lat": 35.0116,
            "lon": 135.7681,
            "phone": "81755551234",
            "product": "Hand-Glazed Matcha Tea Bowl & Porcelain Vase",
            "price": "¥4,500 (₹2,500)",
            "stock": "4 units in stock",
            "keywords": ["pottery", "vase", "ceramic", "bowl", "porcelain", "tea", "handicraft", "decor"],
            "is_new": False
        },
        {
            "id": 7,
            "shop_name": "Bottega Pelle Milano",
            "category": "Traditional Leathercraft",
            "area": "Brera District, Milan, Italy",
            "lat": 45.4642,
            "lon": 9.1900,
            "phone": "39025559876",
            "product": "Full-Grain Vegetable-Tanned Leather Satchel & Shoes",
            "price": "€120 (₹11,000)",
            "stock": "6 units in stock",
            "keywords": ["leather", "shoes", "bag", "satchel", "footwear", "handcrafted", "fashion"],
            "is_new": False
        },
        {
            "id": 8,
            "shop_name": "Oaxaca Barro Negro Workshop",
            "category": "Artisanal Home Decor",
            "area": "San Bartolo Coyotepec, Oaxaca, Mexico",
            "lat": 17.0732,
            "lon": -96.7266,
            "phone": "529515554321",
            "product": "Burnished Black Clay Water Pitcher & Pottery",
            "price": "$45 (₹3,800)",
            "stock": "7 units in stock",
            "keywords": ["pottery", "clay", "vase", "pitcher", "ceramic", "handicraft", "decor", "jar"],
            "is_new": False
        },
        {
            "id": 9,
            "shop_name": "Istanbul Anatolian Copper & Brass",
            "category": "Traditional Metalware",
            "area": "Fatih, Istanbul, Turkey",
            "lat": 41.0107,
            "lon": 28.9681,
            "phone": "902125556789",
            "product": "Hand-Hammered Brass Lamp & Copper Coffee Pot",
            "price": "₺1,200 (₹3,100)",
            "stock": "11 units in stock",
            "keywords": ["brass", "copper", "lamp", "metal", "pot", "utensil", "handicraft", "decor"],
            "is_new": False
        }
    ]

# --- HELPER: HAVERSINE DISTANCE CALCULATION ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# --- HELPER: GEMINI AI MULTIMODAL ANALYZER ---
def analyze_with_ai(api_key, text_query, uploaded_image, mode="buyer"):
    client = genai.Client(api_key=api_key)
    if mode == "buyer":
        prompt = """
        You are a global and hyper-local shopping assistant. Analyze the user's text query and/or uploaded image.
        Identify the product they are looking for and return ONLY a valid JSON object with no markdown formatting:
        {
            "identified_item": "Short clear name of the item",
            "category": "General category",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6"]
        }
        """
    else:
        prompt = """
        You are an AI catalog assistant for an independent shopkeeper. Analyze the uploaded product photo and/or note.
        Generate a clean product listing and return ONLY a valid JSON object with no markdown formatting:
        {
            "identified_item": "Suggested clear product title",
            "category": "Shop category (e.g. Hardware, Handicrafts, Farm Produce, Leathercraft)",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6"]
        }
        """

    contents = [prompt]
    if text_query:
        contents.append(f"Description: {text_query}")
    if uploaded_image:
        contents.append(uploaded_image)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
    raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)

# --- SIDEBAR: SETTINGS & SCOPE SELECTOR ---
with st.sidebar:
    st.title("⚙️ LocalLens Controls")
    default_key = ""
    try:
        default_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        default_key = ""
    api_key = st.text_input("🔑 Gemini API Key", value=default_key, type="password", help="Get a free key from Google AI Studio")

    st.markdown("---")
    st.subheader("🌍 Map & Search Scope")
    scope_mode = st.radio(
        "Discovery Range:",
        ["Local only", "Nearby + Global", "Global only"],
        index=1,
        help="Use local artisans nearby or expand to global sourcing hubs."
    )

    st.markdown("---")
    st.subheader("📍 User Location")
    hub_name = st.selectbox("Choose a location hub", list(GLOBAL_HUBS.keys()), index=0)
    user_lat = st.number_input("Latitude", value=GLOBAL_HUBS[hub_name][0], format="%.4f")
    user_lon = st.number_input("Longitude", value=GLOBAL_HUBS[hub_name][1], format="%.4f")
    st.caption("Default hub is Sanganer, Jaipur. Adjust to match your current area.")

# --- MAIN HEADER ---
st.title("📍 LocalLens AI")
st.markdown("#### Discover nearby makers and global craft alternatives in one local-first shopping assistant.")

# --- SEARCH & VISUAL UPLOAD SECTION ---
col1, col2 = st.columns([2, 1])

with col1:
    text_query = st.text_input(
        "What are you looking for today?",
        placeholder="e.g. 'Blue floral block print bedsheet' or 'brass valve for leaking tap'"
    )

with col2:
    uploaded_file = st.file_uploader("Or upload a photo of the item", type=["jpg", "jpeg", "png", "webp"])

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded item for visual matching", width=220)

search_clicked = st.button("🔍 Find in Nearby Shops", type="primary", use_container_width=True)

# --- SEARCH EXECUTION & RESULTS ---
if search_clicked:
    if not text_query and image is None:
        st.warning("Please enter a description or upload a photo to search.")
    else:
        extracted_keywords = []
        identified_label = text_query or "searched item"

        if api_key:
            with st.spinner("🤖 AI is analyzing your request & matching local inventory..."):
                try:
                    ai_result = analyze_with_ai(api_key, text_query, image, mode="buyer")
                    identified_label = ai_result.get("identified_item", text_query or "searched item")
                    extracted_keywords = [str(k).lower() for k in ai_result.get("keywords", [])]
                    st.success(f"**AI Identified:** {identified_label} | **Tags:** {', '.join(extracted_keywords) if extracted_keywords else 'n/a'}")
                except Exception as e:
                    st.error(f"AI Error: {e}. Falling back to keyword matching.")
                    extracted_keywords = [w.lower() for w in (text_query or "").split()]
        else:
            st.info("AI disabled — running in keyword mode. Add a Gemini API key from the sidebar for better recognition.")
            extracted_keywords = [w.lower() for w in (text_query or "").split()]

        matched_shops = []
        for shop in st.session_state.shops_db:
            shop_keywords = [str(kw).lower() for kw in shop.get("keywords", [])]
            score = 0
            for kw in extracted_keywords:
                if kw and any(kw in skw for skw in shop_keywords):
                    score += 1
            if score > 0:
                dist = calculate_distance(user_lat, user_lon, shop["lat"], shop["lon"])
                shop_copy = shop.copy()
                shop_copy["match_score"] = score
                shop_copy["distance_km"] = dist
                matched_shops.append(shop_copy)

        if not matched_shops:
            st.warning("No direct matches were found. Showing the nearest verified vendors and craft hubs instead.")
            for shop in st.session_state.shops_db:
                shop_copy = shop.copy()
                shop_copy["distance_km"] = calculate_distance(user_lat, user_lon, shop["lat"], shop["lon"])
                shop_copy["match_score"] = 0
                matched_shops.append(shop_copy)

        if scope_mode == "Local only":
            matched_shops = [shop for shop in matched_shops if shop["distance_km"] <= 50]
        elif scope_mode == "Global only":
            matched_shops = [shop for shop in matched_shops if shop["distance_km"] > 50]

        matched_shops.sort(key=lambda x: (-x["match_score"], x["distance_km"]))

        st.markdown("---")
        res_col, map_col = st.columns([1.35, 1])

        with res_col:
            st.subheader(f"🏪 {len(matched_shops)} Local Vendors Found")
            for shop in matched_shops:
                whatsapp_msg = f"Hi {shop['shop_name']}, I found your '{shop['product']}' on LocalLens AI. Is it available today?"
                whatsapp_url = f"https://wa.me{shop['phone']}?text={whatsapp_msg.replace(' ', '%20')}"
                badge_html = '<span class="new-badge">NEW</span>' if shop.get("is_new") else ""
                st.markdown(f"""
                <div class="shop-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <h4 style="margin:0; color:#1b5e20;">{shop['shop_name']}</h4>
                        {badge_html}
                        <span class="badge">📍 {shop['distance_km']} km away</span>
                    </div>
                    <p style="margin:6px 0; color:#555;"><b>Area:</b> {shop['area']} • <i>{shop['category']}</i></p>
                    <p style="margin:8px 0; font-size:1.05em;"><b>Matched Item:</b> {shop['product']} — <span style="color:#2e7d32; font-weight:bold;">{shop['price']}</span></p>
                    <p style="margin:5px 0; font-size:0.9em; color:#388e3c;">✅ {shop['stock']} (Saves ~2 days vs online shipping)</p>
                    <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">💬 Reserve via WhatsApp</a>
                </div>
                """, unsafe_allow_html=True)

        with map_col:
            st.subheader("📍 Neighborhood Map")
            map_data = pd.DataFrame([
                {"lat": shop["lat"], "lon": shop["lon"], "shop": shop["shop_name"]}
                for shop in matched_shops
            ])
            if not map_data.empty:
                st.map(map_data[["lat", "lon"]])
            else:
                st.info("No vendors to show on the map.")

# --- FOOTER / PRODUCTIVITY NOTE ---
st.markdown("---")
st.caption("LocalLens AI helps discover nearby artisan inventory, compare local pricing, and message sellers directly via WhatsApp.")

