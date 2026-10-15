import streamlit as st
import pandas as pd

# ページ基本設定（スマホでも見やすいレイアウト）
st.set_page_config(page_title="適正購入価格シミュレーター", page_icon="🏢", layout="centered")

st.title("🏢 不動産 収益＆適正価格シミュレーター")
st.caption("株式会社チェル - 収益物件の買付目安・利回りを瞬時に計算します")

# --- 入力セクション（共通項目） ---
st.header("📝 1. 物件の収益・経費シミュレーション")

col1, col2 = st.columns(2)
with col1:
    monthly_rent = st.number_input("想定家賃（月額 / 満室時）", min_value=0, value=100000, step=10000)
    vacancy_rate = st.slider("想定空室率（%）", 0, 50, 5, 1)

with col2:
    expense_ratio = st.slider("運営経費率（% / 管理費・修繕・固都税）", 0, 50, 20, 1)
    purchase_cost_ratio = st.slider("購入諸経費率（% / 仲介・登記・取得税など）", 0, 20, 7, 1)

renovation_cost = st.number_input("購入時リフォーム・初期修繕費（円）", min_value=0, value=0, step=100000)

# 基礎計算
yearly_rent_full = monthly_rent * 12
yearly_rent_real = yearly_rent_full * (1 - (vacancy_rate / 100))
yearly_expense = yearly_rent_real * (expense_ratio / 100)
noi = yearly_rent_real - yearly_expense  # 営業純利益（手残り）

st.info(f"💡 実質的な年間家賃収入: **{int(yearly_rent_real):,} 円** / 年間手残り (NOI): **{int(noi):,} 円**")

st.divider()

# --- タブで機能を切り替え ---
tab1, tab2 = st.tabs(["🎯 目標利回りから適正購入価格を逆算", "📊 販売価格から現在の利回りを計算"])

with tab1:
    st.header("🎯 2. 適正購入価格（買付目安）の算出")
    st.write("「この利回りが欲しい！」という目標から、いくらで指値（買付）すべきかを逆算します。")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        target_yield_gross = st.number_input("目標 表面利回り（%）", min_value=1.0, value=12.0, step=0.5)
    with col_t2:
        target_yield_net = st.number_input("目標 実質利回り（%）", min_value=1.0, value=8.0, step=0.5)

    # 計算ロジック
    # 表面利回り逆算: 物件価格 = 年間家賃(満室) / 表面利回り
    target_price_gross = yearly_rent_full / (target_yield_gross / 100)
    
    # 実質利回り逆算: 
    # 目標総投資額 = NOI / 実質利回り
    # 物件価格 = (目標総投資額 - リフォーム費) / (1 + 購入諸経費率)
    target_total_investment = noi / (target_yield_net / 100)
    target_price_net = (target_total_investment - renovation_cost) / (1 + (purchase_cost_ratio / 100))

    st.subheader("算出結果：指値の目安")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label=f"【表面利回り {target_yield_gross}%】達成ライン", value=f"約 {int(target_price_gross):,} 円")
    
    with res_col2:
        if target_price_net > 0:
            st.metric(label=f"【実質利回り {target_yield_net}%】達成ライン(推奨)", value=f"約 {int(target_price_net):,} 円")
            
            st.caption("【内訳】")
            st.write(f"・物件価格: {int(target_price_net):,} 円")
            st.write(f"・購入諸経費: {int(target_price_net * (purchase_cost_ratio / 100)):,} 円")
            st.write(f"・リフォーム: {int(renovation_cost):,} 円")
            st.write(f"**・総投資額: {int(target_total_investment):,} 円**")
        else:
            st.error("⚠️ この条件で目標を達成するには、物件をマイナス価格（お金をもらって買う）にする必要があります。家賃や経費の設定を見直してください。")

with tab2:
    st.header("📊 2. 現在の利回りシミュレーション")
    st.write("マイソク（販売図面）に記載されている物件価格から、本当の利回りを計算します。")
    
    asking_price = st.number_input("物件の販売価格（円）", min_value=100000, value=10000000, step=500000)
    
    # 計算ロジック
    current_gross_yield = (yearly_rent_full / asking_price) * 100
    
    total_cost = asking_price + (asking_price * (purchase_cost_ratio / 100)) + renovation_cost
    current_net_yield = (noi / total_cost) * 100 if total_cost > 0 else 0
    
    st.subheader("算出結果：実際の利回り")
    res_col3, res_col4 = st.columns(2)
    
    with res_col3:
        st.metric(label="表面利回り（満室想定）", value=f"{current_gross_yield:.2f} %")
    with res_col4:
        st.metric(label="実質利回り（諸経費・空室考慮）", value=f"{current_net_yield:.2f} %")
        
    st.caption("【内訳】")
    st.write(f"・物件価格: {int(asking_price):,} 円")
    st.write(f"・購入諸経費: {int(asking_price * (purchase_cost_ratio / 100)):,} 円")
    st.write(f"・リフォーム: {int(renovation_cost):,} 円")
    st.write(f"**・総投資額: {int(total_cost):,} 円**")
