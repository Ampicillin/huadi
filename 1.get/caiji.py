import threading
import time
import random
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False



class Elderly:
    def __init__(self, id):
        self.id = id
        self.age = 60
        self.weight = 60
        self.max_heart_rate = 200 - self.age

        self.virtual_time = datetime.strptime("00:00", "%H:%M")
        self.prev_hr = 70  # 初始心率

        self.sleep_start = datetime.strptime("22:00", "%H:%M").time()
        self.deep_sleep_start = datetime.strptime("00:30", "%H:%M").time()
        self.wake_time = datetime.strptime("06:30", "%H:%M").time()
        self.prev_spo2 = random.uniform(96, 99)
        self.has_respiratory_condition = random.random() < 0.3
        self.meal_times = {
            "breakfast": datetime.strptime("07:30", "%H:%M").time(),
            "lunch": datetime.strptime("12:00", "%H:%M").time(),
            "dinner": datetime.strptime("18:00", "%H:%M").time(),
        }

        self.bp_type = random.choices(["normal", "low", "high"], weights=[0.7, 0.15, 0.15])[0]

        self.glucose = random.uniform(4.0, 6.2)
        self.baseline_glucose = self.glucose
        self.post_meal_target = self.baseline_glucose + random.uniform(1.5, 2.5)
        self.last_meal_time = None

        self.hr_event_minutes = 0
        self.exercise_active = False
        self.light_activity_minutes = 0
        self.prev_systolic = {
            "normal": random.randint(110, 130),
            "low": random.randint(90, 100),
            "high": random.randint(135, 150)
        }[self.bp_type]

    def is_between(self, time, start, end):
        return start <= time <= end if start < end else time >= start or time <= end

    def get_state(self):
        t = self.virtual_time.time()
        sleeping = self.is_between(t, self.sleep_start, self.wake_time)
        deep_sleep = self.is_between(t, self.deep_sleep_start, datetime.strptime("04:00", "%H:%M").time())
        eating = t in self.meal_times.values()

        # 睡眠平滑过渡（转换期：睡前1小时、起床后1小时）
        hour = self.virtual_time.hour + self.virtual_time.minute / 60
        smooth_factor = 0  # 0 表示清醒，1 表示深睡

        if 21 <= hour < 22:
            smooth_factor = (hour - 21)  # 0 → 1
        elif 6.5 <= hour < 7.5:
            smooth_factor = max(0, 1 - (hour - 6.5))  # 1 → 0
        elif self.is_between(self.virtual_time.time(), self.sleep_start, self.wake_time):
            smooth_factor = 1

        return smooth_factor, deep_sleep, eating


    def generate_systolic(self):
        base = {
            "normal": random.randint(110, 130),
            "low": random.randint(90, 100),
            "high": random.randint(135, 150)
        }[self.bp_type]

        sleep_factor, deep_sleep, eating = self.get_state()
        base *= (1 - 0.1 * sleep_factor)
        if deep_sleep:
            base *= 0.85

        hour = self.virtual_time.hour
        if 6 <= hour < 9 or 15 <= hour < 18:
            base += 5
        if eating:
            base += 3

        base += random.uniform(-0.5, 0.5)

        # 平滑过渡（血压变化缓慢）
        new_bp = self.prev_systolic + (base - self.prev_systolic) * 0.1 + random.uniform(-0.2, 0.2)
        self.prev_systolic = new_bp

        return int(max(90, min(new_bp, 180)))

    def generate_heart_rate(self):
        sleep_factor, deep_sleep, eating = self.get_state()
        hour = self.virtual_time.hour

        if sleep_factor >= 0.8:
            target_hr = random.uniform(45, 55)
        elif sleep_factor >= 0.3:
            target_hr = random.uniform(55, 65)
        else:
            target_hr = random.uniform(65, 85)

        if eating:
            target_hr += random.uniform(3, 8)

        # 高强度运动：心率大幅上升，波动较大
        if self.hr_event_minutes > 0:
            noise = random.uniform(-8, 8)
            target_hr += self.max_heart_rate * random.uniform(0.3, 0.6) + noise
            self.hr_event_minutes -= 1
            self.exercise_active = True

        # 轻度活动：心率轻微上升，波动小
        elif self.light_activity_minutes > 0:
            target_hr += random.uniform(10, 20) + random.uniform(-3, 3)
            self.light_activity_minutes -= 1

        # 活动触发逻辑（互斥）
        elif not self.exercise_active and self.light_activity_minutes == 0:
            if hour in range(7, 21):  # 醒着的时间段
                p = random.random()
                if p < 0.02:
                    self.hr_event_minutes = random.randint(15, 45)
                    self.exercise_active = True
                elif p < 0.10:  # 更高概率触发轻度活动
                    self.light_activity_minutes = random.randint(5, 15)

        else:
            self.exercise_active = False

        # 平滑过渡
        new_hr = self.prev_hr + (target_hr - self.prev_hr) * 0.2 + random.uniform(-1, 1)
        self.prev_hr = new_hr

        return int(max(40, min(new_hr, 180)))

    
    def generate_spo2(self):
        sleep_factor, deep_sleep, eating = self.get_state()
        base = 98.0
        if self.has_respiratory_condition:
            base -= random.uniform(2, 3)
        if deep_sleep:
            base -= random.uniform(0.5, 1.0)
        if self.hr_event_minutes > 0:
            if self.hr_event_minutes >= 20:
                base -= random.uniform(1.5, 2.5)
            elif self.hr_event_minutes >= 5:
                base -= random.uniform(0.5, 1.0)
        base += random.uniform(-0.2, 0.2)
        new_spo2 = self.prev_spo2 + (base - self.prev_spo2) * 0.1
        self.prev_spo2 = new_spo2
        return round(max(88.0, min(new_spo2, 100.0)), 1)
    
    def generate_glucose(self):
        time_str = self.virtual_time.strftime("%H:%M")
        if time_str in [t.strftime("%H:%M") for t in self.meal_times.values()]:
            self.last_meal_time = self.virtual_time

        if self.last_meal_time:
            minutes_since = (self.virtual_time - self.last_meal_time).total_seconds() / 60
            if 0 <= minutes_since <= 120:
                if minutes_since <= 30:
                    delta = (self.post_meal_target - self.glucose) * 0.2
                    self.glucose += delta
                else:
                    delta = (self.glucose - self.baseline_glucose) * 0.02
                    self.glucose -= delta
            else:
                self.last_meal_time = None
        else:
            if self.glucose > self.baseline_glucose:
                self.glucose -= (self.glucose - self.baseline_glucose) * 0.01
            noise = random.uniform(-0.02, 0.02)
            self.glucose += noise

        self.glucose = max(3.5, min(self.glucose, 10.0))
        return round(self.glucose, 2)

    def generate_data(self):
        self.virtual_time += timedelta(minutes=1)
        return {
            "time": self.virtual_time.strftime("%H:%M"),
            "systolic": self.generate_systolic(),
            "heart_rate": self.generate_heart_rate(),
            "glucose": self.generate_glucose(),
            "spo2": self.generate_spo2()

        }




# 初始化数据
data_buffer = {
    "time": [],
    "systolic": [],
    "glucose": [],
    "heart_rate": [],
    "spo2": [],
}


elder = Elderly(1)

# 所有时间刻度（24小时，每分钟1点）
time_labels = [(datetime.strptime("00:00", "%H:%M") + timedelta(minutes=i)).strftime("%H:%M") for i in range(24 * 60)]

def simulate_data():
    while True:
        for _ in range(15):
            data = elder.generate_data()
            data_buffer["time"].append(data["time"])
            data_buffer["systolic"].append(data["systolic"])
            data_buffer["glucose"].append(data["glucose"])
            data_buffer["heart_rate"].append(data["heart_rate"])
            data_buffer["spo2"].append(data["spo2"])
        time.sleep(1)

        
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
ax1, ax2, ax3, ax4 = axes.flatten()

def update_plot(frame):
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    ax1.set_ylim(60, 180)
    ax2.set_ylim(0.0, 10.0)
    ax3.set_ylim(40, 200)
    ax4.set_ylim(70, 100)

    time_to_value = {t: None for t in time_labels}
    for t, s, g, h, o in zip(data_buffer["time"], data_buffer["systolic"],
                             data_buffer["glucose"], data_buffer["heart_rate"],
                             data_buffer["spo2"]):
        time_to_value[t] = (s, g, h, o)

    systolic = [time_to_value[t][0] if time_to_value[t] else None for t in time_labels]
    glucose  = [time_to_value[t][1] if time_to_value[t] else None for t in time_labels]
    heart_rate = [time_to_value[t][2] if time_to_value[t] else None for t in time_labels]
    spo2 = [time_to_value[t][3] if time_to_value[t] else None for t in time_labels]

    ax1.plot(time_labels, systolic, color='red', label='收缩压')
    ax2.plot(time_labels, glucose, color='green', label='血糖')
    ax3.plot(time_labels, heart_rate, color='blue', label='心率')
    ax4.plot(time_labels, spo2, color='purple', label='血氧')

    titles = ["收缩压", "血糖", "心率", "血氧"]
    axes_list = [ax1, ax2, ax3, ax4]

    for ax, title in zip(axes_list, titles):
        ax.set_title(title)
        ax.set_xlim(0, len(time_labels) - 1)
        ax.set_xticks(range(0, len(time_labels), 120))
        ax.set_xticklabels([time_labels[i] for i in range(0, len(time_labels), 120)], rotation=45)
        ax.grid(True)
        ax.legend(loc='upper right')

plt.tight_layout()
# 启动数据模拟线程
threading.Thread(target=simulate_data, daemon=True).start()

ani = FuncAnimation(fig, update_plot, interval=1000)
plt.show()

