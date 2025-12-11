import os
import re

from PyQt5.QtCore import QFileSystemWatcher, Qt
from PyQt5.QtWidgets import QApplication, QDockWidget
from qgis.PyQt import uic


class DockPanel(QDockWidget):
    def __init__(self, iface, parent=None):
        super().__init__()
        self.iface = iface
        
        # 各ファイルのパスを設定
        self.ui_path = os.path.join(os.path.dirname(__file__), "dock.ui")
        self.style_path = os.path.join(os.path.dirname(__file__), "dock.qss")

        # .uiを読み込む
        self.load_ui()
        
        # .qss を読み込む
        self.load_style()

        # ファイル監視を設定
        self.setup_file_watcher()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def load_ui(self):
        # UIファイルを読み込む
        if os.path.exists(self.ui_path):
            # 既存のウィジェットをクリア（再読み込み時）
            if hasattr(self, '_ui_loaded'):
                # 子ウィジェットを全て削除
                for child in self.findChildren(QDockWidget):
                    child.deleteLater()
            
            # UIを読み込み
            uic.loadUi(self.ui_path, self)
            self._ui_loaded = True
            print(f"Loaded UI: {self.ui_path}")
            
            # UIロード後にシグナルを再接続
            self.reconnect_signals()
        else:
            print(f"UI file not found: {self.ui_path}")

    def reconnect_signals(self):
        """UIリロード後にシグナルを再接続"""
        # ギャラリーのナビゲーションボタン
        if hasattr(self, 'prevButton'):
            self.prevButton.clicked.connect(self.prev_image)
        if hasattr(self, 'nextButton'):
            self.nextButton.clicked.connect(self.next_image)

        # 初期表示を更新
        self.update_page_indicator()

    def prev_image(self):
        # 前の画像に切り替え（ループ）
        if hasattr(self, 'imageStack'):
            idx = self.imageStack.currentIndex()
            count = self.imageStack.count()
            if count > 0:
                new_idx = (idx - 1) % count
                self.imageStack.setCurrentIndex(new_idx)
                self.update_page_indicator()

    def next_image(self):
        # 次の画像に切り替え（ループ）
        if hasattr(self, 'imageStack'):
            idx = self.imageStack.currentIndex()
            count = self.imageStack.count()
            if count > 0:
                new_idx = (idx + 1) % count
                self.imageStack.setCurrentIndex(new_idx)
                self.update_page_indicator()

    def update_page_indicator(self):
        # ページインジケーターを更新
        if hasattr(self, 'imageStack') and hasattr(self, 'pageIndicator'):
            current = self.imageStack.currentIndex() + 1
            total = self.imageStack.count()
            self.pageIndicator.setText(f"{current} / {total}")

    def load_style(self):
        # スタイルシートを読み込む
        if os.path.exists(self.style_path):
            with open(self.style_path, encoding="utf-8") as f:
                stylesheet = f.read()
                
                # 画像パスを絶対パスに変換
                # url(:/...) 形式（Qtリソース）は除外し、通常のファイルパスのみ変換
                path = os.path.dirname(self.style_path).replace("\\", "/")
                
                # url() の中身が : で始まらない場合のみ絶対パスに変換
                def replace_url(match):
                    url_content = match.group(1)
                    # : で始まる場合（Qtリソース）はそのまま返す
                    if url_content.startswith(':'):
                        return match.group(0)
                    # それ以外は絶対パスに変換
                    return f'url("{path}/{url_content}")'
                
                stylesheet = re.sub(
                    r'url\((.*?)\)',
                    replace_url,
                    stylesheet
                )
                
                self.setStyleSheet(stylesheet)
                print(f"Loaded stylesheet: {self.style_path}")
        else:
            print(f"Stylesheet not found: {self.style_path}")
    
    def setup_file_watcher(self):
        # ファイル監視を設定
        self.file_watcher = QFileSystemWatcher()
        
        # .uiファイルを監視
        if os.path.exists(self.ui_path):
            self.file_watcher.addPath(self.ui_path)
            print(f"Watching UI: {self.ui_path}")
        
        # .qssファイルを監視
        if os.path.exists(self.style_path):
            self.file_watcher.addPath(self.style_path)
            print(f"Watching QSS: {self.style_path}")
        
        # ファイル変更時のシグナル接続
        self.file_watcher.fileChanged.connect(self.on_file_changed)
    
    def on_file_changed(self, path):
        # ファイルが変更されたときに呼ばれる
        print(f"File changed: {path}")
        
        # ファイル監視をクリア
        self.file_watcher.removePaths(self.file_watcher.files())
        
        # どのファイルが変更されたか判定
        if path == self.ui_path:
            print("Reloading UI...")
            self.load_ui()
            # UIリロード後はスタイルも再適用
            self.load_style()
        elif path == self.style_path:
            print("Reloading stylesheet...")
            self.load_style()
        
        # ファイル監視を再追加
        if os.path.exists(self.ui_path):
            self.file_watcher.addPath(self.ui_path)
        if os.path.exists(self.style_path):
            self.file_watcher.addPath(self.style_path)
        
        # UIを強制更新
        app = QApplication.instance()
        app.processEvents()
    
