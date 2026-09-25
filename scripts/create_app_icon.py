"""从项目配色生成多尺寸 Windows 应用图标。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "assets" / "app.ico"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((8, 8, 248, 248), radius=58, fill="#415BD8")
    draw.rounded_rectangle((20, 20, 236, 236), radius=48, outline="#9DAFFF", width=5)
    font_path = Path("C:/Windows/Fonts/msyhbd.ttc")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font = ImageFont.truetype(str(font_path), 150)
    bounds = draw.textbbox((0, 0), "拓", font=font)
    x = 128 - (bounds[2] - bounds[0]) / 2 - bounds[0]
    y = 123 - (bounds[3] - bounds[1]) / 2 - bounds[1]
    draw.text((x, y), "拓", font=font, fill="white")
    canvas.save(output, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)])
    print(output)


if __name__ == "__main__":
    main()
