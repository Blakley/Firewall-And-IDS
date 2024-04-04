from datetime import datetime, timedelta

line = "2024-04-03 16:33:19,111 - Client: 127.0.0.1, just accessed the home page"

time_threshold = datetime.now() - timedelta(seconds=60)

# timestamp_str = line.split(' - ')[0]
# timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')


timestamp_str, client_info = line.split(' - ')
timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')

print(timestamp)
print(time_threshold)

