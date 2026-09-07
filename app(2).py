
import os
import time
import math
import random
from dataclasses import dataclass

import numpy as np
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

st.set_page_config(page_title="교내 유휴공간 학생 분포 시뮬레이션", page_icon="🏫", layout="wide")

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
DEFAULT_MAP = "school_map.png"
IMG_W, IMG_H = 1222, 1374

# 제공된 학교 안내도의 대략적인 좌표(픽셀).
# 실제 건축도면의 정밀 좌표가 아니며, 발표용 시뮬레이션을 위한 초기값입니다.
FLOORS = {
    "1F": {"ymin": 1010, "ymax": 1360, "xmin": 130, "xmax": 1120},
    "2F": {"ymin": 560, "ymax": 950, "xmin": 130, "xmax": 1120},
    "3F": {"ymin": 175, "ymax": 540, "xmin": 130, "xmax": 1120},
}

# 공간 중심점. 필요하면 좌표를 조금씩 수정하면 됩니다.
ROOMS = {
    "1F": [
        ("101 1-1", 1080, 1160, 1.00),
        ("102 1-2", 905, 1160, 1.00),
        ("103 1-3", 820, 1160, 1.00),
        ("104 1-4", 740, 1160, 1.00),
        ("105 도서정보홈베이스", 520, 1160, 1.15),
        ("106 보건실", 285, 1160, 0.55),
        ("108 온라인학습실1", 185, 1195, 0.85),
        ("109 AI정보교육실", 185, 1050, 0.75),
        ("110 지능형스마트영어실", 510, 1030, 0.85),
        ("현관", 960, 1080, 0.80),
        ("1F 복도", 650, 1110, 1.25),
    ],
    "2F": [
        ("201 과학실", 1080, 795, 0.85),
        ("203 2-1", 975, 790, 1.00),
        ("204 2-2", 875, 790, 1.00),
        ("205 교무센터", 790, 790, 0.65),
        ("206 교장실", 700, 790, 0.60),
        ("207 2층교사연구실", 610, 790, 0.65),
        ("208 회의실", 530, 790, 0.65),
        ("209 2-3", 440, 790, 1.00),
        ("210 2-4", 365, 790, 1.00),
        ("211 휴게실", 320, 805, 0.80),
        ("212 홈베이스", 250, 790, 0.90),
        ("213 진로실", 190, 640, 0.65),
        ("215 온라인학습실2", 190, 860, 0.85),
        ("214 스팀실", 510, 615, 0.85),
        ("2F 복도", 650, 760, 1.20),
    ],
    "3F": [
        ("301 Wee클래스", 1080, 420, 0.75),
        ("302 온라인스튜디오", 1005, 420, 0.75),
        ("303 온라인스튜디오", 930, 420, 0.70),
        ("304 3-1", 850, 420, 1.00),
        ("305 3-2", 760, 420, 1.00),
        ("306 3층교사연구실", 675, 420, 0.60),
        ("307 3-3", 595, 420, 1.00),
        ("308 3-4", 505, 420, 1.00),
        ("309 융합실", 430, 420, 0.70),
        ("310 서버실", 365, 420, 0.55),
        ("311 홈베이스", 275, 420, 0.95),
        ("312 가온홀", 190, 420, 0.90),
        ("313 컴퓨팅랩", 470, 255, 0.70),
        ("314 인공지능실", 570, 255, 0.70),
        ("315 창의융합인문사회실", 220, 430, 0.70),
        ("3F 복도", 650, 395, 1.20),
    ],
}

# 유휴공간 후보: 발표용 가상 시나리오.
IDLE_OPTIONS = {
    "2F-215": ("2F", "215 온라인학습실2", 190, 860),
    "2F-213": ("2F", "213 진로실", 190, 640),
    "3F-312": ("3F", "312 가온홀", 190, 420),
    "1F-108": ("1F", "108 온라인학습실1", 185, 1195),
}

TIME_PROFILES = {
    "점심시간": {
        "1F": {"급식/현관": 0.20, "교실": 0.35, "홈베이스/복도": 0.30, "기타": 0.15},
        "2F": {"교실": 0.45, "홈베이스/복도": 0.35, "기타": 0.20},
        "3F": {"교실": 0.45, "홈베이스/복도": 0.35, "기타": 0.20},
    },
    "저녁시간": {
        "1F": {"급식/현관": 0.15, "교실": 0.35, "홈베이스/복도": 0.30, "기타": 0.20},
        "2F": {"교실": 0.40, "홈베이스/복도": 0.35, "기타": 0.25},
        "3F": {"교실": 0.40, "홈베이스/복도": 0.35, "기타": 0.25},
    },
    "아침 자투리시간": {
        "1F": {"급식/현관": 0.25, "교실": 0.40, "홈베이스/복도": 0.25, "기타": 0.10},
        "2F": {"교실": 0.50, "홈베이스/복도": 0.30, "기타": 0.20},
        "3F": {"교실": 0.50, "홈베이스/복도": 0.30, "기타": 0.20},
    },
}

def load_map():
    if os.path.exists(DEFAULT_MAP):
        return Image.open(DEFAULT_MAP).convert("RGB")
    return None

def room_candidates(floor, category):
    rooms = ROOMS[floor]
    if category == "교실":
        r = [x for x in rooms if any(k in x[0] for k in ["1-", "2-", "3-"])]
    elif category == "홈베이스/복도":
        r = [x for x in rooms if any(k in x[0] for k in ["홈베이스", "복도", "휴게실"])]
    elif category == "급식/현관":
        r = [x for x in rooms if any(k in x[0] for k in ["현관", "도서정보"])]
    else:
        r = [x for x in rooms if not any(k in x[0] for k in ["복도", "교사연구실", "서버실", "교무센터", "교장실"])]
    return r if r else rooms

def choose_target(floor, profile, after=False, idle_key="2F-215", preference=0.55):
    cats = list(profile.keys())
    probs = np.array(list(profile.values()), dtype=float)
    probs = probs / probs.sum()

    # AFTER에서는 선택된 유휴공간으로 일정 비율의 학생을 유도
    if after and random.random() < preference:
        f, name, x, y = IDLE_OPTIONS[idle_key]
        if f == floor:
            jitter = np.random.normal(0, [30, 18])
            return np.array([x + jitter[0], y + jitter[1]], dtype=float), name

    cat = random.choices(cats, weights=probs, k=1)[0]
    candidates = room_candidates(floor, cat)
    weights = np.array([max(c[3], 0.1) for c in candidates], dtype=float)
    weights /= weights.sum()
    r = candidates[np.random.choice(len(candidates), p=weights)]
    jitter = np.random.normal(0, [35, 20])
    return np.array([r[1] + jitter[0], r[2] + jitter[1]], dtype=float), r[0]

def generate_agents(n, time_name, after, idle_key, idle_share, seed=42):
    rng = np.random.default_rng(seed)
    random.seed(seed)
    agents = []

    floor_probs = [0.34, 0.33, 0.33]
    floors = rng.choice(["1F", "2F", "3F"], size=n, p=floor_probs)

    for i, floor in enumerate(floors):
        profile = TIME_PROFILES[time_name][floor]
        # 시작 위치는 해당 층의 공간 중 임의 위치
        start, _ = choose_target(floor, profile, after=False)
        target, target_name = choose_target(
            floor, profile, after=after, idle_key=idle_key, preference=idle_share
        )
        agents.append({
            "id": i,
            "floor": floor,
            "pos": start.astype(float),
            "target": target.astype(float),
            "target_name": target_name,
            "speed": rng.uniform(3.0, 6.0),
            "history": [start.copy()],
        })
    return agents

def step_agents(agents, time_name, after, idle_key, idle_share):
    for a in agents:
        pos = a["pos"]
        target = a["target"]
        vec = target - pos
        dist = np.linalg.norm(vec)
        if dist < 8:
            new_target, name = choose_target(
                a["floor"], TIME_PROFILES[time_name][a["floor"]],
                after=after, idle_key=idle_key, preference=idle_share
            )
            a["target"] = new_target
            a["target_name"] = name
            vec = new_target - pos
            dist = np.linalg.norm(vec)

        if dist > 0:
            # 약간의 랜덤성을 섞은 이동
            direction = vec / dist
            noise = np.random.normal(0, 0.25, size=2)
            direction = direction + noise
            direction = direction / max(np.linalg.norm(direction), 1e-6)
            a["pos"] += direction * a["speed"]

        box = FLOORS[a["floor"]]
        a["pos"][0] = np.clip(a["pos"][0], box["xmin"], box["xmax"])
        a["pos"][1] = np.clip(a["pos"][1], box["ymin"], box["ymax"])
        a["history"].append(a["pos"].copy())

def density_from_agents(agents, bins=90):
    if not agents:
        return np.zeros((bins, bins))
    xs = np.array([a["pos"][0] for a in agents])
    ys = np.array([a["pos"][1] for a in agents])
    H, _, _ = np.histogram2d(
        ys, xs, bins=[bins, bins], range=[[0, IMG_H], [0, IMG_W]]
    )
    # 간단한 box smoothing
    for _ in range(2):
        H = (
            H
            + np.roll(H, 1, 0) + np.roll(H, -1, 0)
            + np.roll(H, 1, 1) + np.roll(H, -1, 1)
        ) / 5.0
    return H

def draw_scene(base_img, agents, title, after=False, idle_key="2F-215", show_heat=True, show_agents=True):
    fig, ax = plt.subplots(figsize=(10, 11))
    ax.imshow(base_img, extent=[0, IMG_W, IMG_H, 0])

    if show_heat:
        H = density_from_agents(agents)
        if H.max() > 0:
            ax.imshow(
                H,
                extent=[0, IMG_W, IMG_H, 0],
                origin="upper",
                interpolation="bilinear",
                alpha=0.36,
                cmap="turbo",
                vmin=0,
                vmax=max(1, np.percentile(H, 99)),
            )

    if show_agents:
        xs = [a["pos"][0] for a in agents]
        ys = [a["pos"][1] for a in agents]
        ax.scatter(xs, ys, s=8, alpha=0.72, edgecolors="none")

    # 선택된 유휴공간 표시
    if after:
        f, name, x, y = IDLE_OPTIONS[idle_key]
        rect = Rectangle((x - 70, y - 50), 140, 100, fill=False, linewidth=2.5)
        ax.add_patch(rect)
        ax.text(
            x, y - 62, f"★ AFTER: {name}",
            ha="center", va="bottom", fontsize=9, fontweight="bold"
        )

    ax.set_xlim(0, IMG_W)
    ax.set_ylim(IMG_H, 0)
    ax.axis("off")
    ax.set_title(title, fontsize=16, fontweight="bold")
    plt.tight_layout(pad=0.5)
    return fig

def summarize(agents):
    counts = {}
    for a in agents:
        key = a["target_name"]
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:8])

# ------------------------------------------------------------
# UI
# ------------------------------------------------------------
st.title("🏫 교내 유휴공간 학생 분포 시뮬레이션")
st.caption("학교 안내도를 기반으로 한 발표용 프로토타입 — 실제 인터뷰/설문 결과를 입력하면 모델을 교체할 수 있습니다.")

base_img = load_map()
if base_img is None:
    st.error("school_map.png를 app.py와 같은 폴더에 넣어주세요.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 시뮬레이션 설정")
    n_students = st.slider("가상 학생 수", 50, 600, 300, 10)
    time_name = st.selectbox("시간대", list(TIME_PROFILES.keys()), index=0)
    idle_key = st.selectbox(
        "유휴공간 조성 후보",
        list(IDLE_OPTIONS.keys()),
        format_func=lambda k: f"{k} — {IDLE_OPTIONS[k][1]}"
    )
    idle_share = st.slider(
        "AFTER에서 새 공간으로 유도되는 비율",
        0.0, 1.0, 0.55, 0.05,
        help="현재는 가상값입니다. 설문 결과에 따라 조정하세요."
    )
    steps = st.slider("애니메이션 프레임", 20, 140, 70, 10)
    delay = st.slider("프레임 간격(초)", 0.01, 0.15, 0.04, 0.01)
    show_heat = st.checkbox("히트맵 표시", True)
    show_agents = st.checkbox("학생 점 표시", True)

    st.divider()
    st.info(
        "⚠️ 현재 버전의 학생 비율과 이동 규칙은 시각화용 가정입니다. "
        "실제 인터뷰·설문 결과를 얻으면 TIME_PROFILES와 공간별 비율을 실제 값으로 교체하세요."
    )

col1, col2 = st.columns(2)

# 초기 상태 생성
if "before_agents" not in st.session_state or st.session_state.get("n") != n_students or st.session_state.get("time") != time_name:
    st.session_state.before_agents = generate_agents(n_students, time_name, False, idle_key, idle_share, seed=10)
    st.session_state.after_agents = generate_agents(n_students, time_name, True, idle_key, idle_share, seed=20)
    st.session_state.n = n_students
    st.session_state.time = time_name

with col1:
    st.subheader("🔴 BEFORE — 유휴공간 조성 전")
    fig = draw_scene(
        base_img, st.session_state.before_agents,
        f"현재 학생 분포 · {time_name}",
        after=False, show_heat=show_heat, show_agents=show_agents
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col2:
    st.subheader("🟢 AFTER — 유휴공간 조성 후")
    fig = draw_scene(
        base_img, st.session_state.after_agents,
        f"유휴공간 조성 후 · {time_name}",
        after=True, idle_key=idle_key,
        show_heat=show_heat, show_agents=show_agents
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

b1, b2, b3 = st.columns(3)
with b1:
    if st.button("▶ 학생 이동 시뮬레이션 시작", use_container_width=True):
        before_slot = st.empty()
        after_slot = st.empty()

        before_agents = generate_agents(n_students, time_name, False, idle_key, idle_share, seed=10)
        after_agents = generate_agents(n_students, time_name, True, idle_key, idle_share, seed=20)

        for frame in range(steps):
            step_agents(before_agents, time_name, False, idle_key, idle_share)
            step_agents(after_agents, time_name, True, idle_key, idle_share)

            with before_slot.container():
                fig = draw_scene(
                    base_img, before_agents,
                    f"BEFORE · {time_name} · {frame+1}/{steps}",
                    after=False, show_heat=show_heat, show_agents=show_agents
                )
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            with after_slot.container():
                fig = draw_scene(
                    base_img, after_agents,
                    f"AFTER · {time_name} · {frame+1}/{steps}",
                    after=True, idle_key=idle_key,
                    show_heat=show_heat, show_agents=show_agents
                )
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            time.sleep(delay)

        st.session_state.before_agents = before_agents
        st.session_state.after_agents = after_agents
        st.success("시뮬레이션이 완료되었습니다.")

with b2:
    if st.button("🔄 새로운 학생 배치 생성", use_container_width=True):
        st.session_state.before_agents = generate_agents(n_students, time_name, False, idle_key, idle_share, seed=random.randint(1, 999999))
        st.session_state.after_agents = generate_agents(n_students, time_name, True, idle_key, idle_share, seed=random.randint(1, 999999))
        st.rerun()

with b3:
    if st.button("📊 결과 요약 보기", use_container_width=True):
        st.session_state["show_summary"] = True

if st.session_state.get("show_summary", False):
    st.header("📊 현재 시뮬레이션의 공간별 체류/목표 분포")
    s1, s2 = st.columns(2)

    before_summary = summarize(st.session_state.before_agents)
    after_summary = summarize(st.session_state.after_agents)

    with s1:
        st.markdown("### BEFORE")
        for k, v in before_summary.items():
            st.write(f"**{k}** — {v}명 ({v/n_students*100:.1f}%)")

    with s2:
        st.markdown("### AFTER")
        for k, v in after_summary.items():
            st.write(f"**{k}** — {v}명 ({v/n_students*100:.1f}%)")

    # 발표용 간단한 밀집도 지표
    before_H = density_from_agents(st.session_state.before_agents)
    after_H = density_from_agents(st.session_state.after_agents)

    c1, c2, c3 = st.columns(3)
    c1.metric("BEFORE 최대 셀 밀집도", f"{before_H.max():.1f}")
    c2.metric("AFTER 최대 셀 밀집도", f"{after_H.max():.1f}")
    reduction = (1 - after_H.max() / max(before_H.max(), 1e-9)) * 100
    c3.metric("최대 밀집도 변화", f"{reduction:+.1f}%")

st.divider()
st.caption(
    "연구 활용 팁: 인터뷰 24명의 실제 응답을 확보한 뒤 시간대·학년·공간별 비율을 정리하여 "
    "TIME_PROFILES와 room_candidates의 가중치로 반영하면 '조사 → 모델링 → BEFORE/AFTER 검증' 구조가 됩니다."
)
