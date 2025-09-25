import sys,os,shutil
import threading
from tkinter import *
from tkinter import  messagebox
import numpy as np
import pandas as pd
import time
import random
import math
from concurrent import futures
import queue


from PIL import Image,ImageTk

import simulation
import visualize

class Client:

    def __init__(self, arrival_time, identifier):
        self.id = identifier
        self.arrival = arrival_time
        self.tec = None
        self.free_time = None
        self.begin_operator = None
        self.end_operator = None
        self.queue_size = None
        self.operator = None



class Operator:

    def __init__(self, identifier, controller):
        self.id = identifier
        self.current = None
        self.controller = controller

    def operator(self):
        while self.controller.operators_on:
            free_time = time.time()
            client = self.controller.arrival_queue.get()
            self.controller.free_op += 1
            free_time = float('%.6f' % (time.time() - free_time))
            self.controller.arrival_data.pop(0)
            self.current = client.id
            # print('operator ', self.id, ' started ', client.id)
            begin_time = time.time()
            client.begin_operator = begin_time - self.controller.system_time
            end_time = self.controller.get_operator_time()
            time.sleep(end_time)
            client.end_operator = client.begin_operator + end_time
            # print('operator ', self.id, ' finished ', client.id)
            client.free_time = free_time
            client.operator = self.id
            self.controller.exit_clients.append(client)
            self.current = None
            free_time = 0
            self.controller.free_op -= 1


def exponential_distribution(mean):
    if mean != 0:
        lambda_ = mean
        return abs(math.log(1 - random.random()) / lambda_)
        # return np.random.exponential(1 / mean)


def normal_distribution(mean, std):
    return np.random.normal(1/mean, std)


def uniform_distribution(mean):
    return np.random.uniform(.1/mean, 1.9/mean)


class Controller:

    def __init__(self):

        random.seed()

        self.system_time = None
        self.system_end_time = None
        self.time_bound = 0
        self.speed = 1
        self.client_count = 0
        self.operators = []
        self.arrival_queue = queue.Queue()
        self.arrival_data = []
        self.exit_clients = []
        self.tes = []
        self.threads = None
        self.arrival_on = False
        self.operators_on = False
        self.stopped_system = False
        self.free_op = 0
        self.iteration =0

        self.arrival_distribution = None
        self.lambda_ = None
        self.std_arr =None
        self.operator_distribution = None
        self.std_op = None
        self.mu_ = None

    def start(self,arrival_distribution, lambda_, std_arr, operator_distribution, mu_, std_op, num_operators,speed,iteration):
        self.arrival_distribution = arrival_distribution
        self.lambda_ = lambda_
        self.std_arr = std_arr
        self.operator_distribution = operator_distribution
        self.mu_ = mu_
        self.std_op = std_op
        self.arrival_on = True
        self.operators_on = True
        self.system_time = time.time()
        self.iteration = iteration
        self.speed = speed
        for i in range(num_operators):
            self.operators.append(Operator(i, self))
        workers = 2 + num_operators
        self.threads = futures.ThreadPoolExecutor(max_workers=workers)

        self.system_time = time.time()
        self.threads.submit(self.arrivals)

        # print('start system')
        for i in range(num_operators):
            # print('start operator', i)
            self.threads.submit(self.operators[i].operator)

    def get_arrival_time(self):
        if self.arrival_distribution == 'Exponential Distribution':
            return exponential_distribution(self.lambda_)
        elif self.arrival_distribution == 'Normal Distribution':
            return normal_distribution(self.lambda_, self.std_arr)
        elif self.arrival_distribution == 'Uniform Distribution':
            return uniform_distribution(self.lambda_)

    def get_operator_time(self):
        if self.operator_distribution == 'Exponential Distribution':
            return exponential_distribution(self.mu_)
        elif self.operator_distribution == 'Normal Distribution':
            return normal_distribution(self.mu_, self.std_op)
        elif self.arrival_distribution == 'Uniform Distribution':
            return uniform_distribution(self.mu_)

    def arrivals(self):
        while self.arrival_on:
            tec = self.get_arrival_time()
            time.sleep(tec)
            tec= tec
            localtime = time.time() - self.system_time
            client = Client(localtime, self.client_count)
            client.tec = tec
            queue_len = len(self.arrival_data)
            client.queue_size = (queue_len + 1) if self.free_op > (len(self.operators) - 1) else queue_len
            # print('Client ', self.client_count, 'join the system')
            self.client_count += 1
            self.arrival_data.append(client.id)
            self.arrival_queue.put(client)

    def report_data(self):
        if not self.stopped_system:
            return 'ERROR - SYSTEM STILL WORKING'
        begin_time = 0
        data = {'client_id': list(), 'arrival_time': list(), 'tec': list(), 'begin_time': list(),
                'end_time': list(),'queue_time': list(), 'service_time': list() , 'system_time': list(),
                'free_time': list(),'arrival_time(min)': list(), 'tec(min)': list(), 'begin_time(min)': list(),
                'end_time(min)': list(),'queue_time(min)': list(), 'service_time(min)': list() ,
                'system_time(min)': list(), 'free_time(min)': list(),'queue_size': list(),'operator_id': list()}
        operator_data = None
        for client in self.exit_clients:
            data['client_id'].append(client.id)
            data['arrival_time'].append(float('%.6f' % client.arrival))
            data['tec'].append(float('%.6f' % client.tec))
            data['begin_time'].append(float('%.6f' % client.begin_operator))
            data['end_time'].append(float('%.6f' % client.end_operator))
            data['queue_time'].append(float('%.6f' % (client.begin_operator - client.arrival)))
            data['service_time'].append(float('%.6f' % (client.end_operator - client.begin_operator)))
            data['system_time'].append(float('%.6f' % (client.end_operator - client.arrival)))
            data['free_time'].append(float('%.6f' % client.free_time))
            data['arrival_time(min)'].append(60 * float('%.6f' % client.arrival))
            data['tec(min)'].append(60 * float('%.6f' % client.tec))
            data['begin_time(min)'].append(60 * float('%.6f' % client.begin_operator))
            data['end_time(min)'].append(60 * float('%.6f' % client.end_operator))
            data['queue_time(min)'].append(60 * float('%.6f' % (client.begin_operator - client.arrival)))
            data['service_time(min)'].append(60 * float('%.6f' % (client.end_operator - client.begin_operator)))
            data['system_time(min)'].append(60 * float('%.6f' % (client.end_operator - client.arrival)))
            data['free_time(min)'].append(60 * float('%.6f' % client.free_time))
            data['queue_size'].append(float('%.6f' % client.queue_size))
            data['operator_id'].append(float('%.6f' % client.operator))
            begin_time = client.end_operator
        data = pd.DataFrame(data)
        data =data.sort_values(by='client_id', ascending=True)
        with pd.ExcelWriter(f'./data/all_data.xlsx',engine='openpyxl',mode='a') as file:
            data.to_excel(file,sheet_name=f'iteration_{self.iteration}',index=False)
        return data

    def stop_system(self):
        self.arrival_on = False
        while self.arrival_queue.qsize() > 0:
            time.sleep(0.3)
        self.operators_on = False
        self.system_end_time = time.time() - self.system_time
        self.stopped_system = True
        time.sleep(5)
        self.threads.shutdown(wait=False)
        return self.report_data()

    def get_status(self):
        data = {'total_clients': self.arrival_queue.qsize(), 'list_clients_id': self.arrival_data}
        for operator in self.operators:
            data['operator' + str(operator.id)] = operator.current if operator.current is not None else 0

        return data


def theoretical_stats(lambda_, mi, s):
    stats = {'queue_size': list(),'system_people': list(),'queue_time': list(),'system_time': list(),
             'queue_time(min)':list(),'system_time(min)':list()}
    ro = lambda_ / (mi * s)
    som = 0
    for i in range(0, s):
        som += (((s * ro) ** i) / math.factorial(i))
    term2 = (((s * ro) ** s) / (math.factorial(s) * (1 - ro)))

    pi0 = 1 / (som + term2)
    pjs = term2 * pi0
    lq = (pjs * ro) / (1 - ro)
    wq = lq / lambda_

    l = lq + (lambda_ / mi)
    w = l / lambda_

    stats['queue_size'].append(lq)
    stats['system_people'].append(l)
    stats['queue_time'].append(wq)
    stats['system_time'].append(w)
    stats['queue_time(min)'].append(wq*60)
    stats['system_time(min)'].append(w*60)

    os.makedirs("data", exist_ok=True)
    stats = pd.DataFrame(stats)
    with pd.ExcelWriter(f'./data/all_data.xlsx',engine='openpyxl') as file:
        stats.to_excel(file, sheet_name=f'theoretical_stats',index=False)

    return stats


def get_stats(stats, data):
    stats['queue_size'].append(float('%.6f'%data['queue_size'].mean()))
    stats['max_queue_size'].append(float('%.6f' % data['queue_size'].max()))
    stats['average_arrival_time'].append(float('%.6f'%data['tec'].mean()))
    stats['average_service_time'].append(float('%.6f'%data['service_time'].mean()))
    stats['system_time'].append(float('%.6f'%data['system_time'].mean()))
    stats['op_free'].append(float('%.6f'%data['free_time'].mean()))
    stats['queue_time'].append(float('%.6f'%data['queue_time'].mean()))
    stats['average_arrival_time(min)'].append(float('%.6f' % data['tec(min)'].mean()))
    stats['average_service_time(min)'].append(float('%.6f' % data['service_time(min)'].mean()))
    stats['system_time(min)'].append(float('%.6f' % data['system_time(min)'].mean()))
    stats['op_free(min)'].append(float('%.6f' % data['free_time(min)'].mean()))
    stats['queue_time(min)'].append(float('%.6f' % data['queue_time(min)'].mean()))
    stats['total_customer'].append(1+data['client_id'].max())
    stats['total_service_time'].append(float('%.6f' % data['service_time(min)'].sum()))
    stats['total_simulation_time'].append(float('%.6f'%data['end_time(min)'].max()))


class Bank:
    def __init__(self,root):

        self.process_thread = None
        self.output_dir = "data"
        os.makedirs(self.output_dir, exist_ok=True)
        self.root= root
        self.root.title('Bank Simulation')
        self.root.configure(background="silver")
        self.ws = self.root.winfo_screenwidth()
        pos_x = round((self.ws - 650) / 2)
        self.hs = self.root.winfo_screenheight()
        pos_y = round((self.hs - 400) / 2)
        self.root.geometry("650x400+" + str(pos_x) + "+" + str(pos_y))
        self.root.attributes("-topmost", 0)
        self.root.overrideredirect(0)
        self.root.resizable(width=False,height=False)
        self.full_data = []
        self.method = ['Exponential Distribution', 'Normal Distribution','Uniform Distribution']
        self.stats = {}

        # _________________ المتغيرات ______________________
        self.arrival_distribution= StringVar()
        self.operator_distribution= StringVar()
        self.num_op = IntVar(value=3)
        self.lambda_ = IntVar(value=42)
        self.mu_ = IntVar(value=16)
        self.std_op = IntVar(value=0)
        self.std_arr = IntVar(value=0)
        self.time_span = DoubleVar(value=11.4)
        self.speed = DoubleVar(value=1)
        self.repeat = IntVar(value=1)


        # _________________ ادوات التحكم ______________________
        self.Button1 = Button(self.root,
                              text="Simulate",
                              bg="#f0f0f0",
                              fg="black",
                              font=("arial", 10),
                              bd=0,
                              activebackground="white",
                              activeforeground="black",
                              relief="flat",
                              command=lambda :self.command_button("simulate")
                              )
        self.Button_1 = Button(self.root,
                              text="Emulate",
                              bg="#f0f0f0",
                              fg="black",
                              font=("arial", 10),
                              bd=0,
                              activebackground="white",
                              activeforeground="black",
                              relief="flat",
                              command=lambda :self.command_button("emulate")
                              )
        self.Button2 = Button(self.root,
                              text="Show results",
                              bg="#f0f0f0",
                              fg="black",
                              font=("arial", 10),
                              bd=0,
                              activebackground="white",
                              activeforeground="black",
                              relief="flat",
                              command=self.show_result
                              )
        self.title= Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="[نظام محاكاة لبنك]",
                            )
        self.Entry1 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.lambda_,
                            highlightthickness=1,
                            show="",
                            )
        self.Label1 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="معدل وصول العملاء في الساعة",
                            )
        self.Entry2 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.mu_,
                            highlightthickness=1,
                            show=""
                            )
        self.Label2 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="معدل الخدمات في الساعة",
                            )
        self.Entry3 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.num_op,
                            highlightthickness=1,
                            show="",
                            )
        self.Label3 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="عدد المشغلين",
                            )
        self.arrival_distribution.set(self.method[0])
        self.operator_distribution.set(self.method[0])
        self.option_1 = OptionMenu(self.root,self.arrival_distribution, *self.method,command=self.get_ar_st)
        self.Label_c1 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="طريقة توزيع وصول العملاء",
                            )
        self.Entry4 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.std_arr,
                            highlightthickness=1,
                            show="",
                            )
        self.Label4 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="الانحراف المعياري",
                            )
        self.option_2 = OptionMenu(self.root,self.operator_distribution, *self.method,command=self.get_op_st)
        self.Label_c2 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="طريقة توزيع تقديم الخدمات",
                            )
        self.Entry5 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.std_op,
                            highlightthickness=1,
                            show="",
                            )
        self.Label5 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="الانحراف المعياري",
                            )
        self.Entry6 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.time_span,
                            highlightthickness=1,
                            show="",
                            )
        self.Label6 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="زمن المحاكاة(دقيقة)",
                            )
        self.Entry_6 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.speed,
                            highlightthickness=1,
                            show="",
                            )
        self.Label_6 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="سرعة المحاكاة",
                            )
        self.Entry7 = Entry(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=2,
                            justify='center',
                            textvariable=self.repeat,
                            highlightthickness=1,
                            show="",
                            )
        self.Label7 = Label(self.root,
                            bg="#f0f0f0",
                            fg="black",
                            font=("arial", 13),
                            bd=0,
                            text="عدد مرات الاعادة",
                            )
        self.loading_label = Label(self.root,
                                   bg='silver',
                                   border=0,
                                   highlightthickness=0,
                                   )

        self.title.pack(fill=X)
        self.Entry1.place(x=240, y=77, width=200, height=26)
        self.Label1.place(x=445, y=77, width=200, height=26)
        self.Entry2.place(x=240, y=114, width=200, height=26)
        self.Label2.place(x=445, y=114, width=200, height=26)
        self.Entry3.place(x=240, y=151, width=200, height=26)
        self.Label3.place(x=445, y=151, width=200, height=26)
        self.option_1.place(x=240, y=188, width=200, height=26)
        self.Label_c1.place(x=445, y=188, width=200, height=26)
        self.option_2.place(x=240, y=225, width=200, height=26)
        self.Label_c2.place(x=445, y=225, width=200, height=26)
        self.Entry6.place(x=240, y=262, width=200, height=26)
        self.Label6.place(x=445, y=262, width=200, height=26)
        self.Entry_6.place(x=10, y=262, width=80, height=26)
        self.Label_6.place(x=100, y=262, width=130, height=26)
        self.Entry7.place(x=240, y=300, width=200, height=26)
        self.Label7.place(x=445, y=300, width=200, height=26)
        self.Button1.place(x=100, y=350, width=100, height=30)

    def command_button(self,s):
        if s == "simulate":
            self.process_thread = futures.ThreadPoolExecutor(max_workers=4)
            self.process_thread.submit(self.loading)
            self.process_thread.submit(lambda :self.run(s))
        else:
            self.run(s)




    def run(self,s):

        operator_no = self.num_op.get()
        arrival_distribution = self.arrival_distribution.get()
        operator_distribution = self.operator_distribution.get()
        lambda_ = int(self.lambda_.get())
        mu_ = int(self.mu_.get())
        std_arr = self.std_arr.get()
        std_op = self.std_op.get()
        time_span = self.time_span.get()
        repeat_itr = self.repeat.get()
        speed = self.speed.get()
        if s == "simulate":
            time_span=time_span/60
            try:
                shutil.rmtree("plots")
                shutil.rmtree("data")
            except OSError as e:
                print(f"Error:{e.filename} - {e.strerror}.")
            self.full_data = []
            self.stats = {'queue_size': list(),'max_queue_size':list(), 'average_arrival_time': list(),
                            'average_service_time': list(),'system_time': list(), 'op_free': list(),
                            'queue_time': list(),'total_customer':list(),'average_arrival_time(min)': list(),
                            'average_service_time(min)': list(),'system_time(min)': list(),'op_free(min)': list(),
                            'queue_time(min)': list(),'total_service_time':list(),'total_simulation_time':list()}  # 'system_people':list()
            if operator_no > 0 and lambda_ > 0 and mu_ > 0 and lambda_ > 0 and time_span > 0 and repeat_itr > 0 and speed >0:
                # ____review_____________________
                if repeat_itr <=3:
                    theoretical_stats(lambda_, mu_, operator_no)

                    if (lambda_ / (mu_ * operator_no)) < 1:
                        for i in range(repeat_itr):
                            controller = Controller()
                            controller.start(arrival_distribution, lambda_, std_arr, operator_distribution, mu_, std_op,
                                             operator_no,speed ,i)
                            time.sleep(time_span)
                            data = controller.stop_system()
                            get_stats(self.stats, data)

                        stats_data = pd.DataFrame(self.stats)
                        with pd.ExcelWriter(f'./data/all_data.xlsx',engine='openpyxl',mode='a') as file:
                            stats_data.to_excel(file, sheet_name=f'all_stats',index=False)
                        plot=visualize.Plots(repeat_itr)
                        plot.run()


                        self.Button1.config(text="new simulation",command= lambda : self.command_button("new"))
                        self.Button_1.place(x=250, y=350, width=100, height=30)
                        self.Button2.place(x=400, y=350, width=100, height=30)
                        self.Entry1.config(state="disabled")
                        self.Entry2.config(state="disabled")
                        self.Entry3.config(state="disabled")
                        self.Entry4.config(state="disabled")
                        self.Entry5.config(state="disabled")
                        self.Entry6.config(state="disabled")
                        self.option_1.config(state="disabled")
                        self.option_2.config(state="disabled")
                        self.Entry7.config(state="disabled")
                        self.loading_label.place_forget()
                        self.process_thread.shutdown(wait=False)

                    else:
                        self.loading_label.place_forget()
                        self.process_thread.shutdown(wait=False)
                        messagebox.showerror("خطأ", "النسبة بين معدل العملاء الى معدل الخدمة يجب ان تكون اقل من الواحد ")

                else:
                    self.loading_label.place_forget()
                    self.process_thread.shutdown(wait=False)
                    messagebox.showerror("خطأ", "اقصى عدد لتكرار المحاكاة 3 مرات ")

            else:
                self.loading_label.place_forget()
                self.process_thread.shutdown(wait=False)
                messagebox.showerror("خطأ", "الرجاء ادخال البيانات الصحيحة")


        elif s == "emulate":
            s = simulation.Simulation(arrival_distribution, lambda_, std_arr, operator_distribution, mu_, std_op,
                                      operator_no, time_span, speed, repeat_itr)
            s.on_start()
            s.simulate()

        elif s== "new":
            self.arrival_distribution.set(self.method[0])
            self.operator_distribution.set(self.method[0])
            self.speed.set(1)
            self.time_span.set(1)
            self.repeat.set(1)
            self.num_op.set(1)
            self.std_op.set(0)
            self.std_arr.set(0)
            self.lambda_.set(0)
            self.mu_.set(0)

            self.Button_1.place_forget()
            self.Button2.place_forget()

            self.Entry1.config(state="normal")
            self.Entry2.config(state="normal")
            self.Entry3.config(state="normal")
            self.Entry4.config(state="normal")
            self.Entry5.config(state="normal")
            self.Entry6.config(state="normal")
            self.Entry_6.config(state="normal")
            self.Entry7.config(state="normal")
            self.option_1.config(state="normal")
            self.option_2.config(state="normal")
            self.Button1.config(text="Simulate",command=lambda: self.command_button("simulate"))

    def get_ar_st(self,event):
        if self.arrival_distribution.get() == self.method[0]or self.arrival_distribution.get() == self.method[2]:
            self.Entry4.place_forget()
            self.Label4.place_forget()
            self.std_arr.set(value=0)
        else:
            self.Entry4.place(x=10, y=188, width=80, height=26)
            self.Label4.place(x=100, y=188, width=130, height=26)

    def get_op_st(self,event):
        if self.operator_distribution.get() == self.method[0] or self.operator_distribution.get() == self.method[2]:
            self.Entry5.place_forget()
            self.Label5.place_forget()
            self.std_op.set(value=0)
        else:
            self.Entry5.place(x=10, y=225, width=80, height=26)
            self.Label5.place(x=100, y=225, width=130, height=26)

    def _get_frames(self,img):
        with Image.open(img) as gif:
            index=0
            frames=[]
            while True:
                try:
                    gif.seek(index)
                    gift = gif.resize((150, 150))
                    frame= ImageTk.PhotoImage(gift)
                    frames.append(frame)
                except EOFError:
                    break

                index +=1
            return frames

    def _play_gif(self,label,frames):

        frame=None
        total_delay = 0
        delay_frames = 100
        for frame in frames:
            root.after(total_delay,self._next_frame,frame,label,frames,False)
            total_delay += delay_frames
        root.after(total_delay, self._next_frame, frame, label, frames, True)

    def _next_frame(self,frame,label,frames,restart):
        if restart:
            self._play_gif(label,frames)
            return
        label.config(
            image=frame
        )

    def loading(self):

        self.loading_label.place(x=25, y=25, width=150, height=150)
        frames=self._get_frames('loading2.gif')
        self._play_gif(self.loading_label,frames)



    def show_result(self):
        root.destroy()
        import result


root = Tk()
a = Bank(root)
root.mainloop()
