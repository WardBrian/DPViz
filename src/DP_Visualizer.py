import tkinter as tk, tkinter.scrolledtext as tkst, tkinter.ttk as ttk
import inspect, time, threading, webbrowser
from rcviz import callgraph
from pygments import lex
from pygments.lexers import PythonLexer
from io import BytesIO
from zoom_advanced3 import CanvasImage

from fib import *
from binom import *
from lis import *
from edit_distance import *

## List of all problems
problems = ["Fibonnaci", "Binomial Coefficient", "Longest Increasing Subsequence", "Edit Distance"]

## Dictionary: Problem -> (ArgType, Args{}, (Functs))
functions = {
    "Fibonnaci": ('int', {'n': (1, 10)}, (fib, fib_iter)),
    "Binomial Coefficient": ('int', {'n': (1, 10),'k': (1, 10)}, (binom, binom_iter)),
    "Longest Increasing Subsequence": ('list', ['Sequence'], ((lis, lis_smaller), lis_iter)),
    "Edit Distance": ('str', ['Word 1', 'Word 2'], (edit_distance, edit_distance_iter))
}
## Dictionary: Problem -> Description
descriptions = {
    "Fibonnaci":
    "\tThe Fibonnaci numbers are a sequence of numbers defined such that each number is the sum of the previous two numbers. Classically calculated recursively, it is very easy to make this problem more efficient by storing all results in a table and calculating them from smallest to largest. As you can see, the table of all the results is much smaller than the recursive tree generated.",
    "Binomial Coefficient":
    "\tThe Binomial Coefficient is the number of ways to pick k things from an n total objects. Most commonly calculated using a simple formula involving factorials, the binomial coefficient can also found using a recursive relation, picking from smaller n. Similar to Fibonacci, we can just remember the options for all n and k up to our desired option, and then we are done! As you can see, the table generated is often far smaller than the number of nodes on the recursive tree.",
    "Longest Increasing Subsequence":
    "\tReturns the length of the longest increasing subsequence of a given sequence such that all of the elements are in increasing order. This can be calculated through a recursive method known as Backtracking, where in each step we try to include the last item in the list or not. We can turn this into a dynamic programming version in the same way as the previous two problems.",
    "Edit Distance":
    "\tReturns the minimum number of edits to convert string 1 into string 2. A specific version of the generalized 'alignment' problem, this can be calculated recursively by checking the final letter of each and then recursing. Like the others, we can remember the results of each subproblem from the smallest to the full problem to calculate this efficiently."
}
## Dictionary: Problem -> Read more link
links = {
    "Fibonnaci": r"http://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf",
    "Binomial Coefficient": r"https://www.geeksforgeeks.org/binomial-coefficient-dp-9/",
    "Longest Increasing Subsequence": r"https://people.eecs.berkeley.edu/~vazirani/algorithms/chap6.pdf#page=2",
    "Edit Distance": r"http://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf#page=15"
}


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_tabs()
        self.create_viz()
        self.reset = True

    def create_tabs(self):
        # Create a ttk notebook object
        self.tabContainer = ttk.Notebook(self.master)

        # Create tabs
        self.tabs = [tk.Frame(self.tabContainer) for _ in problems]
        for i in range(len(problems)):
            self.tabContainer.add(self.tabs[i], text=' ' * 4 + problems[i] + ' ' * 4)

        self.inputs = []

        # Populate Each Tab
        for i in range(len(problems)):
            problem = problems[i]
            frame = self.tabs[i]
            frame.problem = problem
            problem_info = functions[problem]

            # Descriptions
            desc_frame = tk.Frame(frame)
            tk.Label(desc_frame, text=descriptions[problem], wraplength=1100, justify='left').grid(row=0, sticky='new')
            link = tk.Label(desc_frame, text="Want to learn more? Click here!\n", fg='blue', cursor='hand2', justify='center')
            link.grid(row=1, sticky='new')
            link.bind("<Button-1>", self.link_callback)
            desc_frame.grid(row=0, column=0, columnspan=3, sticky='nsew')

            # Labels
            tk.Label(frame, text=f"Recursive {problem}:").grid(row=1, column=0)
            tk.Label(frame, text=f"Dynamic {problem}:").grid(row=1, column=2)

            # Text Boxes to show code
            rec_text = tkst.ScrolledText(frame, height=8, width=60)
            rec_func = problem_info[2][0]
            if type(rec_func) == tuple:  # Special case for LIS
                func1, func2 = rec_func
                code = '\n'.join([inspect.getsource(func)[7:] for func in rec_func])
            else:
                code = inspect.getsource(rec_func)[7:]
            rec_text.insert(tk.END, code)
            rec_text.config(state='disabled')
            rec_text.grid(row=2, column=0)
            highlight(rec_text)

            dp_text = tkst.ScrolledText(frame, height=8, width=60)
            dp_func = problem_info[2][1]
            code = inspect.getsource(dp_func)[7:]
            dp_text.insert(tk.END, code)
            dp_text.config(state='disabled')
            dp_text.grid(row=2, column=2)
            highlight(dp_text)

            # Input Handling

            tk.Label(frame, text="Input:").grid(row=3, column=1, pady=5)
            input_type = problem_info[0]
            input_frame = tk.Frame(frame)
            row = 0
            if input_type == 'int':
                ints = []
                for k, v in problem_info[1].items():
                    label = tk.Label(input_frame, text=k, width=3)
                    scale = tk.Scale(input_frame, from_=v[0], to=v[1], orient=tk.HORIZONTAL, width=15)
                    ints.append(scale)
                    label.grid(row=row, column=0)
                    scale.grid(row=row, column=1, sticky='w')
                    row = row + 1
                self.inputs.append(ints)
            elif input_type == 'str' or input_type == 'list':
                strs = []
                for v in problem_info[1]:
                    label = tk.Label(input_frame, text=v, width=10)
                    text = tk.Entry(input_frame, width=15)
                    strs.append(text)
                    label.grid(row=row, column=0)
                    text.grid(row=row, column=1, pady=2, sticky='w')
                    row = row + 2
                self.inputs.append(strs)

            input_frame.grid(row=4, column=1)

        self.tabContainer.grid(row=0, column=0, columnspan=3)
        # Reset the visualization on tab change
        self.tabContainer.bind('<<NotebookTabChanged>>', self.reset_viz)

    def create_viz(self):
        # Tell grid to keep the recursive and DP sides the same size
        self.master.grid_columnconfigure(0, weight=1, uniform="disp")
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1, uniform="disp")

        # Vizualizer controls
        self.begin_viz = tk.Button(self.master, text='Start Visualization!', command=self.begin_viz, width=15)
        self.begin_viz.grid(row=1, column=1)

        self.clear = tk.Button(self.master, text="Reset Simulation", fg="blue", command=self.reset_viz, width=15)
        self.clear.grid(row=2, column=1, pady=5)

        self.quit = tk.Button(self.master, text="Quit", fg="red", command=self.master.destroy, width=15)
        self.quit.grid(row=3, column=1)

        self.rec_display_label = None
        self.dp_display_loop = None
        self.result_label = None

        # Frame to display the output of the function call
        self.outframe = tk.Frame(self.master)
        tk.Label(self.outframe, text="Output:").grid(row=0, sticky='n')
        self.outframe.grid(row=4, column=1)

    def begin_viz(self):
        # Disable the button once pushed
        self.begin_viz.config(state='disabled')
        # Get our current problem information
        problem_index = self.tabContainer.index('current')
        problem = problems[problem_index]
        problem_info = functions[problem]

        # Input parsing
        if (problem_info[0] == 'list'):
            args = [x.get() for x in self.inputs[problem_index]]
            args = [x.split(',') for x in args]
            args = [[int(x) for x in y] for y in args]
        else:
            args = [x.get() for x in self.inputs[problem_index]]

        # Recursive visualization
        if type(problem_info[2][0]) == tuple:
            func = problem_info[2][0][0]
        else:
            func = problem_info[2][0]

        try:
            t0 = time.perf_counter_ns()
            rec_res = func(*args)
            t1 = time.perf_counter_ns()
            tRec = (t1 - t0) / (10**6)
        except:
            pass
        else:
            img_data = callgraph.render('png')
            self.rec_display_label = CanvasImage(self.master, BytesIO(img_data))
            self.rec_display_label.grid(row=4, column=0, rowspan=4, sticky='nsew')

            self.rec_time_label = tk.Label(self.master, text="Time Elapsed: " + str(tRec) + 'ms', width=40)
            self.rec_time_label.grid(row=3, column=0, sticky='new')

            self.result_label = tk.Label(self.outframe, text=str(rec_res), font=('Courier', 20))
            self.result_label.grid(row=1, sticky='new')

        # DP visualization
        func = problem_info[2][1]

        try:
            t0 = time.perf_counter_ns()
            dp_res = func(*args)
            t1 = time.perf_counter_ns()
            tDP = (t1 - t0) / (10**6)
        except:
            pass
        else:
            self.reset = False
            self.dp_display_loop = threading.Thread(target=self.loop_tables, args=(problem_info[2][1].tables, ), daemon=True)
            self.dp_display_loop.start()

            self.dp_time_label = tk.Label(self.master, text="Time Elapsed: " + str(tDP) + 'ms', width=40)
            self.dp_time_label.grid(row=3, column=2, sticky='new')

    def reset_viz(self, event=None):
        # Tell the thread to complete
        self.reset = True
        # Clear the recursive visualization
        callgraph.reset()
        # Remove any labels if they exist
        if self.rec_display_label:
            self.rec_display_label.grid_forget()
            self.rec_display_label = None
            self.rec_time_label.grid_forget()
            self.result_label.grid_forget()
        if self.dp_display_loop:
            self.dp_time_label.grid_forget()
        else:
            self.begin_viz.config(state='normal')

    def loop_tables(self, tables):
        old_label = None
        i = 0
        length = len(tables)

        # Decide how fast to animate
        if length > 20:
            time_incre = 10 / length
        else:
            time_incre = 0.5
        # Loop an animation
        while (not self.reset):
            table_text = np.array2string(tables[i], formatter={'all': lambda x: f'{x:3}'}, separator=',')
            dp_label = tk.Label(self.master, text=table_text, font=('Courier', 16))
            dp_label.grid(row=4, column=2, sticky='new', rowspan=4)

            if old_label:
                old_label.grid_forget()

            old_label = dp_label

            if i == length - 1:
                time.sleep(1.5)
            else:
                time.sleep(time_incre)

            i = (i + 1) % length

        # Cleanup on loop exit
        if old_label:
            old_label.grid_forget()

        self.begin_viz.config(state='normal')
        self.dp_display_loop = None

    def link_callback(self, event):
        problem = problems[self.tabContainer.index('current')]
        webbrowser.open_new(links[problem])


def highlight(tktextobj):
    # Code highlighting using Pygments
    # Based on https://stackoverflow.com/questions/32058760/improve-pygments-syntax-highlighting-speed-for-tkinter-text
    tktextobj.mark_set("range_start", "1.0")

    data = tktextobj.get("1.0", tk.END)
    for token, content in lex(data, PythonLexer()):
        tktextobj.mark_set("range_end", "range_start + %dc" % len(content))
        tktextobj.tag_add(str(token), "range_start", "range_end")
        tktextobj.mark_set("range_start", "range_end")

    tktextobj.tag_configure("Token.Keyword", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Keyword.Constant", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Keyword.Declaration", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Keyword.Namespace", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Keyword.Pseudo", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Keyword.Reserved", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Keyword.Type", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Name.Class", foreground="#003D99")
    tktextobj.tag_configure("Token.Name.Exception", foreground="#003D99")
    tktextobj.tag_configure("Token.Name.Function", foreground="#003D99")
    tktextobj.tag_configure("Token.Operator.Word", foreground="#CC7A00")
    tktextobj.tag_configure("Token.Comment", foreground="#B80000")
    tktextobj.tag_configure("Token.Literal.String", foreground="#248F24")


# Create the application window
root = tk.Tk()
root.minsize(width=1150, height=650)
root.title("DP Visualizer")
app = Application(master=root)
app.mainloop()
