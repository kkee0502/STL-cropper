import streamlit as st
import trimesh
import numpy as np
import io

# 페이지 설정
st.set_page_config(page_title="Dental STL Cropper", layout="wide")

st.title("🦷 Dental STL 정교 크롭 도구")
st.markdown("""
STL 파일을 업로드하고 **상교, 하교, 좌측, 우측** 방향으로 정밀하게 절단하여 다운로드할 수 있습니다.
- **정교:** 상하악이 맞물린 상태를 기준으로 절단면을 조정합니다.
""")

# 1. 파일 업로드
uploaded_file = st.sidebar.file_uploader("STL 파일을 업로드하세요", type=['stl'])

if uploaded_file:
    # 데이터 로드 (캐싱을 통해 속도 향상)
    @st.cache_data
    def load_mesh(file):
        return trimesh.load(io.BytesIO(file.read()), file_type='stl')

    mesh = load_mesh(uploaded_file)
    
    # 모델 정보 표시
    st.sidebar.info(f"모델 크기: {mesh.extents.round(2)}")
    
    # 2. 크롭 설정 UI
    st.subheader("✂️ 크롭 설정")
    col1, col2 = st.columns(2)
    
    with col1:
        mode = st.radio("크롭 방향 선택", ["상교 (Upper)", "하교 (Lower)", "좌측 (Left)", "우측 (Right)"])
        
    # 절단 기준점 (모델의 중심)
    center = mesh.bounds.mean(axis=0)
    
    # 세밀한 위치 조정을 위한 슬라이더 (정교한 조정을 위해 모델 범위 내 이동)
    with col2:
        offset = st.slider("절단면 미세 조정 (Offset)", 
                           min_value=-20.0, max_value=20.0, value=0.0, step=0.1)

    # 3. 크롭 로직 실행
    # 방향 벡터 설정 (Normal Vector)
    normals = {
        "상교 (Upper)": [0, 0, 1],   # Z축 위쪽 남김
        "하교 (Lower)": [0, 0, -1],  # Z축 아래쪽 남김
        "좌측 (Left)": [-1, 0, 0],   # X축 왼쪽 남김 (기준에 따라 X/Y 조정 가능)
        "우측 (Right)": [1, 0, 0]    # X축 오른쪽 남김
    }
    
    selected_normal = np.array(normals[mode])
    adjusted_origin = center + (selected_normal * offset)

    if st.button(f"{mode} 크롭 실행"):
        with st.spinner("메쉬를 정교하게 절단 중입니다..."):
            # slice_plane: 평면을 기준으로 메쉬를 자름
            # cap=True: 잘린 단면을 메꿔서 닫힌(Solid) 모델로 유지
            cropped = mesh.slice_plane(plane_origin=adjusted_origin, 
                                       plane_normal=selected_normal, 
                                       cap=True)
            
            # 결과 저장 및 다운로드 버튼 생성
            export_io = io.BytesIO()
            cropped.export(export_io, file_type='stl')
            
            st.success(f"✅ {mode} 크롭 완료!")
            st.download_button(
                label="📥 크롭된 STL 다운로드",
                data=export_io.getvalue(),
                file_name=f"cropped_{mode.split()[0]}.stl",
                mime="application/sla"
            )
else:
    st.warning("먼저 왼쪽 사이드바에서 STL 파일을 업로드해주세요.")

---
-
-
-
-
-
-
-
-
-
-
