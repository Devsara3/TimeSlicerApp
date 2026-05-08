import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import base64

JST = timezone(timedelta(hours=+9), 'JST')

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Time Slicer | Premium", layout="wide", initial_sidebar_state="expanded")

def inject_custom_design(bg_url):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;600&display=swap');

    /* デフォルトのStreamlit要素を隠す/調整 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{background-color: transparent !important;}}
    
    /* 全体背景 */
    .stApp {{
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.8)), url("{bg_url}") center/cover no-repeat fixed;
        font-family: 'Outfit', sans-serif;
    }}

    /* サイドバーの背景 */
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        background-color: transparent !important;
    }}

    /* タイトルやテキストの色を白ベースに */
    h1, h2, h3, p, label, .stMarkdown p {{
        color: rgba(255, 255, 255, 0.95) !important;
        font-family: 'Outfit', sans-serif;
    }}

    /* メインコンテナ（グラスモーフィズム強化） */
    .block-container {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 24px;
        padding: 48px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 750px;
        margin: 40px auto;
        color: white;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .block-container:hover {{
        box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
    }}

    /* タイムボックス (右上) */
    .time-container {{
        display: flex;
        align-items: baseline;
        justify-content: flex-end;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        padding-bottom: 15px;
    }}
    .time-value {{
        font-weight: 200;
        font-size: 5.5rem;
        line-height: 0.8;
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 15px rgba(167, 139, 250, 0.3);
    }}
    .time-unit {{
        font-size: 1.2rem;
        font-weight: 300;
        margin-left: 10px;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    /* タスクリストのチップ */
    .task-tag {{
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.08);
        padding: 8px 18px;
        border-radius: 20px;
        margin: 6px;
        font-size: 0.95rem;
        font-weight: 300;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }}
    .task-tag:hover {{
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border-color: rgba(167, 139, 250, 0.5);
    }}

    /* ボタンのカスタマイズ */
    div.stButton > button {{
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        width: 100%;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6);
        border: none;
        color: white;
    }}
    div.stButton > button:active {{
        transform: translateY(1px);
    }}
    
    /* ボタンを前面に出す（No Phone Mode等で隠れないように） */
    div.stButton {{
        position: relative;
        z-index: 10000;
    }}

    /* 入力フォーム類のカスタマイズ (セレクトボックス, 数値入力など) */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {{
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
    }}
    .stTextInput > div > div > input:focus, 
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {{
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 1px #8b5cf6 !important;
    }}

    /* タブのカスタマイズ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 20px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        color: rgba(255,255,255,0.6) !important;
        border-bottom-color: transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: #a78bfa !important;
        border-bottom-color: #a78bfa !important;
    }}

    /* 区切り線 */
    hr {{
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* 履歴リストアイテム */
    .history-item {{
        background: rgba(0, 0, 0, 0.2);
        border-left: 4px solid #a78bfa;
        padding: 12px 20px;
        margin-bottom: 10px;
        border-radius: 4px 8px 8px 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease;
    }}
    .history-item:hover {{
        transform: translateX(5px);
        background: rgba(0, 0, 0, 0.3);
    }}
    
    /* ======== ここから新機能（Focus / No-Phone）のCSS ======== */
    .focus-task-title {{
        font-size: 5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        line-height: 1.2;
    }}
    .focus-task-time {{
        font-size: 2.5rem;
        text-align: center;
        color: rgba(255,255,255,0.7);
        margin-bottom: 40px;
    }}

    .no-phone-bg {{
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, #1e3a8a, #064e3b, #0f172a);
        background-size: 200% 200%;
        animation: GradientAnimation 15s ease infinite;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    
    @keyframes GradientAnimation {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .no-phone-text {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 2.5rem;
        font-weight: 300;
        text-align: center;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
        line-height: 1.4;
    }}
    .no-phone-sub {{
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.2rem;
        margin-top: 30px;
        font-weight: 200;
        letter-spacing: 1px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. セッション状態の初期化 ---
if "remaining" not in st.session_state: st.session_state.remaining = 0
if "task_pool" not in st.session_state:
    st.session_state.task_pool = ["英語", "韓国語", "Duolingo", "メール返信", "課題", "読書", "休む"]
if "history" not in st.session_state: st.session_state.history = []
if "start_datetime" not in st.session_state: st.session_state.start_datetime = datetime.now(JST)

# 新機能: Focus Modeの状態管理
if "active_focus" not in st.session_state: st.session_state.active_focus = None


# --- 3. サイドバー (設定 & タスク管理) ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    bg_upload = st.file_uploader("自分の写真を背景にする", type=["png", "jpg", "jpeg"])
    if bg_upload is not None:
        base64_img = base64.b64encode(bg_upload.read()).decode()
        bg_url = f"data:image/jpeg;base64,{base64_img}"
    else:
        bg_url = st.text_input("Background URL (Webの画像を使う場合)", "https://images.unsplash.com/photo-1538370965046-79c0d6907d47?q=80&w=2069&auto=format&fit=crop")
        
    inject_custom_design(bg_url)

    st.divider()
    st.subheader("Task Master")
    new_t = st.text_input("新しいタスクを追加", placeholder="タスク名を入力...")
    
    if st.button("Add Task") and new_t:
        if new_t not in st.session_state.task_pool:
            st.session_state.task_pool.append(new_t)
            st.success(f"'{new_t}' を追加しました！")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("既に存在します")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Reset Session"):
        st.session_state.remaining = 0
        st.session_state.history = []
        st.session_state.active_focus = None
        st.rerun()

# サイドバー外にも適用
inject_custom_design(bg_url)


# --- 4. メイン UI 構造 ---

# A) 自由時間の初期設定画面
if st.session_state.remaining <= 0 and not st.session_state.history and not st.session_state.active_focus:
    
    st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>Focus Flow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); margin-bottom: 40px;'>あなたの『自由時間』を教えてください。</p>", unsafe_allow_html=True)
    
    col_spacer1, col_center, col_spacer2 = st.columns([1, 2, 1])
    with col_center:
        init_time = st.number_input("確保する時間 (分)", min_value=1, max_value=1440, value=60, step=15)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("スライスを開始する", use_container_width=True):
            st.session_state.remaining = init_time
            st.session_state.start_datetime = datetime.now(JST)
            st.rerun()

# B) Focus Mode (実行中画面 - 新機能)
elif st.session_state.active_focus:
    task_name = st.session_state.active_focus["task"]
    task_mins = st.session_state.active_focus["time"]

    # 「スマホをしまえ」アラートの判定
    no_phone_keywords = ["読書", "本", "音声", "休む", "仮眠"]
    is_no_phone = any(k in task_name for k in no_phone_keywords)

    task_start = st.session_state.active_focus.get("start", datetime.now(JST))
    task_end = task_start + timedelta(minutes=task_mins)
    time_str = f"予定時間: {task_start.strftime('%H:%M')} 〜 {task_end.strftime('%H:%M')}"

    if is_no_phone:
        st.markdown(f"""
        <div class="no-phone-bg">
            <div class="no-phone-text">🌿<br>画面を閉じて、<br>ゆったりと時間を過ごしましょう</div>
            <div class="no-phone-sub">Focusing on: {task_name} ({task_mins} min)<br><span style="font-size:1rem; color:#888;">{time_str}</span></div>
            <br><br>
        </div>
        """, unsafe_allow_html=True)
        # ボタンを押しやすく配置
        st.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
        if st.button("Stop / Mark as Done", use_container_width=True):
            st.session_state.remaining -= task_mins
            if st.session_state.remaining < 0: st.session_state.remaining = 0
            st.session_state.history.append({"task": task_name, "time": task_mins})
            st.session_state.active_focus = None
            st.rerun()
    else:
        st.markdown("<p style='text-align:center; color:#a78bfa;'>現在実行中のタスク</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='focus-task-title'>{task_name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='focus-task-time'>{task_mins} min<br><span style='font-size:1.2rem; color:#888;'>{time_str}</span></div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Complete Task & Next", use_container_width=True):
            st.toast(f"「{task_name}」完了！お疲れ様でした！", icon="🎉")
            st.session_state.remaining -= task_mins
            if st.session_state.remaining < 0: st.session_state.remaining = 0
            st.session_state.history.append({"task": task_name, "time": task_mins})
            st.session_state.active_focus = None
            if st.session_state.remaining == 0:
                st.balloons()
            st.rerun()


# C) スライス画面 (元のメインUI + 新機能のワンタップボタン)
else:
    is_finished = st.session_state.remaining == 0

    if not is_finished:
        # 【Top】Time Box (元のデザインを完全維持)
        st.markdown(f"""
        <div class="time-container">
            <span class="time-value">{st.session_state.remaining}</span>
            <span class="time-unit">min left</span>
        </div>
        """, unsafe_allow_html=True)

        # 【Center】Main Action (元のデザインを完全維持)
        st.markdown("### Next Slice")
        col_a, col_b = st.columns([2, 1])

        with col_a:
            selected_task = st.selectbox("タスクを選択", st.session_state.task_pool)
        with col_b:
            max_val = max(1, st.session_state.remaining)
            slice_m = st.number_input("時間 (分)", min_value=1, max_value=max_val, value=min(15, max_val), step=5)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 新機能: ワンタップボタンを元のUIに自然に組み込む
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([2, 1, 1, 1])
        
        with col_btn1:
            if st.button("この時間をスライスして開始", use_container_width=True):
                if st.session_state.remaining >= slice_m:
                    # すぐに履歴に追加せず、Focus Modeに移行する
                    st.session_state.active_focus = {"task": selected_task, "time": slice_m, "start": datetime.now(JST)}
                    st.rerun()
        
        with col_btn2:
            if st.button("⚡ 5分", use_container_width=True):
                st.session_state.active_focus = {"task": selected_task, "time": 5, "start": datetime.now(JST)}
                st.rerun()
        with col_btn3:
            if st.button("⚡ 10分", use_container_width=True):
                st.session_state.active_focus = {"task": selected_task, "time": 10, "start": datetime.now(JST)}
                st.rerun()
        with col_btn4:
            if st.button("⚡ 15分", use_container_width=True):
                st.session_state.active_focus = {"task": selected_task, "time": 15, "start": datetime.now(JST)}
                st.rerun()

    else:
        # 完了時の表示 (元のデザイン)
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="background: linear-gradient(to right, #34d399, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">All Done!</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8);">すべての自由時間を使い切りました！お疲れ様でした。</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 【Bottom】Unfinished & Logic (元のタブを完全維持 + グラフタブ追加)
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🕒 Pending Tasks", "📅 Schedule", "📊 Analytics"])

    with tab1:
        st.markdown("<p style='margin-bottom: 15px; font-weight: 300;'>プールにある未完了のタスク:</p>", unsafe_allow_html=True)
        tags_html = "".join([f'<div class="task-tag">✨ {t}</div>' for t in st.session_state.task_pool])
        st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

    with tab2:
        if not st.session_state.history:
            st.caption("まだスケジュールはありません。")
        else:
            current_dt = st.session_state.start_datetime
            
            for idx, item in enumerate(st.session_state.history):
                start_str = current_dt.strftime("%H:%M")
                current_dt += timedelta(minutes=item['time'])
                end_str = current_dt.strftime("%H:%M")
                
                html = f"""
                <div class="history-item" style="margin-bottom: 0;">
                    <div style="display: flex; flex-direction: column; width: 100%;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <span style="font-weight: 500; font-size: 1.15rem;">{item['task']}</span>
                            <span style="color: #a78bfa; font-weight: 600;">{item['time']} min</span>
                        </div>
                        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); display: flex; align-items: center;">
                            <span style="background: rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 12px; margin-right: 10px;">🕒 {start_str} - {end_str}</span>
                        </div>
                    </div>
                </div>
                """
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(html, unsafe_allow_html=True)
                with col2:
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.remaining += item['time']
                        st.session_state.history.pop(idx)
                        st.rerun()

    with tab3:
        if not st.session_state.history:
            st.caption("タスクを完了すると、ここにグラフが表示されます。")
        else:
            # 新機能: グラフ表示
            df = pd.DataFrame(st.session_state.history)
            summary_df = df.groupby("task")["time"].sum().reset_index()
            summary_df.set_index("task", inplace=True)
            st.bar_chart(summary_df)
