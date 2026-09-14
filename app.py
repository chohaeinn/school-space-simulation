import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from collections import defaultdict


# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="교내 유휴공간 3D 시뮬레이션",
    page_icon="🏫",
    layout="wide"
)


# ============================================================
# 학교 평면도 기반 공간 데이터
#
# 1F / 2F / 3F
#
# 형식:
# (호실, 공간명, x, y, 가로, 세로, 공간유형)
# ============================================================

ROOMS = {

    1: [
        ("101", "1-1", 14, 2, 2, 3, "class"),
        ("102", "1-2", 12, 2, 2, 3, "class"),
        ("103", "1-3", 10, 2, 2, 3, "class"),
        ("104", "1-4", 8, 2, 2, 3, "class"),

        ("105", "도서정보 홈베이스", 3, 2, 5, 3, "common"),

        ("106", "보건실", 0, 4, 3, 2, "support"),

        ("107", "1층 교사 연구실", 8, 0, 2, 2, "staff"),

        ("108", "온라인 학습실1", 0, 2, 3, 2, "common"),

        ("109", "인공지능 정보 교육실", 0, 0, 4, 2, "special"),

        ("110", "지능형 스마트 영어실", 4, 0, 4, 2, "special"),
    ],


    2: [
        ("201", "과학실", 1, 1, 4, 4, "special"),
        ("202", "연구실", 2, 2, 2, 3, "support"),

        ("203", "2-1", 4, 2, 2, 3, "class"),
        ("204", "2-2", 6, 2, 2, 3, "class"),

        ("205", "교무센터", 8, 2, 2, 3, "support"),
        ("206", "교장실", 10, 2, 2, 3, "support"),

        ("207", "2층 교사 연구실", 12, 2, 2, 3, "staff"),

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

        ("306", "3층 교사 연구실", 10, 2, 2, 3, "staff"),

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


# 층 높이
FLOOR_Z = {
    1: 0,
    2: 4,
    3: 8
}


# ============================================================
# 시간대별 기본 이용 성향
# ============================================================

TIME_WEIGHT = {

    "아침 자투리 시간": {
        "class": 0.7,
        "common": 1.8,
        "special": 0.8,
        "event": 0.5,
        "support": 0.2,
        "staff": 0.05
    },

    "점심시간": {
        "class": 0.3,
        "common": 2.0,
        "special": 1.0,
        "event": 1.6,
        "support": 0.2,
        "staff": 0.05
    },

    "저녁 자투리 시간": {
        "class": 0.5,
        "common": 1.7,
        "special": 1.2,
        "event": 1.5,
        "support": 0.2,
        "staff": 0.05
    }
}


# ============================================================
# 공간 설명 키워드
# ============================================================

KEYWORD_EFFECT = {

    "휴식": {
        "common": 3.0,
        "event": 1.2
    },

    "카페": {
        "common": 3.0,
        "event": 1.5
    },

    "스터디": {
        "common": 2.8,
        "special": 1.5
    },

    "학습": {
        "common": 2.5,
        "special": 1.8
    },

    "독서": {
        "common": 3.0
    },

    "게임": {
        "common": 2.5,
        "event": 1.5
    },

    "동아리": {
        "common": 2.0,
        "special": 2.0,
        "event": 1.5
    },

    "전시": {
        "event": 3.0,
        "common": 1.3
    },

    "공연": {
        "event": 3.2
    },

    "체험": {
        "event": 2.6,
        "special": 2.0
    },

    "운동": {
        "event": 2.4
    },

    "창작": {
        "special": 2.8,
        "common": 1.4
    },

    "메이커": {
        "special": 3.0
    },

    "코딩": {
        "special": 2.8
    },

    "AI": {
        "special": 2.8
    },

    "인공지능": {
        "special": 2.8
    }
}


# ============================================================
# 공간 찾기
# ============================================================

def get_room(floor, room_id):

    rooms = ROOMS.get(floor, [])

    for room in rooms:

        if room[0] == room_id:
            return room

    return None


# ============================================================
# 공간 중심점
# ============================================================

def room_center(room):

    x = float(room[2])
    y = float(room[3])

    width = float(room[4])
    height = float(room[5])

    center_x = x + width / 2
    center_y = y + height / 2

    return center_x, center_y


# ============================================================
# 공간 면적
# ============================================================

def room_area(room):

    return float(room[4]) * float(room[5])


# ============================================================
# 입력된 공간 설명 분석
# ============================================================

def analyze_description(description):

    result = defaultdict(float)

    text = str(description).lower()

    for keyword, effects in KEYWORD_EFFECT.items():

        if keyword.lower() in text:

            for room_type, value in effects.items():

                result[room_type] += value

    return result


# ============================================================
# 학생 분포 계산
# ============================================================

def calculate_distribution(
    selected_floor,
    selected_room,
    description,
    time_name,
    capacity,
    students,
    duration
):

    keyword_effect = analyze_description(
        description
    )

    weights = {}

    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            room_id = room[0]
            room_type = room[6]

            weight = TIME_WEIGHT[
                time_name
            ].get(
                room_type,
                0.3
            )

            # 선택한 유휴공간
            if (
                floor == selected_floor
                and room_id == selected_room
            ):

                weight += 12

            # 같은 층에 약간의 이동 효과
            if floor == selected_floor:

                weight += 0.25

            # 공간 설명과 공간 유형 연결
            weight += (
                keyword_effect.get(
                    room_type,
                    0
                ) * 0.5
            )

            # 공간 크기 효과
            area = room_area(room)

            weight *= (
                0.8 +
                min(area / 18, 0.8)
            )

            # 오래 머무는 경우
            if (
                duration >= 60
                and room_type in [
                    "common",
                    "special",
                    "event"
                ]
            ):

                weight *= 1.15

            # 유휴공간 수용인원
            if (
                floor == selected_floor
                and room_id == selected_room
            ):

                weight *= (
                    1 +
                    min(capacity / 500, 1)
                )

            weights[
                (floor, room_id)
            ] = max(
                weight,
                0.01
            )

    total = sum(
        weights.values()
    )

    distribution = {}

    for key, value in weights.items():

        distribution[key] = (
            value / total
        )

    return distribution


# ============================================================
# 3D 방 만들기
# ============================================================

def add_room_3d(
    fig,
    room,
    floor,
    selected_floor,
    selected_room,
    probability,
    max_probability
):

    room_id = room[0]
    room_name = room[1]

    x = room[2]
    y = room[3]

    width = room[4]
    height = room[5]

    z0 = FLOOR_Z[floor]
    z1 = z0 + 1.5

    is_selected = (
        floor == selected_floor
        and room_id == selected_room
    )

    intensity = 0

    if max_probability > 0:

        intensity = (
            probability /
            max_probability
        )

    # 선택 공간은 빨간색
    if is_selected:

        color = "#E63946"
        opacity = 0.90

    else:

        color = "#5B8FF9"

        opacity = (
            0.20 +
            intensity * 0.45
        )

    # 8개 꼭짓점
    xs = [
        x,
        x + width,
        x + width,
        x,
        x,
        x + width,
        x + width,
        x
    ]

    ys = [
        y,
        y,
        y + height,
        y + height,
        y,
        y,
        y + height,
        y + height
    ]

    zs = [
        z0,
        z0,
        z0,
        z0,
        z1,
        z1,
        z1,
        z1
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

    fig.add_trace(
        go.Mesh3d(
            x=xs,
            y=ys,
            z=zs,
            i=i,
            j=j,
            k=k,
            color=color,
            opacity=opacity,
            flatshading=True,
            hovertemplate=(
                f"<b>{floor}F "
                f"{room_id} "
                f"{room_name}</b><br>"
                f"예상 비중: "
                f"{probability * 100:.1f}%"
                "<extra></extra>"
            ),
            showlegend=False
        )
    )

    # 공간 이름
    cx, cy = room_center(room)

    if is_selected:

        fig.add_trace(
            go.Scatter3d(
                x=[cx],
                y=[cy],
                z=[z1 + 0.3],
                mode="markers+text",
                marker=dict(
                    size=13,
                    color="#E63946"
                ),
                text=[
                    f"★ {room_id} {room_name}"
                ],
                textposition="top center",
                textfont=dict(
                    size=11
                ),
                showlegend=False
            )
        )

    else:

        fig.add_trace(
            go.Scatter3d(
                x=[cx],
                y=[cy],
                z=[z1 + 0.05],
                mode="text",
                text=[
                    f"{room_id} {room_name}"
                ],
                textfont=dict(
                    size=8
                ),
                showlegend=False
            )
        )


# ============================================================
# 3D 학교 모델
# ============================================================

def make_3d_model(
    distribution,
    selected_floor,
    selected_room
):

    fig = go.Figure()

    # 층 바닥
    floor_colors = {
        1: "#DDEBFF",
        2: "#E3F4DD",
        3: "#FFF0D5"
    }

    for floor in [1, 2, 3]:

        z = FLOOR_Z[floor]

        fig.add_trace(
            go.Mesh3d(
                x=[
                    0, 26,
                    26, 0
                ],
                y=[
                    0, 0,
                    9, 9
                ],
                z=[
                    z, z,
                    z, z
                ],
                i=[0, 0],
                j=[1, 2],
                k=[2, 3],
                color=floor_colors[floor],
                opacity=0.25,
                showlegend=False,
                hoverinfo="skip"
            )
        )

    max_probability = max(
        distribution.values()
    )

    # 모든 공간 생성
    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            probability = distribution.get(
                (
                    floor,
                    room[0]
                ),
                0
            )

            add_room_3d(
                fig,
                room,
                floor,
                selected_floor,
                selected_room,
                probability,
                max_probability
            )

    fig.update_layout(

        height=700,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        scene=dict(

            xaxis=dict(
                title="X",
                range=[0, 26]
            ),

            yaxis=dict(
                title="Y",
                range=[0, 9]
            ),

            zaxis=dict(
                title="층",
                range=[-1, 11],

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

            aspectmode="manual",

            aspectratio=dict(
                x=2.3,
                y=0.8,
                z=1
            ),

            camera=dict(
                eye=dict(
                    x=1.5,
                    y=1.5,
                    z=1.2
                )
            )
        )
    )

    return fig


# ============================================================
# 히트맵
# ============================================================

def make_heatmap(
    floor,
    distribution,
    selected_floor,
    selected_room
):

    xs = np.linspace(
        0,
        26,
        160
    )

    ys = np.linspace(
        0,
        9,
        80
    )

    X, Y = np.meshgrid(
        xs,
        ys
    )

    heat = np.zeros_like(X)

    for room in ROOMS[floor]:

        room_id = room[0]

        cx, cy = room_center(
            room
        )

        probability = distribution.get(
            (
                floor,
                room_id
            ),
            0
        )

        sigma = max(
            min(
                room[4],
                room[5]
            ) * 0.55,
            0.45
        )

        # 선택된 공간은 영향 범위를 조금 넓게
        if (
            floor == selected_floor
            and room_id == selected_room
        ):

            sigma *= 1.25

        heat += (
            probability *
            np.exp(
                -(
                    (X - cx) ** 2 +
                    (Y - cy) ** 2
                )
                /
                (
                    2 *
                    sigma ** 2
                )
            )
        )

    if heat.max() > 0:

        heat = (
            heat /
            heat.max()
        )

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(

            x=xs,

            y=ys,

            z=heat,

            colorscale="Hot",

            zmin=0,

            zmax=1,

            colorbar=dict(
                title="밀집도"
            )
        )
    )

    # 공간 테두리
    for room in ROOMS[floor]:

        room_id = room[0]
        room_name = room[1]

        x = room[2]
        y = room[3]

        width = room[4]
        height = room[5]

        selected = (
            floor == selected_floor
            and room_id == selected_room
        )

        fig.add_shape(

            type="rect",

            x0=x,
            y0=y,

            x1=x + width,
            y1=y + height,

            line=dict(

                color=(
                    "#FF0000"
                    if selected
                    else "#FFFFFF"
                ),

                width=(
                    4
                    if selected
                    else 1
                )
            ),

            fillcolor=(
                "rgba(0,0,0,0)"
            )
        )

        cx, cy = room_center(
            room
        )

        fig.add_annotation(

            x=cx,
            y=cy,

            text=(
                f"{room_id}<br>"
                f"{room_name}"
            ),

            showarrow=False,

            font=dict(
                size=9
            ),

            bgcolor=(
                "rgba(255,255,255,0.65)"
            )
        )

    fig.update_layout(

        height=470,

        margin=dict(
            l=5,
            r=5,
            t=5,
            b=5
        ),

        xaxis=dict(
            range=[0, 26],
            showgrid=False
        ),

        yaxis=dict(
            range=[0, 9],
            showgrid=False,
            scaleanchor="x",
            scaleratio=1
        )
    )

    return fig


# ============================================================
# 결과 표
# ============================================================

def make_result_table(
    distribution,
    students
):

    rows = []

    for floor in [1, 2, 3]:

        for room in ROOMS[floor]:

            room_id = room[0]
            room_name = room[1]

            probability = distribution.get(
                (
                    floor,
                    room_id
                ),
                0
            )

            rows.append({

                "층": f"{floor}F",

                "공간":
                    f"{room_id} "
                    f"{room_name}",

                "예상 비중":
                    probability,

                "예상 인원":
                    int(
                        round(
                            probability *
                            students
                        )
                    )
            })

    df = pd.DataFrame(
        rows
    )

    return df.sort_values(
        "예상 인원",
        ascending=False
    )


# ============================================================
# 화면
# ============================================================

st.title(
    "🏫 교내 유휴공간 3D 시뮬레이션"
)

st.markdown(
    """
학교 평면도의 **1층·2층·3층 공간을 기반으로**
유휴공간을 새롭게 조성했을 때 학생들이
어떻게 분포할지 예상하는 연구용 시뮬레이션입니다.
"""
)


# ============================================================
# 사이드바
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ 시뮬레이션 설정"
    )

    students = st.number_input(

        "👥 예상 학생 수",

        min_value=10,

        max_value=1500,

        value=300,

        step=10
    )

    time_name = st.selectbox(

        "⏰ 시간대",

        [
            "아침 자투리 시간",
            "점심시간",
            "저녁 자투리 시간"
        ],

        index=1
    )

    st.divider()

    st.subheader(
        "① 유휴공간 설정"
    )

    selected_floor = st.selectbox(

        "층",

        [1, 2, 3],

        format_func=lambda x:
            f"{x}층"
    )

    room_labels = []

    for room in ROOMS[
        selected_floor
    ]:

        room_labels.append(
            f"{room[0]} {room[1]}"
        )

    selected_label = st.selectbox(

        "공간",

        room_labels
    )

    selected_room = (
        selected_label
        .split(" ", 1)[0]
    )

    st.subheader(
        "② 어떻게 만들지 입력"
    )

    description = st.text_area(

        "유휴공간 조성 계획",

        value=(
            "학생들이 점심시간에 "
            "쉬고 대화할 수 있는 "
            "휴식형 카페 공간"
        ),

        height=140
    )

    capacity = st.number_input(

        "수용 가능 인원",

        min_value=5,

        max_value=500,

        value=40,

        step=5
    )

    duration = st.slider(

        "평균 이용 시간",

        min_value=10,

        max_value=180,

        value=45,

        step=5,

        format="%d분"
    )

    st.divider()

    st.caption(
        "💡 예: 휴식형 카페 / 스터디 공간 / "
        "동아리실 / 전시공간 / AI 체험공간"
    )


# ============================================================
# 분포 계산
# ============================================================

distribution = calculate_distribution(

    selected_floor,

    selected_room,

    description,

    time_name,

    capacity,

    students,

    duration
)


# ============================================================
# 선택 공간 정보
# ============================================================

selected_room_data = get_room(

    selected_floor,

    selected_room
)


if selected_room_data is None:

    st.error(
        "선택한 공간을 찾을 수 없습니다."
    )

    st.stop()


selected_name = (
    selected_room_data[1]
)


selected_probability = (
    distribution.get(
        (
            selected_floor,
            selected_room
        ),
        0
    )
)


selected_expected = int(
    round(
        selected_probability *
        students
    )
)


# ============================================================
# 핵심 지표
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "선택 유휴공간",

    f"{selected_floor}F "
    f"{selected_room}"
)

c2.metric(

    "예상 학생 수",

    f"{students:,}명"
)

c3.metric(

    "예상 유입",

    f"{selected_expected}명"
)

c4.metric(

    "예상 유입 비중",

    f"{selected_probability * 100:.1f}%"
)


# ============================================================
# 입력 내용 표시
# ============================================================

st.info(

    f"""
**조성 계획:** {description}

**선택 공간:** 
{selected_floor}층 {selected_room} {selected_name}

**시간대:** {time_name}

**수용 인원:** {capacity}명

**평균 이용 시간:** {duration}분
"""
)


# ============================================================
# 3D 모델
# ============================================================

st.subheader(
    "🧊 1F · 2F · 3F 통합 3D 학교 모델"
)

fig3d = make_3d_model(

    distribution,

    selected_floor,

    selected_room
)

st.plotly_chart(

    fig3d,

    use_container_width=True,

    config={
        "displaylogo": False,
        "scrollZoom": True
    }
)

st.caption(
    "🖱️ 마우스로 드래그하면 3D 모델을 회전할 수 있습니다. "
    "빨간색 공간이 설정한 유휴공간입니다."
)


# ============================================================
# 히트맵
# ============================================================

st.subheader(
    "🔥 예상 학생 분포 히트맵"
)

tab1, tab2, tab3 = st.tabs(
    [
        "1층",
        "2층",
        "3층"
    ]
)


with tab1:

    st.plotly_chart(

        make_heatmap(
            1,
            distribution,
            selected_floor,
            selected_room
        ),

        use_container_width=True
    )


with tab2:

    st.plotly_chart(

        make_heatmap(
            2,
            distribution,
            selected_floor,
            selected_room
        ),

        use_container_width=True
    )


with tab3:

    st.plotly_chart(

        make_heatmap(
            3,
            distribution,
            selected_floor,
            selected_room
        ),

        use_container_width=True
    )


# ============================================================
# 결과표
# ============================================================

st.subheader(
    "📊 공간별 예상 학생 분포"
)

df = make_result_table(

    distribution,

    students
)


display_df = df.copy()

display_df[
    "예상 비중"
] = (

    display_df[
        "예상 비중"
    ] * 100

).round(1).astype(str) + "%"


st.dataframe(

    display_df,

    use_container_width=True,

    hide_index=True
)


# ============================================================
# 상위 공간
# ============================================================

st.subheader(
    "🔎 예상 분포가 높은 공간"
)

top3 = df.head(3)

for _, row in top3.iterrows():

    st.write(

        f"• **{row['층']} "
        f"{row['공간']}** → "
        f"예상 {row['예상 인원']}명"
    )


# ============================================================
# 연구용 주의사항
# ============================================================

st.warning(

    """
⚠️ 현재 결과는 **연구용 예상 모델**입니다.

실제 발표에서는 여러분이 실시한 학생 인터뷰·설문 결과를
시간대별 공간 이용 데이터로 입력하면,
현재의 가상 가중치를 실제 조사 결과 기반으로 바꿀 수 있습니다.
"""
)


# ============================================================
# CSV 다운로드
# ============================================================

csv_data = df.to_csv(
    index=False
).encode("utf-8-sig")


st.download_button(

    "📥 예상 분포 데이터 저장",

    data=csv_data,

    file_name=
    "학교_유휴공간_예상분포.csv",

    mime="text/csv"
)
