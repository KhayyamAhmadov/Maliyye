import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Configure page
st.set_page_config(
    page_title="Maliyyə Paneli", 
    layout="wide",
    page_icon="📊"
)

# All regions list
regions = [
    "Aparat", "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu", "Astara", "Bakı",
    "Babək (Naxçıvan MR)", "Balakən", "Bərdə", "Beyləqan", "Biləsuvar", "Cəbrayıl", "Cəlilabad",
    "Culfa (Naxçıvan MR)", "Daşkəsən", "Füzuli", "Gədəbəy", "Gəncə", "Goranboy", "Göyçay", "Göygöl",
    "Hacıqabul", "Xaçmaz", "Xankəndi", "Xızı", "Xocalı", "Xocavənd", "İmişli", "İsmayıllı", "Kəlbəcər",
    "Kəngərli (Naxçıvan MR)", "Kürdəmir", "Laçın", "Lənkəran", "Lerik", "Masallı", "Mingəçevir",
    "Naftalan", "Neftçala", "Naxçıvan", "Oğuz", "Siyəzən", "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax",
    "Qazax", "Qobustan", "Quba", "Qubadlı", "Qusar", "Saatlı", "Sabirabad", "Sədərək (Naxçıvan MR)",
    "Salyan", "Samux", "Şabran", "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki", "Şəmkir",
    "Şərur (Naxçıvan MR)", "Şirvan", "Şuşa", "Sumqayıt", "Tərtər", "Tovuz", "Ucar", "Yardımlı",
    "Yevlax", "Zaqatala", "Zəngilan", "Zərdab", "Nabran", "Xudat"
]

# Initialize session state
if 'budgets' not in st.session_state:
    st.session_state.budgets = {}

if 'current_items' not in st.session_state:
    st.session_state.current_items = []

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .error-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    .stTab > div:first-child {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Main title with enhanced styling
st.markdown("""
# 📊 Maliyyə İdarəetmə Paneli
### Rayonlar üzrə büdcə planlaması və idarəetmə sistemi
---
""")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Rayon üzrə Smeta", 
    "📂 Cedveller və Redaktə", 
    "📈 Analitika və Hesabatlar",
    "⚙️ Sistem Parametrləri"
])

# Tab 1: Regional Budget Planning
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🎯 Rayon Seçimi")
        selected_region = st.selectbox("Rayon seçin:", regions, key="region_select")
        
        if selected_region:
            st.markdown(f"### 💰 {selected_region} üçün Smeta")
            total_budget = st.number_input(
                "Ümumi məbləğ (AZN)", 
                min_value=0.0, 
                format="%.2f",
                key="total_budget"
            )
            
            if total_budget > 0:
                st.markdown("### 📝 Maddələr")
                num_items = st.number_input(
                    "Madde sayı", 
                    min_value=1, 
                    max_value=20, 
                    step=1,
                    key="num_items"
                )
                
                # Add/Remove items buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("➕ Maddə əlavə et", key="add_item"):
                        st.session_state.current_items.append({
                            "Madde nömrəsi": "",
                            "Madde adı": "",
                            "Məbləğ": 0.0,
                            "%": 0.0
                        })
                
                with col_btn2:
                    if st.button("➖ Son maddəni sil", key="remove_item"):
                        if st.session_state.current_items:
                            st.session_state.current_items.pop()
    
    with col2:
        if selected_region and total_budget > 0:
            st.markdown("### 📋 Maddələrin Daxil Edilməsi")
            
            data = []
            total_amount = 0
            
            # Ensure we have the right number of items
            while len(st.session_state.current_items) < int(num_items):
                st.session_state.current_items.append({
                    "Madde nömrəsi": "",
                    "Madde adı": "",
                    "Məbləğ": 0.0,
                    "%": 0.0
                })
            
            while len(st.session_state.current_items) > int(num_items):
                st.session_state.current_items.pop()
            
            # Create form for items
            with st.form("budget_form"):
                for i in range(int(num_items)):
                    st.markdown(f"**Madde {i+1}**")
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    
                    with col_a:
                        madde_nomresi = st.text_input(
                            f"Nömrə", 
                            value=st.session_state.current_items[i]["Madde nömrəsi"] if i < len(st.session_state.current_items) else "",
                            key=f"nomre_{i}"
                        )
                    
                    with col_b:
                        madde_adi = st.text_input(
                            f"Adı", 
                            value=st.session_state.current_items[i]["Madde adı"] if i < len(st.session_state.current_items) else "",
                            key=f"adi_{i}"
                        )
                    
                    with col_c:
                        mebleg = st.number_input(
                            f"Məbləğ (AZN)", 
                            min_value=0.0, 
                            format="%.2f", 
                            value=st.session_state.current_items[i]["Məbləğ"] if i < len(st.session_state.current_items) else 0.0,
                            key=f"mebleg_{i}"
                        )
                    
                    faiz = round((mebleg / total_budget) * 100 if total_budget > 0 else 0, 2)
                    total_amount += mebleg
                    
                    data.append({
                        "Madde nömrəsi": madde_nomresi,
                        "Madde adı": madde_adi,
                        "Məbləğ": mebleg,
                        "%": faiz
                    })
                
                # Submit button
                submitted = st.form_submit_button("💾 Smetanı Yadda Saxla", use_container_width=True)
                
                if submitted:
                    # Validation
                    if total_amount > total_budget:
                        st.error(f"❌ Cəmi məbləğ ({total_amount:.2f} AZN) smetanı aşır!")
                    else:
                        # Save to session state
                        st.session_state.budgets[selected_region] = {
                            "total_budget": total_budget,
                            "items": data,
                            "total_amount": total_amount,
                            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.success(f"✅ {selected_region} üçün smeta uğurla yadda saxlanıldı!")
            
            # Display summary
            if data:
                st.markdown("### 📊 Xülasə")
                df = pd.DataFrame(data)
                
                # Metrics
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Ümumi Smeta", f"{total_budget:.2f} AZN")
                with col_m2:
                    st.metric("İstifadə Olunan", f"{total_amount:.2f} AZN")
                with col_m3:
                    remaining = total_budget - total_amount
                    st.metric("Qalan", f"{remaining:.2f} AZN", 
                             delta=f"{(remaining/total_budget)*100:.1f}%" if total_budget > 0 else "0%")
                
                # Data table
                st.dataframe(df, use_container_width=True)
                
                # Pie chart
                if total_amount > 0:
                    fig = px.pie(
                        df, 
                        values='Məbləğ', 
                        names='Madde adı',
                        title=f"{selected_region} - Büdcə Bölgüsü"
                    )
                    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Tables and Edit
with tab2:
    st.markdown("### 📂 Rayonlara görə smeta cədvəlləri")
    
    if st.session_state.budgets:
        # Summary table
        summary_data = []
        for region, budget_info in st.session_state.budgets.items():
            summary_data.append({
                "Rayon": region,
                "Ümumi Məbləğ (AZN)": budget_info["total_budget"],
                "İstifadə Olunan (AZN)": budget_info["total_amount"],
                "Maddə Sayı": len(budget_info["items"]),
                "Yaradılma Tarixi": budget_info["created_date"],
                "Status": "✅ Tamamlanmış" if budget_info["total_amount"] == budget_info["total_budget"] else "🔶 Qismən"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Edit section
        st.markdown("### ✏️ Redaktə")
        edit_region = st.selectbox("Redaktə üçün rayon seçin:", list(st.session_state.budgets.keys()))
        
        if edit_region:
            col_edit1, col_edit2 = st.columns([1, 1])
            
            with col_edit1:
                if st.button(f"📝 {edit_region} redaktə et", use_container_width=True):
                    st.session_state.edit_mode = edit_region
                    st.rerun()
            
            with col_edit2:
                if st.button(f"🗑️ {edit_region} sil", use_container_width=True):
                    del st.session_state.budgets[edit_region]
                    st.success(f"{edit_region} uğurla silindi!")
                    st.rerun()
            
            # Show detailed view
            budget_info = st.session_state.budgets[edit_region]
            st.markdown(f"#### 📋 {edit_region} - Detallı Məlumat")
            
            items_df = pd.DataFrame(budget_info["items"])
            st.dataframe(items_df, use_container_width=True)
    else:
        st.info("Hələ heç bir smeta daxil edilməyib. Zəhmət olmasa birinci tabdan başlayın.")

# Tab 3: Analytics and Reports
with tab3:
    st.markdown("### 📈 Analitika və Hesabatlar")
    
    if st.session_state.budgets:
        # Overall statistics
        total_regions = len(st.session_state.budgets)
        total_budget_all = sum([budget["total_budget"] for budget in st.session_state.budgets.values()])
        total_used_all = sum([budget["total_amount"] for budget in st.session_state.budgets.values()])
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Ümumi Rayonlar", total_regions)
        with col_stat2:
            st.metric("Ümumi Büdcə", f"{total_budget_all:.2f} AZN")
        with col_stat3:
            st.metric("İstifadə Olunan", f"{total_used_all:.2f} AZN")
        with col_stat4:
            usage_rate = (total_used_all / total_budget_all * 100) if total_budget_all > 0 else 0
            st.metric("İstifadə Dərəcəsi", f"{usage_rate:.1f}%")
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Budget comparison by region
            region_data = []
            for region, budget in st.session_state.budgets.items():
                region_data.append({
                    "Rayon": region,
                    "Büdcə": budget["total_budget"],
                    "İstifadə": budget["total_amount"]
                })
            
            region_df = pd.DataFrame(region_data)
            fig_bar = px.bar(
                region_df, 
                x='Rayon', 
                y=['Büdcə', 'İstifadə'],
                title="Rayonlar üzrə Büdcə Müqayisəsi",
                barmode='group'
            )
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_chart2:
            # Usage rate by region
            region_data_rate = []
            for region, budget in st.session_state.budgets.items():
                rate = (budget["total_amount"] / budget["total_budget"] * 100) if budget["total_budget"] > 0 else 0
                region_data_rate.append({
                    "Rayon": region,
                    "İstifadə Dərəcəsi (%)": rate
                })
            
            rate_df = pd.DataFrame(region_data_rate)
            fig_rate = px.bar(
                rate_df, 
                x='Rayon', 
                y='İstifadə Dərəcəsi (%)',
                title="Rayonlar üzrə İstifadə Dərəcəsi",
                color='İstifadə Dərəcəsi (%)',
                color_continuous_scale='RdYlGn'
            )
            fig_rate.update_xaxes(tickangle=45)
            st.plotly_chart(fig_rate, use_container_width=True)
        
        # Export functionality
        st.markdown("### 📤 Export")
        if st.button("📊 Excel faylına export et"):
            # This would require openpyxl library
            st.info("Excel export funksiyası əlavə kitabxana tələb edir.")
        
        if st.button("📋 JSON formatında yüklə"):
            json_data = json.dumps(st.session_state.budgets, ensure_ascii=False, indent=2)
            st.download_button(
                label="JSON faylını yüklə",
                data=json_data,
                file_name=f"smeta_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("Analitika üçün ən azı bir rayonun smeta məlumatı daxil edilməlidir.")

# Tab 4: System Parameters
with tab4:
    st.markdown("### ⚙️ Sistem Parametrləri")
    
    col_sys1, col_sys2 = st.columns(2)
    
    with col_sys1:
        st.markdown("#### 🔧 Ümumi Parametrlər")
        
        default_currency = st.selectbox("Valyuta", ["AZN", "USD", "EUR"], index=0)
        decimal_places = st.number_input("Onluq yerlərin sayı", min_value=0, max_value=4, value=2)
        
        st.markdown("#### 📊 Hesabat Parametrləri")
        auto_save = st.checkbox("Avtomatik yadda saxlama", value=True)
        show_percentages = st.checkbox("Faizləri göstər", value=True)
    
    with col_sys2:
        st.markdown("#### 🎨 Görünüş Parametrləri")
        
        theme_color = st.selectbox("Tema rəngi", ["Mavi", "Yaşıl", "Qırmızı", "Bənövşəyi"], index=0)
        table_size = st.selectbox("Cədvəl ölçüsü", ["Kiçik", "Orta", "Böyük"], index=1)
        
        st.markdown("#### 🔄 Sistem Əməliyyatları")
        
        if st.button("🗑️ Bütün məlumatları sil", type="secondary"):
            if st.checkbox("Təsdiq edirəm ki, bütün məlumatlar silinəcək"):
                st.session_state.budgets = {}
                st.session_state.current_items = []
                st.success("Bütün məlumatlar silindi!")
                st.rerun()
        
        if st.button("📥 Nümunə məlumatlar yüklə"):
            # Load sample data
            sample_data = {
                "Bakı": {
                    "total_budget": 500000.0,
                    "items": [
                        {"Madde nömrəsi": "01", "Madde adı": "İnfrastruktur", "Məbləğ": 200000.0, "%": 40.0},
                        {"Madde nömrəsi": "02", "Madde adı": "Təhsil", "Məbləğ": 150000.0, "%": 30.0},
                        {"Madde nömrəsi": "03", "Madde adı": "Səhiyyə", "Məbləğ": 150000.0, "%": 30.0}
                    ],
                    "total_amount": 500000.0,
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "Gəncə": {
                    "total_budget": 300000.0,
                    "items": [
                        {"Madde nömrəsi": "01", "Madde adı": "Yol təmiri", "Məbləğ": 120000.0, "%": 40.0},
                        {"Madde nömrəsi": "02", "Madde adı": "Park yenilənməsi", "Məbləğ": 90000.0, "%": 30.0},
                        {"Madde nömrəsi": "03", "Madde adı": "İdari binalar", "Məbləğ": 90000.0, "%": 30.0}
                    ],
                    "total_amount": 300000.0,
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            st.session_state.budgets.update(sample_data)
            st.success("Nümunə məlumatlar yükləndi!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    📊 Maliyyə İdarəetmə Paneli v2.0 | Azərbaycan Rayonları üçün Büdcə Planlaması
</div>
""", unsafe_allow_html=True)