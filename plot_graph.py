import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
from matplotlib.colors import ListedColormap

# 1. データの読み込み
file_path = "entry_log.csv"
if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        f.write("date,time\n")

df = pd.read_csv(file_path)
df["date"] = pd.to_datetime(df["date"])

# データが空の場合の初期値
weekly_avg = 0
total_days = 0

if not df.empty:
    # 2. 統計情報の計算 (全期間平均)
    first_day = df["date"].min().date()
    today_dt = datetime.datetime.now()
    today = today_dt.date()

    total_days = (today - first_day).days + 1
    total_attendance_days = df["date"].dt.date.nunique()
    weekly_avg = round((total_attendance_days / total_days) * 7, 1)

    # 3. GitHub風カレンダーグラフの作成 (直近30日)
    num_days = 35  # 5週間分くらい表示するときれい
    date_range = pd.date_range(end=today_dt, periods=num_days)
    attendance = [1 if d.date() in df["date"].dt.date.values else 0 for d in date_range]

    # 行列(7行×N週)の作成
    # 曜日は 0=月, 6=日
    weekdays = [d.weekday() for d in date_range]
    # 週番号のオフセットを計算
    base_week = date_range[0].isocalendar()[1]
    weeks = [d.isocalendar()[1] - base_week for d in date_range]

    # データの流し込み (-1:枠外, 0:欠席, 1:出席)
    heatmap_data = np.full((7, max(weeks) + 1), -1.0)
    for w, wd, a in zip(weeks, weekdays, attendance):
        heatmap_data[wd, w] = a

    # 3. 描画設定
    fig, ax = plt.subplots(figsize=(10, 3))
    cmap = ListedColormap(["#ffffff", "#ebedf0", "#216e39"])  # 背景, 欠席, 出席

    # 描画 (edgecolorを削除した修正版)
    im = ax.imshow(heatmap_data, cmap=cmap, aspect="equal")

    # マス目の境界線（白いグリッド）を引く
    ax.set_xticks(np.arange(-0.5, heatmap_data.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 7, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2)

    # --- 月のラベルを下側に追加 ---
    month_labels = []
    month_locs = []
    for i, d in enumerate(date_range):
        # 月が変わるタイミング、またはデータの開始地点でラベルを作成
        if d.day == 1 or i == 0:
            month_name = d.strftime("%b")
            # その日が「その週の何番目か」を考慮して、X軸の週インデックスを取得
            w_idx = weeks[i]
            if month_name not in month_labels:
                month_labels.append(month_name)
                month_locs.append(w_idx)

    ax.set_xticks(month_locs)
    ax.set_xticklabels(month_labels, fontsize=9, color="#586069")
    # ------------------------------

    # 縦軸（曜日）の設定
    ax.set_yticks([0, 2, 4, 6])
    ax.set_yticklabels(["Mon", "Wed", "Fri", "Sun"], fontsize=8, color="#586069")

    # 枠線や余計な線を消す
    ax.tick_params(which="both", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.title(f"Last {num_days} Days Activity", fontsize=11, pad=10)
    plt.savefig("monthly_report.png", bbox_inches="tight", dpi=120)
    plt.close()

# 4. README.md の更新
last_update = datetime.datetime.now().strftime("%Y-%m-%d")
readme_text = f"""# 🏃 平均週 {weekly_avg} 回でつーがく中！
<p align="center">
  <img src="./monthly_report.png" alt="Attendance Calendar">
</p>

___
*最終更新: {last_update}*
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_text)
