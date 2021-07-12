import numpy as np
from numpy.core.records import array
from numpy.linalg.linalg import norm
import scipy.optimize as opt
import pandas as pd

class ChiSquared():
    def __init__(self):
        self.filenamevar = ""
        self.file2namevar= ""
        self.chosenstar = "     1-cluster fit     "
        self.checked3set = 0
        self.checker1set = 1
        self.checker2set = 1
        self.checker3set = 1
        self.checker4set = 1
        self.sliderval1set = 0
        self.bestnameset = "best_params.csv"
        self.avgnameset = "avg_params.csv"
        self.imgnameset = "plot_so_rowX.png"
        self.rownumberset = ""
        self.dset = "785000"
        self.sliderstring1set = "log-log axes"
        self.ulmethset = "Standard"
        self.model_chosen_set = "UVIT_HST"

        while True:
            self.switch = False
            self.intro_gui()
            self.extract_measured_flux()
            self.extract_ul()
            self.extract_sourceids()
            self.convert_to_AB()
            self.convert_to_bandflux()
            self.import_param_vals()
            self.prepare_for_interpolation()
            self.minimize_chisq()
            self.save_output()
            self.display_all_results()


    
    def intro_gui(self):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        mwin = tk.Tk()
        mwin.geometry("830x550+600+200")
        mwin.title("Maximum Likelihood Fitting")
        mwin.config(bg='LightSteelBlue1')
        mwin.resizable(0,0)

        def collectfilename():
            from tkinter import messagebox
            if user_filename.get() == "":
                tk.messagebox.showinfo('Error', 'Please enter a filename.')
                return None
            elif user_file2name.get() == "":
                tk.messagebox.showinfo('Error', 'Please enter a filename.')
                return None

            if "," in user_rownumber.get():
                        rowlist = user_rownumber.get().split(',')
                        for elem in rowlist:
                            try:
                                rowint = int(elem)
                            except:
                                tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                                return None
                            else:
                                introwlist = [int(i) for i in rowlist]
                                lowestelem = introwlist[0]
                                highestelem = introwlist[-1]

            elif ":" in user_rownumber.get():
                rowlist = user_rownumber.get().split(':')
                for elem in rowlist:
                    try:
                        rowint = int(elem)
                    except:
                        tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                        return None
                    else:
                        import numpy as np
                        introwlist = np.arange(int(rowlist[0]),int(rowlist[-1])+1).tolist()
                        lowestelem = introwlist[0]
                        highestelem = introwlist[-1]
            else:
                try:
                    rowint = int(user_rownumber.get())
                except:
                    tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                    return None
                else:
                    introwlist = [rowint]
                    lowestelem = rowint
                    highestelem = rowint

            try:
                import pandas as pd
                self.measuredata = pd.read_csv("{}".format(user_filename.get(),delimiter=","))
                self.filenamevar = user_filename.get()
            except:
                tk.messagebox.showinfo('Error', "Could not find input file for measured fluxes. Please place the file in the program folder and try again.")
                return None
            try:
                import pandas as pd
                self.disc_params = pd.read_csv("{}".format(user_file2name.get(),delimiter=","))
                if starno_chosen.get() == "     1-cluster fit     ":
                    if "log(Z)" not in self.disc_params:
                        tk.messagebox.showinfo('Error', "Please make sure the parameters file has the correct columns for the fitting method you are trying to use.")
                        return None
                if starno_chosen.get() == "     2-cluster fit     ":
                    if "log(Z_hot)" not in self.disc_params:
                        tk.messagebox.showinfo('Error', "Please make sure the parameters file has the correct columns for the fitting method you are trying to use.")
                        return None
                if starno_chosen.get() == "     3-cluster fit     ":
                    if "log(Z_old_1)" not in self.disc_params:
                        tk.messagebox.showinfo('Error', "Please make sure the parameters file has the correct columns for the fitting method you are trying to use.")
                        return None

                self.file2namevar = user_file2name.get()

            except:
                tk.messagebox.showinfo('Error', "Could not find input file for discrete parameters. Please place the file in the program folder and try again.")
                return None
            else:
                if highestelem > len(self.measuredata)+1 or lowestelem < 2:
                    tk.messagebox.showinfo('Error', "Rows specified are out of range.")
                    return None
                if (checker2.get() == 1 and bestname.get()[-4:] != ".csv") or (checker3.get() == 1 and avgname.get()[-4:] != ".csv"):
                    tk.messagebox.showinfo('Error', "The filenames specified are not allowed. Make sure to use the .csv extension.")
                    return None
                elif checker4.get() == 1 and (imgname.get()[-4:] != ".png" and imgname.get()[-4:] != ".jpg"):
                    tk.messagebox.showinfo('Error', "The filenames specified are not allowed. Make sure to use the .png or .jpg extensions.")
                    return None
                else:
                    try:
                        a = int(bestname.get()[0])
                        b = int(avgname.get()[0])
                        c = int(imgname.get()[0])
                        return None
                    except:
                        try:
                            self.rows = [i-2 for i in introwlist]
                            self.rownumberset = user_rownumber.get()
                            self.dispresults = checker1.get()
                            self.bestchiparams = checker2.get()
                            self.avgchiparams = checker3.get()
                            self.saveplots = checker4.get()
                            self.plotscale = currentsliderval1.get()
                            self.checker1set = checker1.get()
                            self.checker2set = checker2.get()
                            self.checker3set = checker3.get()
                            self.checker4set = checker4.get()
                            self.sliderval1set = currentsliderval1.get()
                            self.sliderstring1set = sliderstring1.get()
                            
                            self.model_chosen = user_model_cho.get()
                            self.model_chosen_set = user_model_cho.get()
                            self.ulmeth = user_ulmeth.get()
                            self.ulmethset = user_ulmeth.get()
                            
                            try:
                                self.d = float(user_d.get())
                                self.dset = user_d.get()
                            except:
                                tk.messagebox.showinfo('Error', "Please enter a number for d.")
                                return None

                            if checker2.get() == 1:
                                self.bestfilename = bestname.get()
                            if checker3.get() == 1:
                                self.avgfilename = avgname.get()
                            if checker4.get() == 1:
                                self.imgfilename = imgname.get()
                            
                            self.single_cluster = False
                            self.double_cluster = False
                            self.triple_cluster = False
                            self.chosenstar = starno_chosen.get()
                            if self.chosenstar == "     1-cluster fit     ":
                                self.single_cluster = True

                            elif self.chosenstar == "     2-cluster fit     ":
                                self.double_cluster = True
                                
                            elif self.chosenstar == "     3-cluster fit     ":
                                self.triple_cluster = True
                        except:
                                tk.messagebox.showinfo('Error', "One or more parameters seem to have been entered incorrectly. Please reenter the values and try again.")
                                return None
                        else:
                            self.switch = True
                            mwin.destroy()
        
        def openrows3():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help", "One of the components of the model flux is an interpolation term that performs a 2-D interpolation inside a grid whose axes are Z and log(age)/10. The term accepts a coordinate (Z, log(age)/10) and returns a flux for every filter, subsequently to be used in calcuating the model flux. One property of the data grid of fluxes is left as a choice to the user: its resolution. The program actually contains two grids which the user can choose between. The finer grid is a 13 X 19 grid, and the coarser grid is a 10 X 16 grid, whose ranges in Z and log(age)/10 are roughly the same. The coarser grid was introduced to prevent the optimizer from getting stuck (as it tends to when performing 2-cluster fits). The lower resolution of the grid seems to help remove any local dips in the fluxes, and makes the 2-D landscape more monotonic.")

        user_rownumber = tk.StringVar()
        user_rownumber.set(self.rownumberset)
        enterrownumberpack = tk.Frame(mwin)
        enterrownumberpack.place(x=37,y=195)
        enterrownumber = tk.Entry(enterrownumberpack,textvariable=user_rownumber,width=12)
        enterrownumber.pack(ipady=3)
        labelwhich = tk.Label(mwin,text="Read rows", bg="LightSteelBlue1")
        labelwhich.place(x=39,y=165)
        def openrows():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help","  •  Use csv row labelling (which should start at row 2)\n\n  •  Specify multiple rows with commas: 2,5,6\n\n  •  Specify a selection of rows with a colon: 3:8")
        def openrows2():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help","The cluster distance d appears as a constant in the model flux formula:\n\nflux_mod = M*interp(age,Z)*(10[pc]/d[pc])^2*10^(-0.4*E(B-V)*(k(λ-V)+R(V)))\n\nNote that d must be in parsecs.")
        whichbutton = tk.Button(mwin,text="?",font=("TimesNewRoman 8"),command = openrows)
        whichbutton.place(x=117,y=196)
        enterdpack = tk.Frame(mwin,bg='LightSteelBlue1')
        enterdpack.place(x=167,y=195)
        user_d = tk.StringVar()
        user_d.set(self.dset)
        enterd = tk.Entry(enterdpack,textvariable=user_d,width=12)
        enterd.pack(ipady=3)
        labelwhat = tk.Label(mwin,text="d",bg="LightSteelBlue1")
        labelwhat.place(x=170,y=165)
        whatbutton = tk.Button(mwin,text="?"  ,font=("TimesNewRoman 8"),command = openrows2)
        whatbutton.place(x=247,y=196)
        canvas2 = tk.Canvas(mwin,relief=tk.RIDGE,bd=2,width=330,height=380,bg='LightSteelBlue2')
        canvas2.place(x=310,y=150)
        starno_chosen = tk.StringVar()
        
        gobutton = tk.Button(mwin,text="Fit data",font=("Arial",10),command = collectfilename,pady=10,padx=25,bd=2)
        gobutton.place(x=680,y=170)
        checker1 = tk.IntVar()
        checker1.set(self.checker1set)
        checker2 = tk.IntVar()
        checker2.set(self.checker2set)
        checker3 = tk.IntVar()
        checker3.set(self.checker3set)
        checker4 = tk.IntVar()
        checker4.set(self.checker4set)
        sliderstring1 = tk.StringVar()
        currentsliderval1 = tk.IntVar()
        currentsliderval1.set(self.sliderval1set)
        bestname = tk.StringVar()
        bestname.set(self.bestnameset)
        avgname = tk.StringVar()
        avgname.set(self.avgnameset)
        imgname = tk.StringVar()
        imgname.set(self.imgnameset)
        sliderstring1.set(self.sliderstring1set)
        def changesliderstring1(useless):
            if currentsliderval1.get() == 1:
                sliderstring1.set(" linear axes  ")
            elif currentsliderval1.get() == 0:
                sliderstring1.set("log-log axes")
        
        def grent1():
            if plotslider1['state'] == tk.NORMAL:
                plotslider1['state'] = tk.DISABLED
                sliderstring1.set("                     ")
                sliderlabel1.config(bg="gray95")
            elif plotslider1['state'] == tk.DISABLED:
                plotslider1['state'] = tk.NORMAL
                sliderlabel1.config(bg="white")
                if currentsliderval1.get() == 1:
                    sliderstring1.set(" linear axes  ")
                elif currentsliderval1.get() == 0:
                    sliderstring1.set("log-log axes")

        def grent2():
            if buttentry2['state'] == tk.NORMAL:
                buttentry2.delete(0,30)
                buttentry2['state'] = tk.DISABLED
            elif buttentry2['state'] == tk.DISABLED:
                buttentry2['state'] = tk.NORMAL
                buttentry2.insert(tk.END,"{}".format(self.bestnameset))
        def grent3():
            if buttentry3['state'] == tk.NORMAL:
                buttentry3.delete(0,30)
                buttentry3['state'] = tk.DISABLED
            elif buttentry3['state'] == tk.DISABLED:
                buttentry3['state'] = tk.NORMAL
                buttentry3.insert(tk.END,"{}".format(self.avgnameset))
        def grent4():
            if buttentry4['state'] == tk.NORMAL:
                buttentry4.delete(0,30)
                buttentry4['state'] = tk.DISABLED
            elif buttentry4['state'] == tk.DISABLED:
                buttentry4['state'] = tk.NORMAL
                buttentry4.insert(tk.END,"{}".format(self.imgnameset))
                
        checkbutt1 = tk.Checkbutton(mwin,text="Display results",variable=checker1,command=grent1,bg='LightSteelBlue2')
        plotslider1 = tk.Scale(mwin,from_=0,to=1,orient=tk.HORIZONTAL,showvalue=0,length=65,width=25,variable=currentsliderval1, command=changesliderstring1)
        plotslider1.place(x=500,y=200)
        grayframe1= tk.Frame(mwin,bg="gray95",bd=3)
        grayframe1.place(x=350,y=200)
        sliderlabel1 = tk.Label(grayframe1,textvariable=sliderstring1,padx=5,bg='white')
        sliderlabel1.pack()
        if currentsliderval1.get() == 0:
            plotslider1.set(0)
        if currentsliderval1 == 1:
            plotslider1.set(1)
        checkbutt2 = tk.Checkbutton(mwin,text="Save best-fit parameter data",variable=checker2,command=grent2,bg='LightSteelBlue2')
        checkbutt3 = tk.Checkbutton(mwin,text="Save averages, variances, and other info",variable=checker3,command=grent3,bg='LightSteelBlue2')
        checkbutt4 = tk.Checkbutton(mwin,text="Save plot images (1 per source X)",variable=checker4,command=grent4,bg='LightSteelBlue2')
        buttentry2 = tk.Entry(mwin, textvariable = bestname,width=26)
        buttentry3 = tk.Entry(mwin, textvariable = avgname,width=26)
        buttentry4 = tk.Entry(mwin,textvariable = imgname,width=26)
        if checker2.get() == 0:
            buttentry2['state'] = tk.DISABLED
        if checker3.get() == 0:
            buttentry3['state'] = tk.DISABLED
        if checker4.get() == 0:
            buttentry4['state'] = tk.DISABLED
        checkbutt1.place(x=340,y=170)
        checkbutt2.place(x=340,y=270)
        checkbutt3.place(x=340,y=365)
        checkbutt4.place(x=340,y=460)
        buttentry2.place(x=345,y=300)
        buttentry3.place(x=345,y=395)
        buttentry4.place(x=345,y=490)

        user_ulmeth = tk.StringVar()
        user_ulmeth.set(self.ulmethset)
        ulmethoptions = ["Standard"]
        labelulmeth = tk.Label(mwin,text="Upper limit calculation method",bg="LightSteelBlue1")
        labelulmeth.place(x=37,y=280)
        ulmethmenu = tk.OptionMenu(mwin,user_ulmeth,*ulmethoptions)
        ulmethmenu.place(x=37,y=310)
        user_model_cho = tk.StringVar()
        user_model_cho.set(self.model_chosen_set)
        modelchooptions = ["UVIT_HST","UVIT_SDSS_Spitzer"]
        modelcholabel = tk.Label(mwin,text="Model data filters",bg="LightSteelBlue1")
        modelcholabel.place(x=38,y=370)
        modelchomenu = tk.OptionMenu(mwin,user_model_cho,*modelchooptions)
        modelchomenu.place(x=32,y=400)
        starlabel = tk.Label(mwin,text="Fitting method",bg="LightSteelBlue1").place(x=38,y=460)
        starno_chosen.set(self.chosenstar)
        staroptions = ["     1-cluster fit     ","     2-cluster fit     ","     3-cluster fit     "]
        starmenu = tk.OptionMenu(mwin,starno_chosen,*staroptions)
        starmenu.place(x=32,y=490)

        user_filename = tk.StringVar()
        user_filename.set(self.filenamevar)
        enterfilename = tk.Entry(mwin,textvariable = user_filename,width=72)
        enterfilename.place(x=224,y=34)
        user_file2name = tk.StringVar()
        user_file2name.set(self.file2namevar)
        enterfile2name = tk.Entry(mwin,textvariable = user_file2name,width=63)
        enterfile2name.place(x=297,y=93)
        labeltop = tk.Label(mwin,text="Input measured flux file: ", bg='white',border=2,relief=tk.RIDGE,padx=6,pady=5)
        labeltop.place(x=35,y=29)
        labelbot = tk.Label(mwin,text="Input non-M parameter values file: ", bg='white',border=2,relief=tk.RIDGE,padx=6,pady=5)
        labelbot.place(x=35,y=89)
        grent2()
        grent2()
        grent3()
        grent3()
        grent4()
        grent4()
        mwin.mainloop()

    def extract_measured_flux(self):

        assert self.switch == True, "Program terminated"
        
        if self.model_chosen == "UVIT_HST":

            import pandas as pd
            import numpy as np
            import tkinter as tk
            
            raw_columns = ["F148W_AB","F148W_err","F169M_AB","F169M_err","F172M_AB","F172M_err","N219M_AB","N219M_err","N279N_AB","N279N_err","f275w_vega","f275w_err","f336w_vega","f336w_err","f475w_vega","f475w_err","f814w_vega","f814w_err","f110w_vega","f110w_err","f160w_vega","f160w_err"]

            self.raw_magnitudes_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.raw_magnitudes_frame["{}".format(rawname)] = ""

            savebadcols = []
            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_columns:
                    try:
                        curr_rowdict[colname] = self.measuredata.at[rowno,colname].item()
                    except:
                        curr_rowdict[colname] = -999
                        savebadcols.append(colname)
                self.raw_magnitudes_frame.loc[self.raw_magnitudes_frame.shape[0]] = curr_rowdict

            savebadcols = list(dict.fromkeys(savebadcols))
            badstr = ""
            for badcol in savebadcols:
                badstr += "{} or ".format(badcol)
            badstr = badstr[:-4]

            if len(badstr) != 0:
                import tkinter as tk
                miniwin = tk.Tk()
                miniwin.geometry("10x10+800+500")
                response = tk.messagebox.askquestion('Warning',"No entries found for {}. Do you wish to proceed?\n\n(These filters will not be fitted. If a single column is missing without its error or vice versa, you should double check the file for naming typos)".format(badstr))
                if response == "yes":
                    miniwin.destroy()
                if response == "no":
                    assert response == "yes", "Program terminated"

            for rowind,row in self.raw_magnitudes_frame.iterrows():
                for colind,colelement in enumerate(row):
                    if colelement == -999:
                        self.raw_magnitudes_frame.iat[rowind,colind] = np.nan

        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            
            import pandas as pd
            import numpy as np
            import tkinter as tk
            
            raw_columns = ["F148W_AB","F148W_err","F169M_AB","F169M_err","F172M_AB","F172M_err","N219M_AB","N219M_err","N279N_AB","N279N_err","u_prime","u_prime_err","g_prime","g_prime_err","r_prime","r_prime_err","i_prime","i_prime_err","z_prime","z_prime_err","IRAC1","IRAC1_err","IRAC2","IRAC2_err"]

            self.raw_magnitudes_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.raw_magnitudes_frame["{}".format(rawname)] = ""

            savebadcols = []
            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_columns:
                    try:
                        curr_rowdict[colname] = self.measuredata.at[rowno,colname].item()
                    except:
                        curr_rowdict[colname] = -999
                        savebadcols.append(colname)
                self.raw_magnitudes_frame.loc[self.raw_magnitudes_frame.shape[0]] = curr_rowdict

            savebadcols = list(dict.fromkeys(savebadcols))
            badstr = ""
            for badcol in savebadcols:
                badstr += "{} or ".format(badcol)
            badstr = badstr[:-4]

            if len(badstr) != 0:
                import tkinter as tk
                miniwin = tk.Tk()
                miniwin.geometry("10x10+800+500")
                response = tk.messagebox.askquestion('Warning',"No entries found for {}. Do you wish to proceed?\n\n(These filters will not be fitted. If a single column is missing without its error or vice versa, you should double check the file for naming typos)".format(badstr))
                if response == "yes":
                    miniwin.destroy()
                if response == "no":
                    assert response == "yes", "Program terminated"

            for rowind,row in self.raw_magnitudes_frame.iterrows():
                for colind,colelement in enumerate(row):
                    if colelement == -999:
                        self.raw_magnitudes_frame.iat[rowind,colind] = np.nan

    def extract_ul(self):

        if self.model_chosen == "UVIT_HST":
            import pandas as pd
            import numpy as np
            import tkinter as tk

            raw_limits = ["F148W_ul","F169M_ul","F172M_ul","N219M_ul","N279N_ul","f275w_ul","f336w_ul","f475w_ul","f814w_ul","f110w_ul","f160w_ul"]
            
            self.ul_frame = pd.DataFrame()
            for rawname in raw_limits:
                self.ul_frame["{}".format(rawname)] = ""

            saverowuls = []
            savecoluls = []
            badcoluls = []
            first_time = True
            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_limits:
                    try:
                        if self.measuredata.at[rowno,colname] == ">":
                            curr_rowdict[colname] = 1
                            savecoluls.append(colname)
                            saverowuls.append(str(rowno+2))
                        else:
                            curr_rowdict[colname] = 0
                    except:
                        curr_rowdict[colname] = np.nan
                        badcoluls.append(colname)
                self.ul_frame.loc[self.ul_frame.shape[0]] = curr_rowdict
                
                if first_time == True and len(badcoluls) > 0:
                    miniwin2 = tk.Tk()
                    miniwin2.geometry("10x10+800+500")
                    savebadcols2 = list(dict.fromkeys(badcoluls))
                    badstr2 = ""
                    for badcol2 in savebadcols2:
                        badstr2 += "{} or ".format(badcol2)
                    badstr2 = badstr2[:-4]
                    response2 = tk.messagebox.askquestion('Warning',"No upper limit columns found for {}. Do you wish to proceed?".format(badstr2))
                    if response2 == "yes":
                        miniwin2.destroy()
                        first_time = False
                    if response2 == "no":
                        assert response2 == "yes", "Program terminated"
            
            if len(savecoluls) > 0:
                miniwin = tk.Tk()
                miniwin.geometry("10x10+800+500")
                response = tk.messagebox.askquestion('Info',"Upper limits detected in columns {} in rows {}, respectively. If this sounds correct, click yes to continue.".format(", ".join(savecoluls),", ".join(saverowuls)))
                if response == "yes":
                    miniwin.destroy()
                if response == "no":
                    assert response == "yes", "Program terminated"
        
        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            import pandas as pd
            import numpy as np

            raw_limits = ["F14_ul","F16_ul","F17_ul","N2_ul","N27_ul","a1_ul","a2_ul","a3_ul","a4_ul","a5_ul","a6_ul","a7_ul"]
            
            self.ul_frame = pd.DataFrame()
            for rawname in raw_limits:
                self.ul_frame["{}".format(rawname)] = ""

            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_limits:
                  curr_rowdict[colname] = 0
                self.ul_frame.loc[self.ul_frame.shape[0]] = curr_rowdict
    
    def extract_sourceids(self):
        self.source_ids = []
        for rowno in self.rows:
            self.source_ids.append(self.measuredata['Source_ID'][rowno])
        
    def convert_to_AB(self):
        if self.model_chosen == "UVIT_HST":
            self.ab_magnitudes_frame = self.raw_magnitudes_frame
            for col in self.ab_magnitudes_frame:
                    if col == "f275w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.496))
                    elif col == "f336w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.188))
                    elif col == "f475w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - 0.091)
                    elif col == "f814w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-0.427))
                    elif col == "f110w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-0.7595))
                    elif col == "f160w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.2514))
            
            self.ab_magnitudes_frame.rename(columns={"f275w_vega" : "f275w_AB", "f336w_vega" : "f336w_AB", "f475w_vega" : "f475w_AB", "f814w_vega" : "f814w_AB", "f110w_vega" : "f110w_AB", "f160w_vega" : "f160w_AB"},inplace=True)
        
        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            pass

    def convert_to_bandflux(self):

        if self.model_chosen == "UVIT_HST":

            self.filternames = ["F148W","F169M","F172M","N219M","N279N","f275w","f336w","f475w","f814w","f110w","f160w"]
            self.bandfluxes = pd.DataFrame()
            self.bandfluxerrors = pd.DataFrame()
            self.avgwvlist = [148.1,160.8,171.7,219.6,279.2,270.4,335.5,477.3,802.4,1153.4,1536.9]
            #self.avgwvlist = [150.2491,161.4697,170.856,199.1508,276.0,267.884375,336.8484,476.0,833.0,1096.7245,1522.1981]
            #self.allextinct = [5.52548923, 5.17258596, 5.0540947, 5.83766858, 3.49917568, 3.25288368, 1.95999799, 0.62151591, -1.44589933, -2.10914243, -2.51310314]
            self.allextinct = [ 5.62427152,  5.18640888,  5.04926289,  6.99406125,  3.15901211,  3.42340971, 1.97787612,  0.61008783, -1.33280758, -2.18810981, -2.52165626]

            for colind,col in enumerate(self.ab_magnitudes_frame):
                if colind%2 == 0:
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: (10**(-0.4*(48.60+x)))*10**26)
                    self.bandfluxes["{}".format(col)] = self.ab_magnitudes_frame[col]
                elif colind%2 != 0:
                    for rowind in range(len(self.ab_magnitudes_frame[col])):
                        self.ab_magnitudes_frame.iloc[rowind,colind] = self.ab_magnitudes_frame.iloc[rowind,colind-1]*self.ab_magnitudes_frame.iloc[rowind,colind]/1.0857
                    self.bandfluxerrors["{}".format(col)] = self.ab_magnitudes_frame[col]
        
        elif self.model_chosen == "UVIT_SDSS_Spitzer":

            self.filternames = ["F148W","F169M","F172M","N219M","N279N","u_prime","g_prime","r_prime","i_prime","z_prime","IRAC1","IRAC2"]
            self.bandfluxes = pd.DataFrame()
            self.bandfluxerrors = pd.DataFrame()
            self.avgwvlist = [150.2491,161.4697,170.856,199.1508,276.0,355.1,468.6,616.6,748,893,3550,4490]
            self.allextinct = [ 5.52548923,  5.17258596,  5.0540947,   5.83766858,  3.25288368,  1.74741802, 0.68710903, -0.42704846, -1.11016491, -1.64589927, -2.89828005, -2.93432827]
            for colind,col in enumerate(self.raw_magnitudes_frame):
                if colind%2 == 0:
                    self.bandfluxes["{}".format(col)] = self.raw_magnitudes_frame[col]
                elif colind%2 != 0:
                    self.bandfluxerrors["{}".format(col)] = self.raw_magnitudes_frame[col]

    def import_param_vals(self):
        import pandas as pd

        if self.single_cluster == True:

            raw_columns = ["log(Z)","log(age)/10","E(B-V)"]

            self.refined_param_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.refined_param_frame["{}".format(rawname)] = ""

            for rowno in range(len(self.disc_params.axes[0])):
                curr_rowdict = {}
                for colname in raw_columns:
                    curr_rowdict[colname] = self.disc_params.at[rowno,colname].item()
                self.refined_param_frame.loc[self.refined_param_frame.shape[0]] = curr_rowdict

        if self.double_cluster == True:

            raw_columns = ["log(Z_hot)","log(Z_cool)","log(age_hot)/10","log(age_cool)/10","E(B-V)_hot","E(B-V)_cool"]

            self.refined_param_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.refined_param_frame["{}".format(rawname)] = ""

            for rowno in range(len(self.disc_params.axes[0])):
                curr_rowdict = {}
                for colname in raw_columns:
                    curr_rowdict[colname] = self.disc_params.at[rowno,colname].item()
                self.refined_param_frame.loc[self.refined_param_frame.shape[0]] = curr_rowdict

        if self.triple_cluster == True:

            raw_columns = ["log(Z_old_1)","log(Z_old_2)","log(Z_new)","log(age_old_1)/10","log(age_old_2)/10","log(age_new)/10","E(B-V)_old","E(B-V)_new"]

            self.refined_param_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.refined_param_frame["{}".format(rawname)] = ""

            for rowno in range(len(self.disc_params.axes[0])):
                curr_rowdict = {}
                for colname in raw_columns:
                    curr_rowdict[colname] = self.disc_params.at[rowno,colname].item()
                self.refined_param_frame.loc[self.refined_param_frame.shape[0]] = curr_rowdict
        
        print(self.refined_param_frame)
        
    def prepare_for_interpolation(self):
        import pandas as pd
        import xarray as xr
        import numpy as np

        if self.model_chosen == "UVIT_HST":

            fluxdata = pd.read_csv("fluxpersolarmassUVIT_HST.csv")
            
            blankdata = np.zeros((13,19,11))

            row=0
            for Z in range(13):
                for age in range(19):
                    for filt in range(11):
                        blankdata[Z,age,filt] = fluxdata.iat[row,filt]
                    row += 1

            filleddata = blankdata

            zcoordlist = [-2.617,-2.36173,-2.11185,-1.86881,-1.62577,-1.37645,-1.12564,-0.87822,-0.63202,-0.38809,-0.14836,0.08353,0.303332]
            agecoordlist = [.66,.68,.70,.72,.74,.76,.78,.80,.82,.84,.86,.88,.90,.92,.94,.96,.98,1.0,1.2]
            filtercoordlist = [0,1,2,3,4,5,6,7,8,9,10]

            self.da = xr.DataArray(filleddata,coords=[("Z",zcoordlist),("Age",agecoordlist),("Filter",filtercoordlist)])

        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            fluxdata = pd.read_csv("fluxpersolarmassSDSS_Spitzer.csv")

            blankdata = np.zeros((13,19,12))

            row=0
            for Z in range(13):
                for age in range(19):
                    for filt in range(12):
                        blankdata[Z,age,filt] = fluxdata.iat[row,filt]
                    row += 1

            filleddata = blankdata

            zcoordlist = [-2.617,-2.36173,-2.11185,-1.86881,-1.62577,-1.37645,-1.12564,-0.87822,-0.63202,-0.38809,-0.14836,0.08353,0.303332]
            agecoordlist = [.66,.68,.70,.72,.74,.76,.78,.80,.82,.84,.86,.88,.90,.92,.94,.96,.98,1.0,1.2]
            filtercoordlist = [0,1,2,3,4,5,6,7,8,9,10,11]

            self.da = xr.DataArray(filleddata,coords=[("Z",zcoordlist),("Age",agecoordlist),("Filter",filtercoordlist)])

    def interpolate(self,Z,age,valid_filters_this_row):
        interpolist = []
        interpolated = self.da.interp(Z = Z, Age = age)
        for valid_filter in valid_filters_this_row:
            interpolist.append(interpolated.sel(Filter = valid_filter).data.item()*10**26)
        return interpolist
    
    def extinction(self,valid_filters_this_row):
        extinctlist = []
        for valid_filter in valid_filters_this_row:
            extinctlist.append(self.allextinct[valid_filter])
        return extinctlist

    def minichisqfunc_single(self,tup,valid_filters_this_row):
        Z,age,M,E_bv, = tup

        bestmodels = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels.append(M*interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        return bestmodels

    def minichisqfunc_double(self,tup,valid_filters_this_row):
        Z1,age1,M1,E_bv1,Z2,age2,M2,E_bv2 = tup

        bestmodels1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels1.append(M1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        bestmodels2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels2.append(M2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))
        
        return bestmodels1,bestmodels2

    def minichisqfunc_triple(self,tup,valid_filters_this_row):
        Z_old_1,age_old_1,M_old_1,E_bv_old,Z_old_2,age_old_2,M_old_2,Z_new,age_new,M_new,E_bv_new = tup

        bestmodels1 = []
        interpolist1 = self.interpolate(Z_old_1,age_old_1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels1.append(M_old_1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist1[i]+3.001))))
        bestmodels2 = []
        interpolist2 = self.interpolate(Z_old_2,age_old_2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels2.append(M_old_2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist2[i]+3.001))))
        bestmodels3 = []
        interpolist3 = self.interpolate(Z_new,age_new,valid_filters_this_row)
        extinctolist3 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels3.append(M_new*interpolist3[i]*(10/self.d)**2*10**(-0.4*(E_bv_new*(extinctolist3[i]+3.001))))

        return bestmodels1,bestmodels2,bestmodels3


    def chisqfunc(self,Z,age,M,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row):
        print("Testing row {} with log(Z), log(age)/10, M, E_bv: ".format(self.rows[curr_row]+2), Z,age,M,E_bv)

        models = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(M*interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 - models[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")

        return chisq

    def Tf(self,Z,age,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row):

        models = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((self.bandfluxes.iat[curr_row,valid_ind]/3*models[i])/((self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf = sum(summands)

        return Tf


    def Tm(self,Z,age,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row):

        models = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append(((models[i])/self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append(((models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm = sum(summands)

        return Tm

    def chisqfunc2(self,Z1,age1,M1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row):
        print("Testing row {} with log(Z1), log(age1)/10, M1, E_bv1, log(Z2), log(age2)/10, M2, E_bv2: ".format(self.rows[curr_row]+2), Z1, age1, M1, E_bv1, Z2, age2, M2, E_bv2)

        models1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(M1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        models2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(M2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models1[i]+models2[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 -models1[i]-models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")
        return chisq

    def Tf1(self,Z1,age1,E_bv1,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((self.bandfluxes.iat[curr_row,valid_ind]/3*models1[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models1[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf1 = sum(summands)
        return Tf1

    def Tf2(self,Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((self.bandfluxes.iat[curr_row,valid_ind]/3*models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models2[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf2 = sum(summands)
        return Tf2

    def Tm11(self,Z1,age1,E_bv1,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models1[i]/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append((models1[i]/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm11 = sum(summands)
        return Tm11

    def Tm12(self,Z1,age1,E_bv1,Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        
        models2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models1[i]*models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((models1[i]*models2[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm12 = sum(summands)
        return Tm12

    def Tm22(self,Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models2[i]/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append((models2[i]/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm22 = sum(summands)
        return Tm22

    def chisqfunc3(self,Z_old_1,age_old_1,M_old_1,E_bv_old,Z_old_2,age_old_2,M_old_2,Z_new,age_new,M_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row):
        print("Testing row {} with log(Z_old_1), log(age_old_1)/10, M_old_1, E(B-V)_old, log(Z_old_2), log(age_old_2)/10, M_old_2, log(Z_new), log(age_new)/10, M_new, E(B-V)_new: ".format(self.rows[curr_row]+2),Z_old_1,age_old_1,M_old_1,E_bv_old,Z_old_2,age_old_2,M_old_2,Z_new,age_new,M_new,E_bv_new)

        models1 = []
        interpolist1 = self.interpolate(Z_old_1,age_old_1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(M_old_1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist1[i]+3.001))))
        models2 = []
        interpolist2 = self.interpolate(Z_old_2,age_old_2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(M_old_2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist2[i]+3.001))))
        models3 = []
        interpolist3 = self.interpolate(Z_new,age_new,valid_filters_this_row)
        extinctolist3 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models3.append(M_new*interpolist3[i]*(10/self.d)**2*10**(-0.4*(E_bv_new*(extinctolist3[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models1[i]+models2[i]+models3[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i]-models3[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 -models1[i]-models2[i]-models3[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i]-models3[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")
        return chisq

    def Tf1a(self,Z_old_1,age_old_1,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z_old_1,age_old_1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist1[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((self.bandfluxes.iat[curr_row,valid_ind]/3*models1[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models1[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf1a = sum(summands)
        return Tf1a

    def Tf2a(self,Z_old_2,age_old_2,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(Z_old_2,age_old_2,valid_filters_this_row)
        extinctolist2 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((self.bandfluxes.iat[curr_row,valid_ind]/3*models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models2[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf2a = sum(summands)
        return Tf2a

    def Tf3a(self,Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row):

        models3 = []
        interpolist3 = self.interpolate(Z_new,age_new,valid_filters_this_row)
        extinctolist3 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models3.append(interpolist3[i]*(10/self.d)**2*10**(-0.4*(E_bv_new*(extinctolist3[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((self.bandfluxes.iat[curr_row,valid_ind]/3*models3[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((self.bandfluxes.iat[curr_row,valid_ind]*models3[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tf3a = sum(summands)
        return Tf3a

    def Tm11a(self,Z_old_1,age_old_1,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z_old_1,age_old_1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist1[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models1[i]/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append((models1[i]/(self.bandfluxerrors.iat[curr_row,valid_ind]))**2)

        Tm11a = sum(summands)
        return Tm11a

    def Tm12a(self,Z_old_1,age_old_1,E_bv_old,Z_old_2,age_old_2,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z_old_1,age_old_1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist1[i]+3.001))))

        models2 = []
        interpolist2 = self.interpolate(Z_old_2,age_old_2,valid_filters_this_row)
        extinctolist2 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models1[i]*models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((models1[i]*models2[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm12a = sum(summands)
        return Tm12a

    def Tm13a(self,Z_old_1,age_old_1,E_bv_old,Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row):

        models1 = []
        interpolist1 = self.interpolate(Z_old_1,age_old_1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist1[i]+3.001))))

        models3 = []
        interpolist3 = self.interpolate(Z_new,age_new,valid_filters_this_row)
        extinctolist3 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models3.append(interpolist3[i]*(10/self.d)**2*10**(-0.4*(E_bv_new*(extinctolist3[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models1[i]*models3[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((models1[i]*models3[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm13a = sum(summands)
        return Tm13a

    def Tm22a(self,Z_old_2,age_old_2,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(Z_old_2,age_old_2,valid_filters_this_row)
        extinctolist2 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models2[i]/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append((models2[i]/(self.bandfluxerrors.iat[curr_row,valid_ind]))**2)

        Tm22a = sum(summands)
        return Tm22a

    def Tm33a(self,Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row):

        models3 = []
        interpolist3 = self.interpolate(Z_new,age_new,valid_filters_this_row)
        extinctolist3 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models3.append(interpolist3[i]*(10/self.d)**2*10**(-0.4*(E_bv_new*(extinctolist3[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models3[i]/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append((models3[i]/(self.bandfluxerrors.iat[curr_row,valid_ind]))**2)

        Tm33a = sum(summands)
        return Tm33a

    def Tm23a(self,Z_old_2,age_old_2,E_bv_old,Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row):

        models2 = []
        interpolist2 = self.interpolate(Z_old_2,age_old_2,valid_filters_this_row)
        extinctolist2 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv_old*(extinctolist2[i]+3.001))))

        models3 = []
        interpolist3 = self.interpolate(Z_new,age_new,valid_filters_this_row)
        extinctolist3 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models3.append(interpolist3[i]*(10/self.d)**2*10**(-0.4*(E_bv_new*(extinctolist3[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Standard":
                    summands.append((models2[i]*models3[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3)**2)
            else:
                summands.append((models2[i]*models3[i])/(self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        Tm23a = sum(summands)
        return Tm23a

    def minimize_chisq(self):
        import numpy as np
        
        if self.single_cluster == True:
            self.bestms = []
            self.bestcoords = []
            self.bestchisqs = []
            self.avglist = []
            self.varilist = []
            self.errlist = []

            for curr_row in range(self.bandfluxes.shape[0]):

                print("\n\n ********************* WORKING ON ROW {} ********************* \n\n".format(curr_row+2))

                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1: 
                        ul_filters_this_row.append(valid_ind)

                Tfsthisrow = []
                Tmsthisrow = []
                msthisrow = []
                coordinatesthisrow = []
                chisqsthisrow = []
                for Z in self.refined_param_frame['log(Z)']:
                    for age in self.refined_param_frame['log(age)/10']:
                        for E_bv in self.refined_param_frame['E(B-V)']:
                            print("------------------------------------------\n")
                            coord = [Z,age,E_bv]
                            print("COORD \n",coord)
                            coordinatesthisrow.append(coord)
                            Tfthiscoord = self.Tf(Z,age,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row)
                            print("TF \n",Tfthiscoord)
                            Tfsthisrow.append(Tfthiscoord)
                            Tmthiscoord = self.Tm(Z,age,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row)
                            print("TM \n",Tmthiscoord)
                            Tmsthisrow.append(Tmthiscoord)
                            mthiscoord = Tfthiscoord/Tmthiscoord
                            print("m \n",mthiscoord)
                            msthisrow.append(mthiscoord)
                            chisqthiscoord = self.chisqfunc(coord[0],coord[1],mthiscoord,coord[2],valid_filters_this_row,ul_filters_this_row,curr_row)
                            print("CHISQ \n",chisqthiscoord)
                            chisqsthisrow.append(chisqthiscoord)
                

                print("CHISTHISROW \n",chisqsthisrow)
                print("BEST INDEX \n",chisqsthisrow.index(min(chisqsthisrow)))
                self.bestchisqs.append(chisqsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST CHIs \n",self.bestchisqs)
                print("msthisrow \n",msthisrow)
                self.bestms.append(msthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST Ms \n",self.bestms)
                self.bestcoords.append(coordinatesthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("coordsthisrow \n",coordinatesthisrow)
                print("BEST Coords \n", self.bestcoords)

                import math

                Z_numer_addends = []
                age_numer_addends = []
                M_numer_addends = []
                E_bv_numer_addends = []
                denom_addends = []
                norm_chisqs = []
                norm_chisqs = [chisq-self.bestchisqs[curr_row] for chisq in chisqsthisrow]
                print("NORM CHISQS \n", norm_chisqs)
                print("\n------------- CALCULATING AVERAGES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,m in zip(norm_chisqs,coordinatesthisrow,msthisrow):
                    print("CHISQ, COORD, M \n", chisq,coord,m)
                    Z_numer_addends.append(math.e**(-chisq/2)*coord[0])
                    age_numer_addends.append(math.e**(-chisq/2)*coord[1])
                    M_numer_addends.append(math.e**(-chisq/2)*m)
                    E_bv_numer_addends.append(math.e**(-chisq/2)*coord[2])
                    denom_addends.append(math.e**(-chisq/2))
                    print("Z NUMERATOR = e^(-chisq/2)*Z \n", Z_numer_addends)
                    print("AGE NUMERATOR = e^(-chisq/2)*age \n", age_numer_addends)
                    print("M NUMERATOR = e^(-chisq/2)*M \n", M_numer_addends)
                    print("E_BV NUMERATOR = e^(-chisq/2)*E_bv \n", E_bv_numer_addends)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends)
                Z_avg = sum(Z_numer_addends)/sum(denom_addends)
                age_avg = sum(age_numer_addends)/sum(denom_addends)
                M_avg = sum(M_numer_addends)/sum(denom_addends)
                E_bv_avg = sum(E_bv_numer_addends)/sum(denom_addends)

                print("Averages for this row: \n",Z_avg,age_avg,M_avg,E_bv_avg)

                Z_numer_addends2 = []
                age_numer_addends2 = []
                M_numer_addends2 = []
                E_bv_numer_addends2 = []
                denom_addends2 = []
                print("\n------------- CALCULATING VARIANCES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,m in zip(norm_chisqs,coordinatesthisrow,msthisrow):
                    print("CHISQ, COORD, M \n", chisq,coord,m)
                    Z_numer_addends2.append(math.e**(-chisq/2)*(coord[0]-Z_avg)**2)
                    age_numer_addends2.append(math.e**(-chisq/2)*(coord[1]-age_avg)**2)
                    M_numer_addends2.append(math.e**(-chisq/2)*(m-M_avg)**2)
                    E_bv_numer_addends2.append(math.e**(-chisq/2)*(coord[2]-E_bv_avg)**2)
                    denom_addends2.append(math.e**(-chisq/2))
                    print("Z NUMERATOR = e^(-chisq/2)*(Z-Zavg)^2 \n", Z_numer_addends2)
                    print("AGE NUMERATOR = e^(-chisq/2)*(age-ageavg)^2 \n", age_numer_addends2)
                    print("M NUMERATOR = e^(-chisq/2)*(M-Mavg)^2 \n", M_numer_addends2)
                    print("E_BV NUMERATOR = e^(-chisq/2)*(E_bv-E_bvavg)^2 \n", E_bv_numer_addends2)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends2)
                Z_vari = sum(Z_numer_addends2)/sum(denom_addends2)
                age_vari = sum(age_numer_addends2)/sum(denom_addends2)
                M_vari = sum(M_numer_addends2)/sum(denom_addends2)
                E_bv_vari = sum(E_bv_numer_addends2)/sum(denom_addends2)

                print("Variances for this row: \n",Z_vari,age_vari,M_vari,E_bv_vari)

                Z_err = math.sqrt(Z_vari)
                age_err = math.sqrt(age_vari)
                M_err = math.sqrt(M_vari)
                E_bv_err = math.sqrt(E_bv_vari)

                print("Errors for this row: \n",Z_err,age_err,M_err,E_bv_err)

                self.avglist.append([Z_avg,age_avg,M_avg,E_bv_avg])
                self.varilist.append([Z_vari,age_vari,M_vari,E_bv_vari])
                self.errlist.append([Z_err,age_err,M_err,E_bv_err])

            print("AVGLIST \n",self.avglist,"\n")
            print("VARILIST \n",self.varilist,"\n")
            print("ERRLIST \n",self.errlist,"\n")

        
        elif self.double_cluster == True:
            from numpy.linalg import solve
            self.bestms = []
            self.bestcoords = []
            self.bestchisqs = []
            self.avglist = []
            self.varilist = []
            self.errlist = []

            for curr_row in range(self.bandfluxes.shape[0]): 

                print("\n\n ********************* WORKING ON ROW {} ********************* \n\n".format(curr_row+2))

                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)

                Tf1sthisrow = []
                Tf2sthisrow = []
                Tm11sthisrow = []
                Tm12sthisrow = []
                Tm22sthisrow = []
                mvectorsthisrow = []
                coordinatesthisrow = []
                chisqsthisrow = []
                for Z1 in self.refined_param_frame['log(Z_hot)']:
                    for Z2 in self.refined_param_frame['log(Z_cool)']:
                        for age1 in self.refined_param_frame['log(age_hot)/10']:
                            for age2 in self.refined_param_frame['log(age_cool)/10']:
                                for E_bv1 in self.refined_param_frame['E(B-V)_hot']:
                                    for E_bv2 in self.refined_param_frame['E(B-V)_cool']:
                                        print("------------------------------------------\n")
                                        coord = [Z1,age1,E_bv1,Z2,age2,E_bv2]
                                        print("COORD \n",coord)
                                        coordinatesthisrow.append(coord)
                                        Tf1thiscoord = self.Tf1(Z1,age1,E_bv1,valid_filters_this_row,ul_filters_this_row,curr_row)
                                        print("TF1 \n",Tf1thiscoord)
                                        Tf1sthisrow.append(Tf1thiscoord)
                                        Tf2thiscoord = self.Tf2(Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)
                                        print("TF2 \n",Tf2thiscoord)
                                        Tf2sthisrow.append(Tf2thiscoord)
                                        Tm11thiscoord = self.Tm11(Z1,age1,E_bv1,valid_filters_this_row,ul_filters_this_row,curr_row)
                                        print("TM11 \n",Tm11thiscoord)
                                        Tm11sthisrow.append(Tm11thiscoord)
                                        Tm12thiscoord = self.Tm12(Z1,age1,E_bv1,Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)
                                        print("TM12 \n",Tm12thiscoord)
                                        Tm12sthisrow.append(Tm12thiscoord)
                                        Tm22thiscoord = self.Tm22(Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)
                                        print("TM22 \n",Tm22thiscoord)
                                        Tm22sthisrow.append(Tm22thiscoord)
                                        matrixA = np.array([[Tm11thiscoord,Tm12thiscoord],[Tm12thiscoord,Tm22thiscoord]])
                                        print("matrixA \n",matrixA)
                                        vectorA = np.array([Tf1thiscoord,Tf2thiscoord])
                                        print("vectorA \n",vectorA)
                                        mvectorthiscoord = solve(matrixA,vectorA)
                                        print("mvector \n",mvectorthiscoord)
                                        mvectorsthisrow.append(mvectorthiscoord)
                                        chisqthiscoord = self.chisqfunc2(coord[0],coord[1],mvectorthiscoord[0],coord[2],coord[3],coord[4],mvectorthiscoord[1],coord[5],valid_filters_this_row,ul_filters_this_row,curr_row)
                                        print("CHISQ \n",chisqthiscoord)
                                        chisqsthisrow.append(chisqthiscoord)
                

                print("CHISTHISROW \n",chisqsthisrow)
                print("BEST INDEX \n",chisqsthisrow.index(min(chisqsthisrow)))
                self.bestchisqs.append(chisqsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST CHIs \n",self.bestchisqs)
                print("mvectorsthisrow \n",mvectorsthisrow)
                self.bestms.append(mvectorsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST Ms \n",self.bestms)
                self.bestcoords.append(coordinatesthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("coordsthisrow \n",coordinatesthisrow)
                print("BEST Coords \n", self.bestcoords)

                import math

                Z1_numer_addends = []
                age1_numer_addends = []
                M1_numer_addends = []
                E_bv1_numer_addends = []
                Z2_numer_addends = []
                age2_numer_addends = []
                M2_numer_addends = []
                E_bv2_numer_addends = []
                denom_addends = []
                norm_chisqs = []
                norm_chisqs = [chisq-self.bestchisqs[curr_row] for chisq in chisqsthisrow]
                print("NORM CHISQS \n", norm_chisqs)
                print("\n------------- CALCULATING AVERAGES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,m in zip(norm_chisqs,coordinatesthisrow,mvectorsthisrow):
                    print("CHISQ, COORD, M \n", chisq,coord,m)
                    Z1_numer_addends.append(math.e**(-chisq/2)*coord[0])
                    age1_numer_addends.append(math.e**(-chisq/2)*coord[1])
                    M1_numer_addends.append(math.e**(-chisq/2)*m[0])
                    E_bv1_numer_addends.append(math.e**(-chisq/2)*coord[2])
                    Z2_numer_addends.append(math.e**(-chisq/2)*coord[3])
                    age2_numer_addends.append(math.e**(-chisq/2)*coord[4])
                    M2_numer_addends.append(math.e**(-chisq/2)*m[1])
                    E_bv2_numer_addends.append(math.e**(-chisq/2)*coord[5])
                    denom_addends.append(math.e**(-chisq/2))
                    print("Z1 NUMERATOR = e^(-chisq/2)*Z1 \n", Z1_numer_addends)
                    print("AGE1 NUMERATOR = e^(-chisq/2)*age1 \n", age1_numer_addends)
                    print("M1 NUMERATOR = e^(-chisq/2)*M1 \n", M1_numer_addends)
                    print("E_BV1 NUMERATOR = e^(-chisq/2)*E_bv1 \n", E_bv1_numer_addends)
                    print("Z2 NUMERATOR = e^(-chisq/2)*Z2 \n", Z2_numer_addends)
                    print("AGE2 NUMERATOR = e^(-chisq/2)*age2 \n", age2_numer_addends)
                    print("M2 NUMERATOR = e^(-chisq/2)*M2 \n", M2_numer_addends)
                    print("E_BV2 NUMERATOR = e^(-chisq/2)*E_bv2 \n", E_bv2_numer_addends)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends)
                Z1_avg = sum(Z1_numer_addends)/sum(denom_addends)
                age1_avg = sum(age1_numer_addends)/sum(denom_addends)
                M1_avg = sum(M1_numer_addends)/sum(denom_addends)
                E_bv1_avg = sum(E_bv1_numer_addends)/sum(denom_addends)
                Z2_avg = sum(Z2_numer_addends)/sum(denom_addends)
                age2_avg = sum(age2_numer_addends)/sum(denom_addends)
                M2_avg = sum(M2_numer_addends)/sum(denom_addends)
                E_bv2_avg = sum(E_bv2_numer_addends)/sum(denom_addends)

                print("Averages for this row: \n",Z1_avg,age1_avg,M1_avg,E_bv1_avg,Z2_avg,age2_avg,M2_avg,E_bv2_avg)

                Z1_numer_addends2 = []
                age1_numer_addends2 = []
                E_bv1_numer_addends2 = []
                M1_numer_addends2 = []
                Z2_numer_addends2 = []
                age2_numer_addends2 = []
                M2_numer_addends2 = []
                E_bv2_numer_addends2 = []
                denom_addends2 = []
                print("\n------------- CALCULATING VARIANCES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,m in zip(norm_chisqs,coordinatesthisrow,mvectorsthisrow):
                    print("CHISQ, COORD, M \n", chisq,coord,m)
                    Z1_numer_addends2.append(math.e**(-chisq/2)*(coord[0]-Z1_avg)**2)
                    age1_numer_addends2.append(math.e**(-chisq/2)*(coord[1]-age1_avg)**2)
                    M1_numer_addends2.append(math.e**(-chisq/2)*(m[0]-M1_avg)**2)
                    E_bv1_numer_addends2.append(math.e**(-chisq/2)*(coord[2]-E_bv1_avg)**2)
                    Z2_numer_addends2.append(math.e**(-chisq/2)*(coord[3]-Z2_avg)**2)
                    age2_numer_addends2.append(math.e**(-chisq/2)*(coord[4]-age2_avg)**2)
                    M2_numer_addends2.append(math.e**(-chisq/2)*(m[1]-M2_avg)**2)
                    E_bv2_numer_addends2.append(math.e**(-chisq/2)*(coord[5]-E_bv2_avg)**2)
                    denom_addends2.append(math.e**(-chisq/2))
                    print("Z1 NUMERATOR = e^(-chisq/2)*(Z1-Zavg)^2 \n", Z1_numer_addends2)
                    print("AGE1 NUMERATOR = e^(-chisq/2)*(age1-ageavg)^2 \n", age1_numer_addends2)
                    print("M1 NUMERATOR = e^(-chisq/2)*(M1-Mavg)^2 \n", M1_numer_addends2)
                    print("E_BV1 NUMERATOR = e^(-chisq/2)*(E_bv1-E_bvavg)^2 \n", E_bv1_numer_addends2)
                    print("Z2 NUMERATOR = e^(-chisq/2)*(Z2-Zavg)^2 \n", Z2_numer_addends2)
                    print("AGE2 NUMERATOR = e^(-chisq/2)*(age2-ageavg)^2 \n", age2_numer_addends2)
                    print("M2 NUMERATOR = e^(-chisq/2)*(M2-Mavg)^2 \n", M2_numer_addends2)
                    print("E_BV2 NUMERATOR = e^(-chisq/2)*(E_bv2-E_bvavg)^2 \n", E_bv2_numer_addends2)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends2)
                Z1_vari = sum(Z1_numer_addends2)/sum(denom_addends2)
                age1_vari = sum(age1_numer_addends2)/sum(denom_addends2)
                M1_vari = sum(M1_numer_addends2)/sum(denom_addends2)
                E_bv1_vari = sum(E_bv1_numer_addends2)/sum(denom_addends2)
                Z2_vari = sum(Z2_numer_addends2)/sum(denom_addends2)
                age2_vari = sum(age2_numer_addends2)/sum(denom_addends2)
                M2_vari = sum(M2_numer_addends2)/sum(denom_addends2)
                E_bv2_vari = sum(E_bv2_numer_addends2)/sum(denom_addends2)

                print("Variances for this row: \n",Z1_vari,age1_vari,M1_vari,E_bv1_vari,Z2_vari,age2_vari,M2_vari,E_bv2_vari)

                Z1_err = math.sqrt(Z1_vari)
                age1_err = math.sqrt(age1_vari)
                M1_err = math.sqrt(M1_vari)
                E_bv1_err = math.sqrt(E_bv1_vari)
                Z2_err = math.sqrt(Z2_vari)
                age2_err = math.sqrt(age2_vari)
                M2_err = math.sqrt(M2_vari)
                E_bv2_err = math.sqrt(E_bv2_vari)

                print("Errors for this row: \n",Z1_err,age1_err,M1_err,E_bv1_err,Z2_err,age2_err,M2_err,E_bv2_err)

                self.avglist.append([Z1_avg,age1_avg,M1_avg,E_bv1_avg,Z2_avg,age2_avg,M2_avg,E_bv2_avg])
                self.varilist.append([Z1_vari,age1_vari,M1_vari,E_bv1_vari,Z2_vari,age2_vari,M2_vari,E_bv2_vari])
                self.errlist.append([Z1_err,age1_err,M1_err,E_bv1_err,Z2_err,age2_err,M2_err,E_bv2_err])

        elif self.triple_cluster == True:
            from numpy.linalg import solve
            self.bestms = []
            self.bestcoords = []
            self.bestchisqs = []
            self.avglist = []
            self.varilist = []
            self.errlist = []

            for curr_row in range(self.bandfluxes.shape[0]): 
            
                print("\n\n ********************* WORKING ON ROW {} ********************* \n\n".format(curr_row+2))
        
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
                
                Tf1asthisrow = []
                Tf2asthisrow = []
                Tf3asthisrow = []
                Tm11asthisrow = []
                Tm12asthisrow = []
                Tm22asthisrow = []
                Tm13asthisrow = []
                Tm23asthisrow = []
                Tm33asthisrow = []
                mvectorsthisrow = []
                coordinatesthisrow = []
                chisqsthisrow = []
                for Z_old_1 in self.refined_param_frame['log(Z_old_1)']:
                    for Z_old_2 in self.refined_param_frame['log(Z_old_2)']:
                        for Z_new in self.refined_param_frame['log(Z_new)']:
                            for age_old_1 in self.refined_param_frame['log(age_old_1)/10']:
                                for age_old_2 in self.refined_param_frame['log(age_old_2)/10']:
                                    for age_new in self.refined_param_frame['log(age_new)/10']:
                                        for E_bv_old in self.refined_param_frame['E(B-V)_old']:
                                            for E_bv_new in self.refined_param_frame['E(B-V)_new']:
                                                print("------------------------------------------\n")
                                                coord = [Z_old_1,age_old_1,E_bv_old,Z_old_2,age_old_2,Z_new,age_new,E_bv_new]
                                                print("COORD \n",coord)
                                                coordinatesthisrow.append(coord)
                                                Tf1athiscoord = self.Tf1a(Z_old_1,age_old_1,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TF1a \n",Tf1athiscoord)
                                                Tf1asthisrow.append(Tf1athiscoord)
                                                Tf2athiscoord = self.Tf2a(Z_old_2,age_old_2,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TF2a \n",Tf2athiscoord)
                                                Tf2asthisrow.append(Tf2athiscoord)
                                                Tf3athiscoord = self.Tf3a(Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TF3a \n",Tf3athiscoord)
                                                Tf3asthisrow.append(Tf3athiscoord)
                                                Tm11athiscoord = self.Tm11(Z_old_1,age_old_1,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TM11a \n",Tm11athiscoord)
                                                Tm11asthisrow.append(Tm11athiscoord)
                                                Tm12athiscoord = self.Tm12a(Z_old_1,age_old_1,E_bv_old,Z_old_2,age_old_2,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TM12a \n",Tm12athiscoord)
                                                Tm12asthisrow.append(Tm12athiscoord)
                                                Tm22athiscoord = self.Tm22a(Z_old_2,age_old_2,E_bv_old,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TM22a \n",Tm22athiscoord)
                                                Tm22asthisrow.append(Tm22athiscoord)
                                                Tm13athiscoord = self.Tm13a(Z_old_1,age_old_1,E_bv_old,Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TM13a \n",Tm13athiscoord)
                                                Tm13asthisrow.append(Tm13athiscoord)
                                                Tm23athiscoord = self.Tm23a(Z_old_2,age_old_2,E_bv_old,Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TM23a \n",Tm23athiscoord)
                                                Tm23asthisrow.append(Tm23athiscoord)
                                                Tm33athiscoord = self.Tm33a(Z_new,age_new,E_bv_new,valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("TM33a \n",Tm33athiscoord)
                                                Tm33asthisrow.append(Tm33athiscoord)
                                                matrixA = np.array([[Tm11athiscoord,Tm12athiscoord,Tm13athiscoord],[Tm12athiscoord,Tm22athiscoord,Tm23athiscoord],[Tm13athiscoord,Tm23athiscoord,Tm33athiscoord]])
                                                print("matrixA \n",matrixA)
                                                vectorA = np.array([Tf1athiscoord,Tf2athiscoord,Tf3athiscoord])
                                                print("vectorA \n",vectorA)
                                                mvectorthiscoord = solve(matrixA,vectorA)
                                                print("mvector \n",mvectorthiscoord)
                                                mvectorsthisrow.append(mvectorthiscoord)
                                                chisqthiscoord = self.chisqfunc3(coord[0],coord[1],mvectorthiscoord[0],coord[2],coord[3],coord[4],mvectorthiscoord[1],coord[5],coord[6],mvectorthiscoord[2],coord[7],valid_filters_this_row,ul_filters_this_row,curr_row)
                                                print("CHISQ \n",chisqthiscoord)
                                                chisqsthisrow.append(chisqthiscoord)
                
                print("CHISTHISROW \n",chisqsthisrow)
                print("BEST INDEX \n",chisqsthisrow.index(min(chisqsthisrow)))
                self.bestchisqs.append(chisqsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST CHIs \n",self.bestchisqs)
                print("mvectorsthisrow \n",mvectorsthisrow)
                self.bestms.append(mvectorsthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("BEST Ms \n",self.bestms)
                self.bestcoords.append(coordinatesthisrow[chisqsthisrow.index(min(chisqsthisrow))])
                print("coordsthisrow \n",coordinatesthisrow)
                print("BEST Coords \n", self.bestcoords)


                import math

                Z_old_1_numer_addends = []
                age_old_1_numer_addends = []
                M_old_1_numer_addends = []
                E_bv_old_numer_addends = []
                Z_old_2_numer_addends = []
                age_old_2_numer_addends = []
                M_old_2_numer_addends = []
                Z_new_numer_addends = []
                age_new_numer_addends = []
                M_new_numer_addends = []
                E_bv_new_numer_addends = []
                denom_addends = []
                norm_chisqs = []
                norm_chisqs = [chisq-self.bestchisqs[curr_row] for chisq in chisqsthisrow]
                print("NORM CHISQS \n", norm_chisqs)
                print("\n------------- CALCULATING AVERAGES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,m in zip(norm_chisqs,coordinatesthisrow,mvectorsthisrow):
                    print("CHISQ, COORD, M \n", chisq,coord,m)
                    Z_old_1_numer_addends.append(math.e**(-chisq/2)*coord[0])
                    age_old_1_numer_addends.append(math.e**(-chisq/2)*coord[1])
                    M_old_1_numer_addends.append(math.e**(-chisq/2)*m[0])
                    E_bv_old_numer_addends.append(math.e**(-chisq/2)*coord[2])
                    Z_old_2_numer_addends.append(math.e**(-chisq/2)*coord[3])
                    age_old_2_numer_addends.append(math.e**(-chisq/2)*coord[4])
                    M_old_2_numer_addends.append(math.e**(-chisq/2)*m[1])
                    Z_new_numer_addends.append(math.e**(-chisq/2)*coord[5])
                    age_new_numer_addends.append(math.e**(-chisq/2)*coord[6])
                    M_new_numer_addends.append(math.e**(-chisq/2)*m[2])
                    E_bv_new_numer_addends.append(math.e**(-chisq/2)*coord[7])
                    denom_addends.append(math.e**(-chisq/2))
                    print("Zold1 NUMERATOR = e^(-chisq/2)*Zold1 \n", Z_old_1_numer_addends)
                    print("AGEold1 NUMERATOR = e^(-chisq/2)*ageold1 \n", age_old_1_numer_addends)
                    print("Mold1 NUMERATOR = e^(-chisq/2)*Mold1 \n", M_old_1_numer_addends)
                    print("E_BVold NUMERATOR = e^(-chisq/2)*E_bvold \n", E_bv_old_numer_addends)
                    print("Zold2 NUMERATOR = e^(-chisq/2)*Zold2 \n", Z_old_2_numer_addends)
                    print("AGEold2 NUMERATOR = e^(-chisq/2)*ageold2 \n", age_old_2_numer_addends)
                    print("Mold2 NUMERATOR = e^(-chisq/2)*Mold2 \n", M_old_2_numer_addends)
                    print("Znew NUMERATOR = e^(-chisq/2)*Znew \n", Z_new_numer_addends)
                    print("AGEnew NUMERATOR = e^(-chisq/2)*agenew \n", age_new_numer_addends)
                    print("Mnew NUMERATOR = e^(-chisq/2)*Mnew \n", M_new_numer_addends)
                    print("E_BVnew NUMERATOR = e^(-chisq/2)*E_bvnew \n", E_bv_new_numer_addends)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends)

                Z_old_1_avg = sum(Z_old_1_numer_addends)/sum(denom_addends)
                age_old_1_avg = sum(age_old_1_numer_addends)/sum(denom_addends)
                M_old_1_avg = sum(M_old_1_numer_addends)/sum(denom_addends)
                E_bv_old_avg = sum(E_bv_old_numer_addends)/sum(denom_addends)
                Z_old_2_avg = sum(Z_old_2_numer_addends)/sum(denom_addends)
                age_old_2_avg = sum(age_old_2_numer_addends)/sum(denom_addends)
                M_old_2_avg = sum(M_old_2_numer_addends)/sum(denom_addends)
                Z_new_avg = sum(Z_new_numer_addends)/sum(denom_addends)
                age_new_avg = sum(age_new_numer_addends)/sum(denom_addends)
                M_new_avg = sum(M_new_numer_addends)/sum(denom_addends)
                E_bv_new_avg = sum(E_bv_new_numer_addends)/sum(denom_addends)

                print("Averages for this row: \n",Z_old_1_avg,age_old_1_avg,M_old_1_avg,E_bv_old_avg,Z_old_2_avg,age_old_2_avg,M_old_2_avg,Z_new_avg,age_new_avg,M_new_avg,E_bv_new_avg)

                Z_old_1_numer_addends2 = []
                age_old_1_numer_addends2 = []
                M_old_1_numer_addends2 = []
                E_bv_old_numer_addends2 = []
                Z_old_2_numer_addends2 = []
                age_old_2_numer_addends2 = []
                M_old_2_numer_addends2 = []
                Z_new_numer_addends2 = []
                age_new_numer_addends2 = []
                M_new_numer_addends2 = []
                E_bv_new_numer_addends2 = []
                denom_addends2 = []
                print("\n------------- CALCULATING VARIANCES USING MAX LIKELIHOOD ---------- \n")
                for chisq,coord,m in zip(norm_chisqs,coordinatesthisrow,mvectorsthisrow):
                    print("CHISQ, COORD, M \n", chisq,coord,m)
                    Z_old_1_numer_addends2.append(math.e**(-chisq/2)*(coord[0]-Z_old_1_avg)**2)
                    age_old_1_numer_addends2.append(math.e**(-chisq/2)*(coord[1]-age_old_1_avg)**2)
                    M_old_1_numer_addends2.append(math.e**(-chisq/2)*(m[0]-M_old_1_avg)**2)
                    E_bv_old_numer_addends2.append(math.e**(-chisq/2)*(coord[2]-E_bv_old_avg)**2)
                    Z_old_2_numer_addends2.append(math.e**(-chisq/2)*(coord[3]-Z_old_2_avg)**2)
                    age_old_2_numer_addends2.append(math.e**(-chisq/2)*(coord[4]-age_old_2_avg)**2)
                    M_old_2_numer_addends2.append(math.e**(-chisq/2)*(m[1]-M_old_2_avg)**2)
                    Z_new_numer_addends2.append(math.e**(-chisq/2)*(coord[5]-Z_new_avg)**2)
                    age_new_numer_addends2.append(math.e**(-chisq/2)*(coord[6]-age_new_avg)**2)
                    M_new_numer_addends2.append(math.e**(-chisq/2)*(m[2]-M_new_avg)**2)
                    E_bv_new_numer_addends2.append(math.e**(-chisq/2)*(coord[7]-E_bv_new_avg)**2)
                    denom_addends2.append(math.e**(-chisq/2))
                    print("Zold1 NUMERATOR = e^(-chisq/2)*(Zold1-Zold1avg)^2 \n", Z_old_1_numer_addends2)
                    print("AGEold1 NUMERATOR = e^(-chisq/2)*(ageold1-ageold1avg)^2 \n", age_old_1_numer_addends2)
                    print("Mold1 NUMERATOR = e^(-chisq/2)*(Mold1-Mold1avg)^2 \n", M_old_1_numer_addends2)
                    print("E_BVold NUMERATOR = e^(-chisq/2)*(E_bvold-E_bvoldavg)^2 \n", E_bv_old_numer_addends2)
                    print("Zold2 NUMERATOR = e^(-chisq/2)*(Zold2-Zold2avg)^2 \n", Z_old_2_numer_addends2)
                    print("AGEold2 NUMERATOR = e^(-chisq/2)*(ageold2-ageold2avg)^2 \n", age_old_2_numer_addends2)
                    print("Mold2 NUMERATOR = e^(-chisq/2)*(Mold2-Mold2avg)^2 \n", M_old_2_numer_addends2)
                    print("Znew NUMERATOR = e^(-chisq/2)*(Znew-Znewavg)^2 \n", Z_new_numer_addends2)
                    print("AGEnew NUMERATOR = e^(-chisq/2)*(agenew-avgenewavg)^2 \n", age_new_numer_addends2)
                    print("Mnew NUMERATOR = e^(-chisq/2)*(Mnew-Mnewavg)^2 \n", M_new_numer_addends2)
                    print("E_BVnew NUMERATOR = e^(-chisq/2)*(E_bvnew-E_bvnewavg)^2 \n", E_bv_new_numer_addends2)
                    print("DENOMINATOR = e^(-chisq/2) \n", denom_addends)
                
                Z_old_1_vari = sum(Z_old_1_numer_addends2)/sum(denom_addends2)
                age_old_1_vari = sum(age_old_1_numer_addends2)/sum(denom_addends2)
                M_old_1_vari = sum(M_old_1_numer_addends2)/sum(denom_addends2)
                E_bv_old_vari = sum(E_bv_old_numer_addends2)/sum(denom_addends2)
                Z_old_2_vari = sum(Z_old_2_numer_addends2)/sum(denom_addends2)
                age_old_2_vari = sum(age_old_2_numer_addends2)/sum(denom_addends2)
                M_old_2_vari = sum(M_old_2_numer_addends2)/sum(denom_addends2)
                Z_new_vari = sum(Z_new_numer_addends2)/sum(denom_addends2)
                age_new_vari = sum(age_new_numer_addends2)/sum(denom_addends2)
                M_new_vari = sum(M_new_numer_addends2)/sum(denom_addends2)
                E_bv_new_vari = sum(E_bv_new_numer_addends2)/sum(denom_addends2)

                print("Variances for this row: \n",Z_old_1_vari,age_old_1_vari,M_old_1_vari,E_bv_old_vari,Z_old_2_vari,age_old_2_vari,M_old_2_vari,Z_new_vari,age_new_vari,M_new_vari,E_bv_new_vari)

                Z_old_1_err = math.sqrt(Z_old_1_vari)
                age_old_1_err = math.sqrt(age_old_1_vari)
                M_old_1_err = math.sqrt(M_old_1_vari)
                E_bv_old_err = math.sqrt(E_bv_old_vari)
                Z_old_2_err = math.sqrt(Z_old_2_vari)
                age_old_2_err = math.sqrt(age_old_2_vari)
                M_old_2_err = math.sqrt(M_old_2_vari)
                Z_new_err = math.sqrt(Z_new_vari)
                age_new_err = math.sqrt(age_new_vari)
                M_new_err = math.sqrt(M_new_vari)
                E_bv_new_err = math.sqrt(E_bv_new_vari)

                print("Errors for this row: \n",Z_old_1_err,age_old_1_err,M_old_1_err,E_bv_old_err,Z_old_2_err,age_old_2_err,M_old_2_err,Z_new_err,age_new_err,M_new_err,E_bv_new_err)

                self.avglist.append([Z_old_1_avg,age_old_1_avg,M_old_1_avg,E_bv_old_avg,Z_old_2_avg,age_old_2_avg,M_old_2_avg,Z_new_avg,age_new_avg,M_new_avg,E_bv_new_avg])
                self.varilist.append([Z_old_1_vari,age_old_1_vari,M_old_1_vari,E_bv_old_vari,Z_old_2_vari,age_old_2_vari,M_old_2_vari,Z_new_vari,age_new_vari,M_new_vari,E_bv_new_vari])
                self.errlist.append([Z_old_1_err,age_old_1_err,M_old_1_err,E_bv_old_err,Z_old_2_err,age_old_2_err,M_old_2_err,Z_new_err,age_new_err,M_new_err,E_bv_new_err])

    def display_all_results(self):
        if self.dispresults == 1:
            if self.single_cluster == True:
                for curr_row in range(self.bandfluxes.shape[0]):
                    self.display_results_single(curr_row)
            elif self.double_cluster == True:
                for curr_row in range(self.bandfluxes.shape[0]): 
                    self.display_results_double(curr_row)
            elif self.triple_cluster == True:
                for curr_row in range(self.bandfluxes.shape[0]): 
                    self.display_results_triple(curr_row)

    def save_output(self):

        import numpy as np
        import pandas as pd
        
        if self.single_cluster == True:

            models = self.bandfluxes.copy(deep=True)
            self.truefluxerrors = self.bandfluxerrors.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)

                best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestms[curr_row],self.bestcoords[curr_row][2])
                model = self.minichisqfunc_single(best_tup,valid_filters_this_row)
                used = 0 
                for colno,col in enumerate(models.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        models.iat[curr_row,colno] = model[used]
                        used += 1
                
                for colno, arraytup in enumerate(zip(self.bandfluxerrors.loc[curr_row,:],self.ul_frame.loc[curr_row,:],self.bandfluxes.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        self.truefluxerrors.iat[curr_row,colno] = (arraytup[0])
                    if arraytup[1] == 1:
                        if self.ulmeth == "Limit":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[0]*-3)
                        elif self.ulmeth == "Standard":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[2]*-1/3)
            

            if self.bestchiparams == 1:
    
                colnames = {'Source_ID' : [], "Chi^2_best" : [], "log(Z)_best" : [], "log(age)/10_best" : [], "M_best" : [], "E(B-V)_best" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_best" : self.bestchisqs[curr_row], "log(Z)_best" : self.bestcoords[curr_row][0], "log(age)/10_best" : self.bestcoords[curr_row][1], "M_best" : self.bestms[curr_row], "E(B-V)_best" : self.bestcoords[curr_row][2]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.bestfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            if self.avgchiparams == 1:

                if self.model_chosen == "UVIT_HST":        
                    colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(Z)_avg" : [], "log(age)/10_avg" : [], "M_avg" : [], "E(B-V)_avg" : [], "log(Z)_vari" : [], "log(age)/10_vari" : [], "M_vari" : [], "E(B-V)_vari" : [], "log(Z)_err" : [], "log(age)/10_err" : [], "M_err" : [], "E(B-V)_err" : [], "F148W_model_flux_AvgParams [mJy]" : [], "F169M_model_flux_AvgParams [mJy]" : [], "F172M_model_flux_AvgParams [mJy]" : [], "N219M_model_flux_AvgParams [mJy]" : [], "N279N_model_flux_AvgParams [mJy]" : [], "f275w_model_flux_AvgParams [mJy]" : [], "f336w_model_flux_AvgParams [mJy]" : [], "f475w_model_flux_AvgParams [mJy]" : [], "f814w_model_flux_AvgParams [mJy]" : [], "f110w_model_flux_AvgParams [mJy]" : [], "f160w_model_flux_AvgParams [mJy]" : []}
                elif self.model_chosen == "UVIT_SDSS_Spitzer":
                    colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(Z)_avg" : [], "log(age)/10_avg" : [], "M_avg" : [], "E(B-V)_avg" : [], "log(Z)_vari" : [], "log(age)/10_vari" : [], "M_vari" : [], "E(B-V)_vari" : [], "log(Z)_err" : [], "log(age)/10_err" : [], "M_err" : [], "E(B-V)_err" : [], "F148W_model_flux_AvgParams [mJy]" : [], "F169M_model_flux_AvgParams [mJy]" : [], "F172M_model_flux_AvgParams [mJy]" : [], "N219M_model_flux_AvgParams [mJy]" : [], "N279N_model_flux_AvgParams [mJy]" : [], "u_prime_model_flux_AvgParams [mJy]" : [], "g_prime_model_flux_AvgParams [mJy]" : [], "r_prime_model_flux_AvgParams [mJy]" : [], "i_prime_model_flux_AvgParams [mJy]" : [], "z_prime_model_flux_AvgParams [mJy]" : [], "IRAC1_model_flux_AvgParams [mJy]" : [], "IRAC2_model_flux_AvgParams [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    valid_filters_this_row = []
                    for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                        if np.isnan(bflux) == False:
                            valid_filters_this_row.append(valid_ind)
                    if self.model_chosen == "UVIT_HST":
                        print("Running chisqfunc with average parameters to get Chi^2_avg to save in output.")
                        rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],valid_filters_this_row,ul_filters_this_row,curr_row), "log(Z)_avg" : self.avglist[curr_row][0], "log(age)/10_avg" : self.avglist[curr_row][1], "M_avg" : self.avglist[curr_row][2], "E(B-V)_avg" : self.avglist[curr_row][3], "log(Z)_vari" : self.varilist[curr_row][0], "log(age)/10_vari" : self.varilist[curr_row][1], "M_vari" : self.varilist[curr_row][2], "E(B-V)_vari" : self.varilist[curr_row][3], "log(Z)_err" : self.errlist[curr_row][0], "log(age)/10_err" : self.errlist[curr_row][1], "M_err" : self.errlist[curr_row][2], "E(B-V)_err" : self.errlist[curr_row][3], "F148W_model_flux_AvgParams [mJy]" : models.iat[curr_row,0], "F169M_model_flux_AvgParams [mJy]" : models.iat[curr_row,1], "F172M_model_flux_AvgParams [mJy]" : models.iat[curr_row,2], "N219M_model_flux_AvgParams [mJy]" : models.iat[curr_row,3], "N279N_model_flux_AvgParams [mJy]" : models.iat[curr_row,4], "f275w_model_flux_AvgParams [mJy]" : models.iat[curr_row,5], "f336w_model_flux_AvgParams [mJy]" : models.iat[curr_row,6], "f475w_model_flux_AvgParams [mJy]" : models.iat[curr_row,7], "f814w_model_flux_AvgParams [mJy]" : models.iat[curr_row,8], "f110w_model_flux_AvgParams [mJy]" : models.iat[curr_row,9], "f160w_model_flux_AvgParams [mJy]" : models.iat[curr_row,10]}
                    elif self.model_chosen == "UVIT_SDSS_Spitzer": 
                        print("Running chisqfunc with average parameters to get Chi^2_avg to save in output.")
                        rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],valid_filters_this_row,ul_filters_this_row,curr_row), "log(Z)_avg" : self.avglist[curr_row][0], "log(age)/10_avg" : self.avglist[curr_row][1], "M_avg" : self.avglist[curr_row][2], "E(B-V)_avg" : self.avglist[curr_row][3], "log(Z)_vari" : self.varilist[curr_row][0], "log(age)/10_vari" : self.varilist[curr_row][1], "M_vari" : self.varilist[curr_row][2], "E(B-V)_vari" : self.varilist[curr_row][3], "log(Z)_err" : self.errlist[curr_row][0], "log(age)/10_err" : self.errlist[curr_row][1], "M_err" : self.errlist[curr_row][2], "E(B-V)_err" : self.errlist[curr_row][3], "F148W_model_flux_AvgParams [mJy]" : models.iat[curr_row,0], "F169M_model_flux_AvgParams [mJy]" : models.iat[curr_row,1], "F172M_model_flux_AvgParams [mJy]" : models.iat[curr_row,2], "N219M_model_flux_AvgParams [mJy]" : models.iat[curr_row,3], "N279N_model_flux_AvgParams [mJy]" : models.iat[curr_row,4], "u_prime_model_flux_AvgParams [mJy]" : models.iat[curr_row,5], "g_prime_model_flux_AvgParams [mJy]" : models.iat[curr_row,6], "r_prime_model_flux_AvgParams [mJy]" : models.iat[curr_row,7], "i_prime_model_flux_AvgParams [mJy]" : models.iat[curr_row,8], "z_prime_model_flux_AvgParams [mJy]" : models.iat[curr_row,9], "IRAC1_model_flux_AvgParams [mJy]" : models.iat[curr_row,10], "IRAC2_model_flux_AvgParams [mJy]" : models.iat[curr_row,11]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.avgfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            
        elif self.double_cluster == True:

            hotmodels = self.bandfluxes.copy(deep=True)
            coolmodels = self.bandfluxes.copy(deep=True)
            self.truefluxerrors = self.bandfluxerrors.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
    
                best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestms[curr_row][0],self.bestcoords[curr_row][2],self.bestcoords[curr_row][3],self.bestcoords[curr_row][4],self.bestms[curr_row][1],self.bestcoords[curr_row][5])
                hot,cool = self.minichisqfunc_double(best_tup,valid_filters_this_row)
                usedhot = 0
                usedcool = 0
                for colno,col in enumerate(hotmodels.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        hotmodels.iat[curr_row,colno] = hot[usedhot]
                        usedhot += 1
                for colno,col in enumerate(coolmodels.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        coolmodels.iat[curr_row,colno] = cool[usedcool]
                        usedcool += 1

                for colno, arraytup in enumerate(zip(self.bandfluxerrors.loc[curr_row,:],self.ul_frame.loc[curr_row,:],self.bandfluxes.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        self.truefluxerrors.iat[curr_row,colno] = (arraytup[0])
                    if arraytup[1] == 1:
                        if self.ulmeth == "Limit":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[0]*-3)
                        elif self.ulmeth == "Standard":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[2]*-1/3)


            if self.bestchiparams == 1:
    
                colnames = {'Source_ID' : [], "Chi^2_best" : [], "log(Z_hot)_best" : [], "log(age_hot)/10_best" : [], "M_hot_best" : [], "E(B-V)_hot_best" : [], "log(Z_cool)_best" : [], "log(age_cool)/10_best" : [], "M_cool_best" : [], "E(B-V)_cool_best" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_best" : self.bestchisqs[curr_row], "log(Z_hot)_best" : self.bestcoords[curr_row][0], "log(age_hot)/10_best" : self.bestcoords[curr_row][1], "M_hot_best" : self.bestms[curr_row][0], "E(B-V)_hot_best" : self.bestcoords[curr_row][2], "log(Z_cool)_best" : self.bestcoords[curr_row][3], "log(age_cool)/10_best" : self.bestcoords[curr_row][4], "M_cool_best" : self.bestms[curr_row][1], "E(B-V)_cool_best" : self.bestcoords[curr_row][5]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.bestfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            if self.avgchiparams == 1:

                if self.model_chosen == "UVIT_HST":        
                    colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(Z_hot)_avg" : [], "log(age_hot)/10_avg" : [], "M_hot_avg" : [], "E(B-V)_hot_avg" : [], "log(Z_cool)_avg" : [], "log(age_cool)/10_avg" : [], "M_cool_avg" : [], "E(B-V)_cool_avg" : [], "log(Z_hot)_vari" : [], "log(age_hot)/10_vari" : [], "M_hot_vari" : [], "E(B-V)_hot_vari" : [], "log(Z_cool)_vari" : [], "log(age_cool)/10_vari" : [], "M_cool_vari" : [], "E(B-V)_cool_vari" : [], "log(Z_hot)_err" : [], "log(age_hot)/10_err" : [], "M_hot_err" : [], "E(B-V)_hot_err" : [], "log(Z_cool)_err" : [], "log(age_cool)/10_err" : [], "M_cool_err" : [], "E(B-V)_cool_err" : [], "F148W_hot_flux_AvgParams [mJy]" : [], "F148W_cool_flux_AvgParams [mJy]" : [], "F169M_hot_flux_AvgParams [mJy]" : [], "F169M_cool_flux_AvgParams [mJy]" : [], "F172M_hot_flux_AvgParams [mJy]" : [], "F172M_cool_flux_AvgParams [mJy]" : [], "N219M_hot_flux_AvgParams [mJy]" : [], "N219M_cool_flux_AvgParams [mJy]" : [], "N279N_hot_flux_AvgParams [mJy]" : [], "N279N_cool_flux_AvgParams [mJy]" : [], "f275w_hot_flux_AvgParams [mJy]" : [], "f275w_cool_flux_AvgParams [mJy]" : [], "f336w_hot_flux_AvgParams [mJy]" : [], "f336w_cool_flux_AvgParams [mJy]" : [], "f475w_hot_flux_AvgParams [mJy]" : [], "f475w_cool_flux_AvgParams [mJy]" : [], "f814w_hot_flux_AvgParams [mJy]" : [], "f814w_cool_flux_AvgParams [mJy]" : [], "f110w_hot_flux_AvgParams [mJy]" : [], "f110w_cool_flux_AvgParams [mJy]" : [], "f160w_hot_flux_AvgParams [mJy]" : [], "f160w_cool_flux_AvgParams [mJy]" : []}
                elif self.model_chosen == "UVIT_SDSS_Spitzer":
                    colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(Z_hot)_avg" : [], "log(age_hot)/10_avg" : [], "M_hot_avg" : [], "E(B-V)_hot_avg" : [], "log(Z_cool)_avg" : [], "log(age_cool)/10_avg" : [], "M_cool_avg" : [], "E(B-V)_cool_avg" : [], "log(Z_hot)_vari" : [], "log(age_hot)/10_vari" : [], "M_hot_vari" : [], "E(B-V)_hot_vari" : [], "log(Z_cool)_vari" : [], "log(age_cool)/10_vari" : [], "M_cool_vari" : [], "E(B-V)_cool_vari" : [], "log(Z_hot)_err" : [], "log(age_hot)/10_err" : [], "M_hot_err" : [], "E(B-V)_hot_err" : [], "log(Z_cool)_err" : [], "log(age_cool)/10_err" : [], "M_cool_err" : [], "E(B-V)_cool_err" : [], "F148W_hot_flux_AvgParams [mJy]" : [], "F148W_cool_flux_AvgParams [mJy]" : [], "F169M_hot_flux_AvgParams [mJy]" : [], "F169M_cool_flux_AvgParams [mJy]" : [], "F172M_hot_flux_AvgParams [mJy]" : [], "F172M_cool_flux_AvgParams [mJy]" : [], "N219M_hot_flux_AvgParams [mJy]" : [], "N219M_cool_flux_AvgParams [mJy]" : [], "N279N_hot_flux_AvgParams [mJy]" : [], "N279N_cool_flux_AvgParams [mJy]" : [], "u_prime_hot_flux_AvgParams [mJy]" : [], "u_prime_cool_flux_AvgParams [mJy]" : [], "g_prime_hot_flux_AvgParams [mJy]" : [], "g_prime_cool_flux_AvgParams [mJy]" : [], "r_prime_hot_flux_AvgParams [mJy]" : [], "r_prime_cool_flux_AvgParams [mJy]" : [], "i_prime_hot_flux_AvgParams [mJy]" : [], "i_prime_cool_flux_AvgParams [mJy]" : [], "z_prime_hot_flux_AvgParams [mJy]" : [], "z_prime_cool_flux_AvgParams [mJy]" : [], "IRAC1_hot_flux_AvgParams [mJy]" : [], "IRAC1_cool_flux_AvgParams [mJy]" : [],"IRAC2_hot_flux_AvgParams [mJy]" : [], "IRAC2_cool_flux_AvgParams [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    valid_filters_this_row = []
                    for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                        if np.isnan(bflux) == False:
                            valid_filters_this_row.append(valid_ind)
                    if self.model_chosen == "UVIT_HST":
                        print("Running chisqfunc2 with average parameters to get Chi^2_avg to save in output.") 
                        rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc2(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],valid_filters_this_row,ul_filters_this_row,curr_row), "log(Z_hot)_avg" : self.avglist[curr_row][0], "log(age_hot)/10_avg" : self.avglist[curr_row][1], "M_hot_avg" : self.avglist[curr_row][2], "E(B-V)_hot_avg" : self.avglist[curr_row][3], "log(Z_cool)_avg" : self.avglist[curr_row][4], "log(age_cool)/10_avg" : self.avglist[curr_row][5], "M_cool_avg" : self.avglist[curr_row][6], "E(B-V)_cool_avg" : self.avglist[curr_row][7], "log(Z_hot)_vari" : self.varilist[curr_row][0], "log(age_hot)/10_vari" : self.varilist[curr_row][1], "M_hot_vari" : self.varilist[curr_row][2], "E(B-V)_hot_vari" : self.varilist[curr_row][3], "log(Z_cool)_vari" : self.varilist[curr_row][4], "log(age_cool)/10_vari" : self.varilist[curr_row][5], "M_cool_vari" : self.varilist[curr_row][6], "E(B-V)_cool_vari" : self.varilist[curr_row][7], "log(Z_hot)_err" : self.errlist[curr_row][0], "log(age_hot)/10_err" : self.errlist[curr_row][1], "M_hot_err" : self.errlist[curr_row][2], "E(B-V)_hot_err" : self.errlist[curr_row][3],  "log(Z_cool)_err" : self.errlist[curr_row][4], "log(age_cool)/10_err" : self.errlist[curr_row][5], "M_cool_err" : self.errlist[curr_row][6], "E(B-V)_cool_err" : self.errlist[curr_row][7], "F148W_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,0], "F148W_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,0], "F169M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,1],"F169M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,1], "F172M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,2], "F172M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,2], "N219M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,3], "N219M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,3], "N279N_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,4], "N279N_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,4], "f275w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,5], "f275w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,5], "f336w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,6], "f336w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,6], "f475w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,7], "f475w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,7], "f814w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,8], "f814w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,8], "f110w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,9], "f110w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,9], "f160w_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,10], "f160w_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,10]}
                    elif self.model_chosen == "UVIT_SDSS_Spitzer":
                        print("Running chisqfunc2 with average parameters to get Chi^2_avg to save in output.") 
                        rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc2(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],valid_filters_this_row,ul_filters_this_row,curr_row), "log(Z_hot)_avg" : self.avglist[curr_row][0], "log(age_hot)/10_avg" : self.avglist[curr_row][1], "M_hot_avg" : self.avglist[curr_row][2], "E(B-V)_hot_avg" : self.avglist[curr_row][3], "log(Z_cool)_avg" : self.avglist[curr_row][4], "log(age_cool)/10_avg" : self.avglist[curr_row][5], "M_cool_avg" : self.avglist[curr_row][6], "E(B-V)_cool_avg" : self.avglist[curr_row][7], "log(Z_hot)_vari" : self.varilist[curr_row][0], "log(age_hot)/10_vari" : self.varilist[curr_row][1], "M_hot_vari" : self.varilist[curr_row][2], "E(B-V)_hot_vari" : self.varilist[curr_row][3], "log(Z_cool)_vari" : self.varilist[curr_row][4], "log(age_cool)/10_vari" : self.varilist[curr_row][5], "M_cool_vari" : self.varilist[curr_row][6], "E(B-V)_cool_vari" : self.varilist[curr_row][7], "log(Z_hot)_err" : self.errlist[curr_row][0], "log(age_hot)/10_err" : self.errlist[curr_row][1], "M_hot_err" : self.errlist[curr_row][2], "E(B-V)_hot_err" : self.errlist[curr_row][3],  "log(Z_cool)_err" : self.errlist[curr_row][4], "log(age_cool)/10_err" : self.errlist[curr_row][5], "M_cool_err" : self.errlist[curr_row][6], "E(B-V)_cool_err" : self.errlist[curr_row][7], "F148W_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,0], "F148W_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,0], "F169M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,1],"F169M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,1], "F172M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,2], "F172M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,2], "N219M_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,3], "N219M_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,3], "N279N_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,4], "N279N_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,4], "u_prime_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,5], "u_prime_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,5], "g_prime_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,6], "g_prime_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,6], "r_prime_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,7], "r_prime_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,7], "i_prime_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,8], "i_prime_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,8], "z_prime_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,9], "z_prime_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,9], "IRAC1_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,10], "IRAC1_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,10],"IRAC2_hot_flux_AvgParams [mJy]" : hotmodels.iat[curr_row,11], "IRAC2_cool_flux_AvgParams [mJy]" : coolmodels.iat[curr_row,11]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.avgfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            

        elif self.triple_cluster == True:

            old_1_models = self.bandfluxes.copy(deep=True)
            old_2_models = self.bandfluxes.copy(deep=True)
            new_models = self.bandfluxes.copy(deep=True)
            self.truefluxerrors = self.bandfluxerrors.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
    
                best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestms[curr_row][0],self.bestcoords[curr_row][2],self.bestcoords[curr_row][3],self.bestcoords[curr_row][4],self.bestms[curr_row][1],self.bestcoords[curr_row][5],self.bestcoords[curr_row][6],self.bestms[curr_row][2],self.bestcoords[curr_row][7])
                old1,old2,new = self.minichisqfunc_triple(best_tup,valid_filters_this_row)
                usedold1 = 0
                usedold2 = 0
                usednew = 0
                for colno,col in enumerate(old_1_models.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        old_1_models.iat[curr_row,colno] = old1[usedold1]
                        usedold1 += 1
                for colno,col in enumerate(old_2_models.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        old_2_models.iat[curr_row,colno] = old2[usedold2]
                        usedold2 += 1
                for colno,col in enumerate(new_models.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        new_models.iat[curr_row,colno] = new[usednew]
                        usednew += 1

                for colno, arraytup in enumerate(zip(self.bandfluxerrors.loc[curr_row,:],self.ul_frame.loc[curr_row,:],self.bandfluxes.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        self.truefluxerrors.iat[curr_row,colno] = (arraytup[0])
                    if arraytup[1] == 1:
                        if self.ulmeth == "Limit":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[0]*-3)
                        elif self.ulmeth == "Standard":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[2]*-1/3)
                
            
            if self.bestchiparams == 1:
    
                colnames = {'Source_ID' : [], "Chi^2_best" : [], "log(Z_old_1)_best" : [], "log(age_old_1)/10_best" : [], "M_old_1_best" : [], "E(B-V)_old_best" : [], "log(Z_old_2)_best" : [], "log(age_old_2)/10_best" : [], "M_old_2_best" : [], "log(Z_new)_best" : [], "log(age_new)/10_best" : [], "M_new_best" : [], "E(B-V)_new_best" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_best" : self.bestchisqs[curr_row], "log(Z_old_1)_best" : self.bestcoords[curr_row][0], "log(age_old_1)/10_best" : self.bestcoords[curr_row][1], "M_old_1_best" : self.bestms[curr_row][0], "E(B-V)_old_best" : self.bestcoords[curr_row][2], "log(Z_old_2)_best" : self.bestcoords[curr_row][3], "log(age_old_2)/10_best" : self.bestcoords[curr_row][4], "M_old_2_best" : self.bestms[curr_row][1], "log(Z_new)_best" : self.bestcoords[curr_row][5], "log(age_new)/10_best" : self.bestcoords[curr_row][6], "M_new_best" : self.bestms[curr_row][2], "E(B-V)_new_best" : self.bestcoords[curr_row][7]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.bestfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            if self.avgchiparams == 1:

                if self.model_chosen == "UVIT_HST":        
                    colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(Z_old_1)_avg" : [], "log(age_old_1)/10_avg" : [], "M_old_1_avg" : [], "E(B-V)_old_avg" : [], "log(Z_old_2)_avg" : [], "log(age_old_2)/10_avg" : [], "M_old_2_avg" : [], "log(Z_new)_avg" : [], "log(age_new)/10_avg" : [], "M_new_avg" : [], "E(B-V)_new_avg" : [], "log(Z_old_1)_vari" : [], "log(age_old_1)/10_vari" : [], "M_old_1_vari" : [], "E(B-V)_old_vari" : [], "log(Z_old_2)_vari" : [], "log(age_old_2)/10_vari" : [], "M_old_2_vari" : [], "log(Z_new)_vari" : [], "log(age_new)/10_vari" : [], "M_new_vari" : [], "E(B-V)_new_vari" : [], "log(Z_old_1)_err" : [], "log(age_old_1)/10_err" : [], "M_old_1_err" : [], "E(B-V)_old_err" : [], "log(Z_old_2)_err" : [], "log(age_old_2)/10_err" : [], "M_old_2_err" : [], "log(Z_new)_err" : [], "log(age_new)/10_err" : [], "M_new_err" : [], "E(B-V)_new_err" : [], "F148W_old_1_flux_AvgParams [mJy]" : [], "F148W_old_2_flux_AvgParams [mJy]" : [], "F148W_new_flux_AvgParams [mJy]" : [], "F169M_old_1_flux_AvgParams [mJy]" : [], "F169M_old_2_flux_AvgParams [mJy]" : [], "F169M_new_flux_AvgParams [mJy]" : [], "F172M_old_1_flux_AvgParams [mJy]" : [], "F172M_old_2_flux_AvgParams [mJy]" : [], "F172M_new_flux_AvgParams [mJy]" : [], "N219M_old_1_flux_AvgParams [mJy]" : [], "N219M_old_2_flux_AvgParams [mJy]" : [], "N219M_new_flux_AvgParams [mJy]" : [], "N279N_old_1_flux_AvgParams [mJy]" : [], "N279N_old_2_flux_AvgParams [mJy]" : [], "N279N_new_flux_AvgParams [mJy]" : [], "f275w_old_1_flux_AvgParams [mJy]" : [], "f275w_old_2_flux_AvgParams [mJy]" : [], "f275w_new_flux_AvgParams [mJy]" : [], "f336w_old_1_flux_AvgParams [mJy]" : [], "f336w_old_2_flux_AvgParams [mJy]" : [], "f336w_new_flux_AvgParams [mJy]" : [], "f475w_old_1_flux_AvgParams [mJy]" : [], "f475w_old_2_flux_AvgParams [mJy]" : [], "f475w_new_flux_AvgParams [mJy]" : [], "f814w_old_1_flux_AvgParams [mJy]" : [], "f814w_old_2_flux_AvgParams [mJy]" : [], "f814w_new_flux_AvgParams [mJy]" : [], "f110w_old_1_flux_AvgParams [mJy]" : [], "f110w_old_2_flux_AvgParams [mJy]" : [], "f110w_new_flux_AvgParams [mJy]" : [], "f160w_old_1_flux_AvgParams [mJy]" : [], "f160w_old_2_flux_AvgParams [mJy]" : [], "f160w_new_flux_AvgParams [mJy]" : []}
                elif self.model_chosen == "UVIT_SDSS_Spitzer":
                    colnames = {'Source_ID' : [], "Chi^2_avg" : [], "log(Z_old_1)_avg" : [], "log(age_old_1)/10_avg" : [], "M_old_1_avg" : [], "E(B-V)_old_avg" : [], "log(Z_old_2)_avg" : [], "log(age_old_2)/10_avg" : [], "M_old_2_avg" : [], "log(Z_new)_avg" : [], "log(age_new)/10_avg" : [], "M_new_avg" : [], "E(B-V)_new_avg" : [], "log(Z_old_1)_vari" : [], "log(age_old_1)/10_vari" : [], "M_old_1_vari" : [], "E(B-V)_old_vari" : [], "log(Z_old_2)_vari" : [], "log(age_old_2)/10_vari" : [], "M_old_2_vari" : [], "log(Z_new)_vari" : [], "log(age_new)/10_vari" : [], "M_new_vari" : [], "E(B-V)_new_vari" : [], "log(Z_old_1)_err" : [], "log(age_old_1)/10_err" : [], "M_old_1_err" : [], "E(B-V)_old_err" : [], "log(Z_old_2)_err" : [], "log(age_old_2)/10_err" : [], "M_old_2_err" : [], "log(Z_new)_err" : [], "log(age_new)/10_err" : [], "M_new_err" : [], "E(B-V)_new_err" : [], "F148W_old_1_flux_AvgParams [mJy]" : [], "F148W_old_2_flux_AvgParams [mJy]" : [], "F148W_new_flux_AvgParams [mJy]" : [], "F169M_old_1_flux_AvgParams [mJy]" : [], "F169M_old_2_flux_AvgParams [mJy]" : [], "F169M_new_flux_AvgParams [mJy]" : [], "F172M_old_1_flux_AvgParams [mJy]" : [], "F172M_old_2_flux_AvgParams [mJy]" : [], "F172M_new_flux_AvgParams [mJy]" : [], "N219M_old_1_flux_AvgParams [mJy]" : [], "N219M_old_2_flux_AvgParams [mJy]" : [], "N219M_new_flux_AvgParams [mJy]" : [], "N279N_old_1_flux_AvgParams [mJy]" : [], "N279N_old_2_flux_AvgParams [mJy]" : [], "N279N_new_flux_AvgParams [mJy]" : [], "u_prime_old_1_flux_AvgParams [mJy]" : [], "u_prime_old_2_flux_AvgParams [mJy]" : [], "u_prime_new_flux_AvgParams [mJy]" : [], "g_prime_old_1_flux_AvgParams [mJy]" : [], "g_prime_old_2_flux_AvgParams [mJy]" : [], "g_prime_new_flux_AvgParams [mJy]" : [], "r_prime_old_1_flux_AvgParams [mJy]" : [], "r_prime_old_2_flux_AvgParams [mJy]" : [], "r_prime_new_flux_AvgParams [mJy]" : [], "i_prime_old_1_flux_AvgParams [mJy]" : [], "i_prime_old_2_flux_AvgParams [mJy]" : [], "i_prime_new_flux_AvgParams [mJy]" : [], "z_prime_old_1_flux_AvgParams [mJy]" : [], "z_prime_old_2_flux_AvgParams [mJy]" : [], "z_prime_new_flux_AvgParams [mJy]" : [], "IRAC1_old_1_flux_AvgParams [mJy]" : [], "IRAC1_old_2_flux_AvgParams [mJy]" : [], "IRAC1_new_flux_AvgParams [mJy]" : [], "IRAC2_old_1_flux_AvgParams [mJy]" : [], "IRAC2_old_2_flux_AvgParams [mJy]" : [], "IRAC2_new_flux_AvgParams [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    valid_filters_this_row = []
                    for valid_ind,bflux in enumerate(self.bandfluxes.loc[curr_row,:]):
                        if np.isnan(bflux) == False:
                            valid_filters_this_row.append(valid_ind)
                    if self.model_chosen == "UVIT_HST":
                        print("Running chisqfunc3 with average parameters to get Chi^2_avg to save in output.") 
                        rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc3(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],self.avglist[curr_row][8],self.avglist[curr_row][9],self.avglist[curr_row][10],valid_filters_this_row,ul_filters_this_row,curr_row), "log(Z_old_1)_avg" : self.avglist[curr_row][0], "log(age_old_1)/10_avg" : self.avglist[curr_row][1], "M_old_1_avg" : self.avglist[curr_row][2], "E(B-V)_old_avg" : self.avglist[curr_row][3], "log(Z_old_2)_avg" : self.avglist[curr_row][4], "log(age_old_2)/10_avg" : self.avglist[curr_row][5], "M_old_2_avg" : self.avglist[curr_row][6], "log(Z_new)_avg" : self.avglist[curr_row][7], "log(age_new)/10_avg" : self.avglist[curr_row][8], "M_new_avg" : self.avglist[curr_row][9], "E(B-V)_new_avg" : self.avglist[curr_row][10], "log(Z_old_1)_vari" : self.varilist[curr_row][0], "log(age_old_1)/10_vari" : self.varilist[curr_row][1], "M_old_1_vari" : self.varilist[curr_row][2], "E(B-V)_old_vari" : self.varilist[curr_row][3], "log(Z_old_2)_vari" : self.varilist[curr_row][4], "log(age_old_2)/10_vari" : self.varilist[curr_row][5], "M_old_2_vari" : self.varilist[curr_row][6], "log(Z_new)_vari" : self.varilist[curr_row][7], "log(age_new)/10_vari" : self.varilist[curr_row][8], "M_new_vari" : self.varilist[curr_row][9], "E(B-V)_new_vari" : self.varilist[curr_row][10], "log(Z_old_1)_err" : self.errlist[curr_row][0], "log(age_old_1)/10_err" : self.errlist[curr_row][1], "M_old_1_err" : self.errlist[curr_row][2], "E(B-V)_old_err" : self.errlist[curr_row][3], "log(Z_old_2)_err" : self.errlist[curr_row][4], "log(age_old_2)/10_err" : self.errlist[curr_row][5], "M_old_2_err" : self.errlist[curr_row][6], "log(Z_new)_err" : self.errlist[curr_row][7], "log(age_new)/10_err" : self.errlist[curr_row][8], "M_new_err" : self.errlist[curr_row][9], "E(B-V)_new_err" : self.errlist[curr_row][10], "F148W_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,0], "F148W_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,0], "F148W_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,0], "F169M_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,1], "F169M_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,1], "F169M_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,1], "F172M_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,2], "F172M_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,2], "F172M_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,2], "N219M_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,3], "N219M_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,3], "N219M_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,3], "N279N_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,4], "N279N_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,4], "N279N_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,4], "f275w_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,5], "f275w_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,5], "f275w_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,5], "f336w_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,6], "f336w_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,6], "f336w_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,6], "f475w_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,7], "f475w_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,7], "f475w_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,7], "f814w_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,8], "f814w_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,8], "f814w_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,8], "f110w_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,9], "f110w_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,9], "f110w_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,9], "f160w_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,10], "f160w_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,10], "f160w_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,10]}
                    elif self.model_chosen == "UVIT_SDSS_Spitzer":
                        print("Running chisqfunc3 with average parameters to get Chi^2_avg to save in output.") 
                        rowdict = {'Source_ID' : self.source_ids[curr_row], "Chi^2_avg" : self.chisqfunc3(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],self.avglist[curr_row][8],self.avglist[curr_row][9],self.avglist[curr_row][10],valid_filters_this_row,ul_filters_this_row,curr_row), "log(Z_old_1)_avg" : self.avglist[curr_row][0], "log(age_old_1)/10_avg" : self.avglist[curr_row][1], "M_old_1_avg" : self.avglist[curr_row][2], "E(B-V)_old_avg" : self.avglist[curr_row][3], "log(Z_old_2)_avg" : self.avglist[curr_row][4], "log(age_old_2)/10_avg" : self.avglist[curr_row][5], "M_old_2_avg" : self.avglist[curr_row][6], "log(Z_new)_avg" : self.avglist[curr_row][7], "log(age_new)/10_avg" : self.avglist[curr_row][8], "M_new_avg" : self.avglist[curr_row][9], "E(B-V)_new_avg" : self.avglist[curr_row][10], "log(Z_old_1)_vari" : self.varilist[curr_row][0], "log(age_old_1)/10_vari" : self.varilist[curr_row][1], "M_old_1_vari" : self.varilist[curr_row][2], "E(B-V)_old_vari" : self.varilist[curr_row][3], "log(Z_old_2)_vari" : self.varilist[curr_row][4], "log(age_old_2)/10_vari" : self.varilist[curr_row][5], "M_old_2_vari" : self.varilist[curr_row][6], "log(Z_new)_vari" : self.varilist[curr_row][7], "log(age_new)/10_vari" : self.varilist[curr_row][8], "M_new_vari" : self.varilist[curr_row][9], "E(B-V)_new_vari" : self.varilist[curr_row][10], "log(Z_old_1)_err" : self.errlist[curr_row][0], "log(age_old_1)/10_err" : self.errlist[curr_row][1], "M_old_1_err" : self.errlist[curr_row][2], "E(B-V)_old_err" : self.errlist[curr_row][3], "log(Z_old_2)_err" : self.errlist[curr_row][4], "log(age_old_2)/10_err" : self.errlist[curr_row][5], "M_old_2_err" : self.errlist[curr_row][6], "log(Z_new)_err" : self.errlist[curr_row][7], "log(age_new)/10_err" : self.errlist[curr_row][8], "M_new_err" : self.errlist[curr_row][9], "E(B-V)_new_err" : self.errlist[curr_row][10], "F148W_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,0], "F148W_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,0], "F148W_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,0], "F169M_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,1], "F169M_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,1], "F169M_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,1], "F172M_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,2], "F172M_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,2], "F172M_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,2], "N219M_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,3], "N219M_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,3], "N219M_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,3], "N279N_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,4], "N279N_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,4], "N279N_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,4], "u_prime_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,5], "u_prime_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,5], "u_prime_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,5], "g_prime_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,6], "g_prime_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,6], "g_prime_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,6], "r_prime_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,7], "r_prime_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,7], "r_prime_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,7], "i_prime_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,8], "i_prime_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,8], "i_prime_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,8], "z_prime_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,9], "z_prime_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,9], "z_prime_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,9], "IRAC1_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,10], "IRAC1_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,10], "IRAC1_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,10], "IRAC2_old_1_flux_AvgParams [mJy]" : old_1_models.iat[curr_row,11], "IRAC2_old_2_flux_AvgParams [mJy]" : old_2_models.iat[curr_row,11], "IRAC2_new_flux_AvgParams [mJy]" : new_models.iat[curr_row,11]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.avgfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  


    def display_results_single(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x900+250+20")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
            if np.isnan(arraytup[0]) == False:
                valid_filters_this_row.append(valid_ind)
            if arraytup[1] == 1:
                ul_filters_this_row.append(valid_ind)
        valid_notul_filters_this_row = [i for i in valid_filters_this_row if i not in ul_filters_this_row]

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_notul_fluxes_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])
    
        valid_ul_fluxes_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_notul_errors_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_ul_errors_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind]*-1)  

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_notul_avgwv_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_ul_avgwv_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        best_tup = (self.bestcoords[curr_row][0],self.bestcoords[curr_row][1],self.bestms[curr_row],self.bestcoords[curr_row][2])
        avg_tup = (self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_notul_avgwv_this_row,valid_notul_fluxes_this_row,yerr=valid_notul_errors_this_row,fmt="o",color="orange")
        if self.model_chosen == "UVIT_HST":
            abc.errorbar(valid_ul_avgwv_this_row,valid_ul_fluxes_this_row,yerr=valid_ul_errors_this_row,uplims=True,fmt="o",color="green")
        abc.plot(valid_avgwv_this_row,self.minichisqfunc_single(avg_tup,valid_filters_this_row),color="blue")

        if self.plotscale == 1:
            pass

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            abc.set_xticks([140,200,500,1000,1500])
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=6,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=220)
        textbox2 = tk.Text(topw,height=6,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=250)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=420)
        textbox3 = tk.Text(topw,height=6,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=450)
        label4 = tk.Label(topw,text="Avg. model fluxes (y, blue):")
        label4.place(x=50,y=620)
        textbox4 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_single(avg_tup,valid_filters_this_row)):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=650)
        groove1 = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove1.place(x=405,y=625)
        label5 = tk.Label(topw,text="Best chi^2 value")
        label5.place(x=425,y=635)
        label5a = tk.Label(topw,text="{}".format(format(self.bestchisqs[curr_row],'.6e')),font=("Arial",12))
        label5a.place(x=437,y=685)
        groove2 = tk.Canvas(topw,width=285,height=120,bd=4,relief=tk.RIDGE)
        groove2.place(x=405,y=755)
        label6 = tk.Label(topw,text="Chi^2 value for average parameters")
        label6.place(x=425,y=765)
        print("Running chisqfunc with average parameters to get Chi^2_avg to display in output window.")
        label6a = tk.Label(topw,text="{}".format(format(self.chisqfunc(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],valid_filters_this_row,ul_filters_this_row,curr_row),'.6e')),font=("Arial",12))
        label6a.place(x=437,y=815)
        
        import math
        Z_sticker1 = format(self.bestcoords[curr_row][0],'.6e')
        Z_sticker2 = format(self.avglist[curr_row][0],'.6e')
        Z_sticker3 = format(self.varilist[curr_row][0],'.6e')
        Z_sticker4 = format(self.errlist[curr_row][0],'.6e')

        age_sticker1 = format(self.bestcoords[curr_row][1],'.6e')
        age_sticker2 = format(self.avglist[curr_row][1],'.6e')
        age_sticker3 = format(self.varilist[curr_row][1],'.6e')
        age_sticker4 = format(self.errlist[curr_row][1],'.6e')

        M_sticker1 = format(self.bestms[curr_row],'.6e')
        M_sticker2 = format(self.avglist[curr_row][2],'.6e')
        M_sticker3 = format(self.varilist[curr_row][2],'.6e')
        M_sticker4 = format(self.errlist[curr_row][2],'.6e')

        ebv_sticker1 = format(self.bestcoords[curr_row][2],'.6e')
        ebv_sticker2 = format(self.avglist[curr_row][3],'.6e')
        ebv_sticker3 = format(self.varilist[curr_row][3],'.6e')
        ebv_sticker4 = format(self.errlist[curr_row][3],'.6e')

        colpack1 = tk.Frame(topw)
        colpack1.place(x=850,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=965,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=1100,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1220,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1330,y=600)

        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=10)
        parameter1 = tk.Label(colpack1,text="log(Z)").pack(pady=10)
        parameter2 = tk.Label(colpack1,text="log(age)/10").pack(pady=10)
        parameter3 = tk.Label(colpack1,text="M").pack(pady=10)
        parameter4 = tk.Label(colpack1,text="E(B-V)").pack(pady=10)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=10)
        best1 = tk.Label(colpack2,text="{}".format(Z_sticker1)).pack(pady=10)
        best2 = tk.Label(colpack2,text="{}".format(age_sticker1)).pack(pady=10)
        best3 = tk.Label(colpack2,text="{}".format(M_sticker1)).pack(pady=10)
        best4 = tk.Label(colpack2,text="{}".format(ebv_sticker1)).pack(pady=10)
        errlohead = tk.Label(colpack3,text="Average value",bg="azure").pack(pady=10)
        errlo1 = tk.Label(colpack3,text="{}".format(Z_sticker2)).pack(pady=10)
        errlo2 = tk.Label(colpack3,text="{}".format(age_sticker2)).pack(pady=10)
        errlo3 = tk.Label(colpack3,text="{}".format(M_sticker2)).pack(pady=10)
        errlo4 = tk.Label(colpack3,text="{}".format(ebv_sticker2)).pack(pady=10)
        noteslohead = tk.Label(colpack4,text="Variance",bg="azure").pack(pady=10)
        noteslo1 = tk.Label(colpack4,text="{}".format(Z_sticker3)).pack(pady=10)
        noteslo2 = tk.Label(colpack4,text="{}".format(age_sticker3)).pack(pady=10)
        noteslo2 = tk.Label(colpack4,text="{}".format(M_sticker3)).pack(pady=10)
        noteslo4 = tk.Label(colpack4,text="{}".format(ebv_sticker3)).pack(pady=10)
        errhihead = tk.Label(colpack5,text="Error",bg="azure").pack(pady=10)
        errhi1 = tk.Label(colpack5,text="{}".format(Z_sticker4)).pack(pady=10)
        errhi2 = tk.Label(colpack5,text="{}".format(age_sticker4)).pack(pady=10)
        errhi3 = tk.Label(colpack5,text="{}".format(M_sticker4)).pack(pady=10)
        errhi4 = tk.Label(colpack5,text="{}".format(ebv_sticker4)).pack(pady=10)

        def closethesource():
            topw.destroy()

        groove3 = tk.Canvas(topw,width=200,height=120,bd=4,relief=tk.RIDGE)
        groove3.place(x=605,y=625)
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=632,y=670)
        topw.mainloop()

    
    def display_results_double(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x900+250+20")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
            if np.isnan(arraytup[0]) == False:
                valid_filters_this_row.append(valid_ind)
            if arraytup[1] == 1:
                ul_filters_this_row.append(valid_ind)
        valid_notul_filters_this_row = [i for i in valid_filters_this_row if i not in ul_filters_this_row]

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_notul_fluxes_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])
    
        valid_ul_fluxes_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_notul_errors_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_ul_errors_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind]*-1)  

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_notul_avgwv_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_ul_avgwv_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])
    

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        #best_tup = (self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3],self.results[curr_row].x[4],self.results[curr_row].x[5],self.results[curr_row].x[6],self.results[curr_row].x[7])
        avg_tup = (self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_notul_avgwv_this_row,valid_notul_fluxes_this_row,yerr=valid_notul_errors_this_row,fmt="o",color="orange")
        if self.model_chosen == "UVIT_HST":
            abc.errorbar(valid_ul_avgwv_this_row,valid_ul_fluxes_this_row,yerr=valid_ul_errors_this_row,uplims=True,fmt="o",color="green")
        hotmod = self.minichisqfunc_double(avg_tup,valid_filters_this_row)[0]
        coolmod = self.minichisqfunc_double(avg_tup,valid_filters_this_row)[1]
        abc.plot(valid_avgwv_this_row,hotmod,color="red")
        abc.plot(valid_avgwv_this_row,coolmod,color="blue")
        sumofmodels = [hotmod[i] + coolmod[i] for i in range(len(hotmod))]
        abc.plot(valid_avgwv_this_row,sumofmodels,color="limegreen")

        if self.plotscale == 1:
            pass

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            abc.set_xticks([140,200,500,1000,1500])
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=6,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=195)
        textbox2 = tk.Text(topw,height=6,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=225)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=370)
        textbox3 = tk.Text(topw,height=6,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=400)
        label4 = tk.Label(topw,text="Hot cluster model fluxes (y, red):")
        label4.place(x=50,y=545)
        textbox4 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_double(avg_tup,valid_filters_this_row)[0]):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=575)
        label5 = tk.Label(topw,text="Cool cluster model fluxes (y, blue):")
        label5.place(x=50,y=720)
        textbox5 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_double(avg_tup,valid_filters_this_row)[1]):
            textbox5.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox5.place(x=50,y=750)
        groove1 = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove1.place(x=405,y=625)
        label5 = tk.Label(topw,text="Best chi^2 value")
        label5.place(x=425,y=635)
        label5a = tk.Label(topw,text="{}".format(format(self.bestchisqs[curr_row],'.6e')),font=("Arial",12))
        label5a.place(x=437,y=685)
        groove2 = tk.Canvas(topw,width=285,height=120,bd=4,relief=tk.RIDGE)
        groove2.place(x=405,y=755)
        label6 = tk.Label(topw,text="Chi^2 value for average parameters")
        label6.place(x=425,y=765)
        print("Running chisqfunc2 with average parameters to get Chi^2_avg to display in output window.")
        label6a = tk.Label(topw,text="{}".format(format(self.chisqfunc2(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],valid_filters_this_row,ul_filters_this_row,curr_row),'.6e')),font=("Arial",12))
        label6a.place(x=437,y=815)

        import math
        Z_hot_sticker1 = format(self.bestcoords[curr_row][0],'.6e')
        Z_hot_sticker2 = format(self.avglist[curr_row][0],'.6e')
        Z_hot_sticker3 = format(self.varilist[curr_row][0],'.6e')
        Z_hot_sticker4 = format(self.errlist[curr_row][0],'.6e')

        age_hot_sticker1 = format(self.bestcoords[curr_row][1],'.6e')
        age_hot_sticker2 = format(self.avglist[curr_row][1],'.6e')
        age_hot_sticker3 = format(self.varilist[curr_row][1],'.6e')
        age_hot_sticker4 = format(self.errlist[curr_row][1],'.6e')

        M_hot_sticker1 = format(self.bestms[curr_row][0],'.6e')
        M_hot_sticker2 = format(self.avglist[curr_row][2],'.6e')
        M_hot_sticker3 = format(self.varilist[curr_row][2],'.6e')
        M_hot_sticker4 = format(self.errlist[curr_row][2],'.6e')

        ebv_hot_sticker1 = format(self.bestcoords[curr_row][2],'.6e')
        ebv_hot_sticker2 = format(self.avglist[curr_row][3],'.6e')
        ebv_hot_sticker3 = format(self.varilist[curr_row][3],'.6e')
        ebv_hot_sticker4 = format(self.errlist[curr_row][3],'.6e')

        Z_cool_sticker1 = format(self.bestcoords[curr_row][3],'.6e')
        Z_cool_sticker2 = format(self.avglist[curr_row][4],'.6e')
        Z_cool_sticker3 = format(self.varilist[curr_row][4],'.6e')
        Z_cool_sticker4 = format(self.errlist[curr_row][4],'.6e')

        age_cool_sticker1 = format(self.bestcoords[curr_row][4],'.6e')
        age_cool_sticker2 = format(self.avglist[curr_row][5],'.6e')
        age_cool_sticker3 = format(self.varilist[curr_row][5],'.6e')
        age_cool_sticker4 = format(self.errlist[curr_row][5],'.6e')

        M_cool_sticker1 = format(self.bestms[curr_row][1],'.6e')
        M_cool_sticker2 = format(self.avglist[curr_row][6],'.6e')
        M_cool_sticker3 = format(self.varilist[curr_row][6],'.6e')
        M_cool_sticker4 = format(self.errlist[curr_row][6],'.6e')

        ebv_cool_sticker1 = format(self.bestcoords[curr_row][5],'.6e')
        ebv_cool_sticker2 = format(self.avglist[curr_row][7],'.6e')
        ebv_cool_sticker3 = format(self.varilist[curr_row][7],'.6e')
        ebv_cool_sticker4 = format(self.errlist[curr_row][7],'.6e')

        colpack1 = tk.Frame(topw)
        colpack1.place(x=850,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=980,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=1100,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1220,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1330,y=600)
        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=3)
        parameter1 = tk.Label(colpack1,text="log(Z_hot)").pack(pady=3)
        parameter2 = tk.Label(colpack1,text="log(age_hot)/10").pack(pady=3)
        parameter3 = tk.Label(colpack1,text="M_hot").pack(pady=3)
        parameter4 = tk.Label(colpack1,text="E(B-V)_hot").pack(pady=3)
        parameter5 = tk.Label(colpack1,text="log(Z_cool)").pack(pady=3)
        parameter6 = tk.Label(colpack1,text="log(age_cool)/10").pack(pady=3)
        parameter7 = tk.Label(colpack1,text="M_cool").pack(pady=3)
        parameter8 = tk.Label(colpack1,text="E(B-V)_cool").pack(pady=3)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=3)
        best1 = tk.Label(colpack2,text="{}".format(Z_hot_sticker1)).pack(pady=3)
        best2 = tk.Label(colpack2,text="{}".format(age_hot_sticker1)).pack(pady=3)
        best3 = tk.Label(colpack2,text="{}".format(M_hot_sticker1)).pack(pady=3)
        best4 = tk.Label(colpack2,text="{}".format(ebv_hot_sticker1)).pack(pady=3)
        best5 = tk.Label(colpack2,text="{}".format(Z_cool_sticker1)).pack(pady=3)
        best6 = tk.Label(colpack2,text="{}".format(age_cool_sticker1)).pack(pady=3)
        best7 = tk.Label(colpack2,text="{}".format(M_cool_sticker1)).pack(pady=3)
        best8 = tk.Label(colpack2,text="{}".format(ebv_cool_sticker1)).pack(pady=3)
        errlohead = tk.Label(colpack3,text="Average value",bg="azure").pack(pady=3)
        errlo1 = tk.Label(colpack3,text="{}".format(Z_hot_sticker2)).pack(pady=3)
        errlo2 = tk.Label(colpack3,text="{}".format(age_hot_sticker2)).pack(pady=3)
        errlo3 = tk.Label(colpack3,text="{}".format(M_hot_sticker2)).pack(pady=3)
        errlo4 = tk.Label(colpack3,text="{}".format(ebv_hot_sticker2)).pack(pady=3)
        errlo5 = tk.Label(colpack3,text="{}".format(Z_cool_sticker2)).pack(pady=3)
        errlo6 = tk.Label(colpack3,text="{}".format(age_cool_sticker2)).pack(pady=3)
        errlo7 = tk.Label(colpack3,text="{}".format(M_cool_sticker2)).pack(pady=3)
        errlo8 = tk.Label(colpack3,text="{}".format(ebv_cool_sticker2)).pack(pady=3)
        noteslohead = tk.Label(colpack4,text="Variance",bg="azure").pack(pady=3)
        noteslo1 = tk.Label(colpack4,text="{}".format(Z_hot_sticker3)).pack(pady=3)
        noteslo2 = tk.Label(colpack4,text="{}".format(age_hot_sticker3)).pack(pady=3)
        noteslo3 = tk.Label(colpack4,text="{}".format(M_hot_sticker3)).pack(pady=3)
        noteslo4 = tk.Label(colpack4,text="{}".format(ebv_hot_sticker3)).pack(pady=3)
        noteslo5 = tk.Label(colpack4,text="{}".format(Z_cool_sticker3)).pack(pady=3)
        noteslo6 = tk.Label(colpack4,text="{}".format(age_cool_sticker3)).pack(pady=3)
        noteslo7 = tk.Label(colpack4,text="{}".format(M_cool_sticker3)).pack(pady=3)
        noteslo8 = tk.Label(colpack4,text="{}".format(ebv_cool_sticker3)).pack(pady=3)
        errhihead = tk.Label(colpack5,text="Error",bg="azure").pack(pady=3)
        errhi1 = tk.Label(colpack5,text="{}".format(Z_hot_sticker4)).pack(pady=3)
        errhi2 = tk.Label(colpack5,text="{}".format(age_hot_sticker4)).pack(pady=3)
        errhi3 = tk.Label(colpack5,text="{}".format(M_hot_sticker4)).pack(pady=3)
        errhi4 = tk.Label(colpack5,text="{}".format(ebv_hot_sticker4)).pack(pady=3)
        errhi5 = tk.Label(colpack5,text="{}".format(Z_cool_sticker4)).pack(pady=3)
        errhi6 = tk.Label(colpack5,text="{}".format(age_cool_sticker4)).pack(pady=3)
        errhi7 = tk.Label(colpack5,text="{}".format(M_cool_sticker4)).pack(pady=3)
        errhi8 = tk.Label(colpack5,text="{}".format(ebv_cool_sticker4)).pack(pady=3)

        def closethesource():
            topw.destroy()
        groove3 = tk.Canvas(topw,width=200,height=120,bd=4,relief=tk.RIDGE)
        groove3.place(x=605,y=625)
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=632,y=670)
        topw.mainloop()

    def display_results_triple(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x1000+250+0")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
            if np.isnan(arraytup[0]) == False:
                valid_filters_this_row.append(valid_ind)
            if arraytup[1] == 1:
                ul_filters_this_row.append(valid_ind)
        valid_notul_filters_this_row = [i for i in valid_filters_this_row if i not in ul_filters_this_row]

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_notul_fluxes_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])
    
        valid_ul_fluxes_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_notul_errors_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_ul_errors_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind]*-1)  

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_notul_avgwv_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_ul_avgwv_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])
    

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        avg_tup = (self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],self.avglist[curr_row][8],self.avglist[curr_row][9],self.avglist[curr_row][10])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_notul_avgwv_this_row,valid_notul_fluxes_this_row,yerr=valid_notul_errors_this_row,fmt="o",color="orange")
        if self.model_chosen == "UVIT_HST":
            abc.errorbar(valid_ul_avgwv_this_row,valid_ul_fluxes_this_row,yerr=valid_ul_errors_this_row,uplims=True,fmt="o",color="green")
        old1mod = self.minichisqfunc_triple(avg_tup,valid_filters_this_row)[0]
        old2mod = self.minichisqfunc_triple(avg_tup,valid_filters_this_row)[1]
        newmod = self.minichisqfunc_triple(avg_tup,valid_filters_this_row)[2]
        abc.plot(valid_avgwv_this_row,old1mod,color="red")
        abc.plot(valid_avgwv_this_row,old2mod,color="blue")
        abc.plot(valid_avgwv_this_row,newmod,color="m")
        sumofmodels = [old1mod[i] + old2mod[i] + newmod[i] for i in range(len(old1mod))]
        abc.plot(valid_avgwv_this_row,sumofmodels,color="limegreen")

        if self.plotscale == 1:
            pass

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            abc.set_xticks([140,200,500,1000,1500])
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=5,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=165)
        textbox2 = tk.Text(topw,height=5,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=195)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=310)
        textbox3 = tk.Text(topw,height=5,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=340)
        label4 = tk.Label(topw,text="Old_1 cluster model fluxes (y, red):")
        label4.place(x=50,y=455)
        textbox4 = tk.Text(topw,height=5,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_triple(avg_tup,valid_filters_this_row)[0]):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=485)
        label5 = tk.Label(topw,text="Old_2 cluster model fluxes (y, blue):")
        label5.place(x=50,y=600)
        textbox5 = tk.Text(topw,height=5,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_triple(avg_tup,valid_filters_this_row)[1]):
            textbox5.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox5.place(x=50,y=630)
        label6 = tk.Label(topw,text="Young cluster model fluxes (y, majenta):")
        label6.place(x=50,y=745)
        textbox6 = tk.Text(topw,height=5,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_triple(avg_tup,valid_filters_this_row)[2]):
            textbox6.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox6.place(x=50,y=775)
        groove1 = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove1.place(x=405,y=625)
        label5 = tk.Label(topw,text="Best chi^2 value")
        label5.place(x=425,y=635)
        label5a = tk.Label(topw,text="{}".format(format(self.bestchisqs[curr_row],'.6e')),font=("Arial",12))
        label5a.place(x=437,y=685)
        groove2 = tk.Canvas(topw,width=285,height=120,bd=4,relief=tk.RIDGE)
        groove2.place(x=405,y=755)
        label6 = tk.Label(topw,text="Chi^2 value for average parameters")
        label6.place(x=425,y=765)
        print("Running chisqfunc3 with average parameters to get Chi^2_avg to display in output window.")
        label6a = tk.Label(topw,text="{}".format(format(self.chisqfunc3(self.avglist[curr_row][0],self.avglist[curr_row][1],self.avglist[curr_row][2],self.avglist[curr_row][3],self.avglist[curr_row][4],self.avglist[curr_row][5],self.avglist[curr_row][6],self.avglist[curr_row][7],self.avglist[curr_row][8],self.avglist[curr_row][9],self.avglist[curr_row][10],valid_filters_this_row,ul_filters_this_row,curr_row),'.6e')),font=("Arial",12))
        label6a.place(x=437,y=815)
        
        import math
        Z_old_1_sticker1 = format(self.bestcoords[curr_row][0],'.6e')
        Z_old_1_sticker2 = format(self.avglist[curr_row][0],'.6e')
        Z_old_1_sticker3 = format(self.varilist[curr_row][0],'.6e')
        Z_old_1_sticker4 = format(self.errlist[curr_row][0],'.6e')

        age_old_1_sticker1 = format(self.bestcoords[curr_row][1],'.6e')
        age_old_1_sticker2 = format(self.avglist[curr_row][1],'.6e')
        age_old_1_sticker3 = format(self.varilist[curr_row][1],'.6e')
        age_old_1_sticker4 = format(self.errlist[curr_row][1],'.6e')

        M_old_1_sticker1 = format(self.bestms[curr_row][0],'.6e')
        M_old_1_sticker2 = format(self.avglist[curr_row][2],'.6e')
        M_old_1_sticker3 = format(self.varilist[curr_row][2],'.6e')
        M_old_1_sticker4 = format(self.errlist[curr_row][2],'.6e')

        ebv_old_sticker1 = format(self.bestcoords[curr_row][2],'.6e')
        ebv_old_sticker2 = format(self.avglist[curr_row][3],'.6e')
        ebv_old_sticker3 = format(self.varilist[curr_row][3],'.6e')
        ebv_old_sticker4 = format(self.errlist[curr_row][3],'.6e')

        Z_old_2_sticker1 = format(self.bestcoords[curr_row][3],'.6e')
        Z_old_2_sticker2 = format(self.avglist[curr_row][4],'.6e')
        Z_old_2_sticker3 = format(self.varilist[curr_row][4],'.6e')
        Z_old_2_sticker4 = format(self.errlist[curr_row][4],'.6e')

        age_old_2_sticker1 = format(self.bestcoords[curr_row][4],'.6e')
        age_old_2_sticker2 = format(self.avglist[curr_row][5],'.6e')
        age_old_2_sticker3 = format(self.varilist[curr_row][5],'.6e')
        age_old_2_sticker4 = format(self.errlist[curr_row][5],'.6e')

        M_old_2_sticker1 = format(self.bestms[curr_row][1],'.6e')
        M_old_2_sticker2 = format(self.avglist[curr_row][6],'.6e')
        M_old_2_sticker3 = format(self.varilist[curr_row][6],'.6e')
        M_old_2_sticker4 = format(self.errlist[curr_row][6],'.6e')

        Z_new_sticker1 = format(self.bestcoords[curr_row][5],'.6e')
        Z_new_sticker2 = format(self.avglist[curr_row][7],'.6e')
        Z_new_sticker3 = format(self.varilist[curr_row][7],'.6e')
        Z_new_sticker4 = format(self.errlist[curr_row][7],'.6e')

        age_new_sticker1 = format(self.bestcoords[curr_row][6],'.6e')
        age_new_sticker2 = format(self.avglist[curr_row][8],'.6e')
        age_new_sticker3 = format(self.varilist[curr_row][8],'.6e')
        age_new_sticker4 = format(self.errlist[curr_row][8],'.6e')

        M_new_sticker1 = format(self.bestms[curr_row][2],'.6e')
        M_new_sticker2 = format(self.avglist[curr_row][9],'.6e')
        M_new_sticker3 = format(self.varilist[curr_row][9],'.6e')
        M_new_sticker4 = format(self.errlist[curr_row][9],'.6e')

        ebv_new_sticker1 = format(self.bestcoords[curr_row][7],'.6e')
        ebv_new_sticker2 = format(self.avglist[curr_row][10],'.6e')
        ebv_new_sticker3 = format(self.varilist[curr_row][10],'.6e')
        ebv_new_sticker4 = format(self.errlist[curr_row][10],'.6e')

        colpack1 = tk.Frame(topw)
        colpack1.place(x=850,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=980,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=1100,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1220,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1330,y=600)
        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=3)
        parameter1 = tk.Label(colpack1,text="log(Z_old_1)").pack(pady=3)
        parameter2 = tk.Label(colpack1,text="log(age_old_1)/10").pack(pady=3)
        parameter3 = tk.Label(colpack1,text="M_old_1").pack(pady=3)
        parameter4 = tk.Label(colpack1,text="E(B-V)_old").pack(pady=3)
        parameter5 = tk.Label(colpack1,text="log(Z_old_2)").pack(pady=3)
        parameter6 = tk.Label(colpack1,text="log(age_old_2)/10").pack(pady=3)
        parameter7 = tk.Label(colpack1,text="M_old_2").pack(pady=3)
        parameter9 = tk.Label(colpack1,text="log(Z_young)").pack(pady=3)
        parameter10 = tk.Label(colpack1,text="log(age_young)/10").pack(pady=3)
        parameter11 = tk.Label(colpack1,text="M_young").pack(pady=3)
        parameter8 = tk.Label(colpack1,text="E(B-V)_young").pack(pady=3)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=3)
        best1 = tk.Label(colpack2,text="{}".format(Z_old_1_sticker1)).pack(pady=3)
        best2 = tk.Label(colpack2,text="{}".format(age_old_1_sticker1)).pack(pady=3)
        best3 = tk.Label(colpack2,text="{}".format(M_old_1_sticker1)).pack(pady=3)
        best4 = tk.Label(colpack2,text="{}".format(ebv_old_sticker1)).pack(pady=3)
        best5 = tk.Label(colpack2,text="{}".format(Z_old_2_sticker1)).pack(pady=3)
        best6 = tk.Label(colpack2,text="{}".format(age_old_2_sticker1)).pack(pady=3)
        best7 = tk.Label(colpack2,text="{}".format(M_old_2_sticker1)).pack(pady=3)
        best9 = tk.Label(colpack2,text="{}".format(Z_new_sticker1)).pack(pady=3)
        best10 = tk.Label(colpack2,text="{}".format(age_new_sticker1)).pack(pady=3)
        best11 = tk.Label(colpack2,text="{}".format(M_new_sticker1)).pack(pady=3)
        best8 = tk.Label(colpack2,text="{}".format(ebv_new_sticker1)).pack(pady=3)
        errlohead = tk.Label(colpack3,text="Average value",bg="azure").pack(pady=3)
        errlo1 = tk.Label(colpack3,text="{}".format(Z_old_1_sticker2)).pack(pady=3)
        errlo2 = tk.Label(colpack3,text="{}".format(age_old_1_sticker2)).pack(pady=3)
        errlo3 = tk.Label(colpack3,text="{}".format(M_old_1_sticker2)).pack(pady=3)
        errlo4 = tk.Label(colpack3,text="{}".format(ebv_old_sticker2)).pack(pady=3)
        errlo5 = tk.Label(colpack3,text="{}".format(Z_old_2_sticker2)).pack(pady=3)
        errlo6 = tk.Label(colpack3,text="{}".format(age_old_2_sticker2)).pack(pady=3)
        errlo7 = tk.Label(colpack3,text="{}".format(M_old_2_sticker2)).pack(pady=3)
        errlo9 = tk.Label(colpack3,text="{}".format(Z_new_sticker2)).pack(pady=3)
        errlo10 = tk.Label(colpack3,text="{}".format(age_new_sticker2)).pack(pady=3)
        errlo11 = tk.Label(colpack3,text="{}".format(M_new_sticker2)).pack(pady=3)
        errlo8 = tk.Label(colpack3,text="{}".format(ebv_new_sticker2)).pack(pady=3)
        noteslohead = tk.Label(colpack4,text="Variance",bg="azure").pack(pady=3)
        noteslo1 = tk.Label(colpack4,text="{}".format(Z_old_1_sticker3)).pack(pady=3)
        noteslo2 = tk.Label(colpack4,text="{}".format(age_old_1_sticker3)).pack(pady=3)
        noteslo3 = tk.Label(colpack4,text="{}".format(M_old_1_sticker3)).pack(pady=3)
        noteslo4 = tk.Label(colpack4,text="{}".format(ebv_old_sticker3)).pack(pady=3)
        noteslo5 = tk.Label(colpack4,text="{}".format(Z_old_2_sticker3)).pack(pady=3)
        noteslo6 = tk.Label(colpack4,text="{}".format(age_old_2_sticker3)).pack(pady=3)
        noteslo7 = tk.Label(colpack4,text="{}".format(M_old_2_sticker3)).pack(pady=3)
        noteslo9 = tk.Label(colpack4,text="{}".format(Z_new_sticker3)).pack(pady=3)
        noteslo10 = tk.Label(colpack4,text="{}".format(age_new_sticker3)).pack(pady=3)
        noteslo11 = tk.Label(colpack4,text="{}".format(M_new_sticker3)).pack(pady=3)
        noteslo8 = tk.Label(colpack4,text="{}".format(ebv_new_sticker3)).pack(pady=3)
        errhihead = tk.Label(colpack5,text="Error",bg="azure").pack(pady=3)
        errhi1 = tk.Label(colpack5,text="{}".format(Z_old_1_sticker4)).pack(pady=3)
        errhi2 = tk.Label(colpack5,text="{}".format(age_old_1_sticker4)).pack(pady=3)
        errhi3 = tk.Label(colpack5,text="{}".format(M_old_1_sticker4)).pack(pady=3)
        errhi4 = tk.Label(colpack5,text="{}".format(ebv_old_sticker4)).pack(pady=3)
        errhi5 = tk.Label(colpack5,text="{}".format(Z_old_2_sticker4)).pack(pady=3)
        errhi6 = tk.Label(colpack5,text="{}".format(age_old_2_sticker4)).pack(pady=3)
        errhi7 = tk.Label(colpack5,text="{}".format(M_old_2_sticker4)).pack(pady=3)
        errhi9 = tk.Label(colpack5,text="{}".format(Z_new_sticker4)).pack(pady=3)
        errhi10 = tk.Label(colpack5,text="{}".format(age_new_sticker4)).pack(pady=3)
        errhi11 = tk.Label(colpack5,text="{}".format(M_new_sticker4)).pack(pady=3)
        errhi8 = tk.Label(colpack5,text="{}".format(ebv_new_sticker4)).pack(pady=3)


        def closethesource():
            topw.destroy()
        groove3 = tk.Canvas(topw,width=200,height=120,bd=4,relief=tk.RIDGE)
        groove3.place(x=605,y=625)
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=632,y=670)
        topw.mainloop()


go = ChiSquared()