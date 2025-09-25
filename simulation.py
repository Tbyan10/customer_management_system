import math
import turtle
import time
import random
import pandas as pd

import numpy as np


class Simulation:

    def __init__(self,arrival_distribution, lambda_, std_arr, operator_distribution, mu_, std_op, num_operators,time_span,speed,itr):
        
        
        self.old_last_table = None
        self.last_table = None
        self.data = []
        for _ in range(itr):
            self.data.append(pd.read_excel('data/all_data.xlsx',sheet_name=f'iteration_{_}'))
        self.speed=speed
        self.time_span = time_span
        self.std_op = std_op
        self.std_arr = std_arr
        self.mu_ = mu_/speed
        self.operator_distribution = operator_distribution
        self.lambda_ = lambda_/speed
        self.arrival_distribution = arrival_distribution
        self.processor = None
        self.local_time = 0
        self.end_time = None
        self.begin_time = None
        self.system_time = None
        self.simulation = False
        self.delay = 0.1
        self.wn = turtle.Screen()
        self.wn.title("Bank Simulation")
        self.wn.bgcolor("#000087")
        self.wn.setup(width=600, height=600)  # set_screen_dimension
        self.wn.tracer(0)  # set_delay_for_update_drawing
        self.queue_size = 0
        self.max_queue_size = 0
        self.iteration = []
        self.iteration_but = []
        self.teller = []
        self.table =[]
        self.left_times = []
        self.box = []
        self.tag = []
        self.iteration_now = 0
        self.x_ = 50
        self.x_old = 50
        self.y_ = 0
        self.operator_number = num_operators
        self.customer_number=0
        self.start_text = turtle.Turtle()
        self.start_text.shape("square")
        self.start_text.color("red")
        self.start_text.speed(0)
        self.start_text.penup()
        self.start_text.goto(270, 200)
        self.start_text.hideturtle()
        self.start_text.write("START", align="center", font=("Arial", 10, "bold"))
        self.start = turtle.Turtle()
        self.start.shape("square")
        self.start.color("red")
        self.start.speed(0)
        self.start.penup()
        self.start.goto(270 , 180)
        self.start.onclick(self.start_button)
        self.banner = turtle.Turtle()
        self.banner.shape("square")
        self.banner.color("white")
        self.banner.penup()
        self.banner.speed(0)
        self.banner.hideturtle()
        self.banner.goto(-200,250)
        self.banner.write("Simulation Status", align="center", font=("Arial", 10, "bold"))
        self.timer = turtle.Turtle()
        self.timer.shape("square")
        self.timer.color("white")
        self.timer.penup()
        self.timer.speed(0)
        self.timer.hideturtle()
        self.timer.goto(-80, 250)
        self.timer.write("timer", align="center", font=("Arial", 10, "bold"))
        self.t_timer = turtle.Turtle()
        self.t_timer.shape("square")
        self.t_timer.color("white")
        self.t_timer.penup()
        self.t_timer.speed(0)
        self.t_timer.hideturtle()
        self.t_timer.goto(-40, 250)
        self.t_timer.write("0.00", align="center", font=("Arial", 10, "bold"))


    def draw_customer(self):
        self.customer_number += 1
        new_box = turtle.Turtle()
        shapes = random.choice(['square', 'circle',"triangle"])
        colors =random.choice(["cyan", "orange","black","blue"])
        new_box.shape(shapes)
        new_box.color(colors)
        new_box.speed(0)
        new_box.penup()
        new_box.goto(-200, -270)
        self.box.append([new_box,self.customer_number,float(0),float(0)])
        new_tag = turtle.Turtle()
        new_tag.shape("square")
        new_tag.color("white")
        new_tag.speed(0)
        new_tag.penup()
        new_tag.hideturtle()
        self.tag.append([new_tag, self.customer_number])


    def on_start(self):
        self.draw_teller(self.operator_number)
        self.draw_iteration()
        self.iteration_but[0][self.iteration_now].color("green")

        self.simulate()

    def draw_teller(self,no_teller):
        for i in range(0,no_teller):
            new_teller = turtle.Turtle()
            new_teller.shape("square")
            new_teller.color("white")
            new_teller.speed(0)
            new_teller.penup()
            new_teller.goto(-270 + i * 100, 200)
            new_teller.hideturtle()
            new_teller.write(f"Teller {i + 1}", align="center", font=("Arial", 10, "bold"))
            self.teller.append(new_teller)
            new_table = turtle.Turtle()
            new_table.shape("square")
            new_table.color("red")
            new_table.speed(0)
            new_table.penup()
            new_table.goto(-270 + i * 100, 180)
            self.table.append([new_table,"Busy",f"Teller {i + 1}",None,None,None,0])

    def draw_iteration(self):
        for i in range(0,len(self.data)):
            new_iteration = turtle.Turtle()
            new_iteration.shape("square")
            new_iteration.color("red")
            new_iteration.speed(0)
            new_iteration.penup()
            new_iteration.goto(230 - i * 100, 270)
            new_iteration.hideturtle()
            new_iteration.write(f"iteration {i + 1}", align="center", font=("Arial", 10, "bold"))
            self.iteration.append(new_iteration)
            new_circle = turtle.Turtle()
            new_circle.shape("circle")
            new_circle.color("red")
            new_circle.speed(0)
            new_circle.penup()
            new_circle.goto(230 - i * 100, 250)
            new_circle.onclick(self.set_iteration)
            self.iteration_but.append([new_circle , i])

    def start_button (self, x, y):
        self.run()

    def set_iteration(self,x,y):
        for _ in range(0,len(self.iteration_but)):
            self.iteration_but[_][0].color("red")
        self.iteration_now = int((250-x)//100)
        self.iteration_but[self.iteration_now][0].color("green")

    def run(self):
        self.system_time = time.time()
        if self.start.pencolor() == "red":
            self.queue_size = 0
            self.max_queue_size = 0
            self.left_times = []
            self.box = []
            self.tag = []
            self.x_ = 50
            self.x_old = 50
            self.y_ = 0
            self.last_table = 0
            self.old_last_table = 0
            self.customer_number = 0
            self.start.color("green")
            self.start_text.clear()
            self.start_text.color("green")
            self.start_text.hideturtle()
            self.start_text.write("STOP", align="center", font=("Arial", 10, "bold"))
            for index in range(0,len(self.table)):
                self.table[index][0].color("green")
                self.table[index][1] = "Free"
            self.simulation=True
            self.begin_time = 0
            self.end_time = 0

        else:
            self.start.color("red")
            self.start_text.clear()
            self.start_text.color("red")
            self.start_text.hideturtle()
            self.start_text.write("START", align="center", font=("Arial", 10, "bold"))
            for index in range(0, len(self.table)):
                self.table[index][0].color("red")
                self.table[index][1] = "Busy"
            self.simulation = False

    def simulate(self):
        while True:
            self.wn.update()
            if self.simulation:
                self.move_in_queue()
                self.local_time = time.time() - self.system_time
                for index in range(0, len(self.table)):
                    self.left_times.append(self.table[index][6])
                    if self.local_time >= float(self.table[index][6]) and self.table[index][1] == "Busy":
                        self.table[index][1] = "Free"
                        self.table[index][3].hideturtle()
                        self.table[index][4].clear()

                if self.local_time < 1.25* self.time_span / self.speed:
                    try:
                        tec = self.data[self.iteration_now]['arrival_time(min)'][self.customer_number] / self.speed
                        tes = self.data[self.iteration_now]['end_time(min)'][self.customer_number] / self.speed
                        self.begin_time = tec
                        self.end_time = tes
                        self.on_arrive(tec,tes)
                    except:
                        Exception()
                        self.stop_sys()

                else:
                    self.stop_sys()
            time.sleep(.0001)

    def stop_sys(self):
        if self.local_time > max(self.left_times):
            self.start.color("red")
            self.start_text.clear()
            self.start_text.color("red")
            self.start_text.hideturtle()
            self.start_text.write("START", align="center", font=("Arial", 10, "bold"))
            for index in range(0, len(self.table)):
                self.table[index][0].color("red")
                self.table[index][1] = "Busy"
            self.simulation = False
            self.banner.clear()
            self.banner.write(
                f" Simulation end \n Customer Number:{self.customer_number} \n maximum queue size: {self.max_queue_size} ",
                align="center",
                font=("Arial", 10, "bold"))
            self.timer.clear()
            self.timer.write("time:", align="center", font=("Arial", 10, "bold"))
            self.t_timer.clear()
            self.t_timer.write(f"{round(float(self.local_time), 2)}", align="center", font=("Arial", 10, "bold"))

    def on_arrive(self,tec,tes):
        if self.begin_time <= self.local_time:
            self.draw_customer()
            if len(self.box) == 1:
                self.tag[0][0].goto(-200, 80)
                self.box[0][0].goto(-200, 50)
                self.x_ = 50

            else:
                x_ = self.box[-2][0].xcor()
                y_ = self.box[-2][0].ycor()
                if self.y_ == 0:
                    self.tag[-1][0].goto(x_+self.x_, y_+self.y_+20)
                    self.box[-1][0].goto(x_+self.x_, y_+self.y_)
                else:
                    self.tag[-1][0].goto(x_ + self.x_, y_ + self.y_+20)
                    self.box[-1][0].goto(x_ + self.x_, y_ + self.y_)
                    self.x_ = self.x_old*-1
                    self.y_ = 0
                if  (x_ == 200 and y_%100 == 50
                        or x_ == -150 and y_%100 == 0):
                    self.x_old= self.x_
                    self.x_ = 0
                    self.y_ = self.y_ - 50

            self.tag[-1][0].write(f"{self.tag[-1][1]}" ,align="center", font=("Arial", 10, "bold"))
            self.queue_size += 1
            test= "free"
            for index in range(0, len(self.table)):
                if self.table[index][1] == "Free":
                    test ="free"
                else:
                    test="busy"

            if test == "busy":
                if self.max_queue_size < self.queue_size:
                    self.max_queue_size = self.queue_size

            self.box[-1][2] = self.begin_time
            self.box[-1][3] = self.end_time

    def move_in_queue(self):
        self.timer.clear()
        self.timer.write("time:", align="center", font=("Arial", 10, "bold"))
        self.t_timer.clear()
        self.t_timer.write(f"{round(float(self.local_time), 2)}", align="center", font=("Arial", 10, "bold"))

        for i in range(0, len(self.table)):
            if self.table[i][1]== "Free":
                if len(self.box)>0:
                    self.queue_size -= 1
                    self.tag[0][0].clear()
                    for index in range(len(self.box)-1,0,-1):
                        x=self.box[index-1][0].xcor()
                        y=self.box[index-1][0].ycor()
                        self.tag[index][0].clear()
                        self.tag[index][0].goto(x,y+20)
                        self.tag[index][0].write(f"{self.tag[index][1]}", align="center", font=("Arial", 10, "bold"))
                        self.box[index][0].goto(x,y)

                    self.move_to_teller()
                    self.tag.pop(0)
                    self.box.pop(0)
                else:
                    self.banner.clear()
                    self.banner.write(f"queue size: {self.queue_size}", align="center", font=("Arial", 10, "bold"))
            else:
                self.banner.clear()
                self.banner.write(f"queue size: {self.queue_size}", align="center", font=("Arial", 10, "bold"))

    def move_to_teller(self):
        if self.last_table == len(self.table):
            self.last_table = 0
        for index in range(self.last_table, len(self.table)):
            if self.table[index][1]== "Free":
                self.last_table=index+1
                self.table[index][1] = "Busy"
                x = self.table[index][0].xcor()
                y = self.table[index][0].ycor()
                self.tag[0][0].clear()
                self.table[index][3] = self.box[0][0]
                self.table[index][5] = self.box[0][2]
                self.table[index][6] = self.box[0][3]
                self.table[index][4] = self.tag[0][0]
                self.table[index][4].goto(x, y-50)
                self.table[index][4].write(f"{self.tag[0][1]}", align="center", font=("Arial", 10, "bold"))
                self.table[index][3].goto(x, y-70)
                return
        for index in range(0, len(self.table)):
            if self.table[index][1]== "Free":
                self.table[index][1] = "Busy"
                x = self.table[index][0].xcor()
                y = self.table[index][0].ycor()
                self.tag[0][0].clear()
                self.table[index][3] = self.box[0][0]
                self.table[index][5] = self.box[0][2]
                self.table[index][6] = self.box[0][3]
                self.table[index][4] = self.tag[0][0]
                self.table[index][4].goto(x, y-50)
                self.table[index][4].write(f"{self.tag[0][1]}", align="center", font=("Arial", 10, "bold"))
                self.table[index][3].goto(x, y-70)
                break



    # def exponential_distribution(self, mean):
    #     if mean != 0:
    #         lambda_ =  mean
    #         return abs(math.log(1 - random.random()) / lambda_)
    #
    # def normal_distribution(self,mean, std):
    #     return np.random.normal(mean, std)
    #
    # def uniform_distribution(self,mean):
    #     return np.random.uniform(1, mean * 2 - 1)

    # def get_arrival_time(self):
    #     if self.arrival_distribution == 'Exponential Distribution':
    #         return self.exponential_distribution(self.lambda_)
    #     elif self.arrival_distribution == 'Normal Distribution':
    #         return self.normal_distribution(self.lambda_, self.std_arr)
    #     else:
    #         return self.uniform_distribution(self.lambda_)
    #
    # def get_operator_time(self):
    #     if self.operator_distribution == 'Exponential Distribution':
    #         return self.exponential_distribution(self.mu_)
    #     elif self.operator_distribution == 'Normal Distribution':
    #         return self.normal_distribution(self.mu_, self.std_op)
    #     else:
    #         return self.uniform_distribution(self.mu_)


# def thread_view():
#     s = Simulation()
#     s.on_start()
#     s.simulate()
#
#
# if __name__ == '__main__':
#   turtle.mainloop()
#     thread_view()
