# テーブルウィジェット リファクタリングガイド

このドキュメントは、テーブルウィジェットのリファクタリングに関する説明とガイドラインを提供します。

## 概要

テーブルウィジェットのリファクタリングは、以下の目的で行われています：

1. 重複コードの削減
2. コードの保守性向上
3. 拡張性の向上
4. テスト容易性の向上

## 新しいクラス構造

リファクタリング後のクラス構造は以下の通りです：

```
BaseTableWidget (基底クラス)
├── LapDataTableWidget (ラップデータ表示用)
└── StatisticsTableWidget (統計データ表示用)
```

また、既存のコードとの互換性を保つために、以下のクラスも提供されています：

- `BridgeTableWidget`: 既存の `TableWidget` と新しい `LapDataTableWidget` を橋渡しするクラス
- `BridgeStatsTableWidget`: 既存の `StatsTableWidget` と新しい `StatisticsTableWidget` を橋渡しするクラス

## ファイル構成

リファクタリングで追加されたファイルは以下の通りです：

### 基本クラス
- `src/ui/base_widgets/base_table_widget.py`: テーブルウィジェットの基底クラス
- `src/ui/base_widgets/lap_data_table_widget.py`: ラップデータ表示用テーブルウィジェット
- `src/ui/base_widgets/statistics_table_widget.py`: 統計データ表示用テーブルウィジェット

### 連携モジュール
- `src/ui/base_widgets/table_widget_bridge.py`: 既存のクラスと新しいクラスを橋渡しするモジュール
- `src/ui/base_widgets/table_widget_factory.py`: テーブルウィジェットを生成するファクトリ関数

### 設定UI
- `src/ui/settings/table_widget_settings.py`: 新旧ウィジェットの切り替え設定UI
- `src/ui/settings/settings_integration_example.py`: 設定UIの統合例

### テスト
- `src/test_table_widgets.py`: 視覚的なテスト用スクリプト
- `tests/test_table_widgets.py`: ユニットテスト

## 使用方法

### 方法1: ファクトリの使用 (推奨)

アプリケーションのコードで、テーブルウィジェットの生成をファクトリ関数に置き換えます：

```python
from ui.base_widgets.table_widget_factory import get_lap_table_widget, get_stats_table_widget

# ウィジェットの生成
table = get_lap_table_widget(parent=self)
stats_table = get_stats_table_widget(config_manager=self.config_manager, parent=self)
```

### 方法2: ブリッジクラスの使用

既存のコードを変更せずに新しいウィジェットを使用する場合は、ブリッジクラスを使用します：

```python
from ui.base_widgets.table_widget_bridge import BridgeTableWidget, BridgeStatsTableWidget

# ウィジェットの生成
table = BridgeTableWidget(parent=self)
stats_table = BridgeStatsTableWidget(config_manager=self.config_manager, parent=self)
```

### 方法3: 直接使用

新しいクラスを直接使用する場合：

```python
from ui.base_widgets.lap_data_table_widget import LapDataTableWidget
from ui.base_widgets.statistics_table_widget import StatisticsTableWidget

# ウィジェットの生成
table = LapDataTableWidget(parent=self)
stats_table = StatisticsTableWidget(config_manager=self.config_manager, parent=self)
```

## 新旧実装の切り替え

ユーザーが新旧の実装を切り替えられるように、設定UIが提供されています。これを既存の設定UIに統合する方法の例が `src/ui/settings/settings_integration_example.py` に記載されています。

設定の切り替えは以下のようにプログラムからも行えます：

```python
from ui.base_widgets.table_widget_factory import set_use_new_table_implementation

# 新しい実装を使用する
set_use_new_table_implementation(True)
```

## テスト

### 視覚的なテスト

新旧両方のウィジェットを並べて表示し、動作を比較するためのテストスクリプトを提供しています：

```bash
python src/test_table_widgets.py
```

### ユニットテスト

自動テストを実行して、新旧ウィジェットの動作が同等であることを確認できます：

```bash
python -m unittest tests/test_table_widgets.py
```

## 利点

### 1. コードの重複削減

共通のテーブル設定コードが基底クラスにまとめられているため、コードの重複が大幅に削減されています。

### 2. メンテナンス性の向上

基底クラスの改善が全ての子クラスに反映されるため、変更が一箇所で済みます。

### 3. コードの明確化

各クラスの責任範囲が明確になり、コードの意図が伝わりやすくなります。

### 4. テスト容易性

基底クラスとそのメソッドのテストが可能になり、コンポーネントごとの単体テストが容易になります。

## 移行ステップ

1. テストスクリプトを使用して新旧ウィジェットの動作を確認
2. ファクトリ関数を使用して既存のコードを変更
3. 設定UIを統合して、ユーザーが新旧ウィジェットを切り替えられるようにする
4. ユニットテストを実行して機能の同等性を確認
5. すべての機能が正常に動作することを確認した後、完全に新しい実装に移行

## 注意点

1. 既存のコードを変更せずに、新しいクラスを導入することを心がけています。
2. ファクトリパターンを使用して、コードの変更を最小限に抑えています。
3. 段階的な移行を可能にするため、互換性レイヤーを提供しています。
