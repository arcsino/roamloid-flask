# Backend of Roamloid

## バックエンド環境構築セットアップ

### 必要条件

- Python 3.10 以上あれば大丈夫！知らんけど

### セットアップ手順

1. 移動

   ```powershell
   cd backend
   ```

2. 仮想環境の作成・有効化

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate  # (Windows)
   # source venv/bin/activate  # (macOS/Linux)
   ```

3. 依存パッケージのインストール

   ```powershell
   pip install -r requirements.txt
   ```

4. .env ファイルの作成  
   例:

   ```
   FLASK_APP=run.py
   FLASK_DEBUG=1
   FLASK_CORS_ORIGINS=http://localhost:5173
   GEMINI_API_KEY = APIキー
   ```

5. データベース初期化（初回のみ）

   ```powershell
   flask db init  # 初回のみ
   flask db stamp head  # dbファイルを削除した後のみ
   flask db migrate
   flask db upgrade
   ```

6. サーバー起動

```powershell
python run.py
# or
flask run
```

---

## 備考

- この README.md は AI 作のものですので、自由に改変して構いません。
- 今後、User/Room 管理 API などを追加予定です。
