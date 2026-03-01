import streamlit as st
import pyvista as pv
import trimesh
import numpy as np
from PIL import Image
import io
import os

# Streamlit Cloud에서 렌더링을 위한 설정 (가상 화면 처리)
os.environ["PYVISTA_OFF_SCREEN"] = "True"

st.set_page_config(page_title="Dental STL to Image", layout="wide")
st.title("📸 Dental STL 자동 촬영 도구")
st.markdown("STL 파일을 업로드하면 5개 주요 구도(상, 하, 좌, 우, 정면)로 JPG 사진을 찍어줍니다.")

uploaded_file = st.sidebar.file_uploader("STL 파일을 업로드하세요", type=['stl'])

if uploaded_file:
    # 파일 저장 (PyVista는 파일 경로가 필요할 수 있음)
    with open("temp.stl", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 메쉬 로드
    mesh = pv.read("temp.stl")
    
    # 뷰포트 설정 함수
    def capture_view(view_name):
        plotter = pv.Plotter(off_screen=True, window_size=[1024, 768])
        plotter.add_mesh(mesh, color="white", smooth_shading=True)
        plotter.background_color = "black" # 치과용 사진 느낌을 위해 검정색 배경
        
        # 각 구도별 카메라 설정
        if view_name == "상악 (Upper)":
            plotter.view_xy()      # 위에서 아래로
        elif view_name == "하악 (Lower)":
            plotter.view_xy()
            plotter.camera.azimuth += 180 # 아래에서 위로 (반전)
            plotter.camera.roll += 180
        elif view_name == "정면 (Occlusion)":
            plotter.view_xz()      # 정면
        elif view_name == "좌측 (Left)":
            plotter.view_yz()      # 왼쪽 옆면
        elif view_name == "우측 (Right)":
            plotter.view_yz()
            plotter.camera.azimuth += 180 # 오른쪽 옆면
            
        plotter.reset_camera()
        
        # 스크린샷 캡처
        img_array = plotter.screenshot()
        plotter.close()
        return Image.fromarray(img_array)

    # UI 구성
    st.subheader("🖼 사진 촬영 및 다운로드")
    views = ["상악 (Upper)", "하악 (Lower)", "정면 (Occlusion)", "좌측 (Left)", "우측 (Right)"]
    
    cols = st.columns(len(views))
    
    for i, view in enumerate(views):
        with cols[i]:
            if st.button(f"{view} 촬영"):
                img = capture_view(view)
                st.image(img, caption=view, use_container_width=True)
                
                # 다운로드 버튼
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                st.download_button(
                    label="JPG 다운로드",
                    data=buf.getvalue(),
                    file_name=f"{view}.jpg",
                    mime="image/jpeg"
                )

else:
    st.info("왼쪽에서 STL 파일을 먼저 업로드해 주세요.")
