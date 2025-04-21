import csv

LOGS_CSV = "logs.csv"

logs = [i for i in open("telegram_crawler_20250408.log", 'r', encoding='utf-8').readlines()]

with open(LOGS_CSV, "w", newline='') as file:
    writer = csv.writer(file)
    for i in logs:
        print(i)
        writer.writerow(i)




