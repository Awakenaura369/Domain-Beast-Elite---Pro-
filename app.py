import streamlit as st
import whois
import pandas as pd
import time
from groq import Groq
import datetime

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(
    page_title="Domain Beast Elite - Pro Hunter",
    page_icon="🌐",
    layout="wide"
)

# --- ستايل مخصص (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #161b22;
        border-radius: 5px 5px 0px 0px;
        color: white;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; }
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        border: None;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- العنوان الرئيسي ---
st.title("🚀 Domain Beast Elite")
st.markdown("### الأداة الاحترافية لقنص الدومينات وفحص العلامات التجارية")
st.info("مرحباً بك محسن! هاد النسخة مطورة خصيصاً للعمل على Streamlit و GitHub.")

# --- السايدبار (Sidebar) للإعدادات ---
with st.sidebar:
    st.header("⚙️ الإعدادات والتحكم")
    groq_api_key = st.text_input("Groq API Key:", type="password", help="دخل كود Groq باش يخدم ليك الذكاء الاصطناعي")
    
    st.subheader("فلاتر البحث")
    selected_exts = st.multiselect(
        "الامتدادات (Extensions):",
        [".com", ".net", ".io", ".ai", ".me", ".org", ".co.ma", ".ma", ".shop", ".info"],
        default=[".com", ".io", ".ai"]
    )
    
    delay = st.slider("التأخير بين عمليات الفحص (ثواني):", 0.1, 3.0, 0.5)
    st.markdown("---")
    st.write("Developed by: **Mouhcine Digital Systems**")

# --- تقسيم التطبيق لـ Tabs ---
tab1, tab2, tab3 = st.tabs([
    "💡 توليد سميات بالـ AI", 
    "🔍 فحص التوفر (Bulk Check)", 
    "🛡️ درع العلامات التجارية (Trademark)"
])

# --- Tab 1: AI Name Generation ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("توليد الأفكار")
        niche = st.text_input("وصف المشروع / النيش:", placeholder="مثلاً: E-commerce in Morocco")
        style = st.selectbox("ستايل السميات:", ["Short & Brandable", "SEO Optimized", "Futuristic", "Arabic/English Mix"])
        num_ideas = st.number_input("عدد الاقتراحات:", 5, 50, 15)
        
        generate_btn = st.button("توليد الاقتراحات 🪄")

    if generate_btn:
        if not groq_api_key:
            st.error("⚠️ عافاك دخل Groq API Key في السايدبار.")
        else:
            try:
                client = Groq(api_key=groq_api_key)
                prompt = f"Act as a professional domain expert. Generate {num_ideas} unique, {style} domain names for: {niche}. Provide ONLY a list of names without extensions, one per line. No numbers, no dashes."
                
                with st.spinner("الذكاء الاصطناعي كيقلب ليك على سميات ناضية..."):
                    completion = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    ai_names = completion.choices[0].message.content.strip().split('\n')
                    # تنظيف القائمة
                    st.session_state['generated_names'] = [n.strip().split('. ')[-1].lower() for n in ai_names if n.strip()]
                    st.success(f"لقينا {len(st.session_state['generated_names'])} اقتراح!")
            except Exception as e:
                st.error(f"خطأ في الاتصال بـ Groq: {e}")

    if 'generated_names' in st.session_state:
        with col2:
            st.subheader("الاقتراحات المستخرجة:")
            st.write(", ".join(st.session_state['generated_names']))
            st.info("تقدر دابا تدوز لـ Tab ديال الفحص باش تشيكهم كاملين دقة وحدة.")

# --- Tab 2: Bulk Availability Checker ---
with tab2:
    st.subheader("فحص توفر الدومينات")
    
    # استيراد السميات من الـ AI Tab تلقائياً إذا وجدت
    default_text = "\n".join(st.session_state.get('generated_names', []))
    manual_input = st.text_area("حط السميات هنا (سمية في كل سطر، بلا .com):", value=default_text, height=150)
    
    start_check = st.button("بدء قنص الدومينات المتاحة 🎯")

    if start_check:
        names_to_check = [n.strip() for n in manual_input.strip().split('\n') if n.strip()]
        if not names_to_check or not selected_exts:
            st.warning("دخل السميات واختار الامتدادات أولاً.")
        else:
            final_results = []
            progress_bar = st.progress(0)
            total = len(names_to_check) * len(selected_exts)
            counter = 0

            status_text = st.empty()
            
            for name in names_to_check:
                for ext in selected_exts:
                    target = f"{name}{ext}"
                    status_text.text(f"⏳ جاري فحص: {target}")
                    
                    try:
                        # فحص سريع للتوفر
                        w = whois.whois(target)
                        if not w.domain_name:
                            available = "✅ متاح"
                            expiry = "N/A"
                        else:
                            available = "❌ محجوز"
                            expiry = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
                    except:
                        available = "✅ متاح" # في حالة الخطأ غالباً الدومين غير مسجل
                        expiry = "N/A"

                    final_results.append({
                        "Domain": target,
                        "Status": available,
                        "Expiry Date": expiry
                    })
                    
                    counter += 1
                    progress_bar.progress(counter / total)
                    time.sleep(delay)

            status_text.empty()
            df = pd.DataFrame(final_results)
            
            # عرض النتائج مع تلوين
            def highlight_available(val):
                color = '#2ecc71' if val == "✅ متاح" else '#e74c3c'
                return f'background-color: {color}; color: white; font-weight: bold'

            st.dataframe(df.style.applymap(highlight_available, subset=['Status']), use_container_width=True)
            
            # زر التحميل
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 تحميل قائمة الهموز (CSV)", csv, "beast_domains.csv", "text/csv")

# --- Tab 3: Trademark Shield ---
with tab3:
    st.header("🛡️ Trademark Shield")
    st.markdown("فحص العلامات التجارية كيحميك من المشاكل القانونية.")
    
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        tm_name = st.text_input("السمية المراد فحصها:", placeholder="مثلاً: NikeShoesPro")
        tm_btn = st.button("تحليل المخاطر بالـ AI 🧠")
        
        if tm_btn:
            if not groq_api_key:
                st.error("دخل API Key.")
            else:
                client = Groq(api_key=groq_api_key)
                tm_prompt = f"Check if the domain name '{tm_name}' could infringe on any famous global trademarks. Analyze the name and give a risk score (0-10) and why."
                
                with st.spinner("جاري التحليل القانوني..."):
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": tm_prompt}],
                        model="llama3-8b-8192",
                    )
                    st.markdown("#### نتيجة التحليل:")
                    st.write(res.choices[0].message.content)

    with t_col2:
        st.subheader("روابط فحص رسمية")
        st.write("ضروري تشيك يدوياً هنا:")
        st.markdown(f"- [🇺🇸 USPTO Search](https://tmsearch.uspto.gov/)")
        st.markdown(f"- [🌍 WIPO Global Brand DB](https://www3.wipo.int/branddb/en/)")
        st.markdown(f"- [🇪🇺 EUIPO Search](https://euipo.europa.eu/eusearch/#basic)")
        
        st.image("https://img.icons8.com/fluency/96/shield.png", width=100)

st.markdown("---")
st.caption("© 2026 Marketing Beast AI - Domain Hunting Module")
