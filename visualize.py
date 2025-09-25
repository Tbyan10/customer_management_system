import matplotlib
import seaborn as sns
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import pandas as pd
import matplotlib.pyplot as plt
import os


class Plots:
    def __init__(self,itr):

        self.itr = itr
        self.iteration_now = 0
        self.output_dir = "plots"
        os.makedirs(self.output_dir, exist_ok=True) # Create output directory if it doesn't exist
        self.data = []
        for _ in range(itr):
            self.data.append(pd.read_excel('data/all_data.xlsx',sheet_name=f'iteration_{_}'))

    def run(self):
        self.plot_arrival_vs_service()
        self.plot_idle_time()
        self.plot_customers_in_system_over_time()
        self.plot_waiting_time_distribution()
        self.plot_waiting_time_per_customer()
        self.plot_waiting_time_boxplot()
        self.plot_time_in_system()
        self.plot_service_time_distribution()
        self.plot_server_status_over_time()


    def plot_time_in_system(self):
        for itr in range(self.itr):
            plt.figure(figsize=(10, 5))
            plt.plot(self.data[itr]['system_time(min)'], label='Time in System', color='green')
            plt.xlabel('Customer Index')
            plt.ylabel('Time in System (min)')
            plt.title('Time in System for Each Customer')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/time_in_system_per_customer_{itr+1}.png")
            plt.close()

    def plot_arrival_vs_service(self):
        for itr in range(self.itr):
            plt.figure(figsize=(10, 5))
            plt.scatter(self.data[itr]['arrival_time(min)'],self.data[itr]['service_time(min)'], alpha=0.6)
            plt.xlabel('Arrival Time (min)')
            plt.ylabel('Service Time (min)')
            plt.title('Arrival Time vs Service Time')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/arrival_vs_service_{itr+1}.png")
            plt.close()

    def plot_waiting_time_distribution(self):
        for itr in range(self.itr):
            plt.figure(figsize=(10, 5))
            plt.hist(self.data[itr]['queue_time(min)'], bins=20, color='skyblue', edgecolor='black')
            plt.xlabel('Waiting Time (min)')
            plt.ylabel('Number of Customers')
            plt.title('Distribution of Waiting Time')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/waiting_time_distribution_{itr+1}.png")
            plt.close()

    def plot_idle_time(self):
        for itr in range(self.itr):
            plt.figure(figsize=(10, 5))
            plt.plot(self.data[itr]['arrival_time(min)'], self.data[itr]['free_time(min)'], label='free Time', color='orange')
            plt.xlabel('Arrival Time (min)')
            plt.ylabel('free Time (min)')
            plt.title('Server free Time Over Time')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/free_time_over_time_{itr+1}.png")
            plt.close()

    def plot_service_time_distribution(self):
        for itr in range(self.itr):
            plt.figure(figsize=(10, 5))
            sns.histplot(self.data[itr]['service_time(min)'], kde=True, color='orange', edgecolor='black')
            plt.title("Histogram of Service Times")
            plt.xlabel("Service Time (minutes)")
            plt.ylabel("Number of Customers")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/service_time_distribution_{itr+1}.png")
            plt.close()


    def plot_customers_in_system_over_time(self):
        for itr in range(self.itr):
            # Collecting all unique event times
            events = sorted(set(self.data[itr]['arrival_time(min)'].tolist() + self.data[itr]['end_time(min)'].tolist()))

            customers_in_system = []

            for t in events:
                count = ((self.data[itr]['arrival_time(min)'] <= t) & (self.data[itr]['end_time(min)'] > t)).sum()
                customers_in_system.append(count)

            plt.figure(figsize=(10, 5))
            plt.plot(events, customers_in_system, color='purple')
            plt.title("Number of Customers in System Over Time")
            plt.xlabel("Time (minutes)")
            plt.ylabel("Number of Customers")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/customers_in_system_over_time_{itr+1}.png")
            plt.close()

    def plot_server_status_over_time(self):
        for itr in range(self.itr):
            # Getting all unique event times (arrival or end times)
            event_times = sorted(set(self.data[itr]['arrival_time(min)'].tolist() + self.data[itr]['end_time(min)'].tolist()))
            server_status = []

            # Determining server status at each point
            for t in event_times:
                is_busy = ((self.data[itr]['begin_time(min)'] <= t) & (self.data[itr]['end_time(min)'] > t)).any()
                server_status.append(1 if is_busy else 0)

            plt.figure(figsize=(10, 4))
            plt.plot(event_times, server_status, drawstyle='steps-post', color='red')
            plt.title("Server Status Over Time (1 = Busy, 0 = Idle)")
            plt.xlabel("Time (minutes)")
            plt.ylabel("Server Status")
            plt.yticks([0, 1], ["Idle", "Busy"])
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/server_status_over_time_{itr+1}.png")
            plt.close()

    def plot_waiting_time_boxplot(self):
        for itr in range(self.itr):
            plt.figure(figsize=(6, 5))
            sns.boxplot(y=self.data[itr]['queue_time(min)'], color='lightblue')
            plt.title("Boxplot of Customer Waiting Times")
            plt.ylabel("Waiting Time (minutes)")
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/waiting_time_boxplot_{itr+1}.png")
            plt.close()

    def plot_waiting_time_per_customer(self):
        for itr in range(self.itr):
            plt.figure(figsize=(10, 5))
            plt.plot(range(1, len(self.data[itr]) + 1), self.data[itr]['queue_time(min)'], color='teal')
            plt.title("Waiting Time per Customer")
            plt.xlabel("Customer Index")
            plt.ylabel("Waiting Time (minutes)")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/waiting_time_per_customer_{itr+1}.png")
            plt.close()
