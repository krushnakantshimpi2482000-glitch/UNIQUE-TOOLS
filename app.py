# --- Real Smart Auto-Crop for Photos/Documents with Borders ---
def auto_crop_borders(cv_img):
    h, w = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Noise kami karun sharp edges shodhane
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    # Edges expand karne jyamule photo chi frame bandist bannel
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    best_box = None
    max_area = 0
    img_area = h * w
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Jar contour khupch motha asel (purna screen sarkha) tar sodun dya
        if 0.15 * img_area < area < 0.98 * img_area:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if area > max_area:
                max_area = area
                best_box = cv2.boundingRect(approx)
                
    if best_box is not None:
        x, y, bw, bh = best_box
        # Frame chya aatla bhaag ghenyasaathi 4-5px margin aat ghya (inner crop)
        inset = 6
        x1 = min(w - 1, max(0, x + inset))
        y1 = min(h - 1, max(0, y + inset))
        x2 = max(x1 + 10, min(w, x + bw - inset))
        y2 = max(y1 + 10, min(h, y + bh - inset))
        return cv_img[y1:y2, x1:x2]
        
    return cv_img

# --- Real Clean 2K Enhancer (No Stretch & Clean Crop) ---
def process_autocrop_2k(pil_img, mode="Document", size_preset="2K Pro (2048px)", do_crop=True):
    img = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    # 1. Exact Border Crop
    if do_crop:
        img = auto_crop_borders(img)
        
    h, w = img.shape[:2]
    
    # 2. Aspect Ratio maintain thevun 2K Scaling (Kadhihi Stretch honar nahi)
    target = 2048
    if w >= h:
        target_w = target
        target_h = int((target / w) * h)
    else:
        target_h = target
        target_w = int((target / h) * w)

    upscaled = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    
    if "Document" in mode:
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b_ch))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        result = cv2.detailEnhance(enhanced, sigma_s=10, sigma_r=0.15)
    else:
        # Photo / Portrait mode: Chehryacha grain/noise gayab + natural smoothness
        denoised = cv2.fastNlMeansDenoisingColored(upscaled, None, 6, 6, 7, 21)
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b_ch))
        result = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    final_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    return Image.fromarray(final_rgb), (target_w, target_h)
