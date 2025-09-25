import tkinter as tk
from tkinter import *
from PIL.ImageOps import expand
import pandas as pd
from PIL import Image,ImageTk
import sys,os
# from visualize import (
#     plot_arrival_vs_service,
#     plot_waiting_time_distribution,
#     plot_idle_time,
#     plot_time_in_system,
#     plot_service_time_distribution,
#     plot_customers_in_system_over_time,
#     plot_server_status_over_time,
#     plot_waiting_time_boxplot,
#     plot_waiting_time_per_customer
# )

class Result:

    def __init__(self,root):

        self.option = None
        self.iteration_now = IntVar(value=1)
        self.image_label = None
        self.plot = None
        self.my_pic = None
        self.frame_0 = None
        self.frame_3 = None
        self.data = []
        self.root = root
        self.root.title('[ نتائج المحاكاة ]')
        self.root.configure(background="silver")
        self.ws = self.root.winfo_screenwidth()
        pos_x = round((self.ws - 1080) / 2)
        self.hs = self.root.winfo_screenheight()
        pos_y = round((self.hs - 550) / 2)
        self.root.geometry("1080x550+" + str(pos_x) + "+" + str(pos_y))
        self.root.attributes("-topmost", 0)
        self.root.overrideredirect(0)
        self.data.append(pd.read_excel('data/all_data.xlsx', sheet_name='theoretical_stats'))
        self.data.append(pd.read_excel('data/all_data.xlsx', sheet_name='all_stats'))

        self.index=0
        self.itr = len(self.data[1]['total_customer'])
        self.plot_path = None
        a = []
        for _ in range(self.itr):
            a.append(f'{_ + 1}')
        tk.Label(self.root, text='iteration number:', font=('Consolas', 8)).place(x=800, y=20, width=150, height=25)
        self.option = OptionMenu(self.root,self.iteration_now, *a, command=self.update_frame).place(x=955, y=20,
                                                                                                        width=100,
                                                                                                        height=25)
        tk.Label(self.root, text='Theoretical Values:', font=('Consolas', 15, 'bold')).place(x=5,y=5,width=250,height=25)
        tk.Label(self.root, text='queue size(Lq)', font=('Consolas', 8)).place(x=260,y=10,width=100,height=25)
        tk.Label(self.root, text='system people(L)', font=('Consolas', 8)).place(x=365,y=10,width=100,height=25)
        tk.Label(self.root, text='queue time(Wq)', font=('Consolas', 8)).place(x=470,y=10,width=100,height=25)
        tk.Label(self.root, text='system time(W)', font=('Consolas', 8)).place(x=575,y=10,width=100,height=25)
        tk.Label(self.root, text=self.data[0]['queue_size'][0].round(5), font=('Consolas', 8)).place(x=260,y=40,width=100,height=25)
        tk.Label(self.root, text=self.data[0]['system_people'][0].round(5), font=('Consolas', 8)).place(x=365,y=40,width=100,height=25)
        tk.Label(self.root, text=[self.data[0]['queue_time'][0].round(5),'hours'], font=('Consolas', 8)).place(x=470,y=40,width=100,height=25)
        tk.Label(self.root, text=[self.data[0]['system_time'][0].round(5),'hours'], font=('Consolas', 8)).place(x=575,y=40,width=100,height=25)
        tk.Label(self.root, text=[self.data[0]['queue_time(min)'][0].round(5),'minutes'], font=('Consolas', 8)).place(x=470, y=70,width=100,height=25)
        tk.Label(self.root, text=[self.data[0]['system_time(min)'][0].round(5),'minutes'], font=('Consolas', 8)).place(x=575, y=70,width=100,height=25)
        self.start()
    def start(self):
        self.plot_path = [f'plots/arrival_vs_service_{self.iteration_now.get()}.png',
                          f'plots/customers_in_system_over_time_{self.iteration_now.get()}.png',
                          f'plots/free_time_over_time_{self.iteration_now.get()}.png',
                          f'plots/server_status_over_time_{self.iteration_now.get()}.png',
                          f'plots/service_time_distribution_{self.iteration_now.get()}.png',
                          f'plots/time_in_system_per_customer_{self.iteration_now.get()}.png',
                          f'plots/waiting_time_boxplot_{self.iteration_now.get()}.png',
                          f'plots/waiting_time_distribution_{self.iteration_now.get()}.png',
                          f'plots/waiting_time_per_customer_{self.iteration_now.get()}.png',
                          ]
        self.frame_0 = Frame(self.root,bg='white')
        self.frame_0.place(x=5, y=100, width=1070, height=400)
        frame_1 = Frame(self.frame_0,bg='white')
        frame_1.place(x=5,y=0,width=260,height=400)
        tk.Label(frame_1, text='Performance Metrics', font=('Consolas', 15, 'bold')).pack(pady=5)
        tk.Label(frame_1, text='Total Customers', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Total Simulation Time (min)', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Average Waiting Time (min)', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Average Service Time (min)', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Average Time Between Arrivals (min)', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Average Time in System (min)', font=('Consolas',8)).pack(pady=5)
        # tk.Label(frame_1, text='Server Utilization (%)', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Average Idle Time (min)', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='avg Queue Length', font=('Consolas',8)).pack(pady=5)
        tk.Label(frame_1, text='Max Queue Length', font=('Consolas',8)).pack(pady=5)

        frame_2 = Frame(self.frame_0, bg='white')
        frame_2.place(x=260, y=0, width=65, height=400)
        tk.Label(frame_2, text='Results', font=('Consolas', 11, 'bold')).pack(pady=8)
        tk.Label(frame_2, text=self.data[1]['total_customer'][self.iteration_now.get()-1], font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['total_simulation_time'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['queue_time(min)'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['average_service_time(min)'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['average_arrival_time(min)'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['system_time(min)'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        # tk.Label(frame_2, text=self.data[1]['Server Utilization (%)'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['op_free(min)'][self.iteration_now.get()-1].round(2), font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['queue_size'][self.iteration_now.get()-1], font=('Consolas', 8)).pack(pady=5)
        tk.Label(frame_2, text=self.data[1]['max_queue_size'][self.iteration_now.get()-1], font=('Consolas', 8)).pack(pady=5)

        self.frame_3 = Frame(self.frame_0, bg='white')
        self.frame_3.place(x=330, y=0, width=745, height=400)

        self.my_pic = Image.open(self.plot_path[0])
        self.my_pic = self.my_pic.resize((735, 345))
        self.plot = ImageTk.PhotoImage(self.my_pic)
        self.image_label=tk.Label(self.frame_3,image= self.plot)
        self.image_label.place(x=5, y=50 ,width=735, height=345)

        tk.Button(self.root, text="OK", font=('Consolas', 10), command=self.new_sim).place(x=535, y=510, width=100, height=25)
        tk.Button(self.frame_3, text="previous", font=('Consolas', 10), command=lambda: self.update_plot("previous")).place(x=150, y=20, width=100, height=25)
        tk.Button(self.frame_3, text="next", font=('Consolas', 10), command=lambda :self.update_plot("next")).place(x=545, y=20, width=100, height=25)

    def update_plot(self,operation):
        if operation=="next":
           self.index=self.index+1
           if self.index ==9:
               self.index=0
        else:
            self.index = self.index - 1
            if self.index == -9:
                self.index = 0
        self.image_label.destroy()
        self.my_pic = Image.open(self.plot_path[self.index])
        self.my_pic = self.my_pic.resize((735, 345))
        self.plot = ImageTk.PhotoImage(self.my_pic)
        self.image_label = tk.Label(self.frame_3, image=self.plot)
        self.image_label.place(x=5, y=50, width=735, height=345)

    def update_frame(self,event):
        self.frame_0.destroy()
        self.start()
    def new_sim(self):
        root.destroy()
        import main
        root.quit()

root = Tk()
ob = Result(root)
root.mainloop()
