import streamlit as st
import whois
import pandas as pd
import time
from groq import Groq
import datetime

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(
    page_title="Domain Beast Elite V2",
    page_icon="💰",
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
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #2ecc71 !important; border-bottom: 3px solid white; }
    div.stButton > button:first-child {
        background-color: #2ecc71;
        color: white;
        border-radius: 10px;
        border: None;
        height: 3.5em;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #27ae60;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- العنوان الرئيسي ---
st.title("💰 Domain Beast Elite V2")
st.markdown("### نظام قنص وتحليل الدومينات الاحترافي - جيل 2026")
st.info("مرحباً محسن! هاد النسخة مجهزة بذكاء اصطناعي متطور للبحث عن 'الهموز' ذات القيمة العالية.")

# --- السايدبار (Sidebar) ---
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    groq_api_key = st.text_input("Groq API Key:", type="password")
    
    st.subheader("إعدادات الفحص")
    selected_exts = st.multiselect(
        "الامتدادات المطلوبة:",
        [".com", ".net", ".io", ".ai", ".me", ".org", ".co.ma", ".ma", ".shop"],
        default=[".com", ".io", ".ai"]
    )
    
    delay = st.slider("سرعة الفحص (ثانية):", 0.1, 2.0, 0.5)
    st.markdown("---")
    st.write("🔥 **Status:** Pro Version Active")
    st.write("Developed by: **Mouhcine Digital Systems**")

# --- تقسيم التطبيق لـ Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "💡 AI Generator", 
    "🔍 Bulk Hunter", 
    "🛡️ Trademark Shield",
    "📈 SEO Sniper"
])

# --- Tab 1: AI Name Generation ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("توليد سميات بالذكاء الاصطناعي")
        niche = st.text_input("وصف النيش أو المشروع:", placeholder="مثلاً: Crypto Payment Gateway")
        style = st.selectbox("ستايل السميات:", ["Short & Catchy", "Brandable Mix", "Modern Tech", "SEO Friendly"])
        num_ideas = st.number_input("عدد الأفكار:", 5, 50, 20)
        
        if st.button("توليد السميات 🪄"):
            if not groq_api_key:
                st.error("عافاك دخل API Key أولاً.")
            else:
                try:
                    client = Groq(api_key=groq_api_key)
                    prompt = f"Generate {num_ideas} unique, {style} domain names for '{niche}'. Return ONLY a clean list of names, one per line, no numbers, no dots."
                    with st.spinner("AI is thinking..."):
                        completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        ai_names = completion.choices[0].message.content.strip().split('\n')
                        st.session_state['generated_names'] = [n.strip().replace('-', '').lower() for n in ai_names if n.strip()]
                        st.success("تم التوليد بنجاح!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'generated_names' in st.session_state:
        with col2:
            st.subheader("الأفكار المقترحة:")
            st.write(", ".join(st.session_state['generated_names']))
            st.info("تقدر دابا تفحص التوفر ديالهم في الـ Tab الجاية.")

# --- Tab 2: Bulk Availability Checker ---
with tab2:
    st.subheader("فحص توفر الدومينات (Bulk)")
    default_text = "\n".join(st.session_state.get('generated_names', []))
    manual_input = st.text_area("حط قائمة السميات هنا:", value=default_text, height=150)
    
    if st.button("بدء عملية القنص 🎯"):
        names_to_check = [n.strip() for n in manual_input.strip().split('\n') if n.strip()]
        if not names_to_check:
            st.warning("دخل شي سميات أولاً.")
        else:
            final_results = []
            progress_bar = st.progress(0)
            total = len(names_to_check) * len(selected_exts)
            counter = 0
            
            for name in names_to_check:
                for ext in selected_exts:
                    target = f"{name}{ext}"
                    try:
                        w = whois.whois(target)
                        available = "✅ متاح" if not w.domain_name else "❌ محجوز"
                    except:
                        available = "✅ متاح"

                    final_results.append({"Domain": target, "Status": available})
                    counter += 1
                    progress_bar.progress(counter / total)
                    time.sleep(delay)

            df = pd.DataFrame(final_results)
            st.dataframe(df.style.applymap(lambda x: 'color: #2ecc71' if x == '✅ متاح' else 'color: #e74c3c', subset=['Status']), use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 تحميل التقرير (CSV)", csv, "beast_report.csv")

# --- Tab 3: Trademark Shield ---
with tab3:
    st.header("🛡️ Trademark Risk Analysis")
    tm_name = st.text_input("دخل السمية للفحص القانوني:", key="tm_input")
    if st.button("تحليل المخاطر 🧠"):
        if not groq_api_key:
            st.error("API Key مطلوب.")
        else:
            client = Groq(api_key=groq_api_key)
            with st.spinner("جاري التحليل..."):
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Is the name '{tm_name}' risky for a domain regarding trademarks? Give a score 0-10."}],
                    model="llama-3.3-70b-versatile"
                )
                st.write(res.choices[0].message.content)
                st.markdown(f"[🔍 USPTO Search](https://tmsearch.uspto.gov/) | [🌍 WIPO](https://www3.wipo.int/branddb/en/)")

# --- Tab 4: SEO Sniper (The Money Tab) ---
with tab4:
    st.header("📈 SEO Authority & Backlink Hunter")
    seo_domain = st.text_input("دخل الدومين لتحليل قيمته السوقية:", placeholder="example.com")
    if st.button("تحليل القوة والـ SEO 🚀"):
        if seo_domain:
            client = Groq(api_key=groq_api_key)
            with st.spinner("Analyzing SEO Metrics..."):
                # تحليل ذكي للقيمة
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Analyze the SEO potential and brand value of '{seo_domain}'. Is it a high-value domain? Why?"}],
                    model="llama-3.3-70b-versatile"
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("تقرير الـ AI:")
                    st.write(res.choices[0].message.content)
                with col_b:
                    st.subheader("أدوات الفحص العميق:")
                    st.markdown(f"- [🕰️ Wayback Machine (الأرشيف)] (https://web.archive.org/web/*/{seo_domain})")
                    st.markdown(f"- [📊 Ahrefs Backlink Checker] (https://ahrefs.com/backlink-checker?target={seo_domain})")
                    st.markdown(f"- [🔎 Google Index Status] (https://www.google.com/search?q=site:{seo_domain})")
                    st.success("نصيحة: إذا لقيتِ الدومين متاح وفيه تاريخ قديم في الأرشيف، شريه بلا ما تفكر!")

st.markdown("---")
st.caption("© 2026 Marketing Beast AI - Professional Domaining Suite")
