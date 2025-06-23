import pandas as pd
import os

# 병합
df1 = pd.read_csv("data/steam_top_games.csv")
df2 = pd.read_csv("data/steam_top_games_retry.csv")
df_final = pd.concat([df1, df2]).drop_duplicates(subset="appid")

# 최종 저장
df_final.to_csv("data/steam_top_games_final.csv", index=False)
print(f"✅ 병합 완료! 총 {len(df_final)}개 게임 수록됨.")

# 중간 파일 삭제
remove_files = [
    "data/steam_top_games.csv",
    "data/steam_top_games_retry.csv",
    "data/failed_urls.csv"
]

for file in remove_files:
    try:
        os.remove(file)
        print(f"🗑 삭제됨: {file}")
    except FileNotFoundError:
        print(f"⚠️ 파일 없음: {file}")

print("🧼 정리 완료. 남은 핵심 파일: steam_top_games_final.csv")