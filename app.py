import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image, ImageFilter, ImageEnhance
import plotly.graph_objects as go
import os


# ============================================================
# 페이지 기본 설정
# ============================================================

st.set_page_config(
    page_title="학교 공간 분포 분석",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS - 전체 디자인
# ============================================================

st.markdown("""
<style>

    /* 전체 배경 */
    .stApp {
        background:
            linear-gradient(
                135deg,
                #f8fbff 0%,
                #f4f7fb 45%,
                #eef3f9 100%
            );
    }

    /* 기본 여백 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* 제목 */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -2px;
        color: #172033;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #718096;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* 카드 */
    .glass-card {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(220,228,239,0.9);
        border-radius: 22px;
        padding: 24px;
        box-shadow:
            0 10px 30px rgba(30,55,90,0.06);
    }

    /* 작은 제목 */
    .section-title {
        font-size: 22px;
        font-weight: 750;
        color: #1e293b;
        margin-bottom: 4px;
    }

    .section-description {
        color: #7b8798;
        font-size: 14px;
        margin-bottom: 18px;
    }

    /* 시간 버튼 영역 */
    div[data-testid="stRadio"] > div {
        gap: 10px;
    }

    div[data-testid="stRadio"] label {
        background: white;
        border: 1px solid #dce3ed;
        padding: 12px 28px;
        border-radius: 14px;
        transition: all 0.2s ease;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: #8da8cc;
        transform: translateY(-1px);
    }

    /* Metric */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e1e7ef;
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(30,55,90,0.04);
    }

    /* 탭 */
    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 700;
    }

    /* 구분선 */
    hr {
        border: none;
        height: 1px;
        background: #e3e8f0;
        margin: 30px 0;
    }

    /* 하단 안내 */
    .footer-note {
        background: #f1f5f9;
        border-radius: 16px;
        padding: 16px 20px;
        color: #64748b;
        font-size: 13px;
        line-height: 1.6;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# 학교 공간 데이터
# ============================================================

ROOMS = {

    1: [
        ("101", "1-1", 14, 2, 2, 3, "class"),
        ("102", "1-2", 12, 2, 2, 3, "class"),
        ("103", "1-3", 10, 2, 2, 3, "class"),
        ("104", "1-4", 8, 2, 2, 3, "class"),
        ("105", "도서정보 홈베이스", 3, 2, 5, 3, "common"),
        ("106", "보건실", 0, 4, 3, 2, "support"),
        ("107", "교사 연구실", 8, 0, 2, 2, "staff"),
        ("108", "온라인 학습실1", 0, 2, 3, 2, "common"),
        ("109", "AI 정보 교육실", 0, 0, 4, 2, "special"),
        ("110", "스마트 영어실", 4, 0, 4, 2, "special"),
    ],

    2: [
        ("201", "과학실", 1, 1, 4, 4, "special"),
        ("202", "연구실", 2, 2, 2, 3, "support"),
        ("203", "2-1", 4, 2, 2, 3, "class"),
        ("204", "2-2", 6, 2, 2, 3, "class"),
        ("205", "교무센터", 8, 2, 2, 3, "support"),
        ("206", "교장실", 10, 2, 2, 3, "support"),
        ("207", "교사 연구실", 12, 2, 2, 3, "staff"),
        ("208", "회의실", 14, 2, 2, 3, "support"),
        ("209", "2-3", 16, 2, 2, 3, "class"),
        ("210", "2-4", 18, 2, 2, 3, "class"),
        ("211", "휴게실", 20, 2, 2, 3, "common"),
        ("212", "홈베이스", 22, 2, 2, 3, "common"),
        ("213", "진로실", 0, 0, 4, 2, "common"),
        ("214", "스팀실", 4, 0, 4, 2, "special"),
        ("215", "온라인 학습실2", 0, 5, 4, 2, "common"),
    ],

    3: [
        ("301", "Wee클래스", 1, 1, 4, 4, "support"),
        ("302", "온라인 스튜디오", 2, 2, 2, 3, "special"),
        ("303", "온라인 스튜디오", 4, 2, 2, 3, "special"),
        ("304", "3-1", 6, 2, 2, 3, "class"),
        ("305", "3-2", 8, 2, 2, 3, "class"),
        ("306", "교사 연구실", 10, 2, 2, 3, "staff"),
        ("307", "3-3", 12, 2, 2, 3, "class"),
        ("308", "3-4", 14, 2, 2, 3, "class"),
        ("309", "융합실", 16, 2, 2, 3, "special"),
        ("310", "서버실", 18, 2, 2, 3, "support"),
        ("311", "홈베이스", 20, 2, 2, 3, "common"),
        ("312", "가온홀", 0, 0, 4, 2, "event"),
        ("313", "컴퓨팅랩", 4, 0, 4, 2, "special"),
        ("314", "인공지능실", 8, 0, 4, 2, "special"),
        ("315", "창의융합 인문사회실", 12, 0, 4, 2, "special"),
    ]
}


# ============================================================
# 시간대별 현재 분포 성향
#
# 실제 조사값으로 나중에 교체 가능
# ============================================================

TIME_PROFILES = {

    "🌅 아침": {
        "class": 0.65,
        "common": 1.45,
        "special": 0.75,
        "event": 0.35,
        "support": 0.20,
        "staff": 0.05
    },

    "☀️ 점심": {
        "class": 0.25,
        "common": 1.85,
        "special": 0.90,
        "event": 1.55,
        "support": 0.15,
        "staff": 0.03
    },

    "🌙 저녁": {
        "class": 0.50,
        "common": 1.55,
        "special": 1.15,
        "event": 1.35,
        "support": 0.15,
        "staff": 0.03
    }
}


# ============================================================
# 층별 기본 이동량
#
# 현재 데이터 시각화용
# ============================================================

FLOOR_MULTIPLIER = {

    "🌅 아침": {
        1: 1.20,
        2: 0.90,
        3: 0.75
    },

    "☀️ 점심": {
        1: 1.10,
        2: 1.00,
        3: 1.25
    },

    "🌙 저녁": {
        1: 0.90,
        2: 1.00,
        3: 1.30
    }
}


# ============================================================
# 도면 이미지 불러오기
# ============================================================

MAP_FILE = "school_map.png"


def load_school_map():

    if os.path.exists(MAP_FILE):

        try:
            image = Image.open(
                MAP_FILE
            ).convert("RGBA")

            return image

        except Exception:
            return None

    return None


school_map = load_school_map()


# ============================================================
# 공간 중심
# ============================================================

def room_center(room):

    return (
        room[2] + room[4] / 2,
        room[3] + room[5] / 2
    )


# ============================================================
# 분포 계산
# ============================================================

def calculate_distribution(time_name):

    profile = TIME_PROFILES[
        time_name
    ]

    multiplier = FLOOR_MULTIPLIER[
        time_name
    ]

    raw = {}

    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            room_type = room[6]

            base = profile.get(
                room_type,
                0.2
            )

            area = room[4] * room[5]

            area_factor = (
                0.7 +
                min(area / 15, 1.0)
            )

            value = (
                base *
                area_factor *
                multiplier[floor]
            )

            raw[
                (floor, room[0])
            ] = value

    total = sum(
        raw.values()
    )

    result = {}

    for key, value in raw.items():

        result[key] = (
            value / total
        )

    return result


# ============================================================
# 히트맵 생성
# ============================================================

def create_heatmap(
    floor,
    distribution
):

    width = 260
    height = 100

    heat = np.zeros(
        (height, width)
    )

    for room in ROOMS[floor]:

        probability = distribution.get(
            (
                floor,
                room[0]
            ),
            0
        )

        cx, cy = room_center(
            room
        )

        # 0~26 / 0~9 → 픽셀
        px = int(
            cx / 26 * width
        )

        py = int(
            cy / 9 * height
        )

        sigma_x = max(
            room[4] / 26 * width * 0.75,
            5
        )

        sigma_y = max(
            room[5] / 9 * height * 0.75,
            5
        )

        y_grid, x_grid = np.mgrid[
            0:height,
            0:width
        ]

        blob = np.exp(
            -(
                (
                    (x_grid - px) ** 2
                    /
                    (2 * sigma_x ** 2)
                )
                +
                (
                    (y_grid - py) ** 2
                    /
                    (2 * sigma_y ** 2)
                )
            )
        )

        heat += (
            blob *
            probability
        )

    if heat.max() > 0:

        heat /= heat.max()

    return heat


# ============================================================
# 히트맵을 실제 도면 위에 합성
#
# 학교 도면은 1/2/3층이 세로로 들어있다는 전제
# ============================================================

def make_overlay_map(
    floor,
    distribution,
    opacity=0.55
):

    if school_map is None:

        return None

    base = school_map.copy()

    base = ImageEnhance.Contrast(
        base
    ).enhance(1.03)

    heat = create_heatmap(
        floor,
        distribution
    )

    heat_img = Image.fromarray(
        np.uint8(
            heat * 255
        )
    ).resize(
        base.size
    )

    # 열지도 색상
    arr = np.array(
        heat_img
    )

    rgba = np.zeros(
        (
            arr.shape[0],
            arr.shape[1],
            4
        ),
        dtype=np.uint8
    )

    # 컬러맵:
    # 낮은 값 = 파랑
    # 중간 = 노랑
    # 높은 값 = 빨강

    normalized = arr / 255.0

    rgba[:, :, 0] = (
        np.clip(
            normalized * 2.5,
            0,
            1
        ) * 255
    ).astype(
        np.uint8
    )

    rgba[:, :, 1] = (
        np.clip(
            1 -
            np.abs(
                normalized - 0.5
            ) * 2,
            0,
            1
        ) * 255
    ).astype(
        np.uint8
    )

    rgba[:, :, 2] = (
        np.clip(
            1 -
            normalized * 2.2,
            0,
            1
        ) * 255
    ).astype(
        np.uint8
    )

    # 낮은 값은 투명하게
    alpha = (
        np.clip(
            normalized * 1.8,
            0,
            1
        ) * opacity * 255
    )

    rgba[:, :, 3] = alpha.astype(
        np.uint8
    )

    heat_rgba = Image.fromarray(
        rgba,
        "RGBA"
    )

    result = Image.alpha_composite(
        base,
        heat_rgba
    )

    return result


# ============================================================
# 3D 학교 모델
# ============================================================

def make_3d_school(
    distribution
):

    fig = go.Figure()

    floor_z = {
        1: 0,
        2: 4,
        3: 8
    }

    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            room_id = room[0]
            name = room[1]

            x = room[2]
            y = room[3]

            w = room[4]
            h = room[5]

            z = floor_z[floor]

            probability = distribution.get(
                (
                    floor,
                    room_id
                ),
                0
            )

            # 밀집도
            intensity = min(
                probability * 25,
                1
            )

            # Plotly 색상
            if intensity > 0.65:

                color = "#ff5b5b"

            elif intensity > 0.35:

                color = "#ffc857"

            else:

                color = "#8fb9ff"

            xs = [
                x,
                x + w,
                x + w,
                x,
                x,
                x + w,
                x + w,
                x
            ]

            ys = [
                y,
                y,
                y + h,
                y + h,
                y,
                y,
                y + h,
                y + h
            ]

            zs = [
                z,
                z,
                z,
                z,
                z + 1.2,
                z + 1.2,
                z + 1.2,
                z + 1.2
            ]

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

            fig.add_trace(
                go.Mesh3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    i=i,
                    j=j,
                    k=k,
                    color=color,
                    opacity=0.70,
                    flatshading=True,
                    hovertemplate=(
                        f"<b>{floor}층 "
                        f"{room_id} {name}</b><br>"
                        f"예상 비중: "
                        f"{probability * 100:.1f}%"
                        "<extra></extra>"
                    ),
                    showlegend=False
                )
            )

            cx, cy = room_center(
                room
            )

            fig.add_trace(
                go.Scatter3d(
                    x=[cx],
                    y=[cy],
                    z=[z + 1.35],
                    mode="text",
                    text=[
                        f"{room_id}"
                    ],
                    textfont=dict(
                        size=9
                    ),
                    showlegend=False
                )
            )

    fig.update_layout(

        height=650,

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        scene=dict(

            xaxis=dict(
                visible=False
            ),

            yaxis=dict(
                visible=False
            ),

            zaxis=dict(
                title="층",
                tickvals=[
                    0,
                    4,
                    8
                ],
                ticktext=[
                    "1F",
                    "2F",
                    "3F"
                ]
            ),

            camera=dict(
                eye=dict(
                    x=1.5,
                    y=1.6,
                    z=1.15
                )
            ),

            aspectmode="manual",

            aspectratio=dict(
                x=2.5,
                y=0.9,
                z=1.1
            )
        )
    )

    return fig


# ============================================================
# 제목
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🏫 School Space Flow'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '교내 자투리 시간 학생 분포 시뮬레이션 · '
    '학교 공간 이용 현황 시각화'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 시간 선택
# ============================================================

st.markdown(
    '<div class="section-title">'
    '시간대를 선택하세요'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '시간대에 따라 예상되는 학생들의 공간 이용 분포를 확인할 수 있습니다.'
    '</div>',
    unsafe_allow_html=True
)


time_name = st.radio(

    "시간대",

    [
        "🌅 아침",
        "☀️ 점심",
        "🌙 저녁"
    ],

    horizontal=True,

    label_visibility="collapsed"
)


# ============================================================
# 분포 계산
# ============================================================

distribution = calculate_distribution(
    time_name
)


# ============================================================
# 상단 지표
# ============================================================

total_students = 300

floor_values = {}

for floor in [1, 2, 3]:

    value = sum(
        probability
        for (
            f,
            room
        ), probability
        in distribution.items()
        if f == floor
    )

    floor_values[floor] = value


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "현재 시뮬레이션",
    time_name
)

c2.metric(
    "대상 학생",
    f"{total_students}명"
)

c3.metric(
    "가장 높은 층",
    f"{max(floor_values, key=floor_values.get)}층"
)

c4.metric(
    "최대 층 분포",
    f"{max(floor_values.values()) * 100:.1f}%"
)


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# 실제 도면 + 히트맵
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🗺️ 실제 학교 도면 위 학생 분포'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '학교 평면도와 예상 학생 밀집도를 하나의 화면에서 확인합니다.'
    '</div>',
    unsafe_allow_html=True
)


floor_tabs = st.tabs(
    [
        "1층",
        "2층",
        "3층"
    ]
)


for index, floor in enumerate(
    [1, 2, 3]
):

    with floor_tabs[index]:

        left, right = st.columns(
            [2.5, 1]
        )

        with left:

            if school_map is not None:

                overlay = make_overlay_map(
                    floor,
                    distribution,
                    opacity=0.58
                )

                st.image(
                    overlay,
                    use_container_width=True
                )

            else:

                st.error(
                    "school_map.png를 찾을 수 없습니다."
                )

        with right:

            floor_percent = (
                floor_values[floor]
                * 100
            )

            floor_students = int(
                round(
                    total_students *
                    floor_values[floor]
                )
            )

            st.markdown(
                f"""
                <div class="glass-card">

                <div style="
                    font-size:14px;
                    color:#718096;
                    margin-bottom:8px;
                ">
                {floor}층 예상 분포
                </div>

                <div style="
                    font-size:38px;
                    font-weight:800;
                    color:#172033;
                ">
                {floor_percent:.1f}%
                </div>

                <div style="
                    font-size:14px;
                    color:#64748b;
                    margin-top:4px;
                ">
                약 {floor_students}명
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # 해당 층 공간 순위
            room_rows = []

            for room in ROOMS[floor]:

                probability = distribution.get(
                    (
                        floor,
                        room[0]
                    ),
                    0
                )

                room_rows.append(
                    (
                        room[0],
                        room[1],
                        probability
                    )
                )

            room_rows.sort(
                key=lambda x: x[2],
                reverse=True
            )

            st.markdown(
                "**공간별 예상 밀집도**"
            )

            for room_id, name, probability in room_rows[:5]:

                students = int(
                    round(
                        probability *
                        total_students
                    )
                )

                st.write(
                    f"**{room_id}** "
                    f"{name}  ·  "
                    f"{students}명"
                )


# ============================================================
# 범례
# ============================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background:white;
        border:1px solid #e1e7ef;
        border-radius:18px;
        padding:18px 22px;
        display:flex;
        align-items:center;
        gap:20px;
    ">

    <b>🔥 분포 히트맵</b>

    <span style="color:#3867d6;">
    ● 낮음
    </span>

    <span style="color:#e6a900;">
    ● 중간
    </span>

    <span style="color:#e53935;">
    ● 높음
    </span>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 층별 비교
# ============================================================

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">'
    '📊 층별 학생 분포 비교'
    '</div>',
    unsafe_allow_html=True
)

comparison_df = pd.DataFrame({

    "층": [
        "1층",
        "2층",
        "3층"
    ],

    "예상 분포 (%)": [
        round(
            floor_values[1] * 100,
            1
        ),
        round(
            floor_values[2] * 100,
            1
        ),
        round(
            floor_values[3] * 100,
            1
        )
    ],

    "예상 학생 수": [
        int(
            round(
                floor_values[1] *
                total_students
            )
        ),
        int(
            round(
                floor_values[2] *
                total_students
            )
        ),
        int(
            round(
                floor_values[3] *
                total_students
            )
        )
    ]
})


st.bar_chart(
    comparison_df.set_index("층")[
        "예상 분포 (%)"
    ]
)


# ============================================================
# 3D 학교 모델
# ============================================================

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">'
    '🧊 3D 학교 공간 모델'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '1층 · 2층 · 3층을 분리된 공간으로 구성하여 '
    '시간대별 공간 이용 분포를 입체적으로 확인합니다.'
    '</div>',
    unsafe_allow_html=True
)


fig = make_3d_school(
    distribution
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displaylogo": False,
        "scrollZoom": True
    }
)


# ============================================================
# 공간별 상세 데이터
# ============================================================

with st.expander(
    "📋 공간별 상세 분포 데이터 보기"
):

    rows = []

    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            probability = distribution.get(
                (
                    floor,
                    room[0]
                ),
                0
            )

            rows.append({

                "층":
                    f"{floor}층",

                "공간":
                    f"{room[0]} {room[1]}",

                "예상 분포":
                    f"{probability * 100:.2f}%",

                "예상 학생":
                    int(
                        round(
                            probability *
                            total_students
                        )
                    )
            })

    detail_df = pd.DataFrame(
        rows
    )

    st.dataframe(
        detail_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 연구 안내
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer-note">

    <b>연구용 시뮬레이션 안내</b><br>

    현재 화면은 학교 평면도의 공간 구성을 바탕으로
    시간대별 학생 분포를 시각화한 프로토타입입니다.

    실제 발표에서는 여러분이 조사한
    <b>아침·점심·저녁 학생 인터뷰 및 설문 결과</b>를
    분포값에 반영하면 실제 조사 기반 시뮬레이션으로 발전시킬 수 있습니다.

    </div>
    """,
    unsafe_allow_html=True
)
