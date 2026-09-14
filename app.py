import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import time


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="School Space Flow",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# DESIGN
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(210,225,255,0.55),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(255,230,210,0.45),
            transparent 28%
        ),
        #f5f7fb;
}

.block-container {
    max-width: 1500px;
    padding-top: 35px;
    padding-bottom: 50px;
}

/* HEADER */

.hero {
    background: rgba(255,255,255,0.86);
    border: 1px solid rgba(220,225,235,0.9);
    border-radius: 28px;
    padding: 28px 34px;
    box-shadow: 0 15px 45px rgba(30,50,80,0.07);
    margin-bottom: 25px;
}

.hero-title {
    font-size: 42px;
    font-weight: 850;
    letter-spacing: -2px;
    color: #172033;
}

.hero-sub {
    color: #718096;
    font-size: 15px;
    margin-top: 5px;
}

/* TIME */

.time-card {
    background: white;
    border-radius: 22px;
    padding: 20px 24px;
    border: 1px solid #e4e8ef;
    box-shadow: 0 8px 25px rgba(30,50,80,0.05);
}

/* STAT */

.stat {
    background: rgba(255,255,255,0.9);
    border: 1px solid #e4e8ef;
    border-radius: 20px;
    padding: 18px 20px;
    height: 110px;
}

.stat-label {
    font-size: 13px;
    color: #8792a3;
}

.stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #172033;
    margin-top: 5px;
}

/* SECTION */

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #172033;
    margin-top: 30px;
}

.section-sub {
    color: #7b8798;
    font-size: 14px;
    margin-bottom: 15px;
}

/* BUTTON */

.stButton > button {
    border-radius: 14px;
    border: 1px solid #d9e0ea;
    font-weight: 700;
    min-height: 45px;
}

/* INFO */

.info-box {
    background: rgba(255,255,255,0.75);
    border: 1px solid #e1e6ee;
    border-radius: 18px;
    padding: 18px;
    color: #667085;
    font-size: 13px;
    line-height: 1.65;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

    <div class="hero-title">
        🏫 SCHOOL SPACE FLOW
    </div>

    <div class="hero-sub">
        교내 자투리 시간 학생 공간 분포 · 3D Heatmap Simulation
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# ROOM DATA
#
# x, y = 학교 평면상의 위치
# w, d = 방 크기
# floor = 층
# type = 공간 종류
# =========================================================

ROOMS = {

1: [
    ("101", "1-1", 1, 1, 3, 3, "class"),
    ("102", "1-2", 4.5, 1, 3, 3, "class"),
    ("103", "1-3", 8, 1, 3, 3, "class"),
    ("104", "1-4", 11.5, 1, 3, 3, "class"),

    ("105", "도서정보 홈베이스", 1, 5, 5, 2.5, "common"),
    ("106", "보건실", 7, 5, 3, 2.5, "support"),
    ("107", "교사 연구실", 11, 5, 3.5, 2.5, "staff"),

    ("108", "온라인 학습실1", 1, 8.2, 4, 2.5, "common"),
    ("109", "AI 정보 교육실", 5.7, 8.2, 4, 2.5, "special"),
    ("110", "스마트 영어실", 10.4, 8.2, 4, 2.5, "special"),
],

2: [
    ("201", "과학실", 1, 1, 4, 3, "special"),
    ("202", "연구실", 5.5, 1, 2.5, 3, "support"),

    ("203", "2-1", 8.5, 1, 3, 3, "class"),
    ("204", "2-2", 12, 1, 3, 3, "class"),

    ("205", "교무센터", 15.5, 1, 3, 3, "support"),
    ("206", "교장실", 19, 1, 3, 3, "support"),

    ("207", "교사 연구실", 1, 5, 4, 2.5, "staff"),
    ("208", "회의실", 5.5, 5, 3, 2.5, "support"),

    ("209", "2-3", 9, 5, 3, 2.5, "class"),
    ("210", "2-4", 12.5, 5, 3, 2.5, "class"),

    ("211", "휴게실", 16, 5, 3, 2.5, "common"),
    ("212", "홈베이스", 19.5, 5, 3, 2.5, "common"),

    ("213", "진로실", 1, 8.2, 4, 2.5, "common"),
    ("214", "스팀실", 5.7, 8.2, 4, 2.5, "special"),
    ("215", "온라인 학습실2", 10.4, 8.2, 4, 2.5, "common"),
],

3: [
    ("301", "Wee클래스", 1, 1, 4, 3, "support"),
    ("302", "온라인 스튜디오", 5.5, 1, 2.5, 3, "special"),
    ("303", "온라인 스튜디오", 8.5, 1, 2.5, 3, "special"),

    ("304", "3-1", 11.5, 1, 3, 3, "class"),
    ("305", "3-2", 15, 1, 3, 3, "class"),

    ("306", "교사 연구실", 18.5, 1, 3, 3, "staff"),

    ("307", "3-3", 1, 5, 3, 2.5, "class"),
    ("308", "3-4", 4.5, 5, 3, 2.5, "class"),

    ("309", "융합실", 8, 5, 3, 2.5, "special"),
    ("310", "서버실", 11.5, 5, 3, 2.5, "support"),

    ("311", "홈베이스", 15, 5, 3, 2.5, "common"),

    ("312", "가온홀", 1, 8.2, 4, 2.5, "event"),
    ("313", "컴퓨팅랩", 5.7, 8.2, 4, 2.5, "special"),
    ("314", "인공지능실", 10.4, 8.2, 4, 2.5, "special"),
    ("315", "창의융합 인문사회실", 15.1, 8.2, 4, 2.5, "special"),
]
}


# =========================================================
# TIME PROFILES
#
# 나중에 실제 인터뷰 / 설문 결과로 교체
# =========================================================

TIME_PROFILES = {

    "🌅 아침": {

        "class": 0.35,
        "common": 1.40,
        "special": 0.65,
        "event": 0.35,
        "support": 0.20,
        "staff": 0.05

    },

    "☀️ 점심": {

        "class": 0.20,
        "common": 1.80,
        "special": 1.00,
        "event": 2.20,
        "support": 0.10,
        "staff": 0.02

    },

    "🌙 저녁": {

        "class": 0.35,
        "common": 1.65,
        "special": 1.35,
        "event": 1.80,
        "support": 0.10,
        "staff": 0.02

    }
}


# 층별 이동량

FLOOR_WEIGHT = {

    "🌅 아침": {
        1: 1.25,
        2: 0.95,
        3: 0.80
    },

    "☀️ 점심": {
        1: 1.05,
        2: 1.00,
        3: 1.35
    },

    "🌙 저녁": {
        1: 0.85,
        2: 1.00,
        3: 1.35
    }
}


# =========================================================
# ROOM CENTER
# =========================================================

def get_center(room):

    room_id, name, x, y, w, d, room_type = room

    return (
        x + w / 2,
        y + d / 2
    )


# =========================================================
# DISTRIBUTION
# =========================================================

def calculate_distribution(time_name):

    profile = TIME_PROFILES[time_name]

    floor_weight = FLOOR_WEIGHT[time_name]

    values = {}

    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            room_id = room[0]

            room_type = room[6]

            x = room[2]
            y = room[3]
            w = room[4]
            d = room[5]

            base = profile.get(
                room_type,
                0.2
            )

            area_factor = (
                0.75 +
                min(
                    (w * d) / 14,
                    1.0
                )
            )

            value = (
                base *
                area_factor *
                floor_weight[floor]
            )

            values[
                (floor, room_id)
            ] = value

    total = sum(values.values())

    if total == 0:
        return values

    for key in values:

        values[key] /= total

    return values


# =========================================================
# COLOR
# =========================================================

def heat_color(value):

    # value를 0~1로 변환
    intensity = min(
        value * 28,
        1
    )

    if intensity < 0.25:

        return "#5B8FF9"

    elif intensity < 0.50:

        return "#56C596"

    elif intensity < 0.75:

        return "#F6C85F"

    else:

        return "#F45B69"


# =========================================================
# 3D ROOM BOX
# =========================================================

def add_room_box(
    fig,
    floor,
    room,
    probability
):

    room_id = room[0]
    name = room[1]

    x = room[2]
    y = room[3]

    w = room[4]
    d = room[5]

    # 층 간격
    z = (floor - 1) * 4

    height = 1.2

    color = heat_color(
        probability
    )

    # 8개 꼭짓점

    xs = [
        x, x+w, x+w, x,
        x, x+w, x+w, x
    ]

    ys = [
        y, y, y+d, y+d,
        y, y, y+d, y+d
    ]

    zs = [
        z, z, z, z,
        z+height,
        z+height,
        z+height,
        z+height
    ]

    # 박스 면

    i = [
        0, 0,
        4, 4,
        0, 0,
        1, 1,
        2, 2,
        3, 3
    ]

    j = [
        1, 2,
        5, 6,
        1, 4,
        2, 5,
        3, 6,
        0, 7
    ]

    k = [
        2, 3,
        6, 7,
        4, 5,
        5, 6,
        7, 7,
        4, 4
    ]

    students = probability * 300

    fig.add_trace(
        go.Mesh3d(

            x=xs,
            y=ys,
            z=zs,

            i=i,
            j=j,
            k=k,

            color=color,

            opacity=0.82,

            flatshading=True,

            hovertemplate=(
                f"<b>{floor}층 "
                f"{room_id}</b><br>"
                f"{name}<br>"
                f"예상 분포 : "
                f"{probability*100:.1f}%<br>"
                f"예상 학생 : "
                f"{students:.0f}명"
                "<extra></extra>"
            ),

            showscale=False,

            name=f"{floor}F {room_id}"
        )
    )


# =========================================================
# FLOOR BASE
# =========================================================

def add_floor_base(
    fig,
    floor
):

    z = (floor - 1) * 4

    fig.add_trace(
        go.Mesh3d(

            x=[
                0, 24, 24, 0
            ],

            y=[
                0, 0, 12, 12
            ],

            z=[
                z, z, z, z
            ],

            i=[0],
            j=[1],
            k=[2],

            color="#E9EEF5",

            opacity=0.20,

            showscale=False,

            hoverinfo="skip",

            name=f"{floor}층 바닥"
        )
    )


# =========================================================
# 3D SCHOOL
# =========================================================

def create_school_3d(
    distribution
):

    fig = go.Figure()

    # 바닥
    for floor in [1, 2, 3]:

        add_floor_base(
            fig,
            floor
        )

    # 방
    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            probability = distribution.get(
                (
                    floor,
                    room[0]
                ),
                0
            )

            add_room_box(
                fig,
                floor,
                room,
                probability
            )

    # 층 표시

    for floor in [1, 2, 3]:

        z = (floor - 1) * 4

        fig.add_trace(
            go.Scatter3d(

                x=[-1],

                y=[0],

                z=[z + 0.5],

                mode="text",

                text=[
                    f"{floor}F"
                ],

                textfont=dict(
                    size=18,
                    color="#334155"
                ),

                showlegend=False
            )
        )

    fig.update_layout(

        height=680,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        scene=dict(

            bgcolor="rgba(0,0,0,0)",

            xaxis=dict(
                visible=False
            ),

            yaxis=dict(
                visible=False
            ),

            zaxis=dict(
                visible=False
            ),

            camera=dict(
                eye=dict(
                    x=1.65,
                    y=1.65,
                    z=1.35
                )
            ),

            aspectmode="manual",

            aspectratio=dict(
                x=2.0,
                y=1.0,
                z=1.35
            )
        ),

        showlegend=False
    )

    return fig


# =========================================================
# SIMULATION PATH
# =========================================================

def create_destinations(
    time_name,
    distribution
):

    destinations = []

    sorted_rooms = sorted(
        distribution.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # 상위 공간만 목적지로 사용
    selected = sorted_rooms[:10]

    for (
        (floor, room_id),
        probability
    ) in selected:

        room = next(
            (
                r
                for r in ROOMS[floor]
                if r[0] == room_id
            ),
            None
        )

        if room is None:
            continue

        cx, cy = get_center(
            room
        )

        z = (
            (floor - 1) * 4
            + 1.7
        )

        destinations.append(
            (
                cx,
                cy,
                z
            )
        )

    return destinations


# =========================================================
# MOVING STUDENTS
# =========================================================

def make_students(
    time_name,
    distribution,
    number=80,
    seed=42
):

    rng = np.random.default_rng(
        seed
    )

    destinations = create_destinations(
        time_name,
        distribution
    )

    if not destinations:

        return np.zeros(
            (number, 3)
        )

    # 시작 위치
    positions = []

    for i in range(number):

        floor = rng.choice(
            [1, 2, 3],
            p=[
                0.35,
                0.32,
                0.33
            ]
        )

        x = rng.uniform(
            2,
            21
        )

        y = rng.uniform(
            2,
            10
        )

        z = (
            (floor - 1) * 4
            + 1.6
        )

        positions.append(
            [
                x,
                y,
                z
            ]
        )

    return np.array(
        positions
    )


def simulate_frame(
    start_positions,
    destinations,
    progress,
    rng
):

    positions = (
        start_positions.copy()
    )

    if len(destinations) == 0:

        return positions

    for i in range(
        len(positions)
    ):

        target = destinations[
            rng.integers(
                0,
                len(destinations)
            )
        ]

        # 부드러운 이동
        p = min(
            max(
                progress,
                0
            ),
            1
        )

        # 약간의 랜덤성을 추가
        noise = (
            rng.normal(
                0,
                0.12,
                3
            )
            *
            np.sin(
                p * np.pi
            )
        )

        positions[i] = (
            start_positions[i]
            * (1-p)
            +
            np.array(target)
            * p
            +
            noise
        )

    return positions


# =========================================================
# TIME SELECT
# =========================================================

st.markdown(
    '<div class="section-title">'
    '⏱ 시간대 선택'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-sub">'
    '시간대에 따라 학생들이 향하는 공간과 밀집도가 달라집니다.'
    '</div>',
    unsafe_allow_html=True
)


selected_time = st.radio(

    "시간대",

    [
        "🌅 아침",
        "☀️ 점심",
        "🌙 저녁"
    ],

    horizontal=True,

    label_visibility="collapsed"
)


# =========================================================
# DISTRIBUTION
# =========================================================

distribution = calculate_distribution(
    selected_time
)


floor_distribution = {}

for floor in [1, 2, 3]:

    floor_distribution[floor] = sum(

        value

        for (
            (f, room_id),
            value
        )

        in distribution.items()

        if f == floor
    )


# =========================================================
# STATS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

cols = st.columns(4)

highest_floor = max(
    floor_distribution,
    key=floor_distribution.get
)

highest_value = (
    floor_distribution[
        highest_floor
    ] * 100
)

with cols[0]:

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-label">
                선택 시간
            </div>
            <div class="stat-value">
                {selected_time}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with cols[1]:

    st.markdown(
        """
        <div class="stat">
            <div class="stat-label">
                시뮬레이션 학생
            </div>
            <div class="stat-value">
                300명
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with cols[2]:

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-label">
                가장 높은 층
            </div>
            <div class="stat-value">
                {highest_floor}층
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with cols[3]:

    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-label">
                최고 층 분포
            </div>
            <div class="stat-value">
                {highest_value:.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# MAIN 3D AREA
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🧊 3D 학생 분포 Heatmap'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-sub">'
    '색이 진할수록 해당 공간에 학생이 많이 모일 것으로 예상됩니다. '
    '3D 모델을 드래그하여 원하는 방향에서 볼 수 있습니다.'
    '</div>',
    unsafe_allow_html=True
)


# 세션 상태

if "simulation_running" not in st.session_state:

    st.session_state.simulation_running = False


if "simulation_progress" not in st.session_state:

    st.session_state.simulation_progress = 0


# =========================================================
# CONTROL
# =========================================================

control1, control2, control3 = st.columns(
    [1, 1, 2]
)

with control1:

    start_button = st.button(
        "▶ 시뮬레이션 시작",
        use_container_width=True
    )

with control2:

    reset_button = st.button(
        "↻ 초기화",
        use_container_width=True
    )

with control3:

    speed = st.slider(
        "시뮬레이션 속도",
        min_value=1,
        max_value=10,
        value=5
    )


if reset_button:

    st.session_state.simulation_running = False

    st.session_state.simulation_progress = 0

    st.rerun()


if start_button:

    st.session_state.simulation_running = True

    st.session_state.simulation_progress = 0


# =========================================================
# INITIAL 3D
# =========================================================

chart_placeholder = st.empty()


# =========================================================
# NORMAL VIEW
# =========================================================

if not st.session_state.simulation_running:

    fig = create_school_3d(
        distribution
    )

    chart_placeholder.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True
        }
    )


# =========================================================
# SIMULATION
# =========================================================

else:

    number_students = 80

    rng = np.random.default_rng(
        123
    )

    start_positions = make_students(
        selected_time,
        distribution,
        number_students,
        seed=123
    )

    destinations = create_destinations(
        selected_time,
        distribution
    )

    # 0 → 1
    for frame in range(
        0,
        101,
        2
    ):

        progress = frame / 100

        positions = simulate_frame(
            start_positions,
            destinations,
            progress,
            rng
        )

        fig = create_school_3d(
            distribution
        )

        # 학생
        fig.add_trace(
            go.Scatter3d(

                x=positions[:, 0],

                y=positions[:, 1],

                z=positions[:, 2],

                mode="markers",

                marker=dict(

                    size=5,

                    color="#263B63",

                    opacity=0.90
                ),

                name="학생",

                hovertemplate=
                    "학생<extra></extra>"
            )
        )

        fig.update_layout(
            title=dict(
                text=(
                    f"{selected_time} · "
                    f"학생 이동 "
                    f"{frame}%"
                ),
                x=0.03,
                y=0.97,
                font=dict(
                    size=20
                )
            )
        )

        chart_placeholder.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True
            }
        )

        time.sleep(
            max(
                0.015,
                0.11 -
                speed * 0.009
            )
        )

    st.session_state.simulation_running = False

    st.session_state.simulation_progress = 100

    st.success(
        f"{selected_time} 학생 분포 시뮬레이션이 완료되었습니다."
    )


# =========================================================
# LEGEND
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="info-box">

    <b>🔥 Heatmap 범례</b><br><br>

    🔵 낮은 학생 밀집도 &nbsp;&nbsp;
    🟢 낮음~중간 &nbsp;&nbsp;
    🟡 높은 편 &nbsp;&nbsp;
    🔴 높은 학생 밀집도

    <br><br>

    <b>3D 모델:</b>
    각 공간의 높이는 학교 층을 나타내며,
    공간의 색은 해당 시간대의 예상 학생 분포를 나타냅니다.

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FLOOR DISTRIBUTION
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📊 층별 예상 분포'
    '</div>',
    unsafe_allow_html=True
)

floor_df = pd.DataFrame({

    "층": [
        "1층",
        "2층",
        "3층"
    ],

    "예상 학생 분포 (%)": [

        round(
            floor_distribution[1] * 100,
            1
        ),

        round(
            floor_distribution[2] * 100,
            1
        ),

        round(
            floor_distribution[3] * 100,
            1
        )
    ]
})


st.bar_chart(
    floor_df.set_index("층")
)


# =========================================================
# ROOM RANKING
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📍 공간별 예상 밀집도'
    '</div>',
    unsafe_allow_html=True
)


room_rows = []

for floor in [1, 2, 3]:

    for room in ROOMS[floor]:

        probability = distribution.get(
            (
                floor,
                room[0]
            ),
            0
        )

        room_rows.append({

            "층":
                f"{floor}층",

            "공간":
                f"{room[0]} · {room[1]}",

            "예상 분포":
                probability * 100,

            "예상 학생":
                round(
                    probability * 300
                )
        })


room_df = pd.DataFrame(
    room_rows
)

room_df = room_df.sort_values(
    "예상 분포",
    ascending=False
)


st.dataframe(

    room_df,

    use_container_width=True,

    hide_index=True,

    column_config={

        "예상 분포":
            st.column_config.ProgressColumn(
                "예상 분포",
                min_value=0,
                max_value=15,
                format="%.1f%%"
            ),

        "예상 학생":
            st.column_config.NumberColumn(
                "예상 학생",
                format="%d명"
            )
    }
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="info-box">

    💡 <b>연구 활용 방법</b><br>

    현재 분포값은 프로토타입용 가중치입니다.
    실제 인터뷰·설문 결과가 나오면
    <b>TIME_PROFILES</b> 부분의 값을 실제 조사 결과로 교체하면 됩니다.

    이후 유휴공간 설계가 결정되면,
    이 3D 모델에 새로운 공간을 추가하고
    <b>조성 전 → 조성 후</b> 학생 분포를 비교하는 방식으로 확장할 수 있습니다.

    </div>
    """,
    unsafe_allow_html=True
)
