import streamlit as st
import trimesh
import numpy as np
import io

# 1. 페이지 설정
st.set_page_config(page_title="Dental STL Cropper", layout="wide")

st.title("🦷 Dental STL 정교 크롭 도구")
st.markdown("STL 파일을 업로드하고 상하/좌우 방향으로 정밀하게 절단하여 다운로드하세요.")

# 2. 사이드바 - 파일 업로드
uploaded_file = st.sidebar.file_uploader("STL 파일을 업로드하세요", type=['stl'])

if uploaded_file:
    # 데이터 로드 (캐싱)
    @st.cache_data
    def load_mesh_data(file_content):
        return trimesh.load(io.BytesIO(file_content), file_type='stl')

    try:
        file_bytes = uploaded_file.read()
        mesh = load_mesh_data(file_bytes)
        
        # 모델 정보 표시
        st.sidebar.success("파일 로드 성공!")
        st.sidebar.write(f"삼각형 개수: {len(mesh.faces)}")
        
        # 3. 크롭 설정 UI
        st.subheader("✂️ 크롭 설정")
        col1, col2 = st.columns(2)
        
        with col1:
            mode = st.radio("크롭 방향 선택", ["상교 (Upper)", "하교 (Lower)", "좌측 (Left)", "우측 (Right)"])
            
        # 모델의 중심점 계산
        center = mesh.bounds.mean(axis=0)
        
        with col2:
            offset = st.slider("절단면 미세 조정 (Offset)", 
                               min_value=-50.0, max_value=50.0, value=0.0, step=0.1)

        # 4. 방향 벡터 설정
        normals = {
            "상교 (Upper)": [0, 0, 1],
            "하교 (Lower)": [0, 0, -1],
            "좌측 (Left)": [-1, 0, 0],
            "우측 (Right)": [1, 0, 0]
        }
        
        selected_normal = np.array(normals[mode])
        adjusted_origin = center + (selected_normal * offset)

        # 5. 크롭 실행 버튼
        if st.button(f"{mode} 크롭 및 다운로드 준비"):
            with st.spinner("메쉬 처리 중... 잠시만 기다려주세요."):
                # slice_plane 함수 호출 (괄호 닫힘 확인 완료)
                cropped = mesh.slice_plane(
                    plane_origin=adjusted_origin, 
                    plane_normal=selected_normal, 
                    cap=True
                )
                
                # 결과물 파일화
                export_io = io.BytesIO()
                cropped.export(export_io, file_type='stl')
                result_data = export_io.getvalue()
                
                st.success(f"✅ {mode} 크롭 완료!")
                st.download_button(
                    label="📥 크롭된 STL 파일 다운로드",
                    data=result_data,
                    file_name=f"cropped_{mode.split()[0]}.stl",
                    mime="application/sla"
                )

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

else:
    st.info("왼쪽 사이드바에서 STL 파일을 업로드하면 시작할 수 있습니다.")
