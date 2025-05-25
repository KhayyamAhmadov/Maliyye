import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Səhifə konfiqurasiyası
st.set_page_config(
    page_title="Maliyyə Sistemi",
    page_icon="💰",
    layout="wide"
)

# CSS stil
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    .success-message {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Başlıq
st.markdown("""
<div class="main-header">
    <h1>💰 Maliyyə Sistemi</h1>
</div>
""", unsafe_allow_html=True)

# Rayonların siyahısı
REGIONS = [
    "Aparat", "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu", 
    "Astara", "Bakı", "Babək (Naxçıvan MR)", "Balakən", "Bərdə", "Beyləqan", "Biləsuvar", 
    "Cəbrayıl", "Cəlilabad", "Culfa (Naxçıvan MR)", "Daşkəsən", "Füzuli", "Gədəbəy", 
    "Gəncə", "Goranboy", "Göyçay", "Göygöl", "Hacıqabul", "Xaçmaz", "Xankəndi", "Xızı", 
    "Xocalı", "Xocavənd", "İmişli", "İsmayıllı", "Kəlbəcər", "Kəngərli (Naxçıvan MR)", 
    "Kürdəmir", "Laçın", "Lənkəran", "Lerik", "Masallı", "Mingəçevir", "Naftalan", 
    "Neftçala", "Naxçıvan", "Oğuz", "Siyəzən", "Ordubad (Naxçıvan MR)", "Qəbələ", 
    "Qax", "Qazax", "Qobustan", "Quba", "Qubadlı", "Qusar", "Saatlı", "Sabirabad", 
    "Sədərək (Naxçıvan MR)", "Salyan", "Samux", "Şabran", "Şahbuz (Naxçıvan MR)", 
    "Şamaxı", "Şəki", "Şəmkir", "Şərur (Naxçıvan MR)", "Şirvan", "Şuşa", "Sumqayıt", 
    "Tərtər", "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala", "Zəngilan", "Zərdab", 
    "Nabran", "Xudat"
]

# Session state başlatma
if 'budget_data' not in st.session_state:
    st.session_state.budget_data = {}

def calculate_percentage(amount, total):
    """Faiz hesablama funksiyası"""
    if total == 0:
        return 0
    return round((amount / total) * 100, 2)

def validate_budget(items_df, total_budget):
    """Büdcə doğrulama funksiyası"""
    if items_df.empty:
        return True, ""
    
    total_items = items_df['Məbləğ'].sum()
    if total_items > total_budget:
        return False, f"Xəta: Maddələrin cəmi ({total_items:,.2f} AZN) ümumi büdcədən ({total_budget:,.2f} AZN) çoxdur!"
    return True, ""

# Əsas tab səhifələri
tab1, tab2, tab3 = st.tabs(["📊 Büdcə Planlaması", "📋 Məlumatları İdarə Et", "📁 Excel İdarəetməsi"])

with tab1:
    st.header("🏛️ Rayon və Büdcə Seçimi")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_region = st.selectbox(
            "Rayon seçin:",
            options=["Seçin..."] + REGIONS,
            key="region_select"
        )
    
    with col2:
        if selected_region != "Seçin...":
            total_budget = st.number_input(
                "Ümumi Məbləğ (Smeta) - AZN:",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="budget_input"
            )
    
    if selected_region != "Seçin..." and total_budget > 0:
        st.markdown("---")
        st.header("📝 Maddələr Siyahısı")
        
        # Seçilmiş rayon üçün məlumatları başlat
        if selected_region not in st.session_state.budget_data:
            st.session_state.budget_data[selected_region] = {
                'total_budget': total_budget,
                'items': pd.DataFrame(columns=['Maddə Nömrəsi', 'Maddənin Adı', 'Məbləğ', 'Faiz'])
            }
        
        # Ümumi büdcəni yenilə
        st.session_state.budget_data[selected_region]['total_budget'] = total_budget
        
        # Yeni maddə əlavə etmə formu
        with st.expander("➕ Yeni Maddə Əlavə Et", expanded=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                item_number = st.text_input("Maddə Nömrəsi:", key="item_number")
            
            with col2:
                item_name = st.text_input("Maddənin Adı:", key="item_name")
            
            with col3:
                item_amount = st.number_input(
                    "Məbləğ (AZN):",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    format="%.2f",
                    key="item_amount"
                )
            
            if st.button("➕ Maddə Əlavə Et", key="add_item"):
                if item_number and item_name and item_amount > 0:
                    # Yeni maddə əlavə et
                    current_items = st.session_state.budget_data[selected_region]['items'].copy()
                    
                    # Faizi hesabla
                    percentage = calculate_percentage(item_amount, total_budget)
                    
                    new_item = pd.DataFrame({
                        'Maddə Nömrəsi': [item_number],
                        'Maddənin Adı': [item_name],
                        'Məbləğ': [item_amount],
                        'Faiz': [f"{percentage}%"]
                    })
                    
                    updated_items = pd.concat([current_items, new_item], ignore_index=True)
                    
                    # Doğrulama
                    is_valid, error_msg = validate_budget(updated_items, total_budget)
                    
                    if is_valid:
                        st.session_state.budget_data[selected_region]['items'] = updated_items
                        st.success("✅ Maddə uğurla əlavə edildi!")
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message">{error_msg}</div>', unsafe_allow_html=True)
                else:
                    st.error("❌ Bütün sahələri doldurun!")
        
        # Cədvəli göstər
        current_items = st.session_state.budget_data[selected_region]['items']
        
        if not current_items.empty:
            st.subheader("📊 Mövcud Maddələr")
            
            # Faizləri yenidən hesabla
            for idx, row in current_items.iterrows():
                amount = row['Məbləğ']
                percentage = calculate_percentage(amount, total_budget)
                current_items.at[idx, 'Faiz'] = f"{percentage}%"
            
            # Cədvəli göstər
            st.dataframe(
                current_items,
                use_container_width=True,
                hide_index=True
            )
            
            # Xülasə məlumatları
            col1, col2, col3 = st.columns(3)
            
            total_items_amount = current_items['Məbləğ'].sum()
            remaining_budget = total_budget - total_items_amount
            used_percentage = calculate_percentage(total_items_amount, total_budget)
            
            with col1:
                st.metric("💰 Ümumi Büdcə", f"{total_budget:,.2f} AZN")
            
            with col2:
                st.metric("💸 İstifadə Edilən", f"{total_items_amount:,.2f} AZN", f"{used_percentage}%")
            
            with col3:
                color = "normal" if remaining_budget >= 0 else "inverse"
                st.metric("💳 Qalan Büdcə", f"{remaining_budget:,.2f} AZN", delta_color=color)
            
            # Progress bar
            progress = min(used_percentage / 100, 1.0)
            st.progress(progress)
            
            if remaining_budget < 0:
                st.markdown('<div class="error-message">⚠️ Xəbərdarlıq: Büdcə aşılıb!</div>', unsafe_allow_html=True)

with tab2:
    st.header("📋 Məlumatları İdarə Et və Redaktə Et")
    
    if st.session_state.budget_data:
        # Rayon seçimi
        region_to_edit = st.selectbox(
            "Redaktə etmək üçün rayon seçin:",
            options=list(st.session_state.budget_data.keys()),
            key="edit_region_select"
        )
        
        if region_to_edit:
            region_data = st.session_state.budget_data[region_to_edit]
            
            st.subheader(f"📊 {region_to_edit} - Məlumatları")
            
            # Ümumi büdcəni redaktə et
            col1, col2 = st.columns([1, 1])
            with col1:
                new_total_budget = st.number_input(
                    "Ümumi Büdcəni Yenilə (AZN):",
                    value=region_data['total_budget'],
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key=f"edit_budget_{region_to_edit}"
                )
            
            with col2:
                if st.button("💾 Büdcəni Yenilə", key=f"update_budget_{region_to_edit}"):
                    st.session_state.budget_data[region_to_edit]['total_budget'] = new_total_budget
                    st.success("✅ Büdcə yeniləndi!")
                    st.rerun()
            
            # Maddələri göstər və redaktə et
            current_items = region_data['items'].copy()
            
            if not current_items.empty:
                st.subheader("✏️ Maddələri Redaktə Et")
                
                # Hər maddə üçün redaktə formu
                for idx, row in current_items.iterrows():
                    with st.expander(f"Maddə {idx + 1}: {row['Maddənin Adı']}", expanded=False):
                        col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                        
                        with col1:
                            new_number = st.text_input(
                                "Nömrə:",
                                value=row['Maddə Nömrəsi'],
                                key=f"edit_number_{region_to_edit}_{idx}"
                            )
                        
                        with col2:
                            new_name = st.text_input(
                                "Ad:",
                                value=row['Maddənin Adı'],
                                key=f"edit_name_{region_to_edit}_{idx}"
                            )
                        
                        with col3:
                            new_amount = st.number_input(
                                "Məbləğ:",
                                value=float(row['Məbləğ']),
                                min_value=0.0,
                                step=10.0,
                                format="%.2f",
                                key=f"edit_amount_{region_to_edit}_{idx}"
                            )
                        
                        with col4:
                            col4a, col4b = st.columns(2)
                            with col4a:
                                if st.button("💾", key=f"update_item_{region_to_edit}_{idx}", help="Yenilə"):
                                    # Maddəni yenilə
                                    current_items.at[idx, 'Maddə Nömrəsi'] = new_number
                                    current_items.at[idx, 'Maddənin Adı'] = new_name
                                    current_items.at[idx, 'Məbləğ'] = new_amount
                                    
                                    # Doğrulama
                                    is_valid, error_msg = validate_budget(current_items, new_total_budget)
                                    
                                    if is_valid:
                                        st.session_state.budget_data[region_to_edit]['items'] = current_items
                                        st.success("✅ Maddə yeniləndi!")
                                        st.rerun()
                                    else:
                                        st.error(error_msg)
                            
                            with col4b:
                                if st.button("🗑️", key=f"delete_item_{region_to_edit}_{idx}", help="Sil"):
                                    # Maddəni sil
                                    updated_items = current_items.drop(idx).reset_index(drop=True)
                                    st.session_state.budget_data[region_to_edit]['items'] = updated_items
                                    st.success("✅ Maddə silindi!")
                                    st.rerun()
                
                # Yenilənmiş cədvəli göstər
                updated_items = st.session_state.budget_data[region_to_edit]['items']
                if not updated_items.empty:
                    # Faizləri yenidən hesabla
                    total_budget_current = st.session_state.budget_data[region_to_edit]['total_budget']
                    for idx, row in updated_items.iterrows():
                        amount = row['Məbləğ']
                        percentage = calculate_percentage(amount, total_budget_current)
                        updated_items.at[idx, 'Faiz'] = f"{percentage}%"
                    
                    st.subheader("📊 Yenilənmiş Cədvəl")
                    st.dataframe(updated_items, use_container_width=True, hide_index=True)
            
            # Rayonu tamamilə sil
            st.markdown("---")
            if st.button(f"🗑️ {region_to_edit} rayonunu tamamilə sil", key=f"delete_region_{region_to_edit}"):
                del st.session_state.budget_data[region_to_edit]
                st.success(f"✅ {region_to_edit} rayonu silindi!")
                st.rerun()
    
    else:
        st.info("📝 Hələ heç bir məlumat mövcud deyil. Büdcə Planlaması tabından başlayın.")

with tab3:
    st.header("📁 Excel Faylı İdarəetməsi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Excel Faylını İxrac Et")
        
        if st.session_state.budget_data:
            # Excel faylı yaradılması
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Hər rayon üçün ayrı sheet
                for region, data in st.session_state.budget_data.items():
                    if not data['items'].empty:
                        # Maddələr cədvəli
                        items_df = data['items'].copy()
                        
                        # Xülasə məlumatları əlavə et
                        summary_data = {
                            'Maddə Nömrəsi': ['', 'XÜLASƏ', 'Ümumi Büdcə', 'İstifadə Edilən', 'Qalan Büdcə'],
                            'Maddənin Adı': ['', '', '', '', ''],
                            'Məbləğ': ['', '', data['total_budget'], items_df['Məbləğ'].sum(), 
                                     data['total_budget'] - items_df['Məbləğ'].sum()],
                            'Faiz': ['', '', '100%', f"{calculate_percentage(items_df['Məbləğ'].sum(), data['total_budget'])}%", 
                                   f"{100 - calculate_percentage(items_df['Məbləğ'].sum(), data['total_budget'])}%"]
                        }
                        
                        summary_df = pd.DataFrame(summary_data)
                        final_df = pd.concat([items_df, summary_df], ignore_index=True)
                        
                        final_df.to_excel(writer, sheet_name=region[:30], index=False)
            
            output.seek(0)
            
            # Fayl adı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Maliyye_Melumatları_{timestamp}.xlsx"
            
            st.download_button(
                label="📥 Excel Faylını Endir",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("📝 İxrac etmək üçün məlumat mövcud deyil.")
    
    with col2:
        st.subheader("📤 Excel Faylını İdxal Et")
        
        uploaded_file = st.file_uploader(
            "Excel faylını seçin:",
            type=['xlsx', 'xls'],
            key="excel_upload"
        )
        
        if uploaded_file is not None:
            try:
                # Excel faylını oxu
                excel_file = pd.ExcelFile(uploaded_file)
                
                st.success(f"✅ Fayl yükləndi! Sheet-lər: {', '.join(excel_file.sheet_names)}")
                
                # Hər sheet üçün məlumatları yüklə
                if st.button("📥 Məlumatları İdxal Et", key="import_data"):
                    imported_count = 0
                    
                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                            
                            # Sütun adlarını yoxla
                            required_columns = ['Maddə Nömrəsi', 'Maddənin Adı', 'Məbləğ']
                            if all(col in df.columns for col in required_columns):
                                # XÜLASƏ sətrlərini çıxar
                                df_filtered = df[~df['Maddənin Adı'].isin(['', 'XÜLASƏ']) & 
                                               df['Maddə Nömrəsi'].notna() & 
                                               (df['Maddə Nömrəsi'] != '')]
                                
                                if not df_filtered.empty:
                                    # Rayon məlumatlarını session state-ə əlavə et
                                    region_name = sheet_name
                                    
                                    # Faizləri yenidən hesabla
                                    total_budget = df_filtered['Məbləğ'].sum() * 1.1  # 10% ehtiyat
                                    
                                    for idx, row in df_filtered.iterrows():
                                        amount = row['Məbləğ']
                                        percentage = calculate_percentage(amount, total_budget)
                                        df_filtered.at[idx, 'Faiz'] = f"{percentage}%"
                                    
                                    st.session_state.budget_data[region_name] = {
                                        'total_budget': total_budget,
                                        'items': df_filtered[required_columns + ['Faiz']].reset_index(drop=True)
                                    }
                                    
                                    imported_count += 1
                        
                        except Exception as e:
                            st.warning(f"⚠️ {sheet_name} sheet-i yüklənə bilmədi: {str(e)}")
                    
                    if imported_count > 0:
                        st.success(f"✅ {imported_count} rayon məlumatı uğurla idxal edildi!")
                        st.rerun()
                    else:
                        st.error("❌ Heç bir uyğun məlumat tapılmadı!")
            
            except Exception as e:
                st.error(f"❌ Fayl oxunarkən xəta baş verdi: {str(e)}")
