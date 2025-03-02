#!/usr/bin/env python
"""
テーブルウィジェットのテスト実行スクリプト

このスクリプトは、テーブルウィジェットのリファクタリングの成果を検証するための
テストを実行します。
"""
import os
import sys
import unittest
from PyQt5.QtWidgets import QApplication

# テスト関連のモジュールをインポート
from test_table_widgets import TestWindow  # 視覚的テスト用


def run_visual_test():
    """視覚的なテストを実行"""
    print("=== 視覚的テスト実行中 ===")
    print("既存のテーブルウィジェットと新しいテーブルウィジェットを比較表示します。")
    print("終了するには、ウィンドウを閉じてください。")
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    return app.exec_()


def run_unit_tests():
    """ユニットテストを実行"""
    print("\n=== ユニットテスト実行中 ===")
    # testsディレクトリへのパスを追加
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    try:
        # テストモジュールをインポート
        from tests.test_table_widgets import TestTableWidgets
        
        # テストを実行
        suite = unittest.TestLoader().loadTestsFromTestCase(TestTableWidgets)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        
        if result.wasSuccessful():
            print("\nすべてのユニットテストが成功しました！")
            return 0
        else:
            print("\nいくつかのテストが失敗しました。")
            return 1
            
    except ImportError as e:
        print(f"テストモジュールのインポートに失敗しました: {e}")
        return 1


def show_menu():
    """メニューを表示"""
    print("\n=== テーブルウィジェットテストメニュー ===")
    print("1. 視覚的テスト実行（GUI）")
    print("2. ユニットテスト実行")
    print("3. 両方実行")
    print("q. 終了")
    
    choice = input("選択してください (1-3, q): ")
    return choice


def main():
    """メイン関数"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_visual_test()
        elif choice == '2':
            run_unit_tests()
        elif choice == '3':
            run_visual_test()
            run_unit_tests()
        elif choice.lower() == 'q':
            print("終了します。")
            break
        else:
            print("無効な選択です。もう一度選択してください。")


if __name__ == "__main__":
    main()
