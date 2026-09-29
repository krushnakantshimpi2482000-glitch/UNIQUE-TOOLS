import io
import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

st.set_page_config(
    page_title="UNIQUE TOOLS | सायबर कॅफे सोल्यूशन",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# अल्ट्रा-क्लीन कॉर्पोरेट UI CSS (200MB पट्टी गायब & Max: 2 MB)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* 200MB फाईल साईज पट्टी पूर्णपणे काढून फक्त Max: 2 MB दाखवणे */
    div[data-testid="stFileUploaderDropzoneInstructions"] * {
        display: none !important;
    }
    div[data-testid="stFileUploaderDropzoneInstructions"] {
        font-size: 0px !important;
    }
    div[data-testid="stFileUploaderDropzoneInstructions"]::after {
        content: "Max: 2 MB • JPG, PNG";
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        display: inline-block !important;
        margin-left: 12px !important;
    }

    /* टॅब डिझाईन */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 700;
        color: #475569;
        padding: 10px 20px;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #0284c7 !important;
        border-bottom: 3px solid #0284c7 !important;
        background-color: #f0f9ff !important;
        border-radius: 8px 8px 0 0;
    }

    /* मुख्य ॲक्शन बटण */
    div.stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        transform: translateY(-1px);
    }

    /* डाऊनलोड बटण */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.25) !important;
    }
    div.stDownloadButton > button:hover {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
    }

    .portal-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 22px 26px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

# हेडर बॅनर
st.markdown("""
    <div class="portal-banner">
        <h3 style="margin: 0; font-weight: 800; color: #f8fafc; font-size: 24px;">⚡ UNIQUE TOOLS</h3>
        <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 14px;">
            सायबर कॅफे व सेतू केंद्रांसाठी ऑटो पासपोर्ट, स्वाक्षरी आणि रिअल 2K Ultra HD डॉक्युमेंट/फोटो क्लीनर
        </p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📸 पासपोर्ट फोटो स्टुडिओ (3.5 × 4.5 cm)", 
    "✍️ स्वाक्षरी क्लीनर व क्रॉप",
    "🚀 2K Ultra HD क्लीन व एनहान्सर"
])

# ------------------ १. पासपोर्ट अल्गोरिदम ------------------
def make_bulletproof_passport(img, bg_color_name):
    img = img.convert("RGB")
    if max(img.size) > 700:
        img.thumbnail((700, 700), Image.Resampling.LANCZOS)
    
    colors = {
        "White (पांढरा)": (255, 255, 255),
        "Sky Blue (हलका निळा)": (168, 218, 240),
        "Grey (राखाडी)": (224, 224, 224)
    }
    bg_rgb = colors.get(bg_color_name, (255, 255, 255))
    
    processed = None
    try:
        from rembg import remove, new_session
        session = new_session("u2netp")
        no_bg = remove(img, session=session)
        bg = Image.new("RGBA", no_bg.size, bg_rgb + (255,))
        bg.paste(no_bg, mask=no_bg.split()[3])
        processed = bg.convert("RGB")
    except Exception:
        pass
    
    if processed is None:
        gray = img.convert("L")
        mask = gray.point(lambda p: 255 if p < 235 else 0).filter(ImageFilter.GaussianBlur(1))
        bg = Image.new("RGB", img.size, bg_rgb)
        bg.paste(img, mask=mask)
        processed = bg

    return processed.resize((413, 531), Image.Resampling.LANCZOS)

# ------------------ २. अचूक इनर क्रॉप फंक्शन (फ्रेम रिमूव्हल) ------------------
def clean_and_crop_frame(cv_img, manual_trim_percent=0):
    h, w = cv_img.shape[:2]
    
    # मॅन्युअल ट्रिम (जर फ्रेम खूप जाड असेल तर)
    if manual_trim_percent > 0:
        cut_x = int(w * (manual_trim_percent / 100.0))
        cut_y = int(h * (manual_trim_percent / 100.0))
        cv_img = cv_img[cut_y:max(cut_y + 10, h - cut_y), cut_x:max(cut_x + 10, w - cut_x)]
        h, w = cv_img.shape[:2]

    # आतील खरा फोटो शोधणे
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 130)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    best_rect = None
    max_area = 0
    total_area = h * w
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 0.18 * total_area < area < 0.96 * total_area:
            if area > max_area:
                max_area = area
                best_rect = cv2.boundingRect(cnt)
                
    if best_rect is not None:
        x, y, bw, bh = best_rect
        # आतील बॉर्डर पूर्ण काढण्यासाठी किंचित इनर पॅडिंग
        pad_x = int(bw * 0.02)
        pad_y = int(bh * 0.02)
        x1 = max(0, x + pad_x)
        y1 = max(0, y + pad_y)
        x2 = min(w, x + bw - pad_x)
        y2 = min(h, y + bh - pad_y)
        if (x2 - x1) > 80 and (y2 - y1) > 80:
            return cv_img[y1:y2, x1:x2]
            
    return cv_img

# ------------------ ३. स्टुडिओ-ग्रेड 2K क्लीनिंग (Zero Noise & Natural Skin) ------------------
def process_real_clean_2k(pil_img, mode="Photo", do_crop=True, trim_pct=0):
    img = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    # १. फ्रेम व बॉर्डर्स अचूक कापणे
    if do_crop or trim_pct > 0:
        img = clean_and_crop_frame(img, manual_trim_percent=trim_pct)
        
    h, w = img.shape[:2]
    
    # २. रेशिओ न बिघडवता 2K सुपर रिझोल्यूशन
    target = 2048
    if w >= h:
        target_w = target
        target_h = int((target / w) * h)
    else:
        target_h = target
        target_w = int((target / h) * w)

    upscaled = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    
    if "Document" in mode:
        # डॉक्युमेंट मोड: कागद पांढरा स्वच्छ आणि अक्षरे गडद काळी
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b_ch))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        result = cv2.detailEnhance(enhanced, sigma_s=10, sigma_r=0.15)
    else:
        # फोटो मोड: स्टुडिओ स्मूथिंग (चेहऱ्याचा सर्व नॉईज व डाग निघून नैसर्गिक तेज येईल)
        denoised = cv2.bilateralFilter(upscaled, d=9, sigmaColor=75, sigmaSpace=75)
        
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b_ch = cv2.split(lab)
        # सौम्य कॉन्ट्रास्ट बॅलन्स (चेहरा काळा पडणार नाही)
        clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b_ch))
        result = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    final_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    return Image.fromarray(final_rgb), (target_w, target_h)


# ================== टॅब १: पासपोर्ट फोटो स्टुडिओ ==================
with tab1:
    st.markdown("##### १. ग्राहकाचा फोटो अपलोड करा")
    photo_file = st.file_uploader("फोटो निवडा", type=["jpg", "jpeg", "png"], key="passport_upload")

    c1, c2 = st.columns(2)
    with c1:
        bg_select = st.selectbox("बॅकग्राउंड रंग निवडा:", ["White (पांढरा)", "Sky Blue (हलका निळा)", "Grey (राखाडी)"])
    with c2:
        sheet_select = st.selectbox("प्रिंटिंग फॉरमॅट:", ["१ सिंगल फोटो (Online Form / भरती अर्ज)", "८ फोटो शीट (4x6 इंच फोटो पेपर)"])

    if photo_file:
        if photo_file.size > 2 * 1024 * 1024:
            st.error("⚠️ फोटो २ MB पेक्षा जास्त आहे! कृपया २ MB पेक्षा लहान फाईल निवडा.")
        else:
            if st.button("⚡ पासपोर्ट फोटो त्वरित तयार करा", key="btn_photo"):
                with st.spinner("फोटो प्रोसेस होत आहे..."):
                    try:
                        input_img = Image.open(photo_file)
                        single_result = make_bulletproof_passport(input_img, bg_select)

                        if "८ फोटो" in sheet_select:
                            sheet = Image.new("RGB", (1800, 1200), (255, 255, 255))
                            for row in range(2):
                                for col in range(4):
                                    x = 60 + (col * 430)
                                    y = 65 + (row * 550)
                                    sheet.paste(single_result, (x, y))
                            final_output = sheet
                            dl_filename = "UniqueTools_Passport_Sheet_4x6.jpg"
                        else:
                            final_output = single_result
                            dl_filename = "UniqueTools_Passport_Single.jpg"

                        st.success("✅ पासपोर्ट फोटो तयार झाला!")
                        col_img, col_dl = st.columns([1, 1])
                        with col_img:
                            st.image(final_output, caption="तयार पासपोर्ट फोटो", use_container_width=True)
                        with col_dl:
                            st.markdown("""
                            **📋 फोटो तपशील:**
                            - आकार: ३.५ × ४.५ सेमी (मानक पासपोर्ट साईझ)
                            - रिझोल्यूशन: ३०० DPI (क्रिस्टल क्लिअर)
                            - वापर: सर्व भरती अर्ज, पॅन कार्ड आणि थेट ४×६ प्रिंटिंग
                            """)
                            buf = io.BytesIO()
                            final_output.save(buf, format="JPEG", quality=95)
                            st.download_button("📥 फोटो डाऊनलोड करा (Download)", data=buf.getvalue(), file_name=dl_filename, mime="image/jpeg")
                    except Exception as err:
                        st.error(f"एरर आला: {err}")

# ================== टॅब २: स्वाक्षरी क्लीनर ==================
with tab2:
    st.markdown("##### २. ग्राहकाची स्वाक्षरी अपलोड करा")
    sign_file = st.file_uploader("स्वाक्षरी निवडा", type=["jpg", "jpeg", "png"], key="sign_upload")

    if sign_file:
        if sign_file.size > 2 * 1024 * 1024:
            st.error("⚠️ स्वाक्षरी २ MB पेक्षा जास्त आहे!")
        else:
            if st.button("⚡ स्वाक्षरी स्वच्छ करा", key="btn_sign"):
                with st.spinner("स्वाक्षरी ऑटो-क्रॉप व क्लीन होत आहे..."):
                    try:
                        s_img = Image.open(sign_file).convert("L")
                        enhancer = ImageEnhance.Contrast(s_img)
                        enhanced = enhancer.enhance(3.2)
                        
                        inverted = ImageOps.invert(enhanced)
                        bbox = inverted.getbbox()
                        if bbox:
                            enhanced = enhanced.crop(bbox)
                        
                        final_sign = enhanced.resize((400, 200), Image.Resampling.LANCZOS)
                        st.success("✅ स्वाक्षरी स्वच्छ झाली!")
                        
                        col_sp, col_sd = st.columns([1, 1])
                        with col_sp:
                            st.image(final_sign, caption="स्वच्छ स्वाक्षरी प्रिव्ह्यू", width=300)
                        with col_sd:
                            st.markdown("""
                            **📋 स्वाक्षरी तपशील:**
                            - १००% स्वच्छ पांढरा कागद
                            - आकार: 400 × 200 px (अधिकृत मानके)
                            - फाईल साईझ: ५० KB पेक्षा कमी
                            """)
                            buf_s = io.BytesIO()
                            final_sign.save(buf_s, format="JPEG", quality=85)
                            st.download_button("📥 स्वच्छ स्वाक्षरी डाऊनलोड करा", data=buf_s.getvalue(), file_name="UniqueTools_Clean_Sign.jpg", mime="image/jpeg")
                    except Exception as s_err:
                        st.error(f"एरर आला: {s_err}")

# ================== टॅब ३: 2K Ultra HD क्लीन व एनहान्सर ==================
with tab3:
    st.markdown("##### ३. ऑटो-क्रॉप आणि रिअल 2K अल्ट्रा HD डॉक्युमेंट/फोटो क्लीनर")
    doc_file = st.file_uploader("फोटो किंवा डॉक्युमेंट निवडा", type=["jpg", "jpeg", "png"], key="enhance_upload")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        enhance_type = st.selectbox(
            "प्रकार निवडा:", 
            ["Photo (फोटो / पोर्ट्रेट - चेहरा गोरा व नैसर्गिक ठेवा)", "Document (कागदपत्रे / फॉर्म्स - अक्षरे ठळक करा)"]
        )
    with col_e2:
        auto_crop_flag = st.checkbox("ऑटो-क्रॉप चालू ठेवा (कडा शोधणे)", value=True)

    # फ्रेम/बॉर्डर कापण्यासाठी अचूक स्लायडर
    trim_val = st.slider(
        "✂️ फ्रेम / बॉर्डर कटिंग (Border Trim %):", 
        min_value=0, 
        max_value=20, 
        value=5, 
        step=1,
        help="जर फोटोभोवती जाड चंदेरी फ्रेम किंवा टेबल दिसत असेल तर हा स्लायडर ५% ते १०% वर ठेवा, फ्रेम पूर्णपणे कापली जाईल!"
    )

    if doc_file:
        if doc_file.size > 2 * 1024 * 1024:
            st.error("⚠️ फाईल २ MB पेक्षा जास्त आहे!")
        else:
            if st.button("🚀 बॉर्डर कापा आणि 2K HD मध्ये सुधारा", key="btn_enhance"):
                with st.spinner("बॉर्डर रिमूव्हल आणि स्टुडिओ-ग्रेड 2K क्लीनिंग प्रक्रिया चालू आहे..."):
                    try:
                        raw_doc = Image.open(doc_file)
                        orig_w, orig_h = raw_doc.size
                        
                        enhanced_img, (new_w, new_h) = process_real_clean_2k(
                            raw_doc, 
                            mode=enhance_type, 
                            do_crop=auto_crop_flag,
                            trim_pct=trim_val
                        )
                        
                        st.success(f"✅ काम पूर्ण! आकार: {new_w}×{new_h} px (2K Ultra HD)")
                        
                        col_view1, col_view2 = st.columns(2)
                        with col_view1:
                            st.image(raw_doc, caption="मूळ अपलोड केलेली फाईल", use_container_width=True)
                        with col_view2:
                            st.image(enhanced_img, caption="✨ स्वच्छ क्रॉप + स्टुडिओ 2K HD", use_container_width=True)
                            
                        buf_enh = io.BytesIO()
                        enhanced_img.save(buf_enh, format="JPEG", quality=98, subsampling=0)
                            
                        st.download_button(
                            label="📥 2K HD फाईल डाऊनलोड करा (JPG)",
                            data=buf_enh.getvalue(),
                            file_name="UniqueTools_Clean_2K_Enhanced.jpg",
                            mime="image/jpeg"
                        )
                    except Exception as enh_err:
                        st.error(f"एरर आला: {enh_err}")
