import base64

class BackgroundCSSGenerator:
    def __init__(self, img1_path):
        self.img1_path = img1_path

    def get_img_as_base64(self, file):
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def generate_background_css(self):
        img1 = self.get_img_as_base64(self.img1_path)

        css = f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-image: url("data:image/png;base64,{img1}");
            background-size: cover;
            background-position: center;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}

        [data-testid="stToolbar"] {{
            right: 2rem;
        }}
        </style>
        """
        return css