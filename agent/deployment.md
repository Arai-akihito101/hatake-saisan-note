# 公開と障害の引き継ぎ（2026-11-16）

## 現在の正式URL
https://hatake-saisan-note.nakagawa01984.workers.dev/

## 対応した障害
Cloudflare PagesのGitHub連携プロジェクト hatake-saisan-note で、2026-11-14以降の5件のデプロイがすべて queued/idle のまま停止。各ログは Starting build... のみで開始/完了時刻とビルドコンテナログなし。GitHub CIは正常なため、Pagesのビルド開始前のキュー滞留と判断。Cloudflare内部の根本原因はログから特定できない。公開サイトに変更を反映できないため、Workersへ移行。

## 配信の仕組み
Cloudflare Workersに GitHub public/index.html をJavaScriptの文字列として埋め込み、GET / と GET /index.html に text/html; charset=utf-8 で返す。追加のAPI、DB、KV、Cron、外部分析タグなし。
2026-11-16にCloudflare APIからWorker hatake-saisan-note をアップロード。workers.dev subdomainを有効化。現在の本番はCloudflare Workerで、Pagesプロジェクトは残したままGitHub自動デプロイだけ無効化している。
GitHubへの変更だけでは本番Workerには反映されない。HTML変更時は新しい public/index.html を再取得してWorkerの内容を再生成し、Cloudflare APIへ再アップロードしてバージョンが100%配信に更新されることを確認する。

## 検証済み
- GitHub Actions live-check: 外部HTTPでHTML 12,789 bytes取得、必要な日本語要素確認。run 43792129066（成功）
- GitHub Actions browser: Chromeで初期収支、販売可能率編集、localStorage保存、CSV取得・数値確認、初期化を検証。run 43792548733（成功）
- CI: node tests/smoke.cjs が成功。v0.6ローカルの45項目テストは別実装のため本番保証として流用しない。

## 今後
本番更新と同時にブラウザーCIが再実行されるよう運用手順を確認する。Search Consoleの表示回数・クリック数の実測を始める。実利用者数・収益・検索流入は未測定。Day0は2026-11-16、Day30は12-16、Day60は2027-01-15。追加課金を伴う操作は行わない。
