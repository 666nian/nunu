"""努努梦工厂 — 开发服务器
为 HTML/CSS/JS 设置 no-cache，防止浏览器缓存旧版本；
PNG 图片设置 7 天缓存（配合 Service Worker Cache First 策略）。
"""
import http.server
import os

PORT = 8080

class NunuHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        path = self.path.lower()
        if path.endswith('.html') or path.endswith('.css') or path.endswith('.js'):
            # HTML/CSS/JS — 每次都验证新鲜度，防止缓存旧版本导致 404 或功能异常
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
        elif path.endswith('.png'):
            # PNG 素材 — 7 天缓存（Service Worker 会做更精细的控制）
            self.send_header('Cache-Control', 'public, max-age=604800')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f'努努梦工厂开发服务器已启动 → http://localhost:{PORT}')
    http.server.test(HandlerClass=NunuHandler, port=PORT)
