import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from collections import defaultdict

st.set_page_config(page_title='교내 유휴공간 3D 시뮬레이션', page_icon='🏫', layout='wide')
st.title('🏫 교내 유휴공간 3D 시뮬레이션')
st.caption('제공된 학교 안내도(1F·2F·3F)를 바탕으로 공간 배치를 개념적으로 3D 재구성한 연구용 프로토타입입니다.')

FLOOR_Z = {1: 0.0, 2: 4.0, 3: 8.0}

ROOMS = {
    1: [
        ('109','인공지능 정보 교육실',0.0,0.0,3.2,2.4,'special'),
        ('110','지능형 스마트 영어실',3.2,0.0,4.1,2.4,'special'),
        ('105','도서정보 홈베이스',3.2,2.4,5.8,4.1,'common'),
        ('108','온라인 학습실1',0.0,2.4,3.2,2.0,'common'),
        ('106','보건실',0.0,4.4,3.2,2.1,'support'),
        ('107','1층 교사 연구실',8.9,0.0,2.0,1.9,'staff'),
        ('104','1-4',9.1,3.0,1.6,2.0,'class'),
        ('103','1-3',10.7,3.0,1.6,2.0,'class'),
        ('102','1-2',12.3,3.0,1.6,2.0,'class'),
        ('101','1-1',14.1,2.3,2.0,3.5,'class'),
        ('ENT1','현관/출입구',7.8,3.0,1.3,3.2,'entrance'),
    ],
    2: [
        ('213','진로실',0.0,0.0,3.2,2.5,'common'),
        ('214','스팀실',3.2,0.0,4.1,2.2,'special'),
        ('215','온라인 학습실2',0.0,2.5,3.2,2.7,'common'),
        ('212','홈베이스',3.2,2.5,2.2,2.7,'common'),
        ('211','휴게실',5.4,2.5,1.7,2.7,'common'),
        ('210','2-4',7.1,2.5,1.9,2.7,'class'),
        ('209','2-3',9.0,2.5,1.9,2.7,'class'),
        ('208','회의실',10.9,2.5,1.7,2.7,'support'),
        ('207','2층 교사 연구실',12.6,2.5,1.6,2.7,'staff'),
        ('206','교장실',14.2,2.5,1.7,2.7,'support'),
        ('205','교무센터',15.9,2.5,1.7,2.7,'support'),
        ('204','2-2',17.6,2.5,1.9,2.7,'class'),
        ('203','2-1',19.5,2.5,1.9,2.7,'class'),
        ('202','연구실',21.4,2.5,1.7,2.7,'support'),
        ('201','과학실',23.1,1.9,2.2,3.3,'special'),
    ],
    3: [
        ('312','가온홀',0.0,0.0,3.2,2.6,'event'),
        ('315','창의융합 인문사회실',0.0,2.6,3.2,2.7,'special'),
        ('311','홈베이스',3.2,2.6,2.2,2.7,'common'),
        ('310','서버실',5.4,2.6,1.6,2.7,'support'),
        ('309','융합실',7.0,2.6,2.0,2.7,'special'),
        ('308','3-4',9.0,2.6,1.9,2.7,'class'),
        ('307','3-3',10.9,2.6,1.9,2.7,'class'),
        ('306','3층 교사 연구실',12.8,2.6,1.8,2.7,'staff'),
        ('305','3-2',14.6,2.6,1.9,2.7,'class'),
        ('304','3-1',16.5,2.6,1.9,2.7,'class'),
        ('303','온라인 스튜디오',18.4,2.6,1.8,2.7,'special'),
        ('302','온라인 스튜디오',20.2,2.6,1.8,2.7,'special'),
        ('301','Wee클래스',22.0,1.9,2.2,3.4,'support'),
        ('313','컴퓨팅랩',4.0,0.0,3.2,2.0,'special'),
        ('314','인공지능실',7.2,0.0,3.7,2.0,'special'),
    ],
}

TIME_MULTIPLIER = {
    '아침 자투리 시간': {'common':1.0,'class':0.7,'special':0.7,'event':0.6,'support':0.35,'staff':0.15,'entrance':1.7},
    '점심시간': {'common':1.0,'class':0.35,'special':0.8,'event':1.2,'support':0.3,'staff':0.1,'entrance':1.3},
    '저녁 자투리 시간': {'common':1.0,'class':0.45,'special':1.0,'event':1.1,'support':0.3,'staff':0.1,'entrance':0.9},
}

KEYWORD_EFFECTS = {
    '휴식':{'common':2.8,'event':1.8}, '카페':{'common':2.4,'event':2.0,'entrance':1.4},
    '스터디':{'common':2.7,'special':1.8,'class':1.4}, '학습':{'common':2.6,'special':1.8,'class':1.2},
    '독서':{'common':2.9,'special':1.4}, '게임':{'common':2.6,'event':1.8,'special':1.5},
    '체험':{'event':2.6,'special':2.0}, '전시':{'event':2.5,'common':1.7},
    '공연':{'event':3.2,'common':1.3}, '동아리':{'common':2.1,'special':2.2,'event':1.8},
    '상담':{'support':3.2,'common':1.1}, '운동':{'event':2.2,'common':1.4},
    '식사':{'common':2.1,'event':2.4,'entrance':1.2}, '창작':{'special':2.8,'common':1.6},
    '메이커':{'special':3.0,'event':1.6}, 'AI':{'special':2.7}, '코딩':{'special':2.8},
}

def center(room):
    return room[2] + room[4]/2, room[3] + room[5]/2

def area(room):
    return room[4]*room[5]

def find_room(floor, rid):
    return next((r for r in ROOMS[floor] if r[0] == rid), None)

def keyword_scores(text):
    text = text.lower()
    scores = defaultdict(float)
    for word, effect in KEYWORD_EFFECTS.items():
        if word.lower() in text:
            for kind, v in effect.items():
                scores[kind] += v
    return scores

def compute_weights(selected_floor, selected_room_id, design, time_label, capacity, duration):
    kw = keyword_scores(design)
    weights = {}
    for floor, rooms in ROOMS.items():
        for room in rooms:
            rid, name, x, y, w, h, kind = room
            base = TIME_MULTIPLIER[time_label].get(kind, 0.5)
            if floor == selected_floor and rid == selected_room_id:
                base += 7.0
            if floor == selected_floor:
                base += 0.25
            base += kw.get(kind, 0.0)*0.65
            base *= 0.7 + 0.10*np.sqrt(max(area(room), 1.0))
            if duration >= 60 and kind in ('common','event','special'):
                base *= 1.12
            elif duration <= 30 and kind in ('entrance','class'):
                base *= 1.05
            weights[(floor,rid)] = max(base,0.01)
    if (selected_floor, selected_room_id) in weights:
        weights[(selected_floor, selected_room_id)] *= 1.0 + min(capacity,1000)/500.0
    total = sum(weights.values())
    return {k:v/total for k,v in weights.items()}

def make_3d(selected_floor, selected_room_id, weights, show_heat=True):
    fig = go.Figure()
    for floor, z in FLOOR_Z.items():
        fig.add_trace(go.Mesh3d(x=[0,26,26,0], y=[0,0,9,9], z=[z,z,z,z], i=[0,0], j=[1,2], k=[2,3], opacity=0.10, color=['#EAF3FF','#EEFBEA','#FFF7E6'][floor-1], hoverinfo='skip', showlegend=False))
    max_w = max(weights.values()) if weights else 1
    for floor, rooms in ROOMS.items():
        z0, z1 = FLOOR_Z[floor], FLOOR_Z[floor]+1.6
        for rid,name,x,y,w,h,kind in rooms:
            selected = (floor == selected_floor and rid == selected_room_id)
            color = '#FF4B4B' if selected else '#7EA7D8'
            xs=[x,x+w,x+w,x,x,x+w,x+w,x]; ys=[y,y,y+h,y+h,y,y,y+h,y+h]; zs=[z0,z0,z0,z0,z1,z1,z1,z1]
            ii=[0,0,0,1,1,2,4,4,5,6,3,2]; jj=[1,2,3,2,5,3,5,6,6,7,0,6]; kk=[2,3,7,5,4,7,6,7,7,4,7,3]
            fig.add_trace(go.Mesh3d(x=xs,y=ys,z=zs,i=ii,j=jj,k=kk,color=color,opacity=0.75 if selected else 0.28,flatshading=True,hovertemplate=f'<b>{floor}F {rid} {name}</b><br>유형: {kind}<extra></extra>',showlegend=False))
            cx,cy=center(room)
            fig.add_trace(go.Scatter3d(x=[cx],y=[cy],z=[z1+0.08],mode='text',text=[f'{rid} {name}'],textfont=dict(size=9,color='#222'),hoverinfo='skip',showlegend=False))
            if show_heat:
                intensity = weights[(floor,rid)]/max_w
                fig.add_trace(go.Scatter3d(x=[cx],y=[cy],z=[z1+0.20],mode='markers',marker=dict(size=6+22*intensity,color=[intensity],colorscale='Hot',cmin=0,cmax=1,opacity=0.88,showscale=False),text=[f'{floor}F {rid} {name}<br>상대 분포 {intensity:.2f}'],hovertemplate='%{text}<extra></extra>',showlegend=False))
    fig.update_layout(height=760,margin=dict(l=0,r=0,t=10,b=0),scene=dict(xaxis=dict(title='가로',range=[0,26]),yaxis=dict(title='세로',range=[0,9]),zaxis=dict(title='층',tickvals=[0,4,8],ticktext=['1F','2F','3F'],range=[-0.5,10]),aspectmode='manual',aspectratio=dict(x=2.1,y=0.8,z=1.0),camera=dict(eye=dict(x=1.55,y=1.45,z=1.25))))
    return fig

def make_floor_heatmap(floor, weights, selected_floor, selected_room_id, design):
    nx,ny=110,55
    xs=np.linspace(0,26,nx); ys=np.linspace(0,9,ny); X,Y=np.meshgrid(xs,ys); Z=np.zeros_like(X)
    kw=keyword_scores(design)
    floor_total=sum(v for (f,_),v in weights.items() if f==floor)
    if floor_total<=0: return go.Figure()
    for room in ROOMS[floor]:
        rid,name,x,y,w,h,kind=room; cx,cy=center(room); p=weights[(floor,rid)]
        sigma=max(min(w,h)*0.42,0.35)
        if (floor,rid)==(selected_floor,selected_room_id): sigma*=1.25
        sigma*=1.0+min(kw.get(kind,0),5.0)*0.04
        amp=(p/floor_total)
        Z += amp*np.exp(-((X-cx)**2+(Y-cy)**2)/(2*sigma**2))
    if Z.max()>0: Z/=Z.max()
    fig=go.Figure(go.Heatmap(x=xs,y=ys,z=Z,colorscale='Hot',zmin=0,zmax=1,colorbar=dict(title='밀집도'),hovertemplate='x=%{x:.1f}, y=%{y:.1f}<br>밀집도=%{z:.2f}<extra></extra>',opacity=0.82))
    for rid,name,x,y,w,h,kind in ROOMS[floor]:
        selected=(floor==selected_floor and rid==selected_room_id)
        fig.add_shape(type='rect',x0=x,y0=y,x1=x+w,y1=y+h,line=dict(color='#ff0000' if selected else '#ffffff',width=3 if selected else 1.3),fillcolor='rgba(0,0,0,0)')
        cx,cy=center((rid,name,x,y,w,h,kind))
        fig.add_annotation(x=cx,y=cy,text=f'<b>{rid}</b><br>{name}',showarrow=False,font=dict(size=9,color='#111'),bgcolor='rgba(255,255,255,0.60)')
    fig.update_xaxes(range=[0,26],showgrid=False,zeroline=False); fig.update_yaxes(range=[0,9],showgrid=False,zeroline=False,scaleanchor='x',scaleratio=1)
    fig.update_layout(height=460,margin=dict(l=5,r=5,t=5,b=5))
    return fig

def summary_table(weights, students):
    rows=[]
    for (floor,rid),p in weights.items():
        r=find_room(floor,rid)
        rows.append({'층':f'{floor}F','공간':f'{rid} {r[1]}','예상비중':p,'예상인원':round(p*students)})
    return pd.DataFrame(rows).sort_values('예상인원',ascending=False)

with st.sidebar:
    st.header('🛠️ 시뮬레이션 설정')
    students=st.number_input('예상 학생 수',10,1500,300,10)
    time_label=st.selectbox('시간대',list(TIME_MULTIPLIER.keys()),index=1)
    st.markdown('---')
    st.subheader('① 유휴공간 설정')
    selected_floor=st.selectbox('층',[1,2,3],index=1)
    options={f'{r[0]} {r[1]}':r[0] for r in ROOMS[selected_floor]}
    selected_room_label=st.selectbox('유휴공간',list(options.keys()))
    selected_room_id=options[selected_room_label]
    st.subheader('② 어떻게 만들지 입력')
    design=st.text_area('공간 설계 설명',value='학생들이 점심시간에 쉬고 대화할 수 있는 휴식형 카페 공간',height=120,placeholder='예: 스터디 카페 + 충전 공간 + 소규모 동아리 활동 공간')
    capacity=st.number_input('유휴공간 예상 수용 인원',5,500,40,5)
    duration=st.slider('평균 이용 시간(분)',10,180,45,5)
    run=st.button('🚀 예상 분포 계산',use_container_width=True)
    st.caption('※ 현재 분포는 실제 조사자료가 아닌 연구용 가정 모델입니다. 실제 인터뷰/설문 결과가 있으면 가중치를 교체할 수 있습니다.')

weights=compute_weights(selected_floor,selected_room_id,design,time_label,capacity,duration)
if run or 'result' not in st.session_state:
    st.session_state.result={'weights':weights,'floor':selected_floor,'rid':selected_room_id,'design':design,'students':students,'time':time_label,'capacity':capacity,'duration':duration}
res=st.session_state.result
weights=res['weights']; selected_floor=res['floor']; selected_room_id=res['rid']; design=res['design']; students=res['students']; time_label=res['time']; capacity=res['capacity']; duration=res['duration']
selected=find_room(selected_floor,selected_room_id)

c1,c2,c3,c4=st.columns(4)
c1.metric('선택 공간',f'{selected_floor}F {selected_room_id}')
c2.metric('예상 학생 수',f'{students:,}명')
c3.metric('시간대',time_label)
c4.metric('수용 인원',f'{capacity}명')
st.info(f'**설계 입력:** {design}\n\n선택 공간: **{selected_floor}F {selected_room_id} {selected[1]}**')

st.subheader('🧊 1F · 2F · 3F 통합 3D 모델')
show_heat=st.checkbox('3D 모델에 예상 분포 점 표시',value=True)
st.plotly_chart(make_3d(selected_floor,selected_room_id,weights,show_heat),use_container_width=True)

st.subheader('🔥 층별 예상 분포 히트맵')
tabs=st.tabs(['1F','2F','3F'])
for i,floor in enumerate([1,2,3]):
    with tabs[i]:
        st.plotly_chart(make_floor_heatmap(floor,weights,selected_floor,selected_room_id,design),use_container_width=True)

st.subheader('📊 공간별 예상 분포')
df=summary_table(weights,students)
st.dataframe(df.assign(예상비중=df['예상비중'].map(lambda x:f'{x*100:.1f}%')),use_container_width=True,hide_index=True)

selected_share=weights[(selected_floor,selected_room_id)]
st.subheader('🎯 선택한 유휴공간의 예상 효과')
e1,e2,e3=st.columns(3)
e1.metric('예상 유입 학생',f'{round(selected_share*students)}명')
e2.metric('전체 중 비중',f'{selected_share*100:.1f}%')
e3.metric('평균 이용 시간',f'{duration}분')

st.markdown('''### 해석\n이 모델은 **유휴공간의 위치 + 공간 조성 방식 + 시간대 + 예상 학생 수**를 이용해 예상 학생 분포를 시각화합니다. 실제 건축 도면의 정확한 치수와 실제 동선을 재현하는 것이 아니라, 제공된 학교 안내도의 공간 관계를 이용한 연구용 3D/히트맵 모델입니다. 실제 인터뷰·설문 결과가 확보되면 `TIME_MULTIPLIER`와 `KEYWORD_EFFECTS`를 실제 조사결과로 교체하는 것을 권장합니다.''')

csv=df.to_csv(index=False).encode('utf-8-sig')
st.download_button('📥 예상 분포 CSV 다운로드',csv,'학교_유휴공간_예상분포.csv','text/csv')
